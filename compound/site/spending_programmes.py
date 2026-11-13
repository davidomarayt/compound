"""Validated 2026 allocation atlas for Where's My Money?.

Each row is a published amount, but rows are *not* automatically additive:
some are parent/child allocations, some are incremental Budget measures and
some have different departmental reporting boundaries from their headline
sector. We never present their sum as an official sector decomposition.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from copy import deepcopy
from urllib.parse import urlparse

VALID_QUALIFIERS = {"exact", "approx", "over", "under", "almost"}
VALID_SECTORS = {"social", "health", "education", "housing", "transport", "justice", "other", "debt"}


def amount_display(amount_m: float, qualifier: str) -> str:
    """Respect the source qualifier; do not turn lower bounds into exact claims."""
    if amount_m >= 1000:
        value = f"€{amount_m / 1000:g}bn"
    else:
        value = f"€{amount_m:g}m"
    prefix = {"exact": "", "approx": "About ", "over": "Over ",
              "under": "Under ", "almost": "Almost "}[qualifier]
    return prefix + value


def prepare_programmes(spending: dict, register: dict) -> dict:
    if register.get("year") != 2026 or register.get("units") != "EUR million":
        raise ValueError("Expected 2026 EUR million programme register")
    categories = deepcopy(spending.get("categories") or [])
    sector_by_id = {sector["id"]: sector for sector in categories}
    if set(sector_by_id) != VALID_SECTORS:
        raise ValueError("Programmes must connect to the eight known spending sectors")

    programmes = []
    by_slug = {}
    for row in register.get("programmes") or []:
        p = dict(row)
        slug = str(p.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in by_slug:
            raise ValueError(f"Invalid or duplicate programme slug: {slug}")
        sector_id = p.get("sector")
        if sector_id not in sector_by_id:
            raise ValueError(f"Unknown programme sector: {sector_id}")
        amount_m = p.get("amount_m")
        if not isinstance(amount_m, (int, float)) or not math.isfinite(amount_m) or amount_m <= 0:
            raise ValueError(f"Invalid programme amount: {slug}")
        if p.get("year") != 2026 or p.get("qualifier") not in VALID_QUALIFIERS:
            raise ValueError(f"Unsupported programme year/qualifier: {slug}")
        uri = urlparse(str(p.get("source") or ""))
        if uri.scheme != "https" or not uri.hostname or not (uri.hostname.endswith(".gov.ie") or uri.hostname.endswith(".oireachtas.ie") or uri.hostname == "www.garda.ie" or uri.hostname == "www.nationaltransport.ie"):
            raise ValueError(f"Untrusted programme source: {slug}")
        for key in ("title", "description", "limitation", "kind", "source_label"):
            if len(str(p.get(key) or "").strip()) < 8:
                raise ValueError(f"Missing {key} on programme: {slug}")
        p["sector_name"] = sector_by_id[sector_id]["name"]
        p["sector_url"] = sector_by_id[sector_id]["url"]
        p["url"] = sector_by_id[sector_id]["url"] + slug + "/"
        p["amount_label"] = amount_display(amount_m, p["qualifier"])
        p["reporting_basis_note"] = (
            "This is a budget allocation, forecast or selected published measure, not an audited year-end outturn."
        )
        programmes.append(p)
        by_slug[slug] = p

    if not 30 <= len(programmes) <= 200:
        raise ValueError("Programme register incomplete or unbounded")
    if min(Counter(p["sector"] for p in programmes).values()) < 3:
        raise ValueError("Every sector needs at least three documented programme amounts")
    for p in programmes:
        parent_id = p.get("parent")
        if parent_id:
            parent = by_slug.get(parent_id)
            if not parent or parent["sector"] != p["sector"] or p["amount_m"] > parent["amount_m"]:
                raise ValueError(f"Invalid parent/component relation for {p['slug']}")
            p["parent_record"] = {"title": parent["title"], "url": parent["url"]}
        else:
            p["parent_record"] = None

    for category in categories:
        entries = [p for p in programmes if p["sector"] == category["id"]]
        entries.sort(key=lambda p: (-p["amount_m"], p["slug"]))
        max_m = max(p["amount_m"] for p in entries)
        for p in entries:
            p["bar_width"] = max(0.5, p["amount_m"] / max_m * 100)
            p["siblings"] = [
                {"url": other["url"], "title": other["title"], "amount_label": other["amount_label"]}
                for other in entries if other["slug"] != p["slug"]
            ][:5]
        category["programmes"] = entries
    return {**spending, "categories": categories, "programmes": programmes,
            "programme_count": len(programmes), "programme_updated": register["verified_on"]}
