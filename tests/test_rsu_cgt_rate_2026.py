"""Guard the October 2026 CGT rate change in the canonical RSU/share-option guide.

Revenue eBrief 142/26 (6 October 2026):
https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
Text checks verify an editorial correction, not a production deployment.
"""
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "content/wealth/rsu-share-options-tax-ireland.md"


def test_rsu_guide_uses_dated_standard_cgt_rate_and_correct_example():
    text = GUIDE.read_text(encoding="utf-8")
    assert "For most ordinary share gains, the standard CGT rate is **33%**." not in text
    assert "the standard CGT rate is **31%**" in text
    assert "on or after 7 October 2026" in text
    assert "up to 6 October 2026" in text
    assert "development land" in text
    assert "share disposal date" in text
    assert "€2,730 × 31% = €846.30" in text
    assert "€900.90" in text
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in text
    assert Decimal("2730") * Decimal("0.31") == Decimal("846.30")
    assert Decimal("2730") * Decimal("0.33") == Decimal("900.90")


def test_rsu_guide_retains_canonical_history_and_contextual_destinations():
    text = GUIDE.read_text(encoding="utf-8")
    assert "slug: rsu-share-options-tax-ireland" in text
    assert "date: 2026-10-04" in text and "reviewed: 2026-10-04" in text
    assert "approved_by: \"Explicit evergreen publish instruction — 4 October 2026\"" in text
    assert "This is not a full re-review of the other sections." in text
    assert "[Capital Gains Tax guide](/wealth/capital-gains-tax-ireland/)" in text
    assert "/capital-gains-tax-calculator/" in text
    assert "/take-home-pay-calculator/" in text
    assert "The later sale is a separate event." in text
