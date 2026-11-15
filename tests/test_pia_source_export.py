"""Keep the dated public PIA evidence CSV in sync with the primary-source tracker."""
import csv
from pathlib import Path
import yaml
from scripts.export_pia_provider_sources import render_source_csv

ROOT = Path(__file__).resolve().parents[1]


def test_pia_citable_source_export_is_reproducible():
    tracker = yaml.safe_load((ROOT / "content/pia-providers.yml").read_text(encoding="utf-8"))
    public = (ROOT / "compound/site/static/pia-provider-sources.csv").read_text(encoding="utf-8")
    assert public == render_source_csv(tracker)
    rows = list(csv.DictReader(public.splitlines()))
    assert len(rows) == len(tracker["providers"]) == 5
    assert all(row["statement_checked"] == tracker["updated"] for row in rows)
    assert all(row["official_source_url"].startswith("https://") for row in rows)
    assert all(row["fee_status"] == "not published" for row in rows)
    assert {row["provider"] for row in rows} == {"AIB", "Bank of Ireland", "Irish Life", "PTSB", "Zurich"}
