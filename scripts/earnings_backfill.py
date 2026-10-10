"""Controlled, SEC-verified historical earnings backfill for the existing stock register.

One recent, complete 10-Q or 10-K per eligible SEC issuer; never invent missing
metrics or Q4, silently revise published results, or backdate the article's
publication date. Runs once per day with a small site-wide publication cap.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import logging
import os
from pathlib import Path
import re

import yaml
from earnings import (
    SECClient, SEC_DATA, SEC_TICKERS, build_article, extract_metrics, recent_filings,
    resolve_tickers,
)
from sp500_registry import load_registry

LOG = logging.getLogger("compound.earnings.backfill")


def extra_sec_companies(client, watchlist_path: Path) -> list[dict]:
    """Use SEC identity, never assume the supplied stock ticker is a domestic filer."""
    if not watchlist_path.is_file():
        return []
    watchlist = json.loads(watchlist_path.read_text(encoding="utf-8"))
    listed = watchlist.get("listed", [])
    # Foreign ADRs are monitored for 20-F/6-K separately, never mislabelled 10-Q.
    candidates = [row for row in listed if row.get("slug") == "spcx"
                  and row.get("exchange", "").lower().startswith("nasdaq")]
    if not candidates:
        return []
    mapping = resolve_tickers(client.get_json(SEC_TICKERS), [r["ticker"] for r in candidates])
    result = []
    for row in candidates:
        issuer = mapping.get(row["ticker"])
        if not issuer or not re.search(r"space\s*(?:exploration|x)", issuer[0], re.I):
            LOG.warning("No SEC-verified SpaceX issuer for %s; skipping US-form automation", row["ticker"])
            continue
        result.append({"symbol": row["ticker"], "name": row["name"], "cik": issuer[1]})
    return result


def eligible_universe(registry_path: Path, client, extras_path: Path | None = None) -> list[dict]:
    registry = load_registry(registry_path)
    if registry.get("company_count", 0) < 480:
        raise ValueError("S&P 500 registry is incomplete")
    by_cik = {row["cik"]: {"symbol": row["symbol"], "name": row["name"], "cik": row["cik"]}
              for row in registry["members"] if row["active"]}
    if extras_path:
        for row in extra_sec_companies(client, extras_path):
            by_cik.setdefault(row["cik"], row)
    return sorted(by_cik.values(), key=lambda x: x["symbol"])


def backfill(registry_path: Path, content_dir: Path, *, client, today: date,
             days: int = 550, max_new: int = 8, dry_run: bool = False,
             extras_path: Path | None = None) -> list[str]:
    """Publish at most one historical report per company across the entire library."""
    directory = content_dir / "wealth"
    directory.mkdir(parents=True, exist_ok=True)
    existing = {p.stem for p in directory.glob("*-earnings-fy*.md")}
    universe = eligible_universe(registry_path, client, extras_path)
    LOG.info("Historical backfill: %d distinct issuers, cap=%d", len(universe), max_new)
    written = []
    unavailable = 0
    for company in universe:
        if len(written) >= max_new:
            break
        ticker, cik = company["symbol"], company["cik"]
        prefix = ticker.lower() + "-earnings-fy"
        # One latest eligible historical filing per issuer, plus all future new
        # filings from the regular real-time monitor.
        if any(stem.startswith(prefix) for stem in existing):
            continue
        try:
            submissions = client.get_json(f"{SEC_DATA}/submissions/CIK{cik:010d}.json")
            filings = recent_filings(submissions, today, days)
        except RuntimeError as exc:
            unavailable += 1
            LOG.warning("SEC unavailable for %s: %s", ticker, exc)
            continue
        if not filings:
            continue
        try:
            facts = client.get_json(f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik:010d}.json")
        except RuntimeError as exc:
            unavailable += 1
            LOG.warning("SEC facts unavailable for %s: %s", ticker, exc)
            continue
        for filing in filings:
            metrics = extract_metrics(facts, filing)
            if metrics is None:
                continue
            try:
                slug, article = build_article(ticker, company["name"], cik, filing, metrics,
                                              today, facts=facts)
            except ValueError as exc:
                LOG.debug("No comparable historical report for %s: %s", ticker, exc)
                continue
            if slug in existing:
                continue
            # Publication date remains today; the financial event is marked with
            # its genuine historic filing date and original source accession.
            meta, body = article.split("---\n", 2)[1:]
            fields = yaml.safe_load(meta)
            fields["historical_backfill"] = True
            fields["filing_date"] = filing["filingDate"]
            fields["tags"].append("historical-filing")
            article = ("---\n" + yaml.safe_dump(fields, allow_unicode=True, sort_keys=False,
                                                width=120) + "---\n" + body)
            target = directory / f"{slug}.md"
            if not dry_run:
                target.write_text(article, encoding="utf-8")
            written.append(str(target))
            existing.add(slug)
            LOG.info("BACKFILL %s: SEC %s filed %s", ticker, filing["form"], filing["filingDate"])
            break
    if unavailable >= max(25, len(universe) // 4):
        raise RuntimeError(f"SEC inaccessible for {unavailable} monitored issuers; investigate before publishing")
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("content/earnings-sp500.json"))
    parser.add_argument("--extra-watchlist", type=Path, default=Path("content/company-watchlist.json"))
    parser.add_argument("--content-dir", type=Path, default=Path("content"))
    parser.add_argument("--lookback-days", type=int, default=550)
    parser.add_argument("--max-new", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not (30 <= args.lookback_days <= 730) or not (1 <= args.max_new <= 12):
        parser.error("lookback-days must be 30–730 and max-new 1–12")
    logging.basicConfig(level=logging.INFO)
    client = SECClient(os.getenv("SEC_USER_AGENT", ""))
    found = backfill(args.registry, args.content_dir, client=client,
                     today=datetime.now(timezone.utc).date(),
                     days=args.lookback_days, max_new=args.max_new,
                     dry_run=args.dry_run, extras_path=args.extra_watchlist)
    for path in found:
        print(path)
    print(f"Historical backfill: {len(found)} {'eligible candidates' if args.dry_run else 'reports'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
