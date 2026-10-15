"""Concise earnings hub: newest filings first, searchable full verified archive."""
from __future__ import annotations


def prepare_recent_earnings(companies: list[dict], *, limit: int = 10) -> tuple[list[dict], list[dict]]:
    """Sort by actual SEC filing date, not when backfill happened or quarter ended.

    No duplicate quarterly article URLs are created. Search metadata is limited
    to already-public, source-verified company information.
    """
    if limit < 1:
        raise ValueError("Recent earnings limit must be positive")
    ordered = sorted(
        companies,
        key=lambda c: (
            c["report"].get("latest_filed") or "",
            c["report"]["latest_end"],
            c["symbol"],
        ),
        reverse=True,
    )
    index = [
        {
            "name": company["name"],
            "ticker": company["symbol"],
            "url": company["url"],
            "period": company["report"]["latest_label"],
            "ended": company["report"]["latest_end"],
            "filed": company["report"].get("latest_filed") or "",
        }
        for company in ordered
    ]
    return ordered[:limit], index
