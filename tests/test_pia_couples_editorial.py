"""Editorial regression checks for the 21 November 2026 PIA couples guide.

These assertions protect content integrity and reciprocal navigation. They do
not claim the proposed 2027 account framework is enacted law.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "/wealth/pia-for-couples-ireland/"
ARTICLE = ROOT / "content/wealth/pia-for-couples-ireland.md"

LINKING_FILES = [
    "compound/site/templates/pia_centre.html",
    "content/tool-guides/pia-calculator.md",
    "content/pages/pia-vs-pension.md",
    "content/wealth/personal-investment-account-ireland.md",
    "content/wealth/revolut-joint-investment-accounts-ireland-2026.md",
    "content/wealth/pension-vs-investing-ireland.md",
]


def test_couples_article_published_but_legislation_and_review_status_truthful():
    text = ARTICLE.read_text(encoding="utf-8")
    assert "slug: pia-for-couples-ireland" in text
    assert "publication_status: published" in text
    assert "draft: false" in text
    assert "research_checked: 2026-11-21" in text
    assert "research_review_pending: true" in text
    assert "require_pinned_hero: true" in text
    assert "hero_image_source: \"https://www.pexels.com/photo/" in text
    assert "not enacted law" in text
    assert "conditional on legislation" in text
    assert "Individual Investment Account" in text
    assert "sole name" in text
    assert "beneficial ownership" in text
    assert "unmarried" in text
    assert "€3,000" in text


def test_couples_tax_examples_follow_proposed_individual_threshold_formula():
    def proposed_charge(average_value):
        return 0.01 * max(0, average_value - 50_000)

    assert proposed_charge(80_000) == 300
    assert proposed_charge(40_000) * 2 == 0
    assert proposed_charge(60_000) + proposed_charge(20_000) == 100
    assert proposed_charge(120_000) == 700
    assert proposed_charge(60_000) * 2 == 200
    text = ARTICLE.read_text(encoding="utf-8")
    for phrase in ["€300", "€100", "€0", "€700", "€200", "€500 difference"]:
        assert phrase in text


def test_couples_guide_is_interlinked_with_existing_pia_pages_and_backlinks():
    text = ARTICLE.read_text(encoding="utf-8")
    for destination in [
        "/pia-calculator/",
        "/pia/vs-pension/",
        "/pia/providers/",
        "/pia/daily-valuation/",
        "/wealth/personal-investment-account-ireland/",
        "/news/revolut-joint-investment-accounts-ireland-2026/",
    ]:
        assert destination in text
    for name in LINKING_FILES:
        assert URL in (ROOT / name).read_text(encoding="utf-8"), name
