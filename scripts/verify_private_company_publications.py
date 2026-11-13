#!/usr/bin/env python3
"""Fail closed if any of the three articles lacks canonical, image, backlink or ads."""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LEDGER_DIR = ROOT / "monitoring/private-company-publications"
LEDGER = sorted(LEDGER_DIR.glob("20??-??-??.json"))[-1]
def check() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert len(data["articles"]) == 3 and len({x["slug"] for x in data["articles"]}) == 3
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    audit = os.environ.get("COMPOUND_AUDIT_MODE", "").lower() in ("1", "true", "yes")
    for item in data["articles"]:
        url = item["canonical_url"]
        loc = urlparse(url)
        assert loc.netloc == "compound.ie" and loc.scheme == "https"
        page = PUBLIC / loc.path.strip("/") / "index.html"
        assert page.is_file(), f"Missing article route: {url}"
        html = page.read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="{url}">' in html, url
        assert url in sitemap, f"Missing sitemap: {url}"
        assert "<h1>" in html, url
        assert 'Compound Research</a>' in html, f"Missing truthful neutral attribution: {url}"
        assert "Every article is reviewed and approved before publication" not in html, url
        if not audit:
            assert "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" in html, f"Missing standard ad loader: {url}"
        photo_rel = "/static/images/evergreen/" + Path(item["article_path"]).stem + ".jpg"
        cover = PUBLIC / photo_rel.lstrip("/")
        assert cover.is_file() and cover.stat().st_size > 50000, f"Missing real licensed cover: {cover}"
        with Image.open(cover) as im:
            assert im.format == "JPEG" and im.width >= 1000 and im.height >= 600
            im.verify()
        assert f'src="{photo_rel}"' in html, f"Wrong article cover: {url}"
        social_rel = "/static/discover/" + Path(item["article_path"]).stem + "-16x9.webp"
        social = PUBLIC / social_rel.lstrip("/")
        assert social.is_file() and social.stat().st_size > 20000, f"Missing OG asset: {social}"
        with Image.open(social) as im:
            assert im.format == "WEBP" and im.size == (1200,675)
            im.verify()
        assert f'property="og:image" content="https://compound.ie{social_rel}"' in html, url
        assert f'name="twitter:image" content="https://compound.ie{social_rel}"' in html, url
        assert item["image_source"] in html, url
        hub = PUBLIC / "companies" / item["slug"] / "index.html"
        assert hub.is_file(), f"Missing profile: {hub}"
        hub_html = hub.read_text(encoding="utf-8")
        assert f'href="{loc.path}"' in hub_html, f"Missing profile backlink: {url}"
        assert f'href="/companies/{item["slug"]}/"' in html, f"Missing article backlink: {url}"
        assert f'<time datetime="{item["event_date"]}">' in hub_html or "Latest verified development" in hub_html
        if not audit:
            assert "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" in hub_html, f"Missing profile ad loader: {url}"
        assert item["profile_url"] in sitemap
        print(f"PASS: {item['company']} canonical, research, licence, cover, social and reciprocal profile links")
if __name__ == "__main__":
    check()
