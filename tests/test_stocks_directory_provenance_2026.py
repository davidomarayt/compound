"""Stocks directory must not imply all earnings use SEC filings.

Company results may originate in issuer releases as well as regulatory filings.
The directory should not label every available report SEC-backed.
"""
from pathlib import Path

from compound.site.build import _env

ROOT = Path(__file__).resolve().parents[1]


def test_stocks_directory_primary_source_labels_and_accessible_canonical(settings):
    tickers = ("nvda", "aapl", "msft", "amzn", "googl", "meta", "tsla", "lly")
    companies = [
        {
            "slug": ticker,
            "symbol": ticker.upper(),
            "symbols": [ticker.upper()],
            "name": ticker.upper(),
            "sector": "Technology",
            "report_count": 1,
        }
        for ticker in tickers
    ]
    html = _env(settings).get_template("stocks_hub.html").render(
        title="Stock research", pillar="wealth",
        site_url="https://compound.ie",
        registry={"source": "https://example.com/company-register", "checked": "2026-11-21"},
        companies=companies, checked="2026-11-21", sectors=["Technology"],
    )
    assert html.count("Primary-source earnings available") == 8
    assert "SEC-backed earnings available" not in html
    assert "SEC-linked company earnings" not in html
    assert "issuer releases or regulatory filings, as applicable" in html
    assert "https://compound.ie/stocks/" in html
    assert 'aria-current="page">Stocks' in html
    assert 'data-earnings-search' in html


def test_stocks_directory_change_preserves_template_ad_and_tracking_boundaries():
    template = (ROOT / "compound/site/templates/stocks_hub.html").read_text()
    assert "Primary-source figures" in template
    assert "source-linked company earnings" in template
    assert "base.html" in template
    assert "/static/earnings-directory.js?v=2" in template
    assert "adsbygoogle" not in template
