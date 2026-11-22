"""Regression checks for the October 2026 standard CGT reduction in child savings.

Revenue eBrief 142/26, published 6 October 2026:
https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
These tests check article source; they do not establish publication or legal advice.
"""
from decimal import Decimal
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "content/wealth/saving-for-your-child-ireland.md"


def test_child_savings_share_rate_and_example_are_date_specific():
    text = GUIDE.read_text(encoding="utf-8")
    assert "Most gains fall under 33% CGT;" not in text
    assert "gains fall under 31% standard CGT" in text
    assert "on or after 7 October 2026" in text
    assert "up to 6 October 2026" in text
    assert "disposal date" in text.lower()
    assert "development land exception" in text
    assert "€5,806.30" in text and "€44,193.70" in text
    assert "€6,180.90" in text and "€43,819.10" in text
    assert Decimal("20000") - Decimal("1270") == Decimal("18730")
    assert Decimal("18730") * Decimal("0.31") == Decimal("5806.30")
    assert Decimal("50000") - Decimal("5806.30") == Decimal("44193.70")
    assert Decimal("18730") * Decimal("0.33") == Decimal("6180.90")
    assert Decimal("50000") - Decimal("6180.90") == Decimal("43819.10")


def test_child_savings_other_tax_and_publication_history_preserved():
    text = GUIDE.read_text(encoding="utf-8")
    assert "slug: saving-for-your-child-ireland" in text
    assert "date: '2026-09-17'" in text and "reviewed: '2026-09-30'" in text
    assert "approved_by: 'David O’Mara — explicit Publish instruction, 17 September 2026'" in text
    assert "Irish deposit interest normally has DIRT deducted at 33%" in text
    assert "current rate of **33%**" in text  # CAT, not standard CGT
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in text
    assert "[Capital Gains Tax guide](/wealth/capital-gains-tax-ireland/)" in text
    assert "this is not a full re-review of the guide" in text
    assert "/wealth/inheritance-tax-ireland/" in text
