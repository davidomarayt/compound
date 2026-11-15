"""Validate public PIA provider data, prices and optional future paid placements.

The comparison is editorial. Sponsorships appear separately; referrals only render
after an explicit approved partner configuration. No unknown fee is ever treated as zero.
"""
from __future__ import annotations

import math
from datetime import date
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
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {"updated": "2026-10-10"}
    data = data or {}
    if not isinstance(data, dict):
        raise ValueError("PIA tracker must be a mapping")
    updated = str(data.get("updated") or "").strip()
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", updated):
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


LAUNCH_MILESTONE_STATES = {"confirmed", "unverified", "target"}


def load_pia_launch_tracker(path: Path) -> dict | None:
    """Load a dated, cited editorial launch tracker. Missing test fixtures omit it.

    Confirmed milestones describe *past events*, never enactment by implication.
    Future target dates remain conditional on law and provider readiness.
    """
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("PIA launch tracker must be a mapping")
    try:
        checked = date.fromisoformat(str(data["checked"]))
        target = date.fromisoformat(str(data["target_date"]))
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("PIA tracker requires valid checked and target_date") from exc
    if target <= checked:
        raise ValueError("PIA planned launch must follow source-check date")
    for key in ("headline", "next_checkpoint"):
        if not str(data.get(key) or "").strip():
            raise ValueError(f"PIA tracker missing {key}")
    milestones = data.get("milestones")
    if not isinstance(milestones, list) or len(milestones) < 4:
        raise ValueError("PIA tracker requires at least four sourced milestones")
    seen = set()
    states = set()
    for item in milestones:
        if not isinstance(item, dict):
            raise ValueError("PIA launch milestone must be a mapping")
        ident = str(item.get("id") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident) or ident in seen:
            raise ValueError(f"Duplicate or invalid PIA milestone id: {ident}")
        seen.add(ident)
        state = item.get("state")
        if state not in LAUNCH_MILESTONE_STATES:
            raise ValueError(f"PIA milestone {ident} has unsupported state")
        states.add(state)
        for key in ("title", "date_label", "summary", "source_label"):
            if not str(item.get(key) or "").strip():
                raise ValueError(f"PIA milestone {ident} missing {key}")
        _https_url(item.get("source_url"), f"{ident} milestone source")
        raw_date = item.get("date")
        if state in {"confirmed", "target"}:
            if not raw_date:
                raise ValueError(f"PIA milestone {ident} requires a specific source-backed date")
            try:
                event_day = date.fromisoformat(str(raw_date))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"PIA milestone {ident} date is invalid") from exc
            if state == "confirmed" and event_day > checked:
                raise ValueError(f"Future PIA event {ident} cannot be marked confirmed")
            if state == "target" and event_day != target:
                raise ValueError(f"PIA target milestone {ident} must match published target date")
        elif raw_date:
            raise ValueError(f"Unverified milestone {ident} cannot present a dated event")
        if item.get("internal_url") and item["internal_url"] != "/pia/providers/":
            raise ValueError(f"PIA milestone {ident} uses an unapproved internal URL")
        if item.get("internal_url") and not str(item.get("internal_label") or "").strip():
            raise ValueError(f"PIA milestone {ident} needs an internal link label")
    if not {"confirmed", "unverified", "target"}.issubset(states):
        raise ValueError("PIA tracker must distinguish verified, unverified and target statuses")
    if milestones[-1]["state"] != "target" or sum(m["state"] == "target" for m in milestones) != 1:
        raise ValueError("PIA tracker must finish with exactly one proposed launch target")
    return {"checked": checked.isoformat(), "target_date": target.isoformat(),
            "headline": str(data["headline"]), "next_checkpoint": str(data["next_checkpoint"]),
            "milestones": milestones}
