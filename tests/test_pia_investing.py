"""Regression: proposed PIA vs outside ETF and direct shares comparison."""
from pathlib import Path
import re
import shutil
import subprocess
import json

import pytest
from compound.site.build import render_markdown, build_site

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"content/pages/pia-vs-ordinary-investing.md").read_text(encoding="utf-8")
TEMPLATE=(ROOT/"compound/site/templates/page.html").read_text(encoding="utf-8")
SCRIPT=(ROOT/"compound/site/static/pia-investing.js").read_text(encoding="utf-8")

def test_route_and_readable_original_scenarios(settings):
    assert "canonical_path: /pia/vs-ordinary-investing/" in PAGE
    html=render_markdown(PAGE.split("---",2)[-1])
    assert "PIA vs ETF vs shares: after-tax calculator" in html
    assert "€412,420" in html and "€339,697" in html and "€376,792" in html
    assert "35% — proposed" in html and "38% — current" in html
    assert "Finance (No. 2) Bill 2026" in html
    segment=html.split("Worked example: how the tax differences compound",1)[1].split("Which investments are being compared?",1)[0]
    assert "<table>" in segment, "Published scenarios must be accessible without JavaScript"
    assert "<h2" in html
    temp_page=settings.content_dir/"pages"/"pia-vs-ordinary-investing.md"
    temp_page.parent.mkdir(parents=True,exist_ok=True)
    temp_page.write_text(PAGE,encoding="utf-8")
    build_site(settings)
    generated=(settings.public_dir/"pia"/"vs-ordinary-investing"/"index.html").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://example.test/pia/vs-ordinary-investing/">' in generated
    assert '/static/pia-investing.js?v=20261113-1' in generated
    assert '/static/pia-investing.css?v=20261113-1' in generated
    sitemap=(settings.public_dir/"sitemap.xml").read_text(encoding="utf-8")
    assert "https://example.test/pia/vs-ordinary-investing/" in sitemap

def test_jsonld_and_privacy():
    assert "'pia-vs-ordinary-investing'" in TEMPLATE
    assert '"@type":"WebApplication"' in TEMPLATE
    assert '"@type":"WebPage"' in TEMPLATE
    assert '"isAccessibleForFree":true' in TEMPLATE
    assert "compound_analytics_consent" in SCRIPT
    assert 'pia_investing_compare' in SCRIPT
    assert 'window.gtag("event","pia_investing_compare",{tool_name:"pia-vs-ordinary-investing"})' in SCRIPT
    assert 'window.gtag("event","pia_investing_compare",inputs()' not in SCRIPT

def test_scenario_engine_and_static_table():
    if not shutil.which("node"):
        pytest.skip("node unavailable")
    subprocess.run(["node",str(ROOT/"tests/pia_investing.cjs")],check=True,cwd=ROOT)
    node=subprocess.run(
        ["node",str(ROOT/"scripts/pia_investing_static_examples.cjs")],
        check=True,cwd=ROOT,capture_output=True,text=True
    ).stdout.strip()
    match=re.search(r"<!-- pia-investing-examples:start -->(.*?)<!-- pia-investing-examples:end -->",PAGE,re.S)
    assert match, "Static example table missing"
    assert node==match.group(1).strip(), "Published table differs from exact calculator engine"
