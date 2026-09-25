"""Unit tests for delta planning and slug derivation."""

from __future__ import annotations

from kbsync.converter import MarkdownDoc
from kbsync.scraper import assign_slugs, select_scope, slug_from_url
from kbsync.store import RemoteDoc
from kbsync.sync import plan_sync


def _doc(slug: str, h: str) -> MarkdownDoc:
    return MarkdownDoc(slug=slug, filename=f"{slug}.md", content="x", content_hash=h)


def _remote(slug: str, h: str) -> RemoteDoc:
    return RemoteDoc(name=f"fileSearchStores/s/documents/{slug}", slug=slug, content_hash=h)


def test_plan_sync_classifies_add_update_skip_remove() -> None:
    local = [_doc("a", "1"), _doc("b", "2-new"), _doc("c", "3")]
    remote = {"b": _remote("b", "2-old"), "c": _remote("c", "3"), "gone": _remote("gone", "9")}

    plan = plan_sync(local, remote, prune=True)

    assert [d.slug for d in plan.add] == ["a"]
    assert [(d.slug, r.slug) for d, r in plan.update] == [("b", "b")]
    assert [d.slug for d in plan.skip] == ["c"]
    assert [r.slug for r in plan.remove] == ["gone"]
    assert plan.summary() == "added=1 updated=1 skipped=1 removed=1"


def test_plan_sync_without_prune_never_removes() -> None:
    plan = plan_sync([], {"gone": _remote("gone", "9")}, prune=False)
    assert plan.remove == []


def test_slug_from_url_uses_url_part_not_id() -> None:
    url = "https://support.optisigns.com/hc/en-us/articles/360051014713-How-to-Use-YouTube-with-OptiSigns"
    assert slug_from_url(url, "ignored") == "how-to-use-youtube-with-optisigns"


def test_slug_from_url_falls_back_to_title() -> None:
    assert slug_from_url("https://x/hc/en-us/articles/123", "  Hello, World!  ") == "hello-world"


def _art(i: int, updated: str, promoted: bool = False) -> dict[str, object]:
    return {"id": i, "updated_at": updated, "promoted": promoted}


def test_select_scope_keeps_all_promoted_then_most_recent() -> None:
    arts = [
        _art(1, "2020-01-01", promoted=True),  # old but popular -> always in
        _art(2, "2026-09-01"),
        _art(3, "2026-09-03"),
        _art(4, "2026-09-02"),
        _art(5, "2019-01-01"),
    ]
    assert [a["id"] for a in select_scope(arts, 3)] == [1, 3, 4]
    assert [a["id"] for a in select_scope(arts, 0)] == [1, 3, 4, 2, 5]
    assert [a["id"] for a in select_scope(list(reversed(arts)), 3)] == [1, 3, 4]  # order-independent


def test_assign_slugs_is_deterministic_on_collisions() -> None:
    newer = (200, "https://x/hc/en-us/articles/200-Same-Title", "Same Title")
    older = (100, "https://x/hc/en-us/articles/100-Same-Title", "Same Title")
    other = (300, "https://x/hc/en-us/articles/300-Other", "Other")
    assert assign_slugs([newer, older, other]) == assign_slugs([older, other, newer])
    assert assign_slugs([newer, older]) == {100: "same-title", 200: "same-title-200"}
