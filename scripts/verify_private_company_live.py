#!/usr/bin/env python3
"""HTTP verification of the latest private-company publication ledger after Pages deploy.

The build-time test confirms artifact contents; this checks actual canonical
HTTP pages and their licensed documentary/photo/social URLs, from GitHub's
public runner, *after* the deployment reports success.
"""
from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "monitoring/private-company-publications"
SITE = "https://compound.ie"
AD_LOADER = "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client="


def fetch(url: str, *, binary: bool = False) -> bytes:
    assert url.startswith(SITE + "/"), f"Unexpected host: {url}"
    command = [
        "curl", "--fail", "--silent", "--show-error", "--location",
        "--retry", "8", "--retry-delay", "5", "--retry-all-errors",
        "--connect-timeout", "10", "--max-time", "30",
        "-H", "Cache-Control: no-cache", url,
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    content = result.stdout
    assert len(content) > (18000 if binary else 500), f"Unusually small public response: {url}"
    return content


def verify() -> None:
    ledgers = sorted(LEDGER_DIR.glob("20??-??-??.json"))
    if not ledgers:
        print("No private-company publication ledger to check")
        return
    ledger_file = ledgers[-1]
    ledger_date = date.fromisoformat(ledger_file.stem)
    if (date.today() - ledger_date).days > 7:
        print(f"Latest private-company ledger is older than seven days: {ledger_date}; skipping")
        return
    ledger = json.loads(ledger_file.read_text(encoding="utf-8"))
    count = 0
    for story in ledger.get("articles", []):
        if story.get("status") in {"blocked", "skipped", "held_for_review", "failed"}:
            continue
        url = story["canonical_url"]
        assert urlparse(url).netloc == "compound.ie"
        html = fetch(url).decode("utf-8")
        assert f'<link rel="canonical" href="{url}">' in html, url
        assert 'Compound Research</a>' in html, url
        assert AD_LOADER in html, f"Ad loader not configured on public article: {url}"
        assert f'href="/companies/{story["slug"]}/"' in html, url

        slug = Path(urlparse(url).path.rstrip("/")).name
        social = f"{SITE}/static/discover/{slug}-16x9.webp"
        assert f'property="og:image" content="{social}"' in html, url
        assert f'name="twitter:image" content="{social}"' in html, url
        image_bytes = fetch(social, binary=True)
        assert image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP", social
        cover = f"{SITE}/static/images/evergreen/{slug}.jpg"
        assert f'src="/static/images/evergreen/{slug}.jpg"' in html, url
        photo_bytes = fetch(cover, binary=True)
        assert len(photo_bytes) > 50000 and photo_bytes[:3] == b"\xff\xd8\xff", cover

        profile = f"{SITE}/companies/{story['slug']}/"
        hub = fetch(profile).decode("utf-8")
        assert f'href="/wealth/{slug}/"' in hub, profile
        assert AD_LOADER in hub, f"Profile ad loader missing: {profile}"
        print(f"PASS: production HTML, ad loader, company hub, cover and OG/Twitter WebP: {url}")
        count += 1
    print(f"PASS: {count} independent private-company live publication(s), {ledger_date}")


if __name__ == "__main__":
    verify()
