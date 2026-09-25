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

    def _paginate(self, resource: str) -> Iterator[dict[str, Any]]:
        url: str | None = f"{self._base}/{resource}.json?per_page=100&sort_by=created_at&sort_order=asc"
        while url:
            resp = self._session.get(url, timeout=self._timeout)
            resp.raise_for_status()
            payload = resp.json()
            yield from payload.get(resource, [])
            url = payload.get("next_page")

    def fetch_articles(self, limit: int = 0) -> list[RawArticle]:
        """Return all published (non-draft) articles, oldest first, with unique slugs.

        Args:
            limit: stop after this many articles (0 = no limit). Useful for smoke tests.
        """
        sections = {s["id"]: s for s in self._paginate("sections")}
        categories = {c["id"]: c["name"] for c in self._paginate("categories")}
        log.info("Zendesk: %d sections, %d categories", len(sections), len(categories))

        articles: list[RawArticle] = []
        seen_slugs: set[str] = set()
        for raw in self._paginate("articles"):
            if raw.get("draft") or not raw.get("body"):
                continue
            section = sections.get(raw.get("section_id"), {})
            slug = slug_from_url(raw["html_url"], raw["title"])
            if slug in seen_slugs:  # oldest article keeps the plain slug, newer ones get the id suffix
                slug = f"{slug}-{raw['id']}"
            seen_slugs.add(slug)
            articles.append(
                RawArticle(
                    id=int(raw["id"]),
                    title=raw["title"].strip(),
                    html_url=raw["html_url"],
                    body_html=raw["body"],
                    updated_at=raw.get("edited_at") or raw.get("updated_at") or "",
                    section=section.get("name", ""),
                    category=categories.get(section.get("category_id"), ""),
                    slug=slug,
                )
            )
            if limit and len(articles) >= limit:
                break
        log.info("Zendesk: fetched %d articles", len(articles))
        return articles
