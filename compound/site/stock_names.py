"""Reviewed public-company display labels.

The constituent mirror is not a canonical branding guide. These reviewed
overrides fix inverted names and share-class suffixes on company-level pages.
CIK guards prevent applying an old override to a reassigned ticker.
"""
from __future__ import annotations

# Symbol -> (SEC CIK, reader-facing company name).
DISPLAY_NAMES = {
    "CLX": (21076, "The Clorox Company"),
    "COO": (711404, "The Cooper Companies"),
    "DIS": (1744489, "The Walt Disney Company"),
    "EL": (1001250, "The Estée Lauder Companies Inc."),
    "FOXA": (1754301, "Fox Corporation"),
    "GOOGL": (1652044, "Alphabet Inc."),
    "HD": (354950, "The Home Depot"),
    "HIG": (874766, "The Hartford"),
    "HSY": (47111, "The Hershey Company"),
    "KO": (21344, "The Coca-Cola Company"),
    "LLY": (59478, "Eli Lilly and Company"),
    "MOS": (1285785, "The Mosaic Company"),
    "NWSA": (1564708, "News Corp"),
    "SJM": (91419, "The J.M. Smucker Company"),
    "TRV": (86312, "The Travelers Companies"),
}


def normalise_company_names(members: list[dict]) -> list[dict]:
    """Correct known labels; retain source wording and original identifiers."""
    result = []
    for company in members:
        entry = dict(company)
        target = DISPLAY_NAMES.get(entry.get("symbol"))
        if target and str(entry.get("cik")) == str(target[0]):
            name = entry.get("name")
            if name and name != target[1]:
                entry.setdefault("source_name", name)
                entry["name"] = target[1]
        result.append(entry)
    return result
