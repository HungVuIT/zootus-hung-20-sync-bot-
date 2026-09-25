"""Scrape support.optisigns.com to Markdown and sync the delta into a Gemini File Search store.

Usage:
    python main.py                 # daily run: scrape the 100 most recently updated articles -> upload delta
    python main.py --limit 5       # ad-hoc smoke test on 5 articles (never prunes)
    python main.py --scrape-only   # write Markdown files, touch nothing in Gemini
    python main.py --ask "How do I add a YouTube video?"   # grounded sanity check with citations

Exit code 0 on success, 1 if any upload failed or the run aborted.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from kbsync.config import Settings
from kbsync.converter import MarkdownDoc, estimate_chunks, render_article
from kbsync.scraper import RawArticle, ZendeskClient
from kbsync.store import KnowledgeStore
from kbsync.sync import SyncPlan, plan_sync

log = logging.getLogger("kbsync")
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="ad-hoc scope: only the N most recently updated articles; disables pruning "
        "(default: ARTICLE_LIMIT from the environment, 100; 0 = all)",
    )
    p.add_argument("--scrape-only", action="store_true", help="write Markdown but do not touch Gemini")
    p.add_argument("--no-prune", action="store_true", help="never delete store documents missing locally")
    p.add_argument("--ask", metavar="QUESTION", help="ask the assistant one grounded question and exit")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def write_markdown(articles: list[RawArticle], out_dir: Path, *, prune_stale: bool) -> list[MarkdownDoc]:
    out_dir.mkdir(parents=True, exist_ok=True)
    docs: list[MarkdownDoc] = []
    for a in articles:
        doc = render_article(
            slug=a.slug,
            article_id=a.id,
            title=a.title,
            url=a.html_url,
            section=a.section,
            category=a.category,
            updated_at=a.updated_at,
            body_html=a.body_html,
        )
        (out_dir / doc.filename).write_text(doc.content, encoding="utf-8", newline="\n")
        docs.append(doc)
    if prune_stale:  # keep the folder an exact mirror of the current scope
        keep = {d.filename for d in docs}
        for stale in out_dir.glob("*.md"):
            if stale.name not in keep:
                stale.unlink()
    log.info("Wrote %d Markdown files to %s", len(docs), out_dir)
    return docs


def apply_plan(
    plan: SyncPlan, store: KnowledgeStore, articles_by_slug: dict[str, RawArticle], settings: Settings
) -> tuple[int, dict[str, str]]:
    """Execute uploads/deletes concurrently. Returns (failure count, slug -> document name)."""
    failures = 0
    doc_names: dict[str, str] = {}

    def do_upload(doc: MarkdownDoc, replace_name: str | None) -> tuple[str, str]:
        art = articles_by_slug[doc.slug]
        name = store.upload(
            settings.articles_dir / doc.filename,
            slug=doc.slug,
            content_hash=doc.content_hash,
            url=art.html_url,
            updated_at=art.updated_at,
            article_id=art.id,
        )
        if replace_name:  # upload first, then drop the stale copy, so the bot never sees a gap
            store.delete(replace_name)
        return doc.slug, name

    jobs = [(doc, None) for doc in plan.add] + [(doc, old.name) for doc, old in plan.update]
    with ThreadPoolExecutor(max_workers=settings.upload_workers) as pool:
        futures = {pool.submit(do_upload, doc, old): doc for doc, old in jobs}
        for fut in as_completed(futures):
            doc = futures[fut]
            try:
                slug, name = fut.result()
                doc_names[slug] = name
                log.info("indexed %s", doc.filename)
            except Exception as exc:  # noqa: BLE001 - one bad file must not kill the run
                failures += 1
                log.error("FAILED %s: %s", doc.filename, exc)

    for old in plan.remove:
        try:
            store.delete(old.name)
            log.info("removed %s (no longer published)", old.slug)
        except Exception as exc:  # noqa: BLE001
            failures += 1
            log.error("FAILED to remove %s: %s", old.slug, exc)
    return failures, doc_names


def run_sync(args: argparse.Namespace, settings: Settings) -> int:
    started = time.monotonic()
    zendesk = ZendeskClient(settings.zendesk_base_url, settings.zendesk_locale)
    ad_hoc = args.limit is not None
    limit = args.limit if ad_hoc else settings.article_limit
    log.info(
        "Scope: %s articles (all 'Popular Articles' + most recently updated)%s",
        limit or "all",
        " (ad-hoc, no pruning)" if ad_hoc else "",
    )
    articles = zendesk.fetch_articles(limit=limit)
    docs = write_markdown(articles, settings.articles_dir, prune_stale=not ad_hoc)
    chunk_estimates = {d.slug: estimate_chunks(d.content, settings.chunk_max_tokens, settings.chunk_overlap_tokens) for d in docs}

    if args.scrape_only:
        log.info("SUMMARY scraped=%d files=%d chunks_est=%d (scrape-only)", len(articles), len(docs), sum(chunk_estimates.values()))
        return 0

    store = KnowledgeStore(
        settings.gemini_api_key,
        settings.store_display_name,
        chunk_max_tokens=settings.chunk_max_tokens,
        chunk_overlap_tokens=settings.chunk_overlap_tokens,
    )
    store.ensure_store()
    remote = store.list_documents()
    log.info("Store currently holds %d tracked documents", len(remote))

    prune = not args.no_prune and not ad_hoc
    plan = plan_sync(docs, remote, prune=prune)
    log.info("Plan: %s", plan.summary())

    failures, doc_names = apply_plan(plan, store, {a.slug: a for a in articles}, settings)
    touched = [d for d in plan.add] + [d for d, _ in plan.update]
    embedded_files = len([d for d in touched if d.slug in doc_names])
    embedded_chunks = sum(chunk_estimates[d.slug] for d in touched if d.slug in doc_names)

    stats = store.stats()
    summary = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "duration_s": round(time.monotonic() - started, 1),
        "scraped": len(articles),
        "added": len(plan.add),
        "updated": len(plan.update),
        "skipped": len(plan.skip),
        "removed": len(plan.remove),
        "failed": failures,
        "embedded_files": embedded_files,
        "embedded_chunks_est": embedded_chunks,
        "store": {
            "name": store.store_name,
            "active_documents": stats.active_documents_count,
            "pending_documents": stats.pending_documents_count,
            "failed_documents": stats.failed_documents_count,
            "size_bytes": stats.size_bytes,
        },
        "chunking": {"max_tokens_per_chunk": settings.chunk_max_tokens, "max_overlap_tokens": settings.chunk_overlap_tokens},
    }
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    state = {
        slug: {"content_hash": d.content_hash, "chunks_est": chunk_estimates[slug]}
        for slug, d in ((d.slug, d) for d in docs)
    }
    (settings.data_dir / "state.json").write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    log.info(
        "SUMMARY added=%d updated=%d skipped=%d removed=%d failed=%d | embedded files=%d chunks~%d | store active=%s size=%sB",
        summary["added"], summary["updated"], summary["skipped"], summary["removed"], summary["failed"],
        embedded_files, embedded_chunks, stats.active_documents_count, stats.size_bytes,
    )
    return 1 if failures else 0


def run_ask(question: str, settings: Settings) -> int:
    store = KnowledgeStore(settings.gemini_api_key, settings.store_display_name)
    store.ensure_store()
    answer = store.ask(question, model=settings.gemini_model, system_prompt=PROMPT_PATH.read_text(encoding="utf-8"))
    print(f"Q: {question}\n\n{answer.text.strip()}\n")
    if answer.citations:
        print("Grounding sources:")
        for c in answer.citations:
            print(f"  - {c.title}  {c.url}".rstrip())
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    try:
        settings = Settings.from_env()
        if args.ask:
            return run_ask(args.ask, settings)
        return run_sync(args, settings)
    except Exception as exc:  # noqa: BLE001 - surface a clean message and non-zero exit for the scheduler
        log.exception("Run aborted: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
