"""One continuously updated, SEC-verified earnings dataset per issuer.

Never write a quarterly Markdown article. A new 10-Q pulls all available
standalone Q1/Q2/Q3 quarters for the SAME official fiscal year. SEC periods,
not calendar guesses, determine quarter names.
"""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from earnings import extract_metrics, filing_rows, filing_url, recent_filings, SEC_DATA

EARLIEST = date(2026, 1, 1)
FINANCIAL_KEYS = ("revenue", "net_income", "diluted_eps")


def verified_period(filing: dict, metrics: dict, cik: int) -> dict | None:
    """A financial period is tied to the actual filing, not the publish date."""
    rev = metrics.get("revenue", {})
    fy, fp = rev.get("fy"), rev.get("fp")
    try:
        ended = date.fromisoformat(filing["reportDate"])
        filed = date.fromisoformat(filing["filingDate"])
    except (KeyError, ValueError, TypeError):
        return None
    if filed < EARLIEST or ended < EARLIEST:
        return None
    if not isinstance(fy, int) or not (2026 <= fy <= 2100):
        return None
    if filing["form"] == "10-Q" and fp not in {"Q1", "Q2", "Q3"}:
        return None
    if filing["form"] == "10-K":
        fp = "FY"
    if fp not in {"Q1", "Q2", "Q3", "FY"}:
        return None
    if any(key not in metrics for key in FINANCIAL_KEYS):
        return None
    return {
        "fy": fy, "fp": fp,
        "period_end": ended.isoformat(), "filed": filed.isoformat(),
        "form": filing["form"], "accession": filing["accessionNumber"],
        "source": filing_url(cik, filing),
        "metrics": {
            key: {"current": metrics[key]["current"], "prior_year": metrics[key]["prior"],
                  "unit": metrics[key]["unit"], "tag": metrics[key]["tag"]}
            for key in FINANCIAL_KEYS
        },
    }


def dashboard(existing: dict | None, ticker: str, company: str, cik: int,
              newest: dict, submissions: dict, facts: dict,
              *, checked: date) -> dict | None:
    """Update a single persistent fiscal report; hydrate earlier quarters."""
    current_metrics = extract_metrics(facts, newest)
    if current_metrics is None:
        return None
    latest = verified_period(newest, current_metrics, cik)
    if latest is None:
        return None

    old = existing or {}
    if old and (int(old.get("cik", -1)) != cik or old.get("ticker") != ticker):
        raise ValueError("Existing earnings profile belongs to a different SEC issuer")
    values = {(p["fy"], p["fp"]): p for p in old.get("periods", [])
              if p.get("period_end", "") >= EARLIEST.isoformat()}
    values[(latest["fy"], latest["fp"])] = latest
    fiscal_year = latest["fy"]

    # Locate Q1 and Q2 within the same company's actual FY. No calendar-quarter
    # approximation or Q4 inferred from annual accounts.
    for filing in filing_rows(submissions):
        if filing["form"] != "10-Q" or filing["reportDate"] > latest["period_end"]:
            continue
        if filing["reportDate"] < EARLIEST.isoformat():
            continue
        if filing["reportDate"] > filing["filingDate"] or filing["filingDate"] > checked.isoformat():
            continue
        # Only seek the latest fiscal-year's three quarters. The facts API is
        # already fetched once; do not make separate requests per old filing.
        metrics = extract_metrics(facts, filing)
        if metrics is None or metrics["revenue"]["fy"] != fiscal_year:
            continue
        period = verified_period(filing, metrics, cik)
        if period and period["fp"] in {"Q1", "Q2", "Q3"}:
            key = (period["fy"], period["fp"])
            if key not in values or period["filed"] >= values[key]["filed"]:
                values[key] = period

    ordered = sorted(values.values(), key=lambda p: (p["period_end"], p["filed"]))[-16:]
    if not ordered:
        return None
    latest_overall = max(ordered, key=lambda p: (p["period_end"], p["filed"]))
    result = {"ticker": ticker, "company": company, "cik": cik,
              "updated": checked.isoformat(), "latest": latest_overall,
              "periods": ordered, "source_type": "US SEC XBRL; no analyst estimates"}
    # No empty rewrites when no additional results were published.
    if old and {k: v for k, v in result.items() if k != "updated"} == {
        k: v for k, v in old.items() if k != "updated"
    }:
        return None
    return result


def store_update(directory: Path, ticker: str, data: dict, *, dry_run=False) -> str | None:
    directory.mkdir(parents=True, exist_ok=True) if not dry_run else None
    filename = directory / (ticker.lower() + ".json")
    serialized = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if filename.exists() and filename.read_text(encoding="utf-8") == serialized:
        return None
    if not dry_run:
        filename.write_text(serialized, encoding="utf-8")
    return str(filename)


def summary(data: dict) -> dict:
    """Only compare Q3 to Q2 when both belong to the same official fiscal year."""
    latest = data["latest"]
    fy = latest["fy"]
    by_quarter = {p["fp"]: p for p in data.get("periods", [])
                  if p["fy"] == fy and p["fp"] in ("Q1", "Q2", "Q3")}
    rows = [by_quarter.get(q) for q in ("Q1", "Q2", "Q3")]
    def delta(metric, a, b):
        if not a or not b:
            return None
        top = a["metrics"][metric]["current"]
        base = b["metrics"][metric]["current"]
        if base <= 0:
            return None
        return round((top / base - 1) * 100, 1)
    comparisons = {key: delta(key, by_quarter.get("Q3"), by_quarter.get("Q2"))
                   for key in FINANCIAL_KEYS}
    observed = [r for r in rows if r]
    complete_to = max((i for i, r in enumerate(rows) if r is not None), default=-1)
    complete_ytd = complete_to >= 0 and all(rows[i] is not None for i in range(complete_to + 1))
    totals = {key: sum(p["metrics"][key]["current"] for p in observed)
              for key in ("revenue", "net_income")} if complete_ytd else {}
    return {"fy": fy, "latest": latest, "quarters": rows,
            "comparisons": comparisons, "totals": totals,
            "complete_ytd": complete_ytd}
