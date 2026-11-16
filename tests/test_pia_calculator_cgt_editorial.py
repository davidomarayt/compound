"""Guard the dated Irish CGT comparison in the existing PIA calculator's explanation.

Revenue eBrief 142/26, 6 October 2026:
https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
This is a source-text regression test, not proof of a live deployment or a
human re-review of the complete calculator.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIA_GUIDE = ROOT / "content/tool-guides/pia-calculator.md"


def test_pia_cgt_comparison_has_correct_standard_rate_and_effective_dates():
    text = PIA_GUIDE.read_text(encoding="utf-8")
    assert "> 1% PIA tax versus 33% CGT." not in text
    assert "proposed 1% annual PIA account-value charge versus 31% standard CGT" in text
    assert "**on or after 7 October 2026**" in text
    assert "**6 October 2026**" in text
    assert "**33% development-land rate**" in text
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in text
    assert "31% is not a universal tax rate for all investments outside a PIA" in text


def test_pia_calculator_keeps_canonical_context_and_comparison_links():
    text = PIA_GUIDE.read_text(encoding="utf-8")
    assert "[Capital Gains Tax in Ireland guide](/wealth/capital-gains-tax-ireland/)" in text
    assert "[Investment Tax in Ireland guide](/wealth/investment-tax-ireland/)" in text
    assert "/wealth/personal-investment-account-ireland/" in text
    assert "/pia/vs-pension/" in text
    assert "365" in text and "€50,000" in text and "€12,000" in text
    assert "The calculator runs entirely in your browser." in text
