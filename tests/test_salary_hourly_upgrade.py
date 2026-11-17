"""Focused regression checks for the canonical Irish salary-to-hourly calculator."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def test_salary_tool_search_and_reverse_conversion_inputs():
    tools = yaml.safe_load((ROOT / "content/tools.yml").read_text(encoding="utf-8"))["tools"]
    tool = next(t for t in tools if t["slug"] == "salary-hourly-rate-calculator")
    assert tool["formula"] == "salary_hourly"
    assert "Ireland" in tool["seo_title"]
    assert "€24.65" in tool["meta_description"]
    assert [o["value"] for o in tool["fields"][0]["options"]] == ["annual", "hourly"]
    assert tool["fields"][0]["id"] == "direction"
    assert "annual" in {r["id"] for r in tool["results"]}
    assert "effective_hourly" in {r["id"] for r in tool["results"]}
    assert "source" not in tool["meta_description"].lower()

def test_salary_page_has_reverse_examples_and_related_tool_links():
    guide = (ROOT / "content/tool-guides/salary-hourly-rate-calculator.md").read_text(encoding="utf-8")
    assert "Hourly pay → annual salary" in guide
    assert "€40,560" in guide
    assert "€50,000" in guide
    assert "/take-home-pay-calculator/" in guide
    assert "before PAYE" in guide

def test_salary_page_assets_and_primary_results_are_dynamic():
    template = (ROOT / "compound/site/templates/tool.html").read_text(encoding="utf-8")
    javascript = (ROOT / "compound/site/static/tools.js").read_text(encoding="utf-8")
    css = (ROOT / "compound/site/static/tools.css").read_text(encoding="utf-8")
    assert "salary-upgrade" in template
    assert "syncSalaryBasis(true)" in javascript
    assert "effective_hourly:money" in javascript
    assert 'grid.prepend(primary)' in javascript
    assert 'data-tool-name="salary-hourly-rate-calculator"' in css
