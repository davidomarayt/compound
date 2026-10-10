"""TradingView is a separate, lazy-loaded market context beside verified SEC data."""
import json
from pathlib import Path
import shutil
import subprocess

from compound.site.build import build_site
from compound.site.tradingview import render_tradingview_panel


def test_tradingview_markup_is_safe_and_has_visible_attribution():
    panel = render_tradingview_panel("BRK-B", "Berkshire & <Co>", "advanced")
    assert 'data-tv-symbol="BRK.B"' in panel
    assert "Berkshire &amp; &lt;Co&gt;" in panel
    assert 'data-tv-variant="advanced"' in panel
    assert 'by TradingView' in panel
    assert 'data-tv-expand aria-pressed="false"' in panel
    assert 'aria-label="Expand interactive stock chart"' in panel
    assert 'target="_blank" rel="noopener nofollow"' in panel
    assert 'https://www.tradingview.com/symbols/BRK.B/' in panel
    assert '<script' not in panel and '<iframe' not in panel
    assert render_tradingview_panel('AAPL" onmouseover="bad') == ""
    assert render_tradingview_panel("AAPL", variant="invalid") == ""


def test_company_and_earnings_report_get_different_chart_variants(settings):
    registry = {
        "source": "https://example.test/membership", "checked": "2026-10-10",
        "company_count": 2, "security_count": 2,
        "members": [
            {"cik": 320193, "name": "Apple Inc.", "sector": "Information Technology",
             "symbol": "AAPL", "symbols": ["AAPL"], "active": True},
            {"cik": 920760, "name": "Lennar", "sector": "Consumer Discretionary",
             "symbol": "LEN", "symbols": ["LEN"], "active": True},
        ],
    }
    (settings.content_dir / "earnings-sp500.json").write_text(json.dumps(registry), encoding="utf-8")
    wealth = settings.content_dir / "wealth"
    wealth.mkdir(exist_ok=True, parents=True)
    (wealth / "aapl-test-earnings.md").write_text("""---
title: Apple filing summary
slug: aapl-test-earnings
pillar: wealth
canonical_path: /wealth/earnings/aapl-test-earnings/
date: 2026-10-10
tags: [earnings, automated-earnings, aapl]
summary: SEC-verified financial results
---
SEC filing results described here.
""", encoding="utf-8")
    build_site(settings)
    root = settings.public_dir
    profile = (root / "stocks/aapl/index.html").read_text(encoding="utf-8")
    report = (root / "wealth/earnings/aapl-test-earnings/index.html").read_text(encoding="utf-8")
    assert 'data-tv-symbol="AAPL"' in profile
    assert 'data-tv-variant="advanced"' in profile
    assert "Quarterly and annual earnings" in profile
    assert 'data-tv-symbol="AAPL"' in report
    assert 'data-tv-variant="compact"' in report
    assert 'tradingview-earnings.js?v=3' in report and 'tradingview-earnings.js?v=3' in profile
    assert report.index('compound-tv-panel') < report.index('SEC filing results described here.')
    assert '<link rel="canonical" href="https://example.test/wealth/earnings/aapl-test-earnings/">' in report
    assert 'by TradingView' in profile and 'by TradingView' in report
    assert 'data-tv-symbol="LEN"' in (root / "stocks/len/index.html").read_text(encoding="utf-8")
    js = (root / "static/tradingview-earnings.js").read_text(encoding="utf-8")
    assert "IntersectionObserver" in js
    assert "embed-widget-advanced-chart.js" in js
    assert "embed-widget-symbol-overview.js" in js
    assert "https://s3.tradingview.com/external-embedding/" in js
    assert "compound-tv-scroll-lock" in js
    assert "Close enlarged stock chart" in js
    assert "Escape" in js
    assert "refreshChartSize" in js
    assert "hide_top_toolbar: mobile, hide_legend: mobile, hide_volume: mobile" in js
    assert "chartOnly: mobile" in js
    assert 'earnings.css?v=7' in profile and 'earnings.css?v=7' in report


def test_unverified_report_without_matching_registry_company_has_no_price_widget(settings):
    wealth = settings.content_dir / "wealth"
    wealth.mkdir(exist_ok=True, parents=True)
    (wealth / "unknown-earnings.md").write_text("""---
title: Unknown earnings
slug: unknown-earnings
pillar: wealth
canonical_path: /wealth/earnings/unknown-earnings/
date: 2026-10-10
tags: [earnings, automated-earnings]
---
Earnings data text.
""", encoding="utf-8")
    build_site(settings)
    report = (settings.public_dir / "wealth/earnings/unknown-earnings/index.html").read_text(encoding="utf-8")
    assert "compound-tv-panel" not in report


def test_mobile_charts_break_out_of_narrow_article_columns(settings):
    """Both price chart variants must be readable on a 360px-wide phone."""
    build_site(settings)
    css = (settings.public_dir / "static/earnings.css").read_text(encoding="utf-8")
    assert "@media(max-width:760px)" in css
    assert "width:calc(100vw - 8px)" in css
    assert "height:650px" in css
    assert "height:590px" in css
    assert ".article-prose .compound-tv-panel" in css
    assert ".earnings-hub > .compound-tv-panel" in css
    assert ".compound-tv-panel.tv-expanded" in css
    assert "height:100dvh!important" in css
    assert "min-height:44px" in css


def test_mobile_chart_script_has_valid_javascript(settings):
    build_site(settings)
    node = shutil.which("node")
    if not node:
        return
    subprocess.run(
        [node, "--check", str(settings.public_dir / "static/tradingview-earnings.js")],
        check=True, capture_output=True, text=True,
    )
