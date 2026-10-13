"""Regression checks for the October 2026 search and commercial-funnel sprint.

These tests check repository content and instrumentation. They do NOT claim to
confirm Google's indexing status or successful receipt of GA4 events.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_active_seai_battery_grant_is_primary_article_answer():
    article = read("content/wealth/solar-battery-grant-ireland-budget-2027.md")
    frontmatter = article.split("---", 2)[1]
    assert "expected in Budget 2027" not in frontmatter
    assert "reviewed: 2026-10-13" in frontmatter
    assert "before installation" in article.lower()
    assert "5 kWh" in article
    assert "https://www.seai.ie/grants/home-energy-grants/individual-grants/battery" in article
    assert "](/solar/grants/)" in article
    assert "](/solar/batteries/)" in article


def test_priority_calculators_have_search_intent_and_worked_examples():
    tools = read("content/tools.yml")
    salary = tools.split("  - slug: salary-hourly-rate-calculator", 1)[1].split("\n  - slug:", 1)[0]
    fuel = tools.split("  - slug: fuel-cost-calculator", 1)[1].split("\n  - slug:", 1)[0]
    assert "Salary to Hourly Calculator Ireland" in salary
    assert "€50,000" in salary and "€24.65" in salary
    assert "take-home-pay-calculator" in salary
    assert "Fuel Cost Calculator Ireland" in fuel
    assert "€11.38" in fuel and "15,000 km" in fuel
    assert "/solar/" in fuel


def test_evergreen_guides_link_to_relevant_hubs():
    insurance = [
        "life-insurance-ireland",
        "mortgage-protection-insurance-ireland",
        "income-protection-insurance-ireland",
        "mortgage-protection-drawdown-ireland",
        "health-insurance-price-rises-benefit-cuts-ireland",
    ]
    for slug in insurance:
        assert "](/insurance/)" in read(f"content/wealth/{slug}.md"), slug
    assert "](/solar/)" in read("content/wealth/ev-vs-petrol-vs-diesel-ireland.md")


def test_solar_attribution_is_centralised_and_consent_gated():
    base = read("compound/site/templates/base.html")
    script = read("compound/site/static/solar-funnel.js")
    site = read("compound/site/static/site.js")
    assert "solar-funnel.js" in base
    assert "solar_journey_click" in script
    assert "compound_analytics_consent" in script
    for field in ("source_path", "destination_path", "destination_step", "journey_origin", "audience"):
        assert field in script
    assert "solar_journey_click" not in site  # no double-counting


def test_installer_enquiry_is_not_counted_as_homeowner_lead():
    sponsor = read("compound/site/static/solar-sponsors.js")
    assert 'params.get("submitted")==="1"' in sponsor
    assert "solar_installer_enquiry_submitted" in sponsor
    assert 'audience:"installer_business"' in sponsor
    assert "form.values" not in sponsor
    assert "solar-sponsors.js?v=3" in read("compound/site/templates/page.html")


def test_solar_and_insurance_hubs_have_indexable_canonical_sources():
    for path, canonical in (
        ("content/pages/solar.md", "/solar/"),
        ("content/pages/insurance.md", "/insurance/"),
        ("content/pages/solar-grants.md", "/solar/grants/"),
        ("content/pages/solar-batteries.md", "/solar/batteries/"),
    ):
        page = read(path)
        assert f"canonical_path: {canonical}" in page, path
    builder = read("compound/site/build.py")
    assert 'out / "sitemap.xml"' in builder
    assert "for pg in pages" in builder
    assert 'Disallow: /preview/' in builder
