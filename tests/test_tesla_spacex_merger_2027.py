"""Verify the Tesla-SpaceX 2027 research article and its data presentation."""
import json
from pathlib import Path
import shutil
import subprocess
from compound.site.build import build_site


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "content/wealth/tesla-spacex-merger-2027.md"


def test_merger_report_has_consistent_source_backed_visual_inputs():
    source = ARTICLE.read_text(encoding="utf-8")
    assert "2026-10-10" in source
    assert "94.827" in source and "18.674" in source
    assert "97.690" in source and "14.015" in source
    assert "4.355" in source and "2.589" in source
    assert "7.814" in source and "4.071" in source
    assert "$405m" in source and "$318m" in source and "$87m" in source
    assert "](/stocks/tsla/)" in source
    assert "](/stocks/spcx/)" in source
    assert "hypothetical" in source.lower()
    assert 'data-mx27-simulator' in source
    assert source.count('class="mx27 mx27-chart"') >= 5
    assert "no confirmed merger agreement" in source.lower()
    assert "spcx" in source
    assert "www.sec.gov" in source


def test_merger_article_builds_with_canonical_seo_and_company_backlinks(settings):
    folder = settings.content_dir / "wealth"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / ARTICLE.name).write_text(ARTICLE.read_text(encoding="utf-8"), encoding="utf-8")
    (settings.content_dir / "earnings-sp500.json").write_text(json.dumps({
        "checked": "2026-10-10", "source": "https://example.test/sp500",
        "company_count": 1, "security_count": 1,
        "members": [{
            "cik": 1318605, "name": "Tesla", "sector": "Consumer Discretionary",
            "symbol": "TSLA", "symbols": ["TSLA"], "active": True
        }]
    }), encoding="utf-8")
    (settings.content_dir / "company-watchlist.json").write_text(json.dumps({
        "checked": "2026-10-10",
        "listed": [{
            "slug": "spcx", "name": "SpaceX", "ticker": "SPCX",
            "exchange": "Nasdaq", "market": "United States",
            "sector": "Aerospace", "summary": "Space launch and broadband",
            "source": "https://example.test/spacex", "tv_symbol": "NASDAQ:SPCX"
        }], "private": []
    }), encoding="utf-8")
    build_site(settings)
    out = settings.public_dir
    url = "wealth/tesla-spacex-merger-2027/index.html"
    page = (out / url).read_text(encoding="utf-8")
    tesla = (out / "stocks/tsla/index.html").read_text(encoding="utf-8")
    spacex = (out / "stocks/spcx/index.html").read_text(encoding="utf-8")
    sitemap = (out / "sitemap.xml").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://example.test/wealth/tesla-spacex-merger-2027/">' in page
    assert 'Tesla–SpaceX Merger 2027' in page
    assert "tesla-spacex-merger-2027.css?v=1" in page
    assert "tesla-spacex-merger-2027.js?v=1" in page
    assert page.count('class="mx27 mx27-chart"') >= 5
    assert 'data-mx27-simulator' in page
    assert 'href="/stocks/tsla/"' in page
    assert 'href="/stocks/spcx/"' in page
    assert "Will Tesla and SpaceX Merge in 2027" in tesla
    assert "Will Tesla and SpaceX Merge in 2027" in spacex
    assert 'name="robots" content="noindex,follow"' not in tesla
    assert 'name="robots" content="noindex,follow"' not in spacex
    assert '<loc>https://example.test/wealth/tesla-spacex-merger-2027/</loc>' in sitemap
    assert (out / "static/tesla-spacex-merger-2027.css").is_file()
    assert (out / "static/tesla-spacex-merger-2027.js").is_file()


def test_merger_interactive_script_valid_javascript():
    node = shutil.which("node")
    if node:
        subprocess.run(
            [node, "--check", str(ROOT / "compound/site/static/tesla-spacex-merger-2027.js")],
            check=True, capture_output=True, text=True,
        )
