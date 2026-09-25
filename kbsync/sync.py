"""Pure delta logic: compare local Markdown with what the store already holds."""

from __future__ import annotations

from dataclasses import dataclass, field

from kbsync.converter import MarkdownDoc
from kbsync.store import RemoteDoc


@dataclass
class SyncPlan:
    add: list[MarkdownDoc] = field(default_factory=list)
    update: list[tuple[MarkdownDoc, RemoteDoc]] = field(default_factory=list)
    skip: list[MarkdownDoc] = field(default_factory=list)
    remove: list[RemoteDoc] = field(default_factory=list)

    def summary(self) -> str:
        return f"added={len(self.add)} updated={len(self.update)} skipped={len(self.skip)} removed={len(self.remove)}"


def plan_sync(local: list[MarkdownDoc], remote: dict[str, RemoteDoc], *, prune: bool) -> SyncPlan:
    """Decide per article whether to add, replace, or skip; optionally remove vanished ones.

    Args:
        local: freshly rendered documents.
        remote: slug -> document currently in the store.
        prune: when True, remote documents whose slug no longer exists locally are removed.
            Callers must pass False for partial scrapes (for example with --limit).
    """
    plan = SyncPlan()
    local_slugs: set[str] = set()
    for doc in local:
        local_slugs.add(doc.slug)
        existing = remote.get(doc.slug)
        if existing is None:
            plan.add.append(doc)
        elif existing.content_hash != doc.content_hash:
            plan.update.append((doc, existing))
        else:
            plan.skip.append(doc)
    if prune:
        plan.remove.extend(r for slug, r in remote.items() if slug not in local_slugs)
    return plan
