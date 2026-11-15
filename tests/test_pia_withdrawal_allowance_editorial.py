"""Check PIA contribution/withdrawal guidance against section 747L(2)(d) of the Bill as introduced."""

from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "content/wealth/personal-investment-account-ireland.md"


def test_pia_guide_corrects_withdrawal_allowance_guidance():
    text = GUIDE.read_text(encoding="utf-8")
    assert "### Do withdrawals restore your contribution allowance?" in text
    assert "**No, under the Bill as introduced.**" in text
    assert "Section 747L(2)(d)" in text
    assert "the withdrawal does not create another €5,000" in text
    assert "These are proposed rules" in text
    assert "This also needs final legislative detail." not in text


def test_unused_allowance_caution_keeps_draft_and_source_clear():
    text = GUIDE.read_text(encoding="utf-8")
    assert "Section 747H" in text
    assert "Do not assume unused contribution capacity can be carried" in text
    assert "https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf" in text
    assert "slug: personal-investment-account-ireland" in text
    assert "reviewed: 2026-11-07" in text
