"""Latest earnings shows ten actual filing dates; search still covers every issuer."""
import json
import re
from datetime import date, timedelta
from pathlib import Path

from compound.site.earnings_archive import prepare_recent_earnings


def sample(ticker, filed, end):
    return {
        "name": f"Company {ticker}", "symbol": ticker,
        "url": f"/stocks/{ticker.lower()}/",
        "report": {"latest_filed": filed, "latest_end": end, "latest_label": "FY2026 Q2"},
    }


def test_recent_is_limited_to_ten_but_search_index_contains_every_verified_report():
    start = date(2026, 9, 1)
    companies = [
        sample(f"T{i:02}", (start + timedelta(days=i)).isoformat(), "2026-06-30")
        for i in range(37)
    ]
    latest, archive = prepare_recent_earnings(companies)
    assert len(latest) == 10
    assert len(archive) == 37
    assert latest[0]["symbol"] == "T36"
    assert latest[-1]["symbol"] == "T27"
    assert archive[-1]["ticker"] == "T00"
    assert len({entry["url"] for entry in archive}) == 37


def test_sort_uses_filing_date_not_quarter_end_or_backfill_date():
    entries = [
        sample("ALPHA", "2026-10-01", "2026-09-30"),
        sample("BETA", "2026-10-13", "2026-06-30"),
        sample("GAMMA", "", "2026-10-10"),
    ]
    latest, archive = prepare_recent_earnings(entries)
    assert [row["symbol"] for row in latest] == ["BETA", "ALPHA", "GAMMA"]
    assert archive[0]["filed"] == "2026-10-13"


def test_recent_limit_rejects_nonpositive_values():
    import pytest
    with pytest.raises(ValueError):
        prepare_recent_earnings([], limit=0)


def test_hub_template_only_loops_over_ten_reports_and_has_search_fallback():
    template = (Path(__file__).resolve().parents[1] /
                "compound/site/templates/earnings_hub.html").read_text()
    assert "{% for company in report_cards %}" in template
    assert "data-earnings-recent-card" in template
    assert "data-earnings-report-search" in template
    assert "data-earnings-report-index" in template
    assert "report_search_index|tojson" in template
    assert 'type="search"' in template
