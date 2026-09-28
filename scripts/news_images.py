#!/usr/bin/env python3
"""Attach a relevant image to every published Compound News article.

Primary path:
- Search Pexels with a story-specific query.
- Download the API-provided landscape crop for the website/Open Graph image.
- Download the API-provided portrait crop for Instagram.
- Write visible photographer/Pexels attribution into article front matter.

Fallback:
- If no PEXELS_API_KEY is configured or the search fails, create a unique branded
  Compound editorial JPEG so the article still has a raster cover and Google Discover derivatives.

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
from PIL import Image, ImageDraw, ImageFont, ImageOps

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

# Permanent, locally hosted editorial photographs used as a no-network safety net.
# Each generated cover is written to a slug-specific path, so the site keeps its
# one-cover-per-article validation while never falling back to text graphics.
LOCAL_PHOTOS = {
    "health": [
        {"file": "health.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e", "alt": "Illustrative health and wellbeing photograph"},
        {"file": "nutrition.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1494597564530-871f2b93ac55", "alt": "Illustrative healthy food photograph"},
        {"file": "mindful.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773", "alt": "Illustrative wellbeing photograph"},
        {"file": "adult-sleep.jpg", "credit": "Greg Pappas / Unsplash", "url": "https://unsplash.com/photos/woman-sleeping-on-bed-under-blankets-rUc9hVE-L-E", "alt": "Illustrative sleep photograph"},
        {"file": "oatmeal.jpg", "credit": "Brooke Lark / Unsplash", "url": "https://unsplash.com/photos/two-bowls-of-oatmeal-with-fruits-W9OKrxBqiZA", "alt": "Illustrative nutrition photograph"},
        {"file": "glp1-injector.jpg", "credit": "Haberdoedas / Unsplash", "url": "https://unsplash.com/photos/a-semaglutide-injection-pen-is-shown-TzKc7FGaL7Y", "alt": "Illustrative medicine photograph"},
    ],
    "wealth": [
        {"file": "wealth.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1484154218962-a197022b5858", "alt": "Illustrative financial planning photograph"},
        {"file": "tax-paperwork.jpg", "credit": "Kelly Sikkema / Unsplash", "url": "https://unsplash.com/photos/person-holding-paper-near-pen-and-calculator-xoU52jUVUXA", "alt": "Illustrative tax and household finance photograph"},
        {"file": "retirement-walk.jpg", "credit": "micheile henderson / Unsplash", "url": "https://unsplash.com/photos/man-and-woman-walking-on-road-during-daytime-PpZasS086os", "alt": "Illustrative retirement photograph"},
        {"file": "budget-dublin.jpg", "credit": "Yanhao Fang / Unsplash", "url": "https://unsplash.com/photos/samuel-beckett-bridge-and-dublin-cityscape-reflected-in-the-liffey-bjROiiuUXwA", "alt": "Illustrative Dublin economy and budget photograph"},
        {"file": "landscape.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1470770841072-f978cf4d019e", "alt": "Illustrative long-term planning photograph"},
    ],
    "happiness": [
        {"file": "happiness.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1499750310107-5fef28a66643", "alt": "Illustrative everyday life photograph"},
        {"file": "mindful.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773", "alt": "Illustrative mental wellbeing photograph"},
        {"file": "hobby-painting.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f", "alt": "Illustrative hobbies and creativity photograph"},
        {"file": "landscape.jpg", "credit": "Unsplash", "url": "https://images.unsplash.com/photo-1470770841072-f978cf4d019e", "alt": "Illustrative outdoor wellbeing photograph"},
    ],
}


def parse(path: Path) -> tuple[dict[str, Any], str, re.Match[str]]:
    raw = path.read_text(encoding="utf-8")
    match = FRONT.match(raw)
    if not match:
        raise ValueError(f"{path} has no YAML front matter")
    meta = yaml.safe_load(match.group(1)) or {}
    return meta, raw, match


def is_published(meta: dict[str, Any]) -> bool:
    status = str(meta.get("publication_status") or ("draft" if meta.get("draft") else "published")).lower()
    return status == "published" and not meta.get("draft")


def is_published_news(meta: dict[str, Any]) -> bool:
    tags = {str(x).lower() for x in meta.get("tags") or []}
    canonical = str(meta.get("canonical_path") or "")
    return is_published(meta) and ("news" in tags or canonical.startswith("/news/"))


def image_exists(meta: dict[str, Any]) -> bool:
    image = str(meta.get("image") or "")
    if not image.startswith("/static/"):
        return False
    return (STATIC / image.removeprefix("/static/")).is_file()


def is_fallback(meta: dict[str, Any]) -> bool:
    credit = str(meta.get("image_credit") or "")
    image = str(meta.get("image") or "")
    generic_assets = {
        "/static/images/wealth.jpg",
        "/static/images/tax-paperwork.jpg",
        "/static/images/retirement-walk.jpg",
        "/static/images/budget-dublin.jpg",
        "/static/images/landscape.jpg",
        "/static/images/home-wealth.webp",
    }
    return credit.startswith("Illustration: Compound news fallback") or image in generic_assets


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


def _fallback_font(size: int, bold: bool = False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def _local_photo_for(meta: dict[str, Any]) -> dict[str, str]:
    pillar = str(meta.get("pillar") or "happiness")
    pool = LOCAL_PHOTOS.get(pillar) or LOCAL_PHOTOS["happiness"]
    haystack = " ".join([
        str(meta.get("slug") or ""),
        str(meta.get("title") or ""),
        " ".join(str(x) for x in meta.get("tags") or []),
    ]).lower()

    keyword_preferences = [
        (("sleep", "bedtime"), "adult-sleep.jpg"),
        (("protein", "nutrition", "vitamin", "food", "macro", "creatine"), "nutrition.jpg"),
        (("ozempic", "wegovy", "mounjaro", "glp", "retatrutide", "semaglutide", "tirzepatide"), "glp1-injector.jpg"),
        (("stress", "burnout", "therapy", "mental", "loneliness", "worry", "self-esteem"), "mindful.jpg"),
        (("pension", "retire"), "retirement-walk.jpg"),
        (("tax", "salary", "income", "rent", "credit"), "tax-paperwork.jpg"),
        (("budget", "ireland", "dublin"), "budget-dublin.jpg"),
        (("home", "house", "mortgage", "property"), "wealth.jpg"),
        (("hobby", "fun", "creative"), "hobby-painting.jpg"),
    ]
    slug = str(meta.get("slug") or "")
    for keywords, filename in keyword_preferences:
        if any(k in haystack for k in keywords):
            # Keep the dedicated GLP injector for the core GLP evidence page only.
            # Other GLP/medicine stories should get their own Pexels result, and if
            # stock lookup fails they fall through to a different generic health photo.
            if filename == "glp1-injector.jpg" and slug != "glp1-medicines-ireland-rise-evidence":
                continue
            for item in pool:
                if item["file"] == filename:
                    return item

    # Stable distribution across the remaining pool so adjacent cards do not all
    # show the same source photograph.
    generic_pool = [item for item in pool if not (pillar == "health" and item["file"] == "glp1-injector.jpg")]
    if not generic_pool:
        generic_pool = pool
    seed = sum(ord(ch) for ch in str(meta.get("slug") or meta.get("title") or "compound"))
    return generic_pool[seed % len(generic_pool)]


def fallback_image(meta: dict[str, Any], destination: Path) -> dict[str, str]:
    photo = _local_photo_for(meta)
    source = STATIC / "images" / photo["file"]
    if not source.is_file():
        raise FileNotFoundError(f"Local fallback photograph missing: {source}")

    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw).convert("RGB")
        slug = str(meta.get("slug") or meta.get("title") or "compound")
        seed = sum(ord(ch) for ch in slug)
        x = 0.38 + ((seed % 25) / 100)
        y = 0.42 + (((seed // 7) % 17) / 100)
        image = ImageOps.fit(image, (1200, 660), method=Image.Resampling.LANCZOS, centering=(min(x, .72), min(y, .68)))

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "JPEG", quality=88, optimize=True, progressive=True)
    return photo

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
        # Pinned evergreen covers are stable assets. Do not hit Pexels on every
        # build once the image already exists; that only burns API quota.
        if image_exists(meta) and not force:
            return "skip:has-pinned-image"

        try:
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
        except Exception as exc:
            # A transient Pexels outage/rate limit must never take down the site.
            print(f"Pexels pinned lookup failed for {path.name}: {exc}")
            if image_exists(meta):
                return "skip:pinned-fetch-failed-existing"

            fallback_rel = f"/static/images/{'news' if is_published_news(meta) else 'evergreen'}/{slug}.jpg"
            photo = fallback_image(meta, STATIC / fallback_rel.removeprefix("/static/"))
            fields = {
                "image": fallback_rel,
                "image_alt": photo["alt"],
                "image_credit": photo["credit"],
                "image_source": photo["url"],
                "social_image": fallback_rel,
            }
            inject_fields(path, raw, match, fields)
            return "photo-fallback:pinned-pexels-unavailable"

    if not is_published(meta):
        return "skip:not-published"

    if not is_published_news(meta):
        existing = image_exists(meta)
        if existing and not force and not (api_key and is_fallback(meta)):
            return "skip:has-image"

        query = default_query(meta)
        if api_key:
            try:
                photo = pexels_photo(query, api_key)
                if photo:
                    hero_rel = f"/static/images/evergreen/{slug}.jpg"
                    download(photo["src"]["landscape"], STATIC / hero_rel.removeprefix("/static/"))
                    fields = {
                        "image": hero_rel,
                        "image_alt": str(photo.get("alt") or f"Illustrative photo for {meta.get('title', 'Compound')}"),
                        "image_credit": f"{photo.get('photographer', 'Pexels photographer')} on Pexels",
                        "image_source": str(photo.get("url") or "https://www.pexels.com"),
                        "social_image": hero_rel,
                        "news_image_query": query,
                    }
                    inject_fields(path, raw, match, fields)
                    return f"pexels-evergreen:{photo.get('id')}:{query}"
            except Exception as exc:
                print(f"Pexels evergreen lookup failed for {path.name}: {exc}")

        fallback_rel = f"/static/images/evergreen/{slug}.jpg"
        photo = fallback_image(meta, STATIC / fallback_rel.removeprefix("/static/"))
        fields = {
            "image": fallback_rel,
            "image_alt": photo["alt"],
            "image_credit": photo["credit"],
            "image_source": photo["url"],
            "social_image": fallback_rel,
            "news_image_query": query,
        }
        inject_fields(path, raw, match, fields)
        return f"photo-fallback:evergreen:{query}"

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

    fallback_rel = f"/static/images/news/{slug}.jpg"
    photo = fallback_image(meta, STATIC / fallback_rel.removeprefix("/static/"))
    fields = {
        "image": fallback_rel,
        "image_alt": photo["alt"],
        "image_credit": photo["credit"],
        "image_source": photo["url"],
        "social_image": fallback_rel,
        "news_image_query": query,
    }
    inject_fields(path, raw, match, fields)
    return f"photo-fallback:{query}"


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
