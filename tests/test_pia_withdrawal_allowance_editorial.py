"""Check PIA contribution/withdrawal guidance against committee-amended draft sections 747H, 747L and 747R."""

from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "content/wealth/personal-investment-account-ireland.md"
CALCULATOR = Path(__file__).resolve().parents[1] / "content/tool-guides/pia-calculator.md"
AMENDED_BILL = "https://data.oireachtas.ie/ie/oireachtas/bill/2026/98/eng/ver_a/b98a26d.pdf"


def test_pia_guide_corrects_withdrawal_allowance_guidance():
    text = GUIDE.read_text(encoding="utf-8")
    assert "### Do withdrawals restore your contribution allowance?" in text
    assert "**No, under the committee-amended Bill.**" in text
    assert "747L(2)(d)" in text
    assert "the withdrawal does not create another €5,000" in text
    assert "These are proposed rules" in text
    assert "The final enacted legislation may differ" in text
    assert AMENDED_BILL in text
    assert "This also needs final legislative detail." not in text


def test_unused_allowance_caution_keeps_draft_and_source_clear():
    text = GUIDE.read_text(encoding="utf-8")
    assert "section 747H" in text
    assert "Do not assume unused contribution capacity can be carried" in text
    assert AMENDED_BILL in text
    assert "slug: personal-investment-account-ireland" in text
    assert "reviewed: 2026-11-07" in text


def test_calculator_does_not_restore_allowance_or_hide_excess_charge():
    text = CALCULATOR.read_text(encoding="utf-8")
    assert "### Do withdrawals give me more contribution room?" in text
    assert "No, under the committee-amended draft" in text
    assert "€4,000, not €7,000" in text
    assert "747R" in text
    assert "€30 in total" in text
    assert "models neither excess contributions nor their monthly charge" in text
    assert AMENDED_BILL in text
