"""Keep issuer press releases distinct from SEC-filed statements in earnings search."""
from pathlib import Path

from compound.site.earnings_archive import prepare_recent_earnings


ROOT = Path(__file__).resolve().parents[1]


def _entry(symbol: str, date: str, *, release: bool = False) -> dict:
    result = {
        "name": f"{symbol} Example",
        "symbol": symbol,
        "url": f"/stocks/{symbol.lower()}/",
        "report": {
            "latest_filed": date,
            "latest_end": "2026-09-30",
            "latest_display": "Q3 FY2026",
            "latest_label": "FY2026 Q3",
        },
    }
    if release:
        result["from_release"] = True
    return result


def test_search_archive_preserves_filing_vs_issuer_release_provenance():
    filing = _entry("FILE", "2026-11-12")
    release = _entry("PRESS", "2026-11-13", release=True)
    recent, search_index = prepare_recent_earnings([filing, release], limit=10)

    assert [row["symbol"] for row in recent] == ["PRESS", "FILE"]
    assert [row["ticker"] for row in search_index] == ["PRESS", "FILE"]
    assert [row["from_release"] for row in search_index] == [True, False]
    assert all(row["url"].startswith("/stocks/") for row in search_index)


def test_earnings_hub_and_search_labels_distinguish_source_types():
    template = (ROOT / "compound/site/templates/earnings_hub.html").read_text(
        encoding="utf-8"
    )
    javascript = (ROOT / "compound/site/static/earnings-report-search.js").read_text(
        encoding="utf-8"
    )
    # The server-side latest cards and client-rendered archive must tell the
    # same truth. Company press releases are not automatically SEC filings.
    assert "{% if company.from_release %}COMPANY RESULTS · PUBLISHED" in template
    assert "entry.from_release" in javascript
    assert "COMPANY RESULTS · PUBLISHED " in javascript
    assert "SEC-VERIFIED FINANCIAL REPORT · FILED " in javascript
    assert "10 most recently filed reports" not in template
    assert "Showing 10 latest filings" not in template
    assert "latest filings. Search" not in javascript
    assert "{{ report_cards|length }} recent company results" in template
    assert "source-checked reports and releases" in template


def test_earnings_directory_intro_respects_issuer_release_provenance_and_location():
    """The public intro must not claim every issuer release is SEC-filed."""
    template = (ROOT / "compound/site/templates/earnings_hub.html").read_text(
        encoding="utf-8"
    )
    assert "from US SEC filings and company-issued earnings releases" in template
    assert "where reported, with links to original sources" in template
    assert 'content="Explore company earnings from SEC filings and issuer releases.' in template
    assert 'content="Quarterly and annual earnings from SEC filings and company releases,' in template
    assert "Explore SEC-verified quarterly and annual company earnings" not in template
    assert "checked against US SEC filings. Clear comparisons." not in template
    assert '<span aria-current="page">Earnings</span>' in template
    assert '<link rel="canonical" href="{{ site_url }}/wealth/earnings/">' in template
    assert "{% if company.from_release %}COMPANY RESULTS · PUBLISHED" in template
