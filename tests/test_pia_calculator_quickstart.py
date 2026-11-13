"""PIA conversion/UX improvements preserve the calculator's canonical SEO surface."""
from pathlib import Path

from compound.site.build import load_tools

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "compound/site/templates/tool.html").read_text(encoding="utf-8")
SCRIPT = (ROOT / "compound/site/static/tools.js").read_text(encoding="utf-8")
CSS = (ROOT / "compound/site/static/tools.css").read_text(encoding="utf-8")


def test_pia_example_presets_are_pia_only_and_within_annual_limit():
    assert '{% if tool.slug == "pia-calculator" %}' in TEMPLATE
    for key, contribution, years in [
        ("6k-10y", 6000, 10),
        ("12k-10y", 12000, 10),
        ("12k-20y", 12000, 20),
    ]:
        attrs = f'data-pia-preset="{key}" data-contribution="{contribution}" data-years="{years}"'
        assert attrs in TEMPLATE
        assert 0 <= contribution <= 12000
        assert 1 <= years <= 40
    assert 'aria-pressed="false"' in TEMPLATE
    assert 'data-pia-preset-status role="status" aria-live="polite"' in TEMPLATE
    assert 'id="pia-calculator-estimate"' in TEMPLATE


def test_pia_presets_use_existing_calculator_and_allow_manual_changes():
    assert "root.dataset.toolName==='pia-calculator'" in SCRIPT
    assert "const presetValues={" in SCRIPT
    assert "annual_contribution:Number(button.dataset.contribution)" in SCRIPT
    assert "return_rate:6" in SCRIPT
    assert "selectPiaPreset(button);" in SCRIPT
    assert "syncVisibility();\n      run(false,true);" in SCRIPT
    assert "form.addEventListener('change',()=>{clearPiaPreset();" in SCRIPT
    assert "form.addEventListener('input',()=>{clearPiaPreset();" in SCRIPT
    assert 'data-tool-name="pia-calculator"' in CSS


def test_pia_provider_next_step_links_and_seo_title_stay_intact():
    tools = {t["slug"]: t for t in load_tools(ROOT / "content")}
    pia = tools["pia-calculator"]
    assert pia["url"] == "/pia-calculator/"
    assert pia["seo_title"] == "PIA Calculator Ireland – Tax, Growth & €50k Threshold"
    assert str(pia["updated"]) == "2026-11-13"
    assert 'href="/pia/providers/"' in TEMPLATE
    assert 'href="/pia/vs-pension/"' in TEMPLATE
    assert "[model annual contributions, account growth and the proposed PIA charge](/pia-calculator/)" in (ROOT / "content/wealth/pension-vs-investing-ireland.md").read_text()
    assert "[estimate when a PIA might cross the €50,000 threshold" in (ROOT / "content/wealth/investment-tax-ireland.md").read_text()
