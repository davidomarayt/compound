"""Focused idempotency and evidentiary tests for 12 November private-company coverage."""
import json
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "monitoring/private-company-publications/2026-11-12.json"

def all_publication_records():
    """Preserve historical assertions while allowing newer source-backed profile facts."""
    ledgers = sorted((ROOT / "monitoring/private-company-publications").glob("20??-??-??.json"))
    by_slug = {}
    for path in ledgers:
        daily = json.loads(path.read_text())
        assert daily["date"] == path.stem
        assert len({a["slug"] for a in daily["articles"]}) == len(daily["articles"])
        for record in daily["articles"]:
            assert record["primary_source_urls"]
            assert record["event_date"] <= daily["date"]
            by_slug.setdefault(record["slug"], []).append(record)
    return by_slug


def assert_current_profile_uses_latest_sourced_disclosure(profile, slug, records):
    """Current profile disclosure must have a sourced dated publication trail."""
    assert records, f"No publication evidence for {slug}"
    development = profile["latest_development"]
    allowed = {url for record in records for url in record["primary_source_urls"]}
    assert development["source"] in allowed, f"Unsourced latest profile: {slug}"
    assert development["date"] >= max(record["event_date"] for record in records), f"Profile regressed: {slug}"
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
    records = all_publication_records()
    for prior in d["articles"]:
        latest = profiles[prior["slug"]]["latest_development"]
        assert_current_profile_uses_latest_sourced_disclosure(profiles[prior["slug"]], prior["slug"], records[prior["slug"]])
        assert latest["date"] >= prior["event_date"], f"Profile regressed: {prior['slug']}"



def test_daily_private_company_13_nov_stories_are_distinct_and_photo_sourced():
    latest = json.loads((ROOT / "monitoring/private-company-publications/2026-11-13.json").read_text())
    assert latest["date"] == "2026-11-13"
    assert [r["slug"] for r in latest["articles"]] == ["openai", "anthropic", "blue-origin"]
    assert len({r["story_fingerprint"] for r in latest["articles"]}) == 3
    assert len({r["image_source"] for r in latest["articles"]}) == 3
    watchlist = json.loads((ROOT / "content/company-watchlist.json").read_text())
    profiles = {p["slug"]: p for p in watchlist["private"]}
    records = all_publication_records()
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
        assert_current_profile_uses_latest_sourced_disclosure(profiles[record["slug"]], record["slug"], records[record["slug"]])
        assert profiles[record["slug"]]["latest_development"]["date"] >= record["event_date"]

