"""Fetch Help Center articles through the public Zendesk Help Center API."""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import requests

log = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"/articles/\d+-(.+?)/?$")
_NON_SLUG = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class RawArticle:
    """One article exactly as Zendesk returns it, plus resolved breadcrumb names."""

    id: int
    title: str
    html_url: str
    body_html: str
    updated_at: str
    section: str
    category: str
    slug: str


def slug_from_url(html_url: str, title: str) -> str:
    """Derive a filesystem-safe slug from the article URL (fallback: title)."""
    m = _SLUG_RE.search(html_url)
    raw = m.group(1) if m else title
    slug = _NON_SLUG.sub("-", raw.lower()).strip("-")
    return slug or "article"


class ZendeskClient:
    """Minimal read-only client for /api/v2/help_center (no auth needed for public centers)."""

    def __init__(self, base_url: str, locale: str = "en-us", timeout: float = 30.0) -> None:
        self._base = f"{base_url}/api/v2/help_center/{locale}"
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "kb-sync-bot/1.0 (+help-center-markdown-sync)"

    def _paginate(self, resource: str, sort: str = "") -> Iterator[dict[str, Any]]:
        url: str | None = f"{self._base}/{resource}.json?per_page=100{sort}"
        while url:
            resp = self._session.get(url, timeout=self._timeout)
            resp.raise_for_status()
            payload = resp.json()
            yield from payload.get(resource, [])
            url = payload.get("next_page")

    def fetch_articles(self, limit: int = 0) -> list[RawArticle]:
        """Return published (non-draft) articles, most recently updated first, with unique slugs.

        Args:
            limit: size of the job's scope (0 = all): every promoted "Popular Article" plus the
                most recently updated articles to fill the remaining slots. An edited or newly
                published article enters the window, the least recently updated one drops out
                and is pruned from the store.
        """
        sections = {s["id"]: s for s in self._paginate("sections")}
        categories = {c["id"]: c["name"] for c in self._paginate("categories")}
        log.info("Zendesk: %d sections, %d categories", len(sections), len(categories))

        published = [
            raw
            for raw in self._paginate("articles", sort="&sort_by=updated_at&sort_order=desc")
            if not raw.get("draft") and raw.get("body")
        ]
        raws = select_scope(published, limit)
        log.info(
            "Zendesk: %d published, %d promoted ('Popular Articles'), scope %d",
            len(published), sum(1 for r in published if r.get("promoted")), len(raws),
        )

        slugs = assign_slugs([(int(r["id"]), r["html_url"], r["title"]) for r in raws])
        articles: list[RawArticle] = []
        for raw in raws:
            section = sections.get(raw.get("section_id"), {})
            articles.append(
                RawArticle(
                    id=int(raw["id"]),
                    title=raw["title"].strip(),
                    html_url=raw["html_url"],
                    body_html=raw["body"],
                    updated_at=raw.get("edited_at") or raw.get("updated_at") or "",
                    section=section.get("name", ""),
                    category=categories.get(section.get("category_id"), ""),
                    slug=slugs[int(raw["id"])],
                )
            )
        log.info("Zendesk: fetched %d articles", len(articles))
        return articles


def select_scope(articles: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Pick the articles the job keeps in the store.

    Promoted articles (the Help Center's "Popular Articles" block) are always included; the
    remaining slots up to ``limit`` go to the most recently updated articles. ``limit`` 0 = all.
    Ordering inside each group is by updated_at descending, then id, so the result is stable.
    """
    ordered = sorted(articles, key=lambda a: (a.get("updated_at") or "", -int(a["id"])), reverse=True)
    promoted = [a for a in ordered if a.get("promoted")]
    others = [a for a in ordered if not a.get("promoted")]
    scope = promoted + others
    return scope[:limit] if limit else scope


def assign_slugs(items: list[tuple[int, str, str]]) -> dict[int, str]:
    """Map article id -> unique slug, deterministically regardless of input order.

    When two articles share a slug the one with the smallest id keeps the plain slug and
    the others get an '-<id>' suffix, so file names never flip between runs.
    """
    groups: dict[str, list[int]] = {}
    for article_id, url, title in items:
        groups.setdefault(slug_from_url(url, title), []).append(article_id)
    out: dict[int, str] = {}
    for slug, ids in groups.items():
        for i, article_id in enumerate(sorted(ids)):
            out[article_id] = slug if i == 0 else f"{slug}-{article_id}"
    return out
