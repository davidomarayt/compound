"""Editorial regression safeguards for the PIA mortgage deposit guide.

These source-level checks do not imply lender endorsement, full human
editorial approval, enacted PIA rules or live production deployment.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "/wealth/pia-mortgage-deposit-ireland/"
ARTICLE = ROOT / "content/wealth/pia-mortgage-deposit-ireland.md"
BACKLINK_FILES = [
    "compound/site/templates/pia_centre.html",
    "content/tool-guides/pia-calculator.md",
    "content/wealth/personal-investment-account-ireland.md",
    "content/wealth/pia-for-couples-ireland.md",
    "content/wealth/buying-home-budget-deposit-ireland.md",
    "content/wealth/mortgage-approval-affordability-ireland.md",
    "content/tool-guides/house-deposit-calculator.md",
    "content/pages/pia-invest-now-or-wait.md",
]


def test_pia_mortgage_editorial_status_and_dated_legislative_caution():
    page = ARTICLE.read_text(encoding="utf-8")
    assert "slug: pia-mortgage-deposit-ireland" in page
    assert "publication_status: published" in page
    assert "draft: false" in page
    assert "research_checked: 2026-11-21" in page
    assert "research_review_pending: true" in page
    assert "require_pinned_hero: true" in page
    assert "hero_image_url:" in page
    assert "hero_image_credit:" in page
    assert "hero_image_source:" in page
    assert "not enacted law" in page
    assert "1 July 2027" in page
    assert "No Irish bank has an established, published 2027 PIA-specific" in page


def test_mortgage_guidance_does_not_confuse_trading_with_gambling():
    page = ARTICLE.read_text(encoding="utf-8")
    for phrase in (
        "not automatically",
        "no published blanket Irish mortgage rule",
        "not evidence that broker transfers",
        "CCPC",
        "Bank of Ireland",
        "AIB",
        "Central Bank",
        "regular investing versus frequent trading",
        "repayment capacity",
        "source of funds",
    ):
        assert phrase.lower() in page.lower()


def test_mortgage_stress_arithmetic_and_contribution_limit():
    cost = 400_000
    deposit = cost * 0.1
    annual_contributions = 750 * 12
    assert deposit == 40_000
    assert annual_contributions == 9_000
    assert annual_contributions <= 12_000
    assert 40_000 * 0.75 == 30_000
    assert deposit - 30_000 == 10_000
    page = ARTICLE.read_text(encoding="utf-8")
    for figure in ("€40,000", "€30,000", "€10,000", "€36,000", "€9,000"):
        assert figure in page
    assert "would not reset" in page.replace("**", "")


def test_pia_mortgage_guide_outgoing_and_backlinks():
    page = ARTICLE.read_text(encoding="utf-8")
    for destination in (
        "/pia-calculator/",
        "/pia/providers/",
        "/pia/investment-eligibility/",
        "/pia/daily-valuation/",
        "/pia/invest-now-or-wait/",
        "/wealth/pia-for-couples-ireland/",
        "/wealth/mortgage-approval-affordability-ireland/",
        "/house-deposit-calculator/",
    ):
        assert destination in page
    for path in BACKLINK_FILES:
        assert URL in (ROOT / path).read_text(encoding="utf-8"), path
