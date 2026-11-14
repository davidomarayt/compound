"""Regression checks for the source-backed Irish investor/deposit protection explanation.

Primary evidence checked 2026-11-14:
- https://www.centralbank.ie/consumer-hub/explainers/what-compensation-schemes-protect-consumers-of-authorised-firms
- https://www.centralbank.ie/consumer-hub/deposit-guarantee-scheme
- https://www.ccpc.ie/manage-your-money/saving-and-investments/types-of-investment/ics-protection
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BROKER_GUIDE = ROOT / "content/wealth/choose-investment-broker-ireland.md"


def test_broker_guide_distinguishes_investor_and_deposit_protection():
    text = BROKER_GUIDE.read_text(encoding="utf-8")
    assert "90% of the eligible net loss, up to a maximum payout of €20,000" in text
    assert "€100,000 per person per institution" in text
    assert "is **not automatically** an eligible bank deposit" in text
    assert "Neither ICS nor other investor-compensation arrangements insure you" in text
    assert "the **specific legal entity** and its home-country investor-compensation scheme" in text
    assert "The Central Bank decides which scheme compensates" in text
    assert "does not guarantee eligibility" in text


def test_broker_sources_and_canonical_guide_link_remain_verifiable():
    text = BROKER_GUIDE.read_text(encoding="utf-8")
    assert "https://www.centralbank.ie/consumer-hub/deposit-guarantee-scheme" in text
    assert "https://www.ccpc.ie/manage-your-money/saving-and-investments/types-of-investment/ics-protection" in text
    assert "https://www.centralbank.ie/consumer-hub/explainers/what-compensation-schemes-protect-consumers-of-authorised-firms" in text
    assert "[before-you-invest cash and emergency-fund checklist](/wealth/before-you-invest-ireland/)" in text
    assert "slug: choose-investment-broker-ireland" in text
    assert "date: 2026-09-23" in text
    assert "reviewed: 2026-10-06" in text  # Not a fabricated whole-article review.
