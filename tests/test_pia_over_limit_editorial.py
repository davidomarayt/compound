"""Editorial checks for the 27 November 2026 article on PIA over-limit contributions.

The article explains proposed section 747R of Finance (No. 2) Bill 2026 and
Dáil Report Stage amendments 18 and 45. It must not present them as enacted law.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "/wealth/pia-over-12000-limit/"
ARTICLE = ROOT / "content/wealth/pia-over-12000-limit.md"


def test_over_limit_article_status_and_image_metadata_are_truthful():
    text = ARTICLE.read_text(encoding="utf-8")
    assert "slug: pia-over-12000-limit" in text
    assert "research_review_pending: true" in text
    assert "require_pinned_hero: true" in text
    assert "hero_image_source: https://commons.wikimedia.org/wiki/File:" in text
    assert "CC BY-SA 4.0" in text
    assert "these are proposed rules" in text
    assert "The Seanad stages and signing into law are still to come" in text
    assert "Individual Investment Account" in text


def test_over_limit_examples_follow_proposed_747r_arithmetic():
    def monthly_charge(outstanding_excess):
        return round(0.01 * max(0, outstanding_excess), 2)

    assert monthly_charge(13_000 - 12_000) == 10
    assert monthly_charge(13_000 - 12_000 - 1_000) == 0
    assert monthly_charge(1_000) * 12 == 120
    assert 0.01 * (60_000 - 50_000) == 100
    assert monthly_charge(60) == 0.6
    text = ARTICLE.read_text(encoding="utf-8")
    for phrase in ["**€10**", "**€0**", "**€120 over a year**", "**€100 a year**", "**€0.60**", "€3,000 penalty", "30 days"]:
        assert phrase in text


def test_over_limit_article_is_linked_from_pia_pages():
    text = ARTICLE.read_text(encoding="utf-8")
    for destination in ["/pia-calculator/", "/wealth/personal-investment-account-ireland/", "/pia/#pia-launch-tracker", "/pia/providers/"]:
        assert destination in text
    for path in [
        "compound/site/templates/pia_centre.html",
        "content/wealth/personal-investment-account-ireland.md",
        "content/tool-guides/pia-calculator.md",
    ]:
        assert URL in (ROOT / path).read_text(encoding="utf-8")
