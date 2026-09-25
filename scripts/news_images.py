#!/usr/bin/env python3
"""Attach a relevant image to every published Compound News article.

Primary path:
- Search Pexels with a story-specific query.
- Download the API-provided landscape crop for the website/Open Graph image.
- Download the API-provided portrait crop for Instagram.
- Write visible photographer/Pexels attribution into article front matter.

Fallback:
- If no PEXELS_API_KEY is configured or the search fails, create a unique branded
  Compound editorial SVG so a published news story is never image-less.

RSS/source images are deliberately not scraped: licensing is handled separately.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
STATIC = ROOT / "compound" / "site" / "static"
NEWS_IMAGES = STATIC / "images" / "news"
FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

PILLAR_FALLBACK = {
    "wealth": ("#f0e3d3", "#755436"),
    "health": ("#e4ebe1", "#365e4f"),
    "happiness": ("#e9e3ee", "#715e88"),
}


def parse(path: Path) -> tuple[dict[str, Any], str, re.Match[str]]:
    raw = path.read_text(encoding="utf-8")
    match = FRONT.match(raw)
    if not match:
        raise ValueError(f"{path} has no YAML front matter")
    meta = yaml.safe_load(match.group(1)) or {}
    return meta, raw, match


def is_published_news(meta: dict[str, Any]) -> bool:
    tags = {str(x).lower() for x in meta.get("tags") or []}
    status = str(meta.get("publication_status") or ("draft" if meta.get("draft") else "published")).lower()
    canonical = str(meta.get("canonical_path") or "")
    return status == "published" and not meta.get("draft") and ("news" in tags or canonical.startswith("/news/"))


def image_exists(meta: dict[str, Any]) -> bool:
    image = str(meta.get("image") or "")
    if not image.startswith("/static/"):
        return False
    return (STATIC / image.removeprefix("/static/")).is_file()


def is_fallback(meta: dict[str, Any]) -> bool:
    return str(meta.get("image_credit") or "").startswith("Illustration: Compound news fallback")


def default_query(meta: dict[str, Any]) -> str:
    explicit = str(meta.get("news_image_query") or "").strip()
    if explicit:
        return explicit
    tags = [str(x).replace("-", " ") for x in meta.get("tags") or [] if str(x).lower() not in {"news", "ireland"}]
    pillar = str(meta.get("pillar") or "")
    generic = {
        "wealth": "finance economy money",
        "health": "healthcare research medicine",
        "happiness": "community lifestyle wellbeing",
    }.get(pillar, "Ireland news")
    useful = " ".join(tags[:3]).strip()
    return useful or generic


def pexels_photo(query: str, api_key: str) -> dict[str, Any] | None:
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "orientation": "landscape", "size": "large", "per_page": 8},
        )
        response.raise_for_status()
        photos = response.json().get("photos") or []
        return photos[0] if photos else None


def pexels_photo_by_id(photo_id: str, api_key: str) -> dict[str, Any]:
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(
            f"https://api.pexels.com/v1/photos/{photo_id}",
            headers={"Authorization": api_key},
        )
        response.raise_for_status()
        return response.json()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        destination.write_bytes(response.content)


def wrap(text: str, width: int = 33, max_lines: int = 4) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= width or not current:
            current = test
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines - 1:
            break
    if current and len(lines) < max_lines:
        remaining_index = sum(len(x.split()) for x in lines)
        remaining = " ".join(words[remaining_index:])
        if len(remaining) > width * 2:
            remaining = remaining[: width * 2 - 1].rstrip() + "…"
        lines.append(remaining)
    return lines[:max_lines]


def fallback_svg(meta: dict[str, Any], destination: Path) -> None:
    pillar = str(meta.get("pillar") or "wealth")
    bg, accent = PILLAR_FALLBACK.get(pillar, ("#eee8df", "#755436"))
    title = str(meta.get("title") or "Compound News")
    lines = wrap(title)
    title_svg = "".join(
        f'<text x="84" y="{250 + i * 80}" font-family="Georgia,serif" font-size="62" fill="#33252e">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="660" viewBox="0 0 1200 660">
<rect width="1200" height="660" fill="{bg}"/>
<rect x="0" y="0" width="18" height="660" fill="{accent}"/>
<text x="84" y="95" font-family="Arial,sans-serif" font-size="22" font-weight="700" letter-spacing="4" fill="{accent}">COMPOUND NEWS · {html.escape(pillar.upper())}</text>
<line x1="84" x2="1110" y1="130" y2="130" stroke="#c8bfb9" stroke-width="2"/>
{title_svg}
<text x="84" y="604" font-family="Arial,sans-serif" font-size="20" fill="#5f555b">What changed · What it could mean in Ireland</text>
<text x="1085" y="604" text-anchor="end" font-family="Georgia,serif" font-size="38" fill="{accent}">compound.</text>
</svg>"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8")


def yaml_line(key: str, value: str) -> str:
    return f"{key}: {json.dumps(value, ensure_ascii=False)}\n"


def inject_fields(path: Path, raw: str, match: re.Match[str], fields: dict[str, str]) -> None:
    block = match.group(1)
    # Replace any existing simple scalar field; append otherwise. These fields are
    # intentionally top-level and controlled by this script.
    for key, value in fields.items():
        pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
        replacement = yaml_line(key, value).rstrip("\n")
        if pattern.search(block):
            block = pattern.sub(replacement, block, count=1)
        else:
            anchor = re.search(r"(?m)^sources:\s*$", block)
            if anchor:
                block = block[: anchor.start()] + replacement + "\n" + block[anchor.start():]
            else:
                block = block.rstrip() + "\n" + replacement
    new_raw = "---\n" + block.rstrip() + "\n---\n" + raw[match.end():]
    path.write_text(new_raw, encoding="utf-8")


def process(path: Path, api_key: str, force: bool = False) -> str:
    meta, raw, match = parse(path)
    slug = str(meta.get("slug") or path.stem)

    # Evergreen articles can pin a specific Pexels photo by ID. This keeps the
    # selected cover stable while reusing the same attribution/download pipeline.
    pinned_pexels_id = str(meta.get("pexels_photo_id") or "").strip()
    if pinned_pexels_id:
        if not api_key:
            raise RuntimeError(f"PEXELS_API_KEY is required for pinned cover on {slug}")
        photo = pexels_photo_by_id(pinned_pexels_id, api_key)
        hero_rel = f"/static/images/evergreen/{slug}.jpg"
        download(photo["src"]["landscape"], STATIC / hero_rel.removeprefix("/static/"))
        fields = {
            "image": hero_rel,
            "image_alt": str(photo.get("alt") or f"Illustrative photo for {meta.get('title', 'Compound')}"),
            "image_credit": f"{photo.get('photographer', 'Pexels photographer')} on Pexels",
            "image_source": str(photo.get("url") or "https://www.pexels.com"),
        }
        inject_fields(path, raw, match, fields)
        return f"pexels-pinned:{pinned_pexels_id}"

    if not is_published_news(meta):
        return "skip:not-news"

    existing = image_exists(meta)
    if existing and not force and not (api_key and is_fallback(meta)):
        return "skip:has-image"

    query = default_query(meta)
    NEWS_IMAGES.mkdir(parents=True, exist_ok=True)

    if api_key:
        try:
            photo = pexels_photo(query, api_key)
            if photo:
                hero_rel = f"/static/images/news/{slug}.jpg"
                social_rel = f"/static/images/news/{slug}-portrait.jpg"
                download(photo["src"]["landscape"], STATIC / hero_rel.removeprefix("/static/"))
                portrait_url = photo.get("src", {}).get("portrait") or photo["src"]["landscape"]
                download(portrait_url, STATIC / social_rel.removeprefix("/static/"))
                fields = {
                    "image": hero_rel,
                    "image_alt": str(photo.get("alt") or f"Illustrative photo for {meta.get('title', 'Compound News')}"),
                    "image_credit": f"{photo.get('photographer', 'Pexels photographer')} on Pexels",
                    "image_source": str(photo.get("url") or "https://www.pexels.com"),
                    "social_image": social_rel,
                    "news_image_query": query,
                }
                inject_fields(path, raw, match, fields)
                old = str(meta.get("image") or "")
                if old.endswith(".svg") and old.startswith("/static/images/news/"):
                    old_path = STATIC / old.removeprefix("/static/")
                    if old_path.exists():
                        old_path.unlink()
                return f"pexels:{photo.get('id')}:{query}"
        except Exception as exc:
            print(f"Pexels lookup failed for {path.name}: {exc}")

    fallback_rel = f"/static/images/news/{slug}.svg"
    fallback_svg(meta, STATIC / fallback_rel.removeprefix("/static/"))
    fields = {
        "image": fallback_rel,
        "image_alt": f"Compound editorial graphic for {meta.get('title', 'this news story')}",
        "image_credit": "Illustration: Compound news fallback",
        "image_source": "#image-note",
        "social_image": fallback_rel,
        "news_image_query": query,
    }
    inject_fields(path, raw, match, fields)
    return f"fallback:{query}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Replace existing news images too")
    args = parser.parse_args()

    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    changed = 0
    for pillar in ("health", "wealth", "happiness"):
        directory = CONTENT / pillar
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            result = process(path, api_key, args.force)
            if not result.startswith("skip:"):
                changed += 1
                print(f"{path}: {result}")
    print(f"News image pipeline changed {changed} article(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
