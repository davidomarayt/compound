#!/usr/bin/env python3
"""Fail a production site build if unreviewed private-company stories carry ads or missing covers."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "monitoring/private-company-publications/2026-11-11.json"
PUBLIC = ROOT / "public"


def verify() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")

    for story in data["articles"]:
        url = story["canonical_url"]
        parsed = urlparse(url)
        assert parsed.scheme == "https" and parsed.netloc == "compound.ie"
        html_path = PUBLIC / parsed.path.strip("/") / "index.html"
        assert html_path.exists(), f"Missing article: {html_path}"
        html = html_path.read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="{url}">' in html, url
        assert "<h1>" in html and url in sitemap, url
        assert "awaiting human review" in html, f"Human review label absent: {url}"
        assert "not received human editorial approval" in html, url
        assert "pagead2.googlesyndication.com" not in html, url
        assert "adsbygoogle" not in html and "data-ad-client" not in html, url
        assert "Every article is reviewed and approved before publication" not in html, url

        slug = Path(story["article_path"]).stem
        photo_rel = f"/static/images/evergreen/{slug}.jpg"
        photo = PUBLIC / photo_rel.lstrip("/")
        assert photo.is_file() and photo.stat().st_size > 50000, f"Missing approved photograph: {photo}"
        with Image.open(photo) as image:
            assert image.format == "JPEG" and image.width >= 1000 and image.height >= 600
            image.verify()
        assert f'src="{photo_rel}"' in html, f"Wrong cover: {url}"
        # The visible JPEG is not the social image: site/build.py generates
        # a 1200x675 WebP for Open Graph and Twitter from the pinned photo.
        social_rel = f"/static/discover/{slug}-16x9.webp"
        social = PUBLIC / social_rel.lstrip("/")
        assert social.is_file() and social.stat().st_size > 20000, (
            f"Missing generated social image: {social}"
        )
        with Image.open(social) as image:
            assert image.format == "WEBP" and image.size == (1200, 675), (
                f"Wrong social image format/dimensions: {social}"
            )
            image.verify()
        assert f'property="og:image" content="https://compound.ie{social_rel}"' in html, (
            f"Wrong Open Graph image: {url}"
        )
        assert f'name="twitter:image" content="https://compound.ie{social_rel}"' in html, (
            f"Wrong Twitter image: {url}"
        )
        assert story["image_source"] in html, f"Image source missing: {url}"

        hub_path = PUBLIC / "companies" / story["slug"] / "index.html"
        assert hub_path.is_file(), f"Missing private-company hub: {hub_path}"
        hub = hub_path.read_text(encoding="utf-8")
        assert f'href="{parsed.path}"' in hub, f"Company hub does not link article: {url}"
        assert f'href="/companies/{story["slug"]}/"' in html, f"Article lacks hub link: {url}"
        assert "pagead2.googlesyndication.com" not in hub
        assert "adsbygoogle" not in hub and "data-ad-client" not in hub
        assert story["profile_url"] in sitemap
        print(f"PASS: {story['company']} article and profile have original cover, links and zero Google ads")

    print("PASS: all three private-company stories meet ad-free and media publication checks")


if __name__ == "__main__":
    verify()
