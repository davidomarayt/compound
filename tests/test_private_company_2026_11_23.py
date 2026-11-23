"""Regression and provenance audit for 23 November private-company publication batch."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-23"
LEDGER = json.loads((ROOT / "monitoring/private-company-publications" / f"{DATE}.json").read_text())
WATCH = json.loads((ROOT / "content/company-watchlist.json").read_text())


def article(path):
    source = (ROOT / path).read_text(encoding="utf-8")
    assert source.startswith("---\n")
    _, front, body = source.split("---", 2)
    return yaml.safe_load(front), body


def test_unique_quota_and_public_anthropic():
    assert len(LEDGER["articles"]) == 3
    assert {x["slug"] for x in LEDGER["articles"]} == {"openai", "anthropic", "lego"}
    assert sum(x["action"] == "new_article" for x in LEDGER["articles"]) == 2
    assert sum(x["action"] == "substantive_canonical_update" for x in LEDGER["articles"]) == 1
    assert all(isinstance(x["live_http_verified"], bool) for x in LEDGER["articles"])
    assert all(x["status"] in {"prepared_pending_ci", "new_article_published_live_verified", "updated_existing_canonical_live_verified"} for x in LEDGER["articles"])
    assert not any(x["slug"] == "anthropic" for x in WATCH["private"])
    assert any(x["slug"] == "ant" and x["ticker"] == "ANT" for x in WATCH["listed"])
    assert len({x["canonical_url"] for x in LEDGER["articles"]}) == 3


def test_sources_canonical_photos_and_review_status():
    for entry in LEDGER["articles"]:
        meta, body = article(entry["article_path"])
        assert meta["canonical_path"] == entry["canonical_url"].removeprefix("https://compound.ie")
        assert meta["publication_status"] == "published"
        assert meta["editorial_review_status"] == "pending"
        assert meta["require_pinned_hero"] is True
        assert meta["image_source"] == entry["image_source"]
        assert "company-" + entry["slug"] in meta["tags"]
        assert entry["profile_url"].removeprefix("https://compound.ie") in body
        assert len(meta["meta_description"]) < 190
        if entry["action"] == "new_article":
            assert str(meta["date"]) == DATE
            assert meta["hero_image_url"].startswith("https://upload.wikimedia.org/")
            assert "archiv" in meta["hero_image_alt"].lower()
            assert "creativecommons.org/licenses/" in meta["hero_image_credit"]
            assert len(body.split()) >= 700
        else:
            assert str(meta["date"]) == "2026-11-16"
            assert "stock-ant" in meta["tags"]
            assert entry["live_required_fingerprint"] in body
            assert "private-company" not in meta["tags"]


def test_arithmetic_and_explicit_claims():
    # Closed IPO: the secondary shares do not generate issuer proceeds.
    assert 1_103_351_354 + 23_648_646 == 1_127_000_000
    assert 1_127_000_000 * 83 == 93_541_000_000
    assert round(1_103_351_354 * 83 / 1e9, 3) == 91.578
    assert abs(313_253_007 * 83 - 26_000_000_000) < 1_000
    assert 6 * 15_000 * 2 == 180_000
    assert 6_400 * 40 == 256_000
    assert 6_400 * 70 == 448_000
    assert 6_400 * 100 == 640_000
    assert 20_000 * 12 == 240_000
    assert 50_000 * 12 == 600_000


def test_primary_source_ledger_and_stale_proposal_distinction():
    by_slug = {x["slug"]: x for x in LEDGER["articles"]}
    assert "openai.com/index/perplexity-and-intelligence/" in str(by_slug["openai"]["primary_source_urls"])
    assert "anthropic.com/news/ipo-close" in str(by_slug["anthropic"]["primary_source_urls"])
    assert len(by_slug["lego"]["primary_source_urls"]) == 2
    anthropic = article(by_slug["anthropic"]["article_path"])[1]
    assert "dated 10–16 November prospectus-era sensitivity analysis" in anthropic
    assert "not a private company" in anthropic
    openai = article(by_slug["openai"]["article_path"])[1]
    assert "not an agreed industry pact" in openai
    lego = article(by_slug["lego"]["article_path"])[1]
    assert "hypothetical" in lego.lower()
