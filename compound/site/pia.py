"""Validate public PIA provider data, prices and optional future paid placements.

The comparison is editorial. Sponsorships appear separately; referrals only render
after an explicit approved partner configuration. No unknown fee is ever treated as zero.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

FEE_FIELDS = (
    "account_annual_eur",
    "account_annual_pct",
    "custody_annual_pct",
    "fund_annual_pct",
    "trade_eur",
)
ALLOWED_STAGES = {"intent", "launch-planned", "live"}
ALLOWED_CATEGORIES = {"Bank", "Insurer", "Broker", "Investment firm", "Other"}


def _https_url(value: object, description: str) -> str:
    url = str(value or "").strip()
    parts = urlparse(url)
    if (
        parts.scheme != "https" or not parts.hostname or parts.username
        or parts.password or parts.fragment or any(char.isspace() for char in url)
    ):
        raise ValueError(f"{description} must be an absolute, public HTTPS URL")
    return url


def _fee_model(model: object, slug: str) -> dict:
    if not isinstance(model, dict):
        raise ValueError(f"Invalid fee model on {slug}")
    if not model.get("verified", False):
        if any(model.get(k) is not None for k in FEE_FIELDS):
            raise ValueError(f"{slug} has unverified numeric PIA fees")
        return {"verified": False}
    for key in ("as_of", "source_url", "reference_investment"):
        if not str(model.get(key) or "").strip():
            raise ValueError(f"Verified fee model on {slug} missing {key}")
    _https_url(model["source_url"], f"{slug} fee source")
    values = {}
    for key in FEE_FIELDS:
        if isinstance(model.get(key), bool) or not isinstance(model.get(key), (int, float)):
            raise ValueError(f"{slug}: {key} requires a verified numeric value, including zero")
        value = float(model[key])
        if not math.isfinite(value) or value < 0 or (key.endswith("_pct") and value > 100):
            raise ValueError(f"Invalid {key} for {slug}")
        values[key] = value
    return {"verified": True, **values, "as_of": str(model["as_of"]),
            "source_url": model["source_url"], "reference_investment": str(model["reference_investment"])}


def load_pia_tracker(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {}
    data = data or {}
    if not isinstance(data, dict):
        raise ValueError("PIA tracker must be a mapping")
    updated = str(data.get("updated") or "").strip()
    if not re.fullmatch(r"20\\d{2}-\\d{2}-\\d{2}", updated):
        raise ValueError("PIA tracker needs an YYYY-MM-DD last-checked date")
    providers = data.get("providers") or []
    if not isinstance(providers, list):
        raise ValueError("PIA providers must be a list")
    seen = set()
    for p in providers:
        if not isinstance(p, dict):
            raise ValueError("PIA provider entry must be an object")
        slug = str(p.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Invalid or duplicate PIA provider slug: {slug}")
        seen.add(slug)
        for key in ("name", "statement", "status", "availability", "annual_fee",
                    "dealing_fee", "fund_fee", "fx_fee", "minimum_investment",
                    "transfer_terms", "investment_range", "source_label", "checked"):
            if not str(p.get(key) or "").strip():
                raise ValueError(f"Missing {key} for PIA provider {slug}")
        if p.get("category") not in ALLOWED_CATEGORIES:
            raise ValueError(f"Unsupported PIA provider type: {slug}")
        if p.get("stage") not in ALLOWED_STAGES:
            raise ValueError(f"Unsupported PIA provider stage: {slug}")
        _https_url(p.get("source_url"), f"{slug} official source")
        model = _fee_model(p.get("fee_model") or {"verified": False}, slug)
        p["fee_model"] = model
        referral = p.get("referral") or {}
        if referral.get("active"):
            if not referral.get("approved") or not all(str(referral.get(k) or "").strip()
                for k in ("url", "label", "disclosure", "agreement_reference")):
                raise ValueError(f"Active referral on {slug} requires a verified agreement and disclosure")
            _https_url(referral["url"], f"{slug} affiliate destination")
        p["referral"] = referral
    sponsors = data.get("sponsorships") or []
    if not isinstance(sponsors, list):
        raise ValueError("PIA sponsorships must be a list")
    for sponsor in sponsors:
        if not isinstance(sponsor, dict):
            raise ValueError("Invalid PIA sponsor")
        if sponsor.get("active"):
            if not sponsor.get("approved") or not all(str(sponsor.get(k) or "").strip()
                for k in ("name", "label", "url", "disclosure", "agreement_reference")):
                raise ValueError("Active PIA sponsorship requires a contract and clear disclosure")
            if "sponsored" not in sponsor["label"].lower():
                raise ValueError("Paid PIA promotions must be labelled Sponsored")
            _https_url(sponsor["url"], "sponsor destination")
    return {
        "updated": updated,
        "providers": sorted(providers, key=lambda p: p["name"].casefold()),
        "sponsorships": [s for s in sponsors if s.get("active")],
        "complete_fee_count": sum(p["fee_model"]["verified"] for p in providers),
    }
