"""Resumable 2026+ SEC earnings hydration for existing S&P 500 stock dashboards.

One profile per verified CIK; no new article URLs or invented quarters.
The routine uses the exact same SEC/XBRL validation and consolidated dashboard
builder as the continuously running earnings monitor. A saved cursor makes
scheduled batches idempotent and bounded; temporarily unavailable SEC issuers
receive one final retry pass. Existing verified profiles are never deleted.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import logging
import os
from pathlib import Path

from earnings import SECClient, SEC_DATA, recent_filings
from earnings_consolidated import dashboard, store_update
from sp500_registry import load_registry

LOG = logging.getLogger("compound.earnings.historical")
EARLIEST = date(2026, 1, 1)
VERSION = 1
DEFAULT_STATE = {
    "version": VERSION, "cursor": 0, "completed": False,
    "scanned": 0, "created": 0, "updated": 0,
    "already_verified": 0, "no_eligible_filing": 0,
    "pending_retry": [], "permanently_unavailable": [],
    "last_run": "",
}


def universe(registry_path: Path) -> list[dict]:
    registry = load_registry(registry_path)
    active = [row for row in registry["members"] if row["active"]]
    if not 480 <= len(active) <= 515 or registry["company_count"] != len(active):
        raise ValueError("S&P 500 registry must contain 480–515 unique active companies")
    by_cik = {}
    for row in active:
        cik = int(row["cik"])
        if cik in by_cik:
            raise ValueError("Duplicate issuer CIK in S&P 500 backfill")
        by_cik[cik] = row
    return sorted(by_cik.values(), key=lambda r: r["symbol"])


def read_state(path: Path) -> dict:
    state = dict(DEFAULT_STATE)
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or loaded.get("version") != VERSION:
            raise ValueError("Unknown or malformed earnings backfill progress")
        state.update(loaded)
    for key in ("cursor", "scanned", "created", "updated", "already_verified", "no_eligible_filing"):
        if type(state[key]) is not int or state[key] < 0:
            raise ValueError("Invalid earnings backfill cursor or counter")
    for key in ("pending_retry", "permanently_unavailable"):
        if not isinstance(state[key], list) or not all(isinstance(s, str) for s in state[key]):
            raise ValueError("Invalid earnings backfill retry queue")
    if not isinstance(state["completed"], bool):
        raise ValueError("Invalid completion flag")
    return state


def check_company(client, row: dict, profiles: Path, now: date):
    """Return (status, verified dataset | None); 'failed' denotes an SEC outage."""
    ticker, cik = row["symbol"], int(row["cik"])
    existing_path = profiles / (ticker.lower() + ".json")
    old = json.loads(existing_path.read_text(encoding="utf-8")) if existing_path.is_file() else None
    if old and (int(old.get("cik", -1)) != cik or old.get("ticker") != ticker):
        raise ValueError(f"SEC identity mismatch in existing profile {ticker}")
    try:
        submissions = client.get_json(f"{SEC_DATA}/submissions/CIK{cik:010d}.json")
    except RuntimeError as exc:
        LOG.warning("SEC submissions unavailable for %s: %s", ticker, exc)
        return "failed", None
    candidates = [
        f for f in recent_filings(submissions, now, days=400)
        if f["reportDate"] >= EARLIEST.isoformat()
    ]
    candidates.sort(key=lambda f: (f["reportDate"], f["filingDate"]), reverse=True)
    if not candidates:
        return "ineligible", None
    previous_accns = {p.get("accession") for p in old.get("periods", [])} if old else set()
    if candidates[0]["accessionNumber"] in previous_accns:
        return "unchanged", None
    try:
        facts = client.get_json(f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik:010d}.json")
    except RuntimeError as exc:
        LOG.warning("SEC XBRL unavailable for %s: %s", ticker, exc)
        return "failed", None
    for filing in candidates:
        if filing["accessionNumber"] in previous_accns:
            return "unchanged", None
        verified = dashboard(old, ticker, row["name"], cik, filing, submissions, facts, checked=now)
        if verified is not None:
            return ("updated" if old else "created"), verified
    return "ineligible", None


def backfill(registry_path: Path, content_dir: Path, state_path: Path, *,
             client, now: date, batch_size: int = 20, dry_run: bool = False) -> dict:
    if not 1 <= batch_size <= 40:
        raise ValueError("Batch size must be 1–40")
    members = universe(registry_path)
    by_symbol = {r["symbol"]: r for r in members}
    state = read_state(state_path)
    if state["cursor"] > len(members):
        raise ValueError("Backfill cursor exceeds the current registry")
    if state["completed"]:
        LOG.info("Historical earnings backfill is complete; no further SEC requests.")
        return state
    profiles = content_dir / "earnings-profiles"
    retry_phase = state["cursor"] >= len(members)
    if retry_phase:
        queue = [s for s in state["pending_retry"] if s in by_symbol]
        selected = [by_symbol[s] for s in queue[:batch_size]]
    else:
        selected = members[state["cursor"]:state["cursor"] + batch_size]
    proposals: list[tuple[str, dict]] = []
    failed: list[str] = []
    changes = {"created": 0, "updated": 0, "unchanged": 0, "ineligible": 0}
    for row in selected:
        ticker = row["symbol"]
        status, report = check_company(client, row, profiles, now)
        if status == "failed":
            failed.append(ticker)
        else:
            changes[status] += 1
            if report:
                proposals.append((ticker, report))
        LOG.info("%s %s", ticker, status)
    if len(failed) >= max(5, (len(selected) + 2) // 3):
        raise RuntimeError(f"SEC unreachable for {len(failed)} of {len(selected)} companies; "
                           "do not advance progress or publish partial batch")
    result = {**state}
    if retry_phase:
        result["pending_retry"] = result["pending_retry"][len(selected):]
        result["permanently_unavailable"] = sorted(set(result["permanently_unavailable"] + failed))
    else:
        result["cursor"] += len(selected)
        result["scanned"] += len(selected)
        result["pending_retry"] = sorted(set(result["pending_retry"] + failed))
    result["created"] += changes["created"]
    result["updated"] += changes["updated"]
    result["already_verified"] += changes["unchanged"]
    result["no_eligible_filing"] += changes["ineligible"]
    result["last_run"] = now.isoformat()
    result["completed"] = result["cursor"] >= len(members) and not result["pending_retry"]
    result["company_count"] = len(members)
    result["last_batch"] = {
        "phase": "retry" if retry_phase else "scan", "checked": len(selected),
        "created": changes["created"], "updated": changes["updated"],
        "already_verified": changes["unchanged"], "ineligible": changes["ineligible"],
        "temporarily_unavailable": len(failed),
    }
    if not dry_run:
        for ticker, report in proposals:
            store_update(profiles, ticker, report, dry_run=False)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    LOG.info("Historical batch %s; coverage created=%d updated=%d scanned=%d/%d; "
             "pending retries=%d finished=%s%s",
             result["last_batch"], result["created"], result["updated"], result["cursor"],
             len(members), len(result["pending_retry"]), result["completed"],
             " DRY RUN" if dry_run else "")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hydrate 2026+ SEC reports into permanent stock pages")
    parser.add_argument("--registry", type=Path, default=Path("content/earnings-sp500.json"))
    parser.add_argument("--content-dir", type=Path, default=Path("content"))
    parser.add_argument("--state", type=Path, default=Path("content/earnings-backfill-state.json"))
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    client = SECClient(os.environ.get("SEC_USER_AGENT", ""))
    result = backfill(args.registry, args.content_dir, args.state,
                      client=client, now=datetime.now(timezone.utc).date(),
                      batch_size=args.batch_size, dry_run=args.dry_run)
    print("Historical SEC profiles: " + json.dumps({
        "cursor": result["cursor"], "total": result.get("company_count"),
        "created": result["created"], "updated": result["updated"],
        "completed": result["completed"],
        "last_batch": result.get("last_batch", {}),
        "pending_retry": len(result["pending_retry"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
