#!/usr/bin/env python3
"""Normalize this batch's licensed pinned photos to browser-compatible JPEGs.

Wikimedia JPEGs with MPF metadata may be detected as MPO by Pillow.
Keep the original news-image downloader and shared cache untouched, and
normalise only the three specifically approved unreviewed research covers.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "monitoring/private-company-publications/2026-11-11.json"
STATIC = ROOT / "compound/site/static/images/evergreen"


def normalise_pinned_photo(path: Path) -> None:
    """Validate the source resolution and save the primary frame as real JPEG."""
    with Image.open(path) as original:
        original_format = original.format
        width, height = original.size
        if width < 1000 or height < 600:
            raise ValueError(f"Pinned photograph too small: {width}x{height} ({path})")
        if original_format == "JPEG":
            original.verify()
            return
        if original_format not in {"MPO", "PNG", "WEBP"}:
            raise ValueError(f"Unsupported pinned photo format: {original_format} ({path})")
        primary = ImageOps.exif_transpose(original).convert("RGB")

    primary.save(path, format="JPEG", quality=92, optimize=True)
    with Image.open(path) as converted:
        assert converted.format == "JPEG" and converted.size == (width, height), path
        converted.verify()


def normalise_private_company_batch() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for story in ledger["articles"]:
        source = ROOT / story["article_path"]
        article = source.read_text(encoding="utf-8")
        assert "unreviewed-ai" in article and "require_pinned_hero: true" in article, source
        cover = STATIC / (source.stem + ".jpg")
        assert cover.is_file(), f"Missing pinned approved cover: {cover}"
        normalise_pinned_photo(cover)
        print(f"PASS: approved browser-compatible JPEG for {story['company']}")


if __name__ == "__main__":
    normalise_private_company_batch()
