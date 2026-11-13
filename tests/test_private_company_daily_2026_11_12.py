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
    # The evergreen profile is a living hub: its latest dated development may
    # advance beyond the 12 November article when new independently sourced
    # daily coverage is added. Preserve old article source validation while
    # checking the latest profile update against the newest publication ledger.
    recent = json.loads((ROOT / "monitoring/private-company-publications/2026-11-13.json").read_text())
    recent_by_slug = {x["slug"]: x for x in recent["articles"]}
    for prior in d["articles"]:
        latest = profiles[prior["slug"]]["latest_development"]
        source_urls = list(prior["primary_source_urls"])
        if prior["slug"] in recent_by_slug:
            source_urls += recent_by_slug[prior["slug"]]["primary_source_urls"]
        assert latest["source"] in source_urls, f"Unsourced latest profile: {prior['slug']}"
        assert latest["date"] >= prior["event_date"], f"Profile regressed: {prior['slug']}"


def test_daily_private_company_13_nov_stories_are_distinct_and_photo_sourced():
    latest = json.loads((ROOT / "monitoring/private-company-publications/2026-11-13.json").read_text())
    assert latest["date"] == "2026-11-13"
    assert [r["slug"] for r in latest["articles"]] == ["openai", "anthropic", "blue-origin"]
    assert len({r["story_fingerprint"] for r in latest["articles"]}) == 3
    assert len({r["image_source"] for r in latest["articles"]}) == 3
    watchlist = json.loads((ROOT / "content/company-watchlist.json").read_text())
    profiles = {p["slug"]: p for p in watchlist["private"]}
    for record in latest["articles"]:
        article = (ROOT / record["article_path"]).read_text()
        meta = yaml.safe_load(article.split("---", 2)[1])
        assert meta["date"].isoformat() == "2026-11-13" if hasattr(meta["date"], "isoformat") else meta["date"] == "2026-11-13"
        assert meta["editorial_review_status"] == "pending"
        assert "reviewed" not in meta and "approved_by" not in meta
        assert meta["require_pinned_hero"] is True
        assert "archival" in meta["hero_image_alt"]
        assert meta["hero_image_source"] == record["image_source"]
        assert meta["hero_image_url"] == record["photo_download_url"]
        assert meta["image"].endswith(Path(record["article_path"]).stem + ".jpg")
        assert "company-" + record["slug"] in meta["tags"]
        assert record["profile_url"].removeprefix("https://compound.ie") in article
        assert record["primary_source_urls"][0] in article
        assert len(article.split()) >= 900
        assert profiles[record["slug"]]["latest_development"]["source"] in record["primary_source_urls"]
        assert profiles[record["slug"]]["latest_development"]["date"] == record["event_date"]

