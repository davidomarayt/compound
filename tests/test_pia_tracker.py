"""Safety and data-quality checks for PIA fee and paid partnership records."""
from copy import deepcopy

import pytest
import yaml

from compound.site.pia import load_pia_tracker


BASE = {
    "updated": "2026-10-10",
    "providers": [{
        "name": "Sample Bank", "slug": "sample-bank", "category": "Bank",
        "stage": "intent", "status": "Plans to offer", "statement": "Publicly considering the scheme",
        "availability": "Not open yet", "annual_fee": "Not published", "dealing_fee": "Not published",
        "fund_fee": "Not published", "fx_fee": "Not published",
        "minimum_investment": "Not published", "transfer_terms": "Not published",
        "investment_range": "Not published", "checked": "2026-10-10",
        "source_url": "https://example.com/pia", "source_label": "Official provider page",
        "fee_model": {"verified": False}, "referral": {"active": False},
    }],
    "sponsorships": [],
}


def read_tracker(tmp_path, data):
    p = tmp_path / "pia-providers.yml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return load_pia_tracker(p)


def test_unknown_fees_are_not_zero(tmp_path):
    result = read_tracker(tmp_path, deepcopy(BASE))
    assert result["complete_fee_count"] == 0
    assert result["providers"][0]["fee_model"] == {"verified": False}
    assert not result["sponsorships"]


def test_unverified_numeric_fees_rejected(tmp_path):
    data = deepcopy(BASE)
    data["providers"][0]["fee_model"]["account_annual_eur"] = 0
    with pytest.raises(ValueError, match="unverified"):
        read_tracker(tmp_path, data)


def test_fee_schedule_needs_all_components_and_primary_source(tmp_path):
    data = deepcopy(BASE)
    data["providers"][0]["fee_model"] = {
        "verified": True, "as_of": "2026-10-10",
        "source_url": "https://example.com/pia-fees",
        "reference_investment": "Reference investment",
        "account_annual_eur": 12, "account_annual_pct": 0.2,
        "custody_annual_pct": 0.1, "fund_annual_pct": 0.3,
        "trade_eur": 1.0,
    }
    result = read_tracker(tmp_path, data)
    assert result["complete_fee_count"] == 1
    assert result["providers"][0]["fee_model"]["verified"] is True
    del data["providers"][0]["fee_model"]["fund_annual_pct"]
    with pytest.raises(ValueError, match="fund_annual_pct"):
        read_tracker(tmp_path, data)


def test_referrals_require_approved_agreement_and_disclosure(tmp_path):
    data = deepcopy(BASE)
    data["providers"][0]["referral"] = {"active": True, "url": "https://example.com/open"}
    with pytest.raises(ValueError, match="verified agreement"):
        read_tracker(tmp_path, data)
    data["providers"][0]["referral"] = {
        "active": True, "approved": True, "url": "javascript:alert(1)",
        "label": "Open PIA", "disclosure": "Compound may earn a fee",
        "agreement_reference": "signed-agreement-001",
    }
    with pytest.raises(ValueError, match="HTTPS"):
        read_tracker(tmp_path, data)
    data["providers"][0]["referral"]["url"] = "https://example.com/open-account"
    assert read_tracker(tmp_path, data)["providers"][0]["referral"]["active"] is True


def test_sponsorship_separate_from_organic_ranking(tmp_path):
    data = deepcopy(BASE)
    data["sponsorships"] = [{
        "active": True, "approved": True, "name": "Partner One",
        "label": "Sponsored placement", "url": "https://example.com/",
        "disclosure": "Paid advertising", "agreement_reference": "contract-123",
    }]
    result = read_tracker(tmp_path, data)
    assert len(result["sponsorships"]) == 1
    assert result["providers"][0]["name"] == "Sample Bank"
    data["sponsorships"][0]["label"] = "Independent best provider"
    with pytest.raises(ValueError, match="Sponsored"):
        read_tracker(tmp_path, data)


def test_invalid_duplicates_and_unapproved_urls_rejected(tmp_path):
    data = deepcopy(BASE)
    data["providers"].append(deepcopy(data["providers"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        read_tracker(tmp_path, data)
    data = deepcopy(BASE)
    data["providers"][0]["source_url"] = "http://example.com/"
    with pytest.raises(ValueError, match="HTTPS"):
        read_tracker(tmp_path, data)
