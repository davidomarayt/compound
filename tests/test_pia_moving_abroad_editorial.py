"""Editorial checks for the 28 November 2026 article on moving abroad with a PIA.

The article explains proposed section 747M (change of residence) of Finance
(No. 2) Bill 2026 as passed by the Dáil. It must not present it as enacted law.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "/wealth/pia-moving-abroad-ireland/"
ARTICLE = ROOT / "content/wealth/pia-moving-abroad-ireland.md"


def test_moving_abroad_status_and_image_metadata_are_truthful():
    text = ARTICLE.read_text(encoding="utf-8")
    assert "slug: pia-moving-abroad-ireland" in text
    assert "research_review_pending: true" in text
    assert "require_pinned_hero: true" in text
    assert "hero_image_source: https://commons.wikimedia.org/wiki/File:" in text
    assert "CC BY-SA 4.0" in text
    assert "these are proposed rules" in text
    assert "The Seanad stages and signing into law are still to come" in text
    assert "ver_b/b98b26d.pdf" in text
    assert "Individual Investment Account" in text


def test_moving_abroad_examples_follow_proposed_747m_and_747q():
    from datetime import date, timedelta

    relevant = date(2029, 9, 1)
    window_end = relevant + timedelta(days=30)
    assert window_end == date(2029, 10, 1)
    assert date(2029, 9, 5) <= window_end < date(2029, 10, 5)

    def charge(average):
        return round(0.01 * max(0, average - 50_000), 2)

    assert charge(80_000) == 300
    assert charge(45_000) == 0
    text = ARTICLE.read_text(encoding="utf-8")
    for phrase in ["**€300**", "**€0**", "**1 October**", "**1 January of the next tax year**", "**€3,000 penalty**", "within 30 days"]:
        assert phrase in text


def test_moving_abroad_article_is_linked_from_pia_pages():
    text = ARTICLE.read_text(encoding="utf-8")
    for destination in ["/pia-calculator/", "/wealth/personal-investment-account-ireland/", "/pia/#pia-launch-tracker", "/pia/providers/"]:
        assert destination in text
    for path in [
        "compound/site/templates/pia_centre.html",
        "content/wealth/personal-investment-account-ireland.md",
        "content/tool-guides/pia-calculator.md",
    ]:
        assert URL in (ROOT / path).read_text(encoding="utf-8")
