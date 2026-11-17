"""Guard the export-income tax limitation disclosed by both existing solar tools.

Primary sources verified 17 November 2026:
- Revenue eBrief 016/24 (11 January 2024): €400 per qualifying person,
  excess domestic microgeneration profit is potentially taxable.
- Revenue eBrief 020/26 (28 January 2026): Finance Act 2025 extends
  this domestic exemption through 31 December 2028.

This tests the explanatory source Markdown. It does not assert that tax is
calculated by the interactive tools, prove a generated-page deployment, or
constitute human review.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLAR_PAYBACK = ROOT / "content/tool-guides/solar-payback-calculator.md"
SOLAR_OPTIMISER = ROOT / "content/tool-guides/solar-ev-battery-optimiser.md"
EXPORT_TAX_GUIDE = ROOT / "content/wealth/tax-on-solar-export-payments-ireland.md"
REVENUE_NOTICE = (
    "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-0202026.aspx"
)
REVENUE_MANUAL = (
    "https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-07/07-01-44.pdf"
)
TAX_GUIDE_URL = "/wealth/tax-on-solar-export-payments-ireland/"


def test_solar_payback_explains_gross_export_tax_limit():
    text = SOLAR_PAYBACK.read_text(encoding="utf-8")
    assert "### Are export payments after tax?" in text
    assert "does not deduct Income Tax, USC or PRSI" in text
    assert "€400 of annual qualifying export profit exempt" in text
    assert "31 December 2028" in text
    assert "potentially taxable profit, not the amount of tax" in text
    assert TAX_GUIDE_URL in text
    assert REVENUE_NOTICE in text
    assert REVENUE_MANUAL in text
    assert "Compare the solar-only and solar-plus-battery cases separately." in text


def test_solar_optimiser_distinguishes_export_from_avoided_import():
    text = SOLAR_OPTIMISER.read_text(encoding="utf-8")
    assert "**Export-income tax limitation:**" in text
    assert "20-year net-benefit comparisons" in text
    assert "before any tax on taxable export profit" in text
    assert "do not calculate personal Income Tax, USC or PRSI" in text
    assert "31 December 2028" in text
    assert "€400 of qualifying annual profit per eligible individual" in text
    assert TAX_GUIDE_URL in text
    assert REVENUE_NOTICE in text


def test_existing_canonical_tax_guide_remains_source_linked():
    text = EXPORT_TAX_GUIDE.read_text(encoding="utf-8")
    assert "canonical_path: /wealth/tax-on-solar-export-payments-ireland/" in text
    assert "publication_status: published" in text
    assert REVENUE_NOTICE in text
