"""Protect the privacy and event semantics of PIA calculator engagement tracking."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "compound/site/static/tools.js").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "compound/site/templates/tool.html").read_text(encoding="utf-8")


def test_pia_events_are_consent_gated_without_financial_inputs():
    assert "localStorage.getItem('compound_analytics_consent')!=='granted'" in SCRIPT
    assert "window.gtag('event',eventName,{tool_name:'pia-calculator'})" in SCRIPT
    for event in ("pia_calculate", "pia_save_comparison", "pia_compare"):
        assert f"trackPia('{event}')" in SCRIPT
    assert "window.gtag('event',eventName,values)" not in SCRIPT


def test_pia_initial_render_is_not_counted_as_a_calculation():
    assert "const run=(showErrors=true,trackInteraction=false)" in SCRIPT
    assert "if(trackInteraction){" in SCRIPT
    assert "form.addEventListener('submit',e=>{e.preventDefault();run(true,isPia);});" in SCRIPT
    assert "form.addEventListener('change',()=>{clearPiaPreset();syncVisibility();run(false,isPia);});" in SCRIPT
    assert "run(false,true);\n      if(piaPresetStatus)" in SCRIPT
    assert "tools.js?v=20261113-pia-events" in TEMPLATE


def test_comparison_requires_saved_scenario_and_a_changed_input():
    assert "savedScenario={results:snapshotResults(),signature:JSON.stringify(values)}" in SCRIPT
    assert "if(signature!==savedScenario.signature && signature!==lastComparedSignature)" in SCRIPT
