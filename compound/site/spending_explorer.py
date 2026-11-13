"""Data preparation for Compound's independent Irish public-spending explainer pages.

Official figures and year-status metadata stay in content JSON. This module only
validates, joins and derives *labelled comparisons*; it does not estimate
programme-level allocations.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite


def prepare_spending_explorer(snapshot: dict, editorial: dict) -> dict:
    """Join the 2026 sector snapshot and the 2027 Budget comparison.

    Fail closed when any sector, ID, total or chronology is inconsistent.
    """
    if snapshot.get("year") != 2026 or editorial.get("comparison_year") != 2027:
        raise ValueError("Expected 2026 snapshot and 2027 Budget comparison")
    sectors = deepcopy(snapshot.get("categories") or [])
    explanations = editorial.get("sectors") or []
    if len(sectors) != 8 or len(explanations) != 8:
        raise ValueError("Expected eight official sector totals and eight descriptions")

    by_id = {}
    for entry in explanations:
        ident = entry.get("id")
        if not ident or ident in by_id:
            raise ValueError("Duplicate or missing sector detail ID")
        if not entry.get("slug") or not entry.get("intro") or len(entry.get("questions") or []) < 2:
            raise ValueError(f"Incomplete sector explanation: {ident}")
        by_id[ident] = entry

    total_2026 = float(snapshot.get("total_billion") or 0)
    total_2027 = float(editorial.get("comparison_total_billion") or 0)
    if not (total_2026 > 0 and total_2027 > 0):
        raise ValueError("Invalid published spending totals")
    if abs(sum(float(c["billion"]) for c in sectors) - total_2026) > 0.051:
        raise ValueError("2026 sectors do not reconcile")

    slugs = set()
    result = []
    for c in sectors:
        ident = c["id"]
        if ident not in by_id:
            raise ValueError(f"Missing sector editorial: {ident}")
        extra = by_id[ident]
        slug = extra["slug"]
        if slug in slugs or not all(ch.isalnum() or ch == "-" for ch in slug):
            raise ValueError(f"Invalid or duplicate slug: {slug}")
        slugs.add(slug)
        value_2026 = float(c["billion"])
        value_2027 = float(extra["next_billion"])
        if not all(isfinite(v) and v >= 0 for v in (value_2026, value_2027)):
            raise ValueError(f"Non-finite sector figure: {slug}")
        sector = {**c, **extra}
        sector["url"] = f"/wheres-my-money/spending/{slug}/"
        sector["share_2026"] = value_2026 / total_2026 * 100
        sector["share_2027"] = value_2027 / total_2027 * 100
        sector["increase_billion"] = value_2027 - value_2026
        sector["increase_pct"] = (value_2027 / value_2026 - 1) * 100 if value_2026 else 0
        series = []
        if extra.get("past_billion") is not None:
            p = float(extra["past_billion"])
            if not (isfinite(p) and p > 0):
                raise ValueError(f"Invalid past sector figure: {slug}")
            series.append({"year": 2025, "value": p, "status": "Provisional 2025 outturn"})
        series.extend([
            {"year": 2026, "value": value_2026, "status": "2026 estimate"},
            {"year": 2027, "value": value_2027, "status": "2027 Budget estimate"},
        ])
        max_value = max(p["value"] for p in series)
        sector["series"] = [{**point, "bar_pct": point["value"] / max_value * 100} for point in series]
        result.append(sector)

    if abs(sum(c["next_billion"] for c in result) - total_2027) > 0.051:
        raise ValueError("2027 sectors do not reconcile")
    return {**snapshot,
        "updated": editorial["updated"],
        "comparison_year": 2027,
        "comparison_total_billion": total_2027,
        "comparison_source": editorial["comparison_source"],
        "comparison_kind": editorial["comparison_kind"],
        "past_kind": editorial["past_kind"],
        "categories": result,
    }
