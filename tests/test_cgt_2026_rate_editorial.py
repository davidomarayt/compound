"""Regression guard for the October 2026 CGT rate change in editorial material.

Revenue eBrief 142/26: https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
Revenue calculation guide: https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx
"""
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_canonical_cgt_guide_uses_effective_date_and_correct_examples():
    guide = _source("content/wealth/capital-gains-tax-ireland.md")
    assert "standard CGT rate is **31% for disposals made on or after 7 October 2026**" in guide
    assert "33% for standard disposals up to and including 6 October 2026" in guide
    assert "Development land continues to have a separate 33% rate" in guide
    assert "date: '2026-09-30'" in guide  # Preserve original publication.
    assert "reviewed: '2026-09-30'" in guide  # Targeted rate check is not blanket review.
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in guide
    for taxable_gain in (6430, 6730, 77730, 10730):
        tax = Decimal(taxable_gain) * Decimal("0.31")
        rendered = f"€{tax:,.2f}"
        assert f"CGT at 31%: **{rendered}**" in guide
    assert "€393.70" in guide  # 31% x €1,270 annual exemption.


def test_related_explanation_keeps_cgt_distinct_from_dirt_and_fund_tax():
    overview = _source("content/wealth/investment-tax-ireland.md")
    calculator_guide = _source("content/tool-guides/capital-gains-tax-calculator.md")
    tools = _source("content/tools.yml")
    assert "standard CGT rate is **31% for most disposals made on or after 7 October 2026**" in overview
    assert "**CGT at 31%:** €1,466.30" in overview  # (€6,000 - €1,270) x 31%.
    assert "| Deposit interest | DIRT | 33% for Irish-resident individuals |" in overview
    assert "38% individual rate from 1 Jan 2026" in overview
    assert "standard CGT rate is 31% for most disposals made on or after 7 October 2026" in calculator_guide
    assert "Earlier standard disposals and development land" not in tools  # Avoid false universal rules.
    assert "earlier standard disposals and development land generally retain the 33% rate" in tools
