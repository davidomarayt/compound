"""Guard 2026 Rent Tax Credit limits against unqualified Budget 2027 claims.

Primary evidence checked 18 November 2026:
- Revenue Rent Tax Credit overview, published 1 January 2026.
- Oireachtas Budget Statement 2027, Dáil Éireann, 6 October 2026.
This asserts source text, not enactment, production deployment or human review.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "content/wealth/rent-tax-credit-ireland-who-can-claim.md"
BUDGET_GUIDE = ROOT / "content/wealth/rent-tax-credit-budget-2027-ireland.md"
CALCULATOR_GUIDE = ROOT / "content/tool-guides/rent-tax-credit-calculator.md"


def test_2026_rent_credit_guide_distinguishes_proposed_next_year_amounts():
    text = GUIDE.read_text(encoding="utf-8")
    assert "2024–2026" in text
    assert "€1,000" in text and "€2,000" in text
    assert "2027–2028 planning note" in text
    assert "proposed for the **2027 and 2028 tax years**" in text
    assert "€1,150 for an individual" in text
    assert "€2,300 for a jointly assessed couple" in text
    assert "final legislative position and updated Revenue claim rules were not independently verified" in text
    assert "https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/land-and-property/rent-credit/index.aspx" in text
    assert "https://www.oireachtas.ie/en/debates/debate/dail/2026-10-06/3/" in text
    assert "The 2024 to 2028 figures are the ones that apply this year." not in text


def test_rent_credit_guide_preserves_canonicals_and_original_date():
    source = GUIDE.read_text(encoding="utf-8")
    budget = BUDGET_GUIDE.read_text(encoding="utf-8")
    calc = CALCULATOR_GUIDE.read_text(encoding="utf-8")
    assert "slug: rent-tax-credit-ireland-who-can-claim" in source
    assert "date: '2026-09-13'" in source
    assert "/wealth/rent-tax-credit-budget-2027-ireland/" in source
    assert "/rent-tax-credit-calculator/" in source
    assert "slug: rent-tax-credit-budget-2027-ireland" in budget
    assert "## Budget 2027 Rent Tax Credit increase" in calc
    assert "The calculator now defaults to 2027" in calc
