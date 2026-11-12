#!/usr/bin/env python3
"""Validate and standardise only this run's approved real Wikimedia photo covers."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "monitoring/private-company-publications/2026-11-12.json"
STATIC = ROOT / "compound/site/static/images/evergreen"

def validate_and_normalise() -> None:
    for story in json.loads(LEDGER.read_text())["articles"]:
        path = STATIC / (Path(story["article_path"]).stem + ".jpg")
        if not path.is_file():
            raise AssertionError(f"Pinned documentary photograph missing: {path}")
        with Image.open(path) as im:
            w, h = im.size
            if w < 1000 or h < 600:
                raise ValueError(f"Photograph too small ({w}x{h}): {path}")
            fmt = im.format
            if fmt == "JPEG":
                im.verify()
                continue
            if fmt not in {"MPO", "PNG", "WEBP"}:
                raise ValueError(f"Unsupported image format {fmt}: {path}")
            primary = ImageOps.exif_transpose(im).convert("RGB")
        primary.save(path, "JPEG", quality=92, optimize=True)
        with Image.open(path) as check:
            assert check.format == "JPEG" and check.size == (w, h)
            check.verify()
        print(f"PASS: standardised archive photo: {story['company']}")
if __name__ == "__main__":
    validate_and_normalise()
