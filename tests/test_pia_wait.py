"""PIA launch-timing tool: rendered SEO, editorial evidence and numerical regression."""
from pathlib import Path
import shutil
import subprocess
import pytest

from compound.site.build import build_site, render_markdown

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "content/pages/pia-invest-now-or-wait.md").read_text(encoding="utf-8")
SCRIPT = (ROOT / "compound/site/static/pia-wait.js").read_text(encoding="utf-8")
STYLES = (ROOT / "compound/site/static/pia-wait.css").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "compound/site/templates/page.html").read_text(encoding="utf-8")
CENTRE = (ROOT / "compound/site/templates/pia_centre.html").read_text(encoding="utf-8")


def test_editorial_distinctness_and_static_worked_examples():
    assert "canonical_path: /pia/invest-now-or-wait/" in PAGE
    assert "17 November 2026" in PAGE
    assert "226 calendar days" in PAGE
    assert "€12,000" in PAGE and "€50,000" in PAGE
    assert "31%" in PAGE and "35%" in PAGE and "38%" in PAGE
    assert "DIRT" in PAGE and "Finance (No. 2) Bill 2026" in PAGE
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in PAGE
    assert "https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx" in PAGE
    html = render_markdown(PAGE.split("---", 2)[-1])
    assert "Invest today or wait for the PIA?" in html
    assert "data-pia-wait-tool" in html
    assert "€4,505" in html and "€5,041" in html and "€5,165" in html and "€5,104" in html
    assert "−15%" in html
    assert "<table>" in html
    assert "not a prediction" in html.lower()
    assert "you do not have to sell" in html.lower()


def test_static_build_indexability_assets_links_and_analytics(settings):
    destination = settings.content_dir / "pages" / "pia-invest-now-or-wait.md"
    destination.write_text(PAGE, encoding="utf-8")
    build_site(settings)
    page = (settings.public_dir / "pia/invest-now-or-wait/index.html").read_text(encoding="utf-8")
    sitemap = (settings.public_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://example.test/pia/invest-now-or-wait/">' in page
    assert 'name="description"' in page
    assert 'data-pia-wait-tool' in page
    assert '/static/pia-wait.js?v=20261117-1' in page
    assert '/static/pia-wait.css?v=20261117-1' in page
    assert '"@type":"WebApplication"' in page
    assert '"@type":"BreadcrumbList"' in page
    assert '"isAccessibleForFree":true' in page
    assert "https://example.test/pia/invest-now-or-wait/" in sitemap
    assert "href=\"/pia/invest-now-or-wait/\"" in CENTRE
    assert "pia-wait-tool" in TEMPLATE
    assert "compound_analytics_consent" in SCRIPT
    assert 'window.gtag("event", "pia_wait_compare", {tool_name: "pia-invest-now-or-wait"})' in SCRIPT
    assert "investment_disposal_tax" not in SCRIPT.split('window.gtag("event"')[1].split(');')[0]
    assert "#pia-wait-tool" in STYLES


def test_node_scenario_engine():
    if not shutil.which("node"):
        pytest.skip("node unavailable")
    subprocess.run(["node", "--check", str(ROOT / "compound/site/static/pia-wait.js")], check=True)
    subprocess.run(["node", str(ROOT / "tests/pia_wait.cjs")], check=True)
