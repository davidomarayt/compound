"""Guard the dated direct-share CGT comparison in the shares/ETFs/funds guide.

Primary sources, checked 23 November 2026:
https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx
Source tests are not proof of successful production deployment.
"""

from decimal import Decimal
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "content/wealth/shares-etfs-funds-ireland.md"


def test_direct_share_cgt_rates_have_effective_dates_and_primary_source():
    text = GUIDE.read_text(encoding="utf-8")
    assert "standard CGT rate is 31% for most disposals on or after 7 October 2026" in text
    assert "33% for standard disposals up to and including 6 October 2026" in text
    assert "Development land has its own 33% rate" in text
    assert "€1,270 annual personal CGT exemption" in text
    assert "disposal date" in text
    assert "no-1422026.aspx" in text
    assert "how-to-calculate-cgt.aspx" in text
    assert Decimal("18730") * Decimal("0.31") == Decimal("5806.30")
    assert Decimal("18730") * Decimal("0.33") == Decimal("6180.90")


def test_existing_guide_scope_metadata_and_canonical_links_remain():
    text = GUIDE.read_text(encoding="utf-8")
    assert "slug: shares-etfs-funds-ireland" in text
    assert "date: 2026-09-23" in text
    assert "reviewed: 2026-10-06" in text
    assert "Investing in Ireland 101 · Chapter 3 of 9" in text
    assert "38%" in text  # 2026 relevant fund treatment is separate from share CGT
    assert "eight-year deemed-disposal rule" in text
    assert "[Capital Gains Tax Calculator](/capital-gains-tax-calculator/)" in text
    assert "[Capital Gains Tax guide](/wealth/capital-gains-tax-ireland/)" in text
    assert "This targeted CGT check is not a full review" in text
    assert "23 November 2026" in text
    assert "31% for most disposals" in text
    assert "The tax row is deliberately cautious" in text
