"""Regression coverage for Budget 2027 energy journalism and honest solar journeys."""
from pathlib import Path

from compound.site.build import article_from_file, parse_markdown_file

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "content/wealth/no-energy-credit-budget-2027-electricity-bills-winter.md"
OLD = ROOT / "content/wealth/social-democrats-400-energy-credit-budget-2027.md"


def test_winter_energy_news_is_sourced_indexable_and_charted():
    metadata, body = parse_markdown_file(NEW)
    article = article_from_file(NEW)
    assert article is not None
    assert article.canonical_path == "/news/no-energy-credit-budget-2027-electricity-bills-winter/"
    assert article.date.isoformat() == "2026-10-12"
    assert article.publication_status == "published"
    assert metadata["pexels_photo_id"] == 6964105
    assert len(article.charts) == 2
    rendered = article.body_with_charts
    assert rendered.count('class="chart chart-bar"') == 2
    assert "<svg " in rendered
    assert "€636" in rendered
    assert "before VAT" in rendered
    assert "not a forecast" in body.lower() or "not a projection" in body.lower()
    assert all(path in rendered for path in (
        "/electricity-cost-calculator/", "/solar-payback-calculator/",
        "/solar/get-quotes/", "/solar/installers/", "/solar/grants/",
        "/wealth/electricity-tariffs-ireland/",
    ))
    assert all(key in rendered for key in (
        'data-energy-funnel="electricity_tool"',
        'data-energy-funnel="solar_payback"',
        'data-energy-funnel="quote_brief"',
    ))
    assert len(article.sources) >= 6
    assert not any("https://compound.ie/solar/for-installers/" in s.get("url", "") for s in article.sources)


def test_old_proposal_preserves_url_and_corrects_status():
    metadata, body = parse_markdown_file(OLD)
    article = article_from_file(OLD)
    assert article.canonical_path == "/news/social-democrats-400-energy-credit-budget-2027/"
    assert article.date.isoformat() == "2026-10-01"
    assert article.reviewed.isoformat() == "2026-10-12"
    assert "was NOT included" in body
    assert "Budget 2027 is due" not in body
    assert "/news/no-energy-credit-budget-2027-electricity-bills-winter/" in body
    assert "€70,000" in body and "not an enacted eligibility rule" in body
    assert "/solar-payback-calculator/" in body
    assert "approved_by" in metadata


def test_energy_solar_events_require_analytics_consent():
    js = (ROOT / "compound/site/static/energy-budget-2027.js").read_text(encoding="utf-8")
    solar_js = (ROOT / "compound/site/static/solar-hub.js").read_text(encoding="utf-8")
    template = (ROOT / "compound/site/templates/article.html").read_text(encoding="utf-8")
    assert "compound_analytics_consent" in js
    assert "==='granted'" in js
    assert "energy_solar_payback_click" not in js
    assert "energy_electricity_tool_click" in js
    assert "energy_quote_brief_click" not in js
    assert "source_page:location.pathname" in js
    assert "solarTrack(events[link.pathname])" not in solar_js
    sitewide = (ROOT / "compound/site/static/solar-funnel.js").read_text(encoding="utf-8")
    base = (ROOT / "compound/site/templates/base.html").read_text(encoding="utf-8")
    assert "solar_journey_click" in sitewide
    assert "destination_step: step" in sitewide
    assert "journey_origin: origin" in sitewide
    assert "solar-funnel.js?v=20261012-1" in base
    assert "energy-budget-2027.css?v=1" in template
    assert "energy-budget-2027.js?v=1" in template
    assert "no-energy-credit-budget-2027-electricity-bills-winter" in template


def test_energy_hubs_link_back_to_articles():
    paths = {
        "content/pages/solar.md": "/news/no-energy-credit-budget-2027-electricity-bills-winter/",
        "content/wealth/electricity-tariffs-ireland.md": "/news/no-energy-credit-budget-2027-electricity-bills-winter/",
        "content/wealth/budget-2027-what-to-watch.md": "/news/no-energy-credit-budget-2027-electricity-bills-winter/",
        "content/tool-guides/electricity-cost-calculator.md": "/news/no-energy-credit-budget-2027-electricity-bills-winter/",
        "content/tool-guides/solar-payback-calculator.md": "/news/no-energy-credit-budget-2027-electricity-bills-winter/",
    }
    for path, target in paths.items():
        assert target in (ROOT / path).read_text(encoding="utf-8")
