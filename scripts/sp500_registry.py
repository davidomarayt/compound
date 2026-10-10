"""Refresh a reviewed, versioned S&P 500 constituent register.

Source is Wikipedia's public constituent table (NOT an S&P-licensed official feed).
Never overwrite a valid prior snapshot with a partial/broken scrape.
CIK is the company identity; share classes are consolidated.
"""
from __future__ import annotations

import argparse
import csv
import io
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
DATASET_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
SECTORS = {
    "Information Technology", "Financials", "Health Care", "Consumer Discretionary",
    "Communication Services", "Industrials", "Consumer Staples", "Energy",
    "Utilities", "Real Estate", "Materials",
}


class ConstituentsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.depth = 0
        self.in_row = False
        self.in_cell = False
        self.rows = []
        self.cells = []
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "table":
            if self.in_table:
                self.depth += 1
            elif attributes.get("id") == "constituents":
                self.in_table = True
                self.depth = 1
        if not self.in_table:
            return
        if tag == "tr" and self.depth == 1:
            self.in_row = True
            self.cells = []
        if tag in {"td", "th"} and self.in_row and not self.in_cell:
            self.in_cell = True
            self.chunks = []

    def handle_data(self, data):
        if self.in_table and self.in_cell:
            self.chunks.append(data)

    def handle_endtag(self, tag):
        if not self.in_table:
            return
        if tag in {"td", "th"} and self.in_cell:
            self.cells.append(" ".join("".join(self.chunks).split()))
            self.in_cell = False
        if tag == "tr" and self.in_row and self.depth == 1:
            if self.cells:
                self.rows.append(self.cells)
            self.in_row = False
        if tag == "table":
            self.depth -= 1
            if self.depth == 0:
                self.in_table = False


def parse_constituents(html: str, *, strict: bool = True) -> list[dict]:
    parser = ConstituentsParser()
    parser.feed(html)
    if not parser.rows:
        raise ValueError("Wikipedia constituent table not found")
    headers = [x.lower().replace(" ", "") for x in parser.rows[0]]
    required = {"symbol", "security", "gicssector", "cik"}
    if not required.issubset(headers):
        raise ValueError(f"Missing constituent table columns: {required - set(headers)}")
    cols = {key: headers.index(key) for key in required}
    securities = []
    seen = set()
    for values in parser.rows[1:]:
        if len(values) <= max(cols.values()):
            raise ValueError("Malformed constituent row")
        symbol = values[cols["symbol"]].upper().replace(".", "-").replace(" ", "")
        name = values[cols["security"]].strip()
        sector = values[cols["gicssector"]].strip()
        cik_str = values[cols["cik"]].replace(",", "").strip()
        if not re.fullmatch(r"[A-Z0-9-]{1,12}", symbol) or not name or sector not in SECTORS or not re.fullmatch(r"\d{1,10}", cik_str):
            raise ValueError(f"Invalid constituent row: {values[:4]}")
        if symbol in seen:
            raise ValueError(f"Duplicate security in constituent source: {symbol}")
        seen.add(symbol)
        securities.append({"symbol": symbol, "name": name, "sector": sector, "cik": int(cik_str)})
    if strict:
        if not 490 <= len(securities) <= 520 or len({x["cik"] for x in securities}) < 480:
            raise ValueError(f"Constituent feed unexpectedly small or large ({len(securities)} securities)")
        if set(x["sector"] for x in securities) != SECTORS:
            raise ValueError("Constituent source has missing GICS sectors")
    return securities


def parse_dataset_csv(content: str, *, strict: bool = True) -> list[dict]:
    """Daily public mirror of the Wikipedia constituent table, with CIKs."""
    reader = csv.DictReader(io.StringIO(content))
    if not {"Symbol", "Security", "GICS Sector", "CIK"}.issubset(reader.fieldnames or []):
        raise ValueError("Unexpected public constituent CSV schema")
    rows = []
    seen = set()
    for row in reader:
        symbol = (row.get("Symbol") or "").upper().strip().replace(".", "-")
        sector = (row.get("GICS Sector") or "").strip()
        name = (row.get("Security") or "").strip()
        raw_cik = (row.get("CIK") or "").strip()
        if (not re.fullmatch(r"[A-Z0-9-]{1,12}", symbol)
                or sector not in SECTORS or not name
                or not re.fullmatch(r"\d{1,10}", raw_cik)
                or symbol in seen):
            raise ValueError(f"Invalid public constituent CSV row: {row}")
        seen.add(symbol)
        rows.append({"symbol": symbol, "sector": sector, "name": name, "cik": int(raw_cik)})
    if strict:
        if not 490 <= len(rows) <= 520 or len({x["cik"] for x in rows}) < 480:
            raise ValueError(f"Unexpected public CSV constituent count: {len(rows)}")
        if {x["sector"] for x in rows} != SECTORS:
            raise ValueError("Missing GICS sectors in public CSV")
    return rows


