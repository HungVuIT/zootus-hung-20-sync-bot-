"""Thin wrapper around the Gemini File Search API (create store, list/upload/delete documents, ask)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors, types

log = logging.getLogger(__name__)

META_SLUG = "slug"
META_HASH = "content_hash"
META_URL = "url"
META_UPDATED = "updated_at"
META_ARTICLE_ID = "article_id"


@dataclass(frozen=True)
class RemoteDoc:
    """A document already present in the store, identified by the metadata we attached on upload."""

    name: str
    slug: str
    content_hash: str
    url: str = ""
    updated_at: str = ""


@dataclass
class Citation:
    title: str
    url: str


@dataclass
class Answer:
    text: str
    citations: list[Citation] = field(default_factory=list)


def _meta_to_dict(meta: list[types.CustomMetadata] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in meta or []:
        if m.key and m.string_value is not None:
            out[m.key] = m.string_value
    return out


class KnowledgeStore:
    """Manages one File Search store whose documents carry slug + content-hash metadata.

    The store itself is the source of truth for change detection: a stateless container can
    rebuild the full slug-to-hash map from list_documents() on every run.
    """

    def __init__(
        self,
        api_key: str,
        display_name: str,
        *,
        chunk_max_tokens: int = 400,
        chunk_overlap_tokens: int = 60,
        poll_interval: float = 2.0,
        max_retries: int = 3,
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._display_name = display_name
        self._chunking = types.ChunkingConfig(
            white_space_config=types.WhiteSpaceConfig(
                max_tokens_per_chunk=chunk_max_tokens, max_overlap_tokens=chunk_overlap_tokens
            )
        )
        self._poll_interval = poll_interval
        self._max_retries = max_retries
        self._store_name: str | None = None

    # ---- store -------------------------------------------------------------------------
    @property
    def store_name(self) -> str:
        if self._store_name is None:
            raise RuntimeError("call ensure_store() first")
        return self._store_name

    def ensure_store(self) -> str:
        """Find the store by display name or create it. Returns the resource name."""
        for store in self._client.file_search_stores.list():
            if store.display_name == self._display_name and store.name:
                self._store_name = store.name
                log.info("Using existing File Search store %s (%s)", store.name, self._display_name)
                return store.name
        created = self._client.file_search_stores.create(
            config=types.CreateFileSearchStoreConfig(display_name=self._display_name)
        )
        if not created.name:
            raise RuntimeError("File Search store creation returned no name")
        self._store_name = created.name
        log.info("Created File Search store %s (%s)", created.name, self._display_name)
        return created.name

    def stats(self) -> types.FileSearchStore:
        return self._client.file_search_stores.get(name=self.store_name)

    # ---- documents ---------------------------------------------------------------------
    def list_documents(self) -> dict[str, RemoteDoc]:
        """Map slug -> RemoteDoc for every document that carries our metadata."""
        found: dict[str, RemoteDoc] = {}
        for doc in self._client.file_search_stores.documents.list(parent=self.store_name):
            meta = _meta_to_dict(doc.custom_metadata)
            slug = meta.get(META_SLUG)
            if not slug or not doc.name:
                continue
            found[slug] = RemoteDoc(
                name=doc.name,
                slug=slug,
                content_hash=meta.get(META_HASH, ""),
                url=meta.get(META_URL, ""),
                updated_at=meta.get(META_UPDATED, ""),
            )
        return found

    def upload(
        self, path: Path, *, slug: str, content_hash: str, url: str, updated_at: str, article_id: int
    ) -> str:
        """Upload one Markdown file and block until it is indexed. Returns the document name."""
        config = types.UploadToFileSearchStoreConfig(
            display_name=path.name,
            mime_type="text/markdown",
            chunking_config=self._chunking,
            custom_metadata=[
                types.CustomMetadata(key=META_SLUG, string_value=slug),
                types.CustomMetadata(key=META_HASH, string_value=content_hash),
                types.CustomMetadata(key=META_URL, string_value=url),
                types.CustomMetadata(key=META_UPDATED, string_value=updated_at),
                types.CustomMetadata(key=META_ARTICLE_ID, numeric_value=article_id),
            ],
        )
        for attempt in range(1, self._max_retries + 1):
            try:
                op = self._client.file_search_stores.upload_to_file_search_store(
                    file=str(path), file_search_store_name=self.store_name, config=config
                )
                while not op.done:
                    time.sleep(self._poll_interval)
                    op = self._client.operations.get(op)
                if op.error:
                    raise RuntimeError(f"indexing failed: {op.error}")
                return _document_name_from_operation(op)
            except (errors.APIError, RuntimeError) as exc:
                if attempt == self._max_retries or not _retryable(exc):
                    raise
                wait = 2.0**attempt
                log.warning(
                    "upload %s failed (%s); retry %d/%d in %.0fs", path.name, exc, attempt, self._max_retries, wait
                )
                time.sleep(wait)
        raise RuntimeError("unreachable")

    def delete(self, doc_name: str) -> None:
        self._client.file_search_stores.documents.delete(name=doc_name, config=types.DeleteDocumentConfig(force=True))

    # ---- querying ----------------------------------------------------------------------
    def ask(self, question: str, *, model: str, system_prompt: str) -> Answer:
        """Answer a question grounded on the store, returning text + cited article URLs."""
        response = self._client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[types.Tool(file_search=types.FileSearch(file_search_store_names=[self.store_name]))],
            ),
        )
        answer = Answer(text=response.text or "")
        seen: set[str] = set()
        candidates = response.candidates or []
        grounding = candidates[0].grounding_metadata if candidates else None
        for chunk in (grounding.grounding_chunks if grounding else None) or []:
            ctx = chunk.retrieved_context
            if ctx is None:
                continue
            title = ctx.title or ""
            url = _url_from_chunk_text(ctx.text or "")
            key = url or title
            if key and key not in seen:
                seen.add(key)
                answer.citations.append(Citation(title=title, url=url))
        return answer


def _document_name_from_operation(op: Any) -> str:
    resp = op.response
    if resp is not None:
        for attr in ("document_name", "name"):
            value = getattr(resp, attr, None)
            if value:
                return str(value)
        if isinstance(resp, dict):
            for key in ("documentName", "document_name", "name"):
                if resp.get(key):
                    return str(resp[key])
    raise RuntimeError(f"upload finished without a document name: {op}")


def _retryable(exc: Exception) -> bool:
    if isinstance(exc, errors.APIError):
        return exc.code in (408, 429, 500, 502, 503, 504)
    return "indexing failed" not in str(exc)


def _url_from_chunk_text(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Article URL:"):
            return line.removeprefix("Article URL:").strip()
        if line.startswith("url:"):
            return line.removeprefix("url:").strip()
    return ""
