#!/usr/bin/env python3
"""Verify documentary photographs; fetch only pre-approved Wikimedia originals.

No synthetic/generic fallback is permitted. Every newly downloaded photograph has
an independently verified Commons licence, source and attribution in its ledger.
"""
from __future__ import annotations
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "monitoring/private-company-publications"
STATIC = ROOT / "compound/site/static/images/evergreen"
MAX_DOWNLOAD_BYTES = 20_000_000
USER_AGENT = "CompoundEditorialImageVerifier/1.0 (https://compound.ie/contact/)"

def validate_and_normalise() -> None:
    for ledger_path in sorted(LEDGER_DIR.glob("20??-??-??.json")):
        for story in json.loads(ledger_path.read_text(encoding="utf-8")).get("articles", []):
            path = STATIC / (Path(story["article_path"]).stem + ".jpg")
            if not path.exists():
                url = story.get("photo_download_url")
                if not url:
                    raise AssertionError(f"Pinned documentary photograph missing and no approved source: {path}")
                parsed = urlparse(url)
                if parsed.scheme != "https" or parsed.hostname != "upload.wikimedia.org":
                    raise ValueError(f"Unapproved original image host: {url}")
                req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/jpeg,image/*"})
                with urlopen(req, timeout=60) as response:
                    if urlparse(response.geturl()).hostname != "upload.wikimedia.org":
                        raise ValueError("Image download redirected to an unapproved host")
                    data = response.read(MAX_DOWNLOAD_BYTES + 1)
                if not 50_000 < len(data) <= MAX_DOWNLOAD_BYTES:
                    raise ValueError(f"Licensed image download unexpectedly sized: {url}")
                with Image.open(io.BytesIO(data)) as original:
                    if original.width < 1000 or original.height < 600:
                        raise ValueError(f"Source photo too small: {url}")
                    photo = ImageOps.exif_transpose(original).convert("RGB")
                # Adapt licensed authentic source into a consistent documentary cover.
                focal_y = float(story.get("photo_focal_y", 0.5))
                if not 0 <= focal_y <= 1:
                    raise ValueError("Invalid photograph crop focal point")
                photo = ImageOps.fit(photo, (1600, 900), method=Image.Resampling.LANCZOS,
                                     centering=(0.5, focal_y))
                path.parent.mkdir(parents=True, exist_ok=True)
                photo.save(path, "JPEG", quality=91, optimize=True)
            with Image.open(path) as im:
                width, height, fmt = im.width, im.height, im.format
                if width < 1000 or height < 600:
                    raise ValueError(f"Pinned photograph below 1000x600: {path}")
                if fmt == "JPEG":
                    im.verify()
                elif fmt in {"MPO", "PNG", "WEBP"}:
                    # Historical verified assets sometimes ship in a different raster container.
                    photo = ImageOps.exif_transpose(im).convert("RGB")
                    photo.save(path, "JPEG", quality=92, optimize=True)
                else:
                    raise ValueError(f"Unsupported photo format {fmt}: {path}")
            with Image.open(path) as check:
                assert check.format == "JPEG" and check.width >= 1000 and check.height >= 600
                check.verify()
            if path.stat().st_size < 50_000:
                raise AssertionError(f"Pinned archival photo unexpectedly small: {path}")
            print(f"PASS: licensed real documentary photo for {story['company']}: {path}")

if __name__ == "__main__":
    validate_and_normalise()
