"""Poll every registered source and store unseen items.

First poll of a source: the newest FIRST_RUN_BACKFILL items are queued as 'new'; the rest are
stored as 'seen' so the owner is not sent a year of back-catalogue.
"""
from __future__ import annotations

import logging

from compound.config import Settings
from compound.db import Database
from compound.sources import Source

log = logging.getLogger(__name__)


def poll_all(db: Database, sources: list[Source], settings: Settings, *, dry_run: bool = False) -> list[int]:
    new_ids: list[int] = []
    for src in sources:
        try:
            new_ids.extend(poll_source(db, src, settings, dry_run=dry_run))
        except Exception:  # one broken source must not stop the others
            log.exception("polling %s failed", src.key)
    return new_ids


def poll_source(db: Database, src: Source, settings: Settings, *, dry_run: bool = False) -> list[int]:
    row = db.ensure_source(src.key, src.name, src.pillar)
    first_run = not row["initialised"]
    items = src.fetch()
    log.info("%s: %d items listed", src.key, len(items))
    if dry_run:
        for it in items[:10]:
            flag = "seen" if db.item_exists(src.key, it.external_id) else "NEW "
            print(f"  [{flag}] {it.external_id}  {it.title}  {it.url}")
        return []

    new_ids: list[int] = []
    backfill = max(0, settings.first_run_backfill)
    for idx, it in enumerate(items):
        if db.item_exists(src.key, it.external_id):
            continue
        status = "new"
        if first_run and idx >= backfill:
            status = "seen"
        item_id = db.insert_item(
            source_key=src.key,
            external_id=it.external_id,
            pillar=src.pillar,
            title=it.title,
            url=it.url,
            summary=it.summary,
            published_at=it.published_at,
            status=status,
        )
        if status == "new":
            new_ids.append(item_id)
    db.mark_source_polled(src.key, initialised=True)
    return new_ids


def load_source_text(db: Database, src: Source, item_id: int) -> str:
    """Fetch and cache the readable text of an item's page. Empty string if it cannot be fetched."""
    item = db.get_item(item_id)
    if item is None:
        return ""
    if item["source_text"]:
        return item["source_text"]
    if not item["url"]:
        return ""
    try:
        text = src.fetch_text(item["url"])
    except Exception:
        log.exception("could not fetch %s", item["url"])
        return ""
    db.set_item_source_text(item_id, text)
    return text
