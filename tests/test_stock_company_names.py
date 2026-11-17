"""Audit the complete 500+10 stock register and preserve vetted company labels."""
import json
import re
from pathlib import Path

from compound.site.stock_names import DISPLAY_NAMES, normalise_company_names

ROOT = Path(__file__).resolve().parents[1]


def current_register():
    registry = json.loads((ROOT / "content/earnings-sp500.json").read_text())
    watchlist = json.loads((ROOT / "content/company-watchlist.json").read_text())
    return registry, watchlist


def test_all_510_company_directory_entries_have_unique_valid_identity_and_readable_names():
    registry, watchlist = current_register()
    active = [entry for entry in registry["members"] if entry["active"]]
    extra = watchlist["listed"]
    assert len(active) == 500
    assert len(extra) == 10
    assert len({item["symbol"] for item in active}) == 500
    slugs = [item["symbol"].lower() for item in active] + [item["slug"] for item in extra]
    assert len(slugs) == len(set(slugs)) == 510

    for item in active:
        assert isinstance(item["cik"], int) and item["cik"] > 0
        assert item["symbol"] in item["symbols"]
        assert item["sector"] and item["name"] and item["name"].strip() == item["name"]
        assert not re.search(r"\((?:The|Eli|Class [A-Z])\)$", item["name"]), item
    for item in extra:
        assert item["name"] and item["ticker"] and item["slug"] and item["source"].startswith("https://")
        assert item["name"].strip() == item["name"]
    assert len({item["name"] for item in active + extra}) == 510


def test_all_15_reviewed_overrides_match_exact_ciks_and_preserve_source_names():
    registry, _ = current_register()
    by_ticker = {item["symbol"]: item for item in registry["members"]}
    assert len(DISPLAY_NAMES) == 15
    for ticker, (cik, official_name) in DISPLAY_NAMES.items():
        row = by_ticker[ticker]
        assert row["cik"] == cik
        assert row["name"] == official_name
        assert row["source_name"] != official_name
        assert row["symbol"] in row["symbols"]
    after = normalise_company_names(registry["members"])
    assert after == registry["members"], "Already-correct labels must remain stable"
    assert len(after) == len(registry["members"])


def test_ticker_reassignment_does_not_apply_old_name_override():
    hypothetical = [{"symbol": "LLY", "cik": 99999999, "name": "New Company", "symbols": ["LLY"]}]
    fixed = normalise_company_names(hypothetical)
    assert fixed == hypothetical
    assert fixed[0] is not hypothetical[0]


def test_stock_pages_display_corrected_name_and_keep_class_tickers(settings):
    from compound.site.build import build_site
    build_site(settings)
    root = settings.public_dir
    index = (root / "stocks/index.html").read_text()
    assert "Eli Lilly and Company" in index
    assert "Lilly (Eli)" not in index
    assert "The Walt Disney Company" in index
    assert "Walt Disney Company (The)" not in index
    assert "Alphabet Inc." in index
    assert "Alphabet Inc. (Class A)" not in index
    assert "GOOG, GOOGL" in index
    profile = (root / "stocks/lly/index.html").read_text()
    assert "Eli Lilly and Company" in profile
    assert "LLY" in profile
    assert "Original SEC report" in profile
