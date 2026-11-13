"""2026 voted supply-grant layer for Compound.ie.

The Dáil's individual Vote ceilings are *net Exchequer supply grants* and are
not equivalent to gross sector expenditure or to the published programme
announcements. This module validates and connects them without manufacturing
subhead allocations or residual balances.
"""
from __future__ import annotations

import math
import re
from copy import deepcopy
from urllib.parse import urlparse

EXPECTED_NUMBERS = list(range(1,11)) + [13,16] + list(range(20,26)) + list(range(27,46))


def prepare_votes(spending: dict, register: dict) -> dict:
    if register.get("year") != 2026 or register.get("approved_date") != "2026-03-25":
        raise ValueError("Vote record must match 25 March 2026 approved Revised Estimates")
    source = urlparse(str(register.get("source") or ""))
    if source.netloc != "data.oireachtas.ie" or source.scheme != "https":
        raise ValueError("Revised Estimates Vote source must be an official Oireachtas document")
    raw = deepcopy(register.get("votes") or [])
    nums = [v.get("number") for v in raw]
    if nums != EXPECTED_NUMBERS:
        raise ValueError("Incomplete or out-of-order 2026 approved Votes")
    sector_ids = {s["id"] for s in spending["categories"]}
    if len(sector_ids) != 8:
        raise ValueError("Sector atlas must include eight distinct sectors")
    seen = set()
    detail_votes = []
    for v in raw:
        n = v["number"]
        amount = v.get("net_supply_eur")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError(f"Invalid exact net grant for Vote {n}")
        if not math.isfinite(amount):
            raise ValueError(f"Non-finite net grant for Vote {n}")
        if v.get("year") != 2026 or v.get("estimate_type") != "net Exchequer supply grant":
            raise ValueError(f"Wrong reporting basis for Vote {n}")
        if v.get("source") != register["source"] or v.get("sector") not in sector_ids:
            raise ValueError(f"Source or sector mismatch for Vote {n}")
        if len(v.get("description", "")) < 45 or len(v.get("limit", "")) < 40:
            raise ValueError(f"Missing specific explanation for Vote {n}")
        if not re.match(r"^[A-Za-z]", v["title"]):
            raise ValueError(f"Invalid title for Vote {n}")
        slug_base = re.sub(r"[^a-z0-9]+", "-", v["title"].lower()).strip("-")
        v["slug"] = f"vote-{n}-{slug_base}-2026"
        v["url"] = f"/wheres-my-money/spending/votes/{v['slug']}/"
        if v["slug"] in seen:
            raise ValueError("Duplicate vote slug")
        seen.add(v["slug"])
        v["amount_million"] = amount / 1_000_000
        v["amount_display"] = ("€{:,.3f}bn".format(amount/1_000_000_000)
                               if amount >= 1_000_000_000
                               else "€{:,.3f}m".format(amount/1_000_000))
        v["sector_record"] = next(c for c in spending["categories"] if c["id"] == v["sector"])
        v["other_votes"] = []
        if v.get("detail"):
            detail_votes.append(v)
    if len(detail_votes) < 10:
        raise ValueError("Not enough useful detailed vote pages")
    by_amount = sorted(raw, key=lambda x: x["net_supply_eur"], reverse=True)
    max_amount = max(v["net_supply_eur"] for v in raw)
    for v in raw:
        v["bar_percent"] = v["net_supply_eur"] / max_amount * 100
        v["other_votes"] = [
            {"title": other["title"], "number": other["number"],
             "url": other["url"] if other["detail"] else "/wheres-my-money/spending/votes/",
             "amount_display": other["amount_display"],
             "detail": other["detail"]}
            for other in by_amount if other["number"] != v["number"]
            and (other["sector"] == v["sector"] or other["number"] in (37,38,31))
        ][:8]
    return {**spending, "votes": raw, "votes_featured": by_amount[:12],
            "vote_details": detail_votes, "vote_count": len(raw),
            "vote_date": register["verified_on"], "vote_source": register["source"],
            "vote_grant_sum": sum(v["net_supply_eur"] for v in raw),
            "vote_scope": register["scope"], "vote_statistic": register["statistic"]}
