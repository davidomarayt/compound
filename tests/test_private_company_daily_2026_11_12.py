"""Focused idempotency and evidentiary tests for 12 November private-company coverage."""
import json
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "monitoring/private-company-publications/2026-11-12.json"
def test_daily_private_company_unique_sourced_real_photos():
    d = json.loads(LEDGER.read_text())
    assert d["date"] == "2026-11-12"
    assert [r["slug"] for r in d["articles"]] == ["openai", "anthropic", "revolut"]
    assert len({r["story_fingerprint"] for r in d["articles"]}) == 3
    for r in d["articles"]:
        raw = (ROOT / r["article_path"]).read_text()
        assert raw.startswith("---\n")
        meta = yaml.safe_load(raw.split("---", 2)[1])
        assert meta["date"].isoformat() == "2026-11-12" if hasattr(meta["date"], "isoformat") else meta["date"] == "2026-11-12"
        assert meta["editorial_review_status"] == "pending"
        assert "reviewed" not in meta and "approved_by" not in meta
        assert meta["require_pinned_hero"] is True
        assert meta["hero_image_url"].startswith("https://upload.wikimedia.org/")
        assert "CC BY 2.0" in meta["hero_image_credit"]
        assert "company-" + r["slug"] in meta["tags"]
        assert meta["hero_image_source"] == r["image_source"]
        assert r["profile_url"].replace("https://compound.ie","") in raw
        assert len(raw.split()) > 680
    watchlist = json.loads((ROOT / "content/company-watchlist.json").read_text())
    profiles = {p["slug"]: p for p in watchlist["private"]}
    assert all(profiles[x["slug"]]["latest_development"]["source"] in x["primary_source_urls"] for x in d["articles"])
