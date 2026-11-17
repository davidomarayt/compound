"""Targeted, human-visible search-intent upgrades using November 2026 GSC exports.

These assertions verify source and rendering affordances; they do not claim a
future Google CTR increase or indexing outcome.
"""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


@pytest.mark.parametrize("slug,term,link", [
    ("salary-hourly-rate-calculator", "€24.65", "/take-home-pay-calculator/"),
    ("fuel-cost-calculator", "€11.38", "/ev-charging-cost-calculator/"),
    ("electricity-cost-calculator", "€0.60", "/wealth/electricity-tariffs-ireland/"),
    ("inflation-calculator", "€1,344", "/compound-interest-calculator/"),
    ("pia-calculator", "€50,000", "/pia/"),
])
def test_priority_calculator_has_genuine_quick_answer(slug, term, link):
    entries = yaml.safe_load(read("content/tools.yml"))["tools"]
    tool = next(t for t in entries if t["slug"] == slug)
    assert term in tool["quick_answer"]
    assert len(tool["quick_answer"]) > 90
    assert tool["quick_link_url"] == link
    assert tool["quick_link_label"]
    assert "Ireland" in (tool.get("seo_title") or tool["title"])


def test_quick_answers_precede_calculator_and_are_accessible():
    template = read("compound/site/templates/tool.html")
    assert 'aria-label="Quick calculator answer"' in template
    assert template.index("tool-quick-answer") < template.index('<section class="tool-workspace">')
    assert "{{ tool.quick_answer }}" in template
    assert "{{ tool.quick_link_url }}" in template
    assert ".tool-quick-answer{" in read("compound/site/static/tools.css")


def test_stock_directory_answers_what_you_can_find():
    template = read("compound/site/templates/stocks_hub.html")
    assert "S&P 500 Stocks Directory" in template
    assert "ticker or sector" in template
    assert "verified research is available" in template
    assert 'href="/stocks/{{ company.slug }}/"' in template
    assert "SEC filings" in template


def test_pia_hub_links_company_research_without_claiming_eligibility():
    template = read("compound/site/templates/pia_centre.html")
    assert 'href="/stocks/"' in template
    assert "not confirmation of PIA investment eligibility" in template
    assert "The scheme is not law yet" in template
