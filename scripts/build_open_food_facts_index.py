#!/usr/bin/env python3
"""Build a compact Irish-focused nutrition dataset from Open Food Facts.

The script streams the public Open Food Facts TSV gzip export, keeps only
products sold in Ireland with usable calorie data, normalises a small set of
fields, and writes a gzip-compressed NDJSON file plus a manifest.

The raw Open Food Facts dump is never committed to the repository.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import math
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
SOURCE_NAME = "Open Food Facts"
SOURCE_LICENSE = "Open Database License (ODbL) 1.0"
SOURCE_ATTRIBUTION = "Data from Open Food Facts — https://openfoodfacts.org"

FIELDS = {
    "code",
    "product_name",
    "brands",
    "quantity",
    "serving_size",
    "countries_tags",
    "energy-kcal_100g",
    "energy_100g",
    "proteins_100g",
    "carbohydrates_100g",
    "fat_100g",
    "fiber_100g",
    "sugars_100g",
    "salt_100g",
    "last_modified_t",
}

_NUMBER_RE = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")


def _number(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if not _NUMBER_RE.match(value):
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return round(number, 3)


def _calories(row: dict[str, str]) -> float | None:
    kcal = _number(row.get("energy-kcal_100g"))
    if kcal is not None and 0 <= kcal <= 1000:
        return kcal

    # OFF's energy_100g is normally kJ. Use it as a fallback when kcal is absent.
    kj = _number(row.get("energy_100g"))
    if kj is None or not 0 <= kj <= 4200:
        return None
    return round(kj / 4.184, 1)


def _is_irish(row: dict[str, str]) -> bool:
    tags = (row.get("countries_tags") or "").lower()
    return "en:ireland" in {part.strip() for part in tags.split(",")}


def _normalise(row: dict[str, str]) -> dict[str, Any] | None:
    code = (row.get("code") or "").strip()
    name = (row.get("product_name") or "").strip()
    calories = _calories(row)

    if not code or not name or calories is None:
        return None

    result: dict[str, Any] = {
        "code": code,
        "name": name,
        "kcal_100g": calories,
    }

    optional_text = {
        "brand": row.get("brands"),
        "quantity": row.get("quantity"),
        "serving_size": row.get("serving_size"),
    }
    for key, value in optional_text.items():
        value = (value or "").strip()
        if value:
            result[key] = value

    optional_numbers = {
        "protein_100g": row.get("proteins_100g"),
        "carbs_100g": row.get("carbohydrates_100g"),
        "fat_100g": row.get("fat_100g"),
        "fibre_100g": row.get("fiber_100g"),
        "sugars_100g": row.get("sugars_100g"),
        "salt_100g": row.get("salt_100g"),
    }
    for key, value in optional_numbers.items():
        number = _number(value)
        if number is not None and 0 <= number <= 1000:
            result[key] = number

    modified = (row.get("last_modified_t") or "").strip()
    if modified.isdigit():
        result["last_modified"] = int(modified)

    return result


def _open_source(url: str):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Compound.ie food index builder (+https://compound.ie)"},
    )
    response = urllib.request.urlopen(request, timeout=120)
    return gzip.GzipFile(fileobj=response)


def build(source_url: str, output_dir: Path, max_rows: int = 0) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "products.ie.ndjson.gz"
    started = time.monotonic()
    scanned = kept = skipped_invalid = 0

    with _open_source(source_url) as compressed:
        text = io.TextIOWrapper(compressed, encoding="utf-8", errors="replace", newline="")
        reader = csv.DictReader(text, delimiter="\t")
        missing = FIELDS.difference(reader.fieldnames or [])
        required_missing = {"code", "product_name", "countries_tags"}.intersection(missing)
        if required_missing:
            raise RuntimeError(f"Open Food Facts export missing required columns: {sorted(required_missing)}")

        with gzip.open(output_path, "wt", encoding="utf-8", compresslevel=9) as out:
            for row in reader:
                scanned += 1
                if max_rows and scanned > max_rows:
                    break
                if not _is_irish(row):
                    continue
                product = _normalise(row)
                if product is None:
                    skipped_invalid += 1
                    continue
                out.write(json.dumps(product, ensure_ascii=False, separators=(",", ":")))
                out.write("\n")
                kept += 1

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE_NAME,
        "source_url": source_url,
        "source_license": SOURCE_LICENSE,
        "attribution": SOURCE_ATTRIBUTION,
        "scope": "Products tagged as sold in Ireland with usable calorie data",
        "rows_scanned": scanned,
        "products_kept": kept,
        "irish_rows_skipped_for_missing_core_data": skipped_invalid,
        "output_file": output_path.name,
        "output_bytes": output_path.stat().st_size,
        "build_seconds": round(time.monotonic() - started, 2),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--output-dir", type=Path, default=Path("build/food-index"))
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Stop after N source rows; 0 means scan the complete export.",
    )
    args = parser.parse_args()

    manifest = build(args.source_url, args.output_dir, max_rows=max(0, args.max_rows))
    print(json.dumps(manifest, indent=2))
    if manifest["products_kept"] == 0:
        print("No usable Irish products were produced.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
