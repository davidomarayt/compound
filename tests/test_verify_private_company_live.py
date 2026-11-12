"""Offline tests of the post-deployment private-company HTTP publishing gate."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from scripts import verify_private_company_live as verifier


def _data():
    return {
        "date": date.today().isoformat(),
        "articles": [{
            "company": "OpenAI",
            "slug": "openai",
            "status": "prepared_not_live",
            "canonical_url": "https://compound.ie/wealth/test-company-news/",
        }],
    }


def _responses():
    url = "https://compound.ie/wealth/test-company-news/"
    social = "https://compound.ie/static/discover/test-company-news-16x9.webp"
    profile = "https://compound.ie/companies/openai/"
    html = (
        f'<link rel="canonical" href="{url}">'
        '<a href="/about/">Compound Research</a>'
        '<a href="/companies/openai/">OpenAI</a>'
        f'<meta property="og:image" content="{social}">'
        f'<meta name="twitter:image" content="{social}">'
        '<img src="/static/images/evergreen/test-company-news.jpg">'
        + verifier.AD_LOADER
    ).encode()
    return {
        url: html,
        social: b"RIFF" + (b"x" * 4) + b"WEBP" + b"x" * 21000,
        "https://compound.ie/static/images/evergreen/test-company-news.jpg": bytes([0xFF, 0xD8, 0xFF]) + b"x" * 51000,
        profile: (('<a href="/wealth/test-company-news/">Read</a>' + verifier.AD_LOADER)).encode(),
    }


def test_checks_public_html_and_social_and_cover(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(verifier, "LEDGER_DIR", tmp_path)
    ledger = tmp_path / f"{date.today().isoformat()}.json"
    ledger.write_text(json.dumps(_data()))
    responses = _responses()
    seen = []

    def fake_fetch(url, *, binary=False):
        seen.append((url, binary))
        return responses[url]

    monkeypatch.setattr(verifier, "fetch", fake_fetch)
    verifier.verify()
    assert len(seen) == 4
    assert sum(binary for _, binary in seen) == 2
    assert "PASS: 1 independent private-company live publication" in capsys.readouterr().out


def test_bad_live_social_image_causes_publication_verification_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "LEDGER_DIR", tmp_path)
    (tmp_path / f"{date.today().isoformat()}.json").write_text(json.dumps(_data()))
    responses = _responses()
    responses["https://compound.ie/static/discover/test-company-news-16x9.webp"] = b"not a webp" * 3000
    monkeypatch.setattr(verifier, "fetch", lambda url, *, binary=False: responses[url])
    with pytest.raises(AssertionError):
        verifier.verify()


def test_old_ledger_does_not_block_unrelated_future_deployments(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "LEDGER_DIR", tmp_path)
    old = date.today() - timedelta(days=9)
    (tmp_path / f"{old.isoformat()}.json").write_text(json.dumps(_data()))
    monkeypatch.setattr(verifier, "fetch", lambda *args, **kw: pytest.fail("stale ledger was fetched"))
    verifier.verify()
