"""Regenerate the official-source-only PIA provider CSV from the curated YAML.

Usage: python scripts/export_pia_provider_sources.py
Never fabricate numeric provider fees or infer live availability from intent.
"""
from __future__ import annotations
import csv
import io
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "pia-providers.yml"
OUTPUT = ROOT / "compound" / "site" / "static" / "pia-provider-sources.csv"
HEADERS = ("provider", "category", "provider_stage", "statement_checked", "official_source_url", "fee_status")


def render_source_csv(data: dict) -> str:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=HEADERS, lineterminator="\n")
    writer.writeheader()
    for provider in sorted(data["providers"], key=lambda item: item["name"].casefold()):
        if provider.get("fee_model", {}).get("verified"):
            raise ValueError("This export requires a review before adding confirmed numeric fee claims")
        if any(provider.get(k) != "Not published" for k in ("annual_fee", "dealing_fee", "fund_fee", "fx_fee")):
            raise ValueError("Provider fee status disagrees with source-only export")
        writer.writerow({
            "provider": provider["name"],
            "category": provider["category"],
            "provider_stage": provider["stage"],
            "statement_checked": provider["checked"],
            "official_source_url": provider["source_url"],
            "fee_status": "not published",
        })
    return buf.getvalue()


if __name__ == "__main__":
    OUTPUT.write_text(render_source_csv(yaml.safe_load(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
    print("PIA provider source dataset regenerated")
