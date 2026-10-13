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


def test_new_east_west_solar_evergreen_is_original_and_connected():
    article = read("content/wealth/east-west-facing-solar-panels-ireland.md")
    assert "publication_status: published" in article
    assert "2026-10-13" in article
    assert "require_pinned_hero: true" in article
    assert "images.pexels.com/photos/8457868/" in article
    assert "Stoneybatter" in article and "PVGIS" in article
    assert "irradiation" in article.lower() and "not" in article.lower()
    assert "<svg" in article and "aria-labelledby" in article
    assert "](/solar/)" in article and "](/solar-payback-calculator/)" in article
    for feeder in (
        "content/pages/solar.md",
        "content/wealth/solar-panels-ireland.md",
        "content/wealth/how-many-solar-panels-do-i-need-ireland.md",
    ):
        assert "/wealth/east-west-facing-solar-panels-ireland/" in read(feeder)


def test_winter_solar_article_chart_source_transparency_and_funnel():
    path = "content/wealth/solar-panels-winter-ireland.md"
    text = read(path)
    assert "publication_status: published" in text
    assert "require_pinned_hero: true" in text
    assert "images.pexels.com/photos/15922991/" in text
    assert text.count('class="chart-svg"') >= 2
    assert "aria-labelledby=" in text
    assert "Dublin PVGIS-based" in text
    assert "CC BY 4.0" in text
    assert "did **not** query the PVGIS API independently" in text
    assert "12.8%" in text
    assert "55.8%" in text
    assert "€873" in text
    for href in ("/solar/", "/solar/compare-quotes/", "/solar/grants/",
                 "/solar/batteries/", "/solar-payback-calculator/",
                 "/wealth/east-west-facing-solar-panels-ireland/"):
        assert href in text
    for feeder in ("content/pages/solar.md",
                   "content/wealth/solar-panels-ireland.md",
                   "content/wealth/how-many-solar-panels-do-i-need-ireland.md",
                   "content/wealth/average-home-electricity-use-ireland.md"):
        assert "/wealth/solar-panels-winter-ireland/" in read(feeder)


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