def build_snapshot(securities: list[dict], previous: dict | None, checked: str,
                   source: str = SOURCE_URL) -> dict:
    by_cik: dict[int, dict] = {}
    for row in securities:
        cik = row["cik"]
        if cik not in by_cik:
            by_cik[cik] = {"cik": cik, "name": row["name"], "sector": row["sector"],
                           "symbol": row["symbol"], "symbols": [], "active": True}
        by_cik[cik]["symbols"].append(row["symbol"])
    old_members = (previous or {}).get("members") or []
    old_by_cik = {int(x["cik"]): x for x in old_members if isinstance(x, dict) and x.get("cik")}
    for cik, row in by_cik.items():
        row["symbols"] = sorted(set(row["symbols"]))
        if "GOOGL" in row["symbols"]:
            row["symbol"] = "GOOGL"
        if cik in old_by_cik and old_by_cik[cik].get("symbol") in row["symbols"]:
            row["symbol"] = old_by_cik[cik]["symbol"]
    for cik, old in old_by_cik.items():
        if cik not in by_cik:
            by_cik[cik] = {**old, "active": False}
    return {"source": source, "source_type": "third-party public reference (not licensed S&P constituents)",
            "checked": checked, "security_count": len(securities),
            "company_count": len({x["cik"] for x in securities}),
            "members": sorted(by_cik.values(), key=lambda x: x["symbol"])}


def refresh(path: Path, fetch=None, now: str | None = None) -> bool:
    checked = now or datetime.now(timezone.utc).date().isoformat()
    source = SOURCE_URL
    if fetch is None:
        def fetch(url):
            req = Request(url, headers={"User-Agent": "Compound.ie Financial Research (david@compound.ie)",
                                        "Accept": "text/csv,text/html"})
            with urlopen(req, timeout=40) as response:
                return response.read().decode("utf-8")
        # Mirror is updated regularly and gives a stable machine-readable schema.
        # If unavailable, attempt the original public HTML reference directly.
        try:
            securities = parse_dataset_csv(fetch(DATASET_URL))
            source = "https://github.com/datasets/s-and-p-500-companies/blob/main/data/constituents.csv"
        except (OSError, ValueError) as first_exc:
            try:
                securities = parse_constituents(fetch(SOURCE_URL))
            except (OSError, ValueError) as fallback_exc:
                raise RuntimeError(f"Both public membership sources failed: {first_exc}; {fallback_exc}") from fallback_exc
    else:
        securities = parse_constituents(fetch(SOURCE_URL))
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    updated = build_snapshot(securities, previous, checked, source=source)
    serialized = json.dumps(updated, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == serialized:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized, encoding="utf-8")
    return True


def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"members": [], "security_count": 0, "company_count": 0, "checked": None, "source": SOURCE_URL}
    data = json.loads(path.read_text(encoding="utf-8"))
    members = data.get("members")
    if not isinstance(members, list):
        raise ValueError("Invalid S&P 500 registry")
    for member in members:
        if (not isinstance(member, dict) or not isinstance(member.get("cik"), int)
                or not isinstance(member.get("active"), bool)
                or not isinstance(member.get("symbols"), list)
                or member.get("symbol") not in member["symbols"]
                or member.get("sector") not in SECTORS):
            raise ValueError("Malformed S&P 500 registry member")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh S&P 500 member register from public reference source")
    parser.add_argument("--output", type=Path, default=Path("content/earnings-sp500.json"))
    args = parser.parse_args()
    changed = refresh(args.output)
    data = load_registry(args.output)
    print(f"S&P register: {data['security_count']} securities / {data['company_count']} unique companies, updated={changed}")