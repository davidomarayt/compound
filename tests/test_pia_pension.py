"""PIA versus pension interactive route, privacy and arithmetic regression."""
from pathlib import Path
import shutil
import subprocess

import pytest
from compound.site.build import render_markdown

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"content/pages/pia-vs-pension.md").read_text(encoding="utf-8")
TEMPLATE=(ROOT/"compound/site/templates/page.html").read_text(encoding="utf-8")
JS=(ROOT/"compound/site/static/pia-pension.js").read_text(encoding="utf-8")

def test_calculator_is_on_existing_canonical_page_and_no_new_route():
    assert "canonical_path: /pia/vs-pension/" in PAGE
    html=render_markdown(PAGE.split("---",2)[-1])
    assert 'data-pia-pension-tool' in html
    assert 'name="monthly_net"' in html
    assert 'name="relief_headroom"' in html
    assert 'data-pp-result="pension-net"' in html
    assert '/static/pia-pension.js?v=20261113-1' in TEMPLATE
    assert '/static/pia-pension.css?v=20261113-1' in TEMPLATE

def test_calculator_is_consent_gated_and_no_inputs_sent():
    assert 'compound_analytics_consent' in JS
    assert '"pia_pension_calculate",{tool_name:"pia-vs-pension"}' in JS
    assert 'window.gtag("event","pia_pension_calculate",v)' not in JS
    assert 'if(typeof document==="undefined")return' in JS

def test_javascript_arithmetic():
    if not shutil.which("node"):
        pytest.skip("Node.js unavailable")
    subprocess.run(["node",str(ROOT/"tests/pia_pension.cjs")],check=True,cwd=ROOT)
