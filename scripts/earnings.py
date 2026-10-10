"""Compound Earnings: publish deterministic, source-linked financial-results briefs.

Only 10-Q and 10-K filings whose matching SEC XBRL facts supply revenue,
net income and diluted EPS for both current and prior-year periods qualify.
This intentionally does not paraphrase unverified earnings-release claims.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import math
import logging
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

LOG = logging.getLogger("compound.earnings")
SEC_DATA = "https://data.sec.gov"
SEC_TICKERS = "https://www.sec.gov/files/company_tickers.json"
REVENUE_TAGS = (
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
)
NET_TAG = "NetIncomeLoss"
EPS_TAG = "EarningsPerShareDiluted"
FORMS = {"10-Q", "10-K"}


class SECClient:
    """Polite, identifying SEC client; response can be injected for offline tests."""

    def __init__(self, user_agent: str, delay: float = .35):
        if not user_agent or "@" not in user_agent or len(user_agent.strip()) < 12:
            raise ValueError("SEC_USER_AGENT must contain a contact email and organisation name")
        self.user_agent = user_agent.strip()
        self.delay = delay
        self.last = 0.0

    def get_json(self, url: str) -> dict:
        if not url.startswith((SEC_DATA + "/", "https://www.sec.gov/files/")):
            raise ValueError("Only SEC data sources are permitted")
        for attempt in range(3):
            time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
            self.last = time.monotonic()
            try:
                req = Request(url, headers={
                    "User-Agent": self.user_agent,
                    "Accept-Encoding": "identity", "Accept": "application/json",
                })
                with urlopen(req, timeout=24) as response:
                    return json.load(response)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt == 2:
                    raise RuntimeError(f"SEC response unavailable from {url}: {exc}") from exc
                time.sleep(2 ** attempt)
        raise AssertionError("unreachable")


def resolve_tickers(raw: dict, tickers: list[str]) -> dict[str, tuple[str, int]]:
    mapping = {}
    for row in raw.values():
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").upper()
        if ticker in tickers:
            mapping[ticker] = (str(row["title"]), int(row["cik_str"]))
    return mapping


def filing_rows(submissions: dict) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    columns = ("accessionNumber", "form", "filingDate", "reportDate", "primaryDocument")
    if not all(isinstance(recent.get(key), list) for key in columns):
        return []
    return [dict(zip(columns, row)) for row in zip(*(recent[key] for key in columns))]


def _iso(s: str) -> date:
    return date.fromisoformat(s)


def recent_filings(submissions: dict, today: date, days: int = 5) -> list[dict]:
    found = []
    for item in filing_rows(submissions):
        if item["form"] not in FORMS:
            continue
        try:
            filed = _iso(item["filingDate"])
            report_end = _iso(item["reportDate"])
        except (TypeError, ValueError):
            continue
        if filed > today or filed < today - timedelta(days=days):
            continue
        # Sanity-check the accession and document component before using URLs.
        if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", str(item["accessionNumber"])):
            continue
        if not re.fullmatch(r"[\w.-]+\.(?:htm|html|txt|xml)", str(item["primaryDocument"]), re.I):
            continue
        if report_end > filed:
            continue
        found.append(item)
    return sorted(found, key=lambda x: x["filingDate"], reverse=True)


def _duration_ok(row: dict, end: date, is_annual: bool) -> bool:
    try:
        a, b = _iso(row["start"]), _iso(row["end"])
    except (KeyError, ValueError, TypeError):
        return False
    days = (b - a).days
    return abs((b - end).days) <= 7 and (325 <= days <= 400 if is_annual else 65 <= days <= 115)


def _metric_candidates(facts: dict, tag: str, unit: str) -> list[dict]:
    family = facts.get("facts", {}).get("us-gaap", {}).get(tag, {})
    return family.get("units", {}).get(unit, [])


def _pick_pair(rows: list[dict], accn: str, end: date, filed: date, is_annual: bool):
    valid = [r for r in rows if _duration_ok(r, end, is_annual)
             and r.get("accn") == accn and r.get("form") in FORMS
             and isinstance(r.get("val"), (int, float)) and not isinstance(r.get("val"), bool)]
    if not valid:
        return None
    valid.sort(key=lambda r: ("frame" in r, str(r.get("filed") or "")), reverse=True)
    now = valid[0]
    start = _iso(now["start"])
    old_end = end - timedelta(days=365)
    prior = []
    for r in rows:
        try:
            r_end, r_start = _iso(r["end"]), _iso(r["start"])
        except (KeyError, TypeError, ValueError):
            continue
        if (abs((r_end - old_end).days) > 17
                or abs(((r_end - r_start) - (end - start)).days) > 10
                or r.get("form") not in FORMS
                or str(r.get("filed") or "") > filed.isoformat()
                or not isinstance(r.get("val"), (int, float)) or isinstance(r.get("val"), bool)):
            continue
        prior.append(r)
    if not prior:
        return None
    prior.sort(key=lambda r: (r.get("accn") == accn, abs((_iso(r["end"]) - old_end).days) * -1, str(r.get("filed") or "")), reverse=True)
    return now, prior[0]


def extract_metrics(facts: dict, filing: dict) -> dict | None:
    """Choose matching tags/units for an exact filing and comparable duration.

    Do not synthesize Q4 from annual minus YTD; the first version publishes
    complete 10-K annual financials and 10-Q standalone quarters only.
    """
    is_annual = filing["form"] == "10-K"
    end, filed = _iso(filing["reportDate"]), _iso(filing["filingDate"])
    accn = filing["accessionNumber"]
    outputs = {}
    for name, options, unit in (
        ("revenue", REVENUE_TAGS, "USD"),
        ("net_income", (NET_TAG,), "USD"),
        ("diluted_eps", (EPS_TAG,), "USD/shares"),
    ):
        for tag in options:
            pair = _pick_pair(_metric_candidates(facts, tag, unit), accn, end, filed, is_annual)
            if pair:
                outputs[name] = {"tag": tag, "unit": unit,
                                 "current": pair[0]["val"], "prior": pair[1]["val"],
                                 "start": pair[0]["start"], "end": pair[0]["end"],
                                 "fy": pair[0].get("fy"), "fp": pair[0].get("fp")}
                break
        if name not in outputs:
            LOG.warning("Skipping %s: no verified comparable %s", accn, name)
            return None
    # Require aligned reporting periods across all financial statement metrics.
    if len({(v["start"], v["end"]) for v in outputs.values()}) != 1:
        LOG.warning("Skipping %s: financial metrics refer to different periods", accn)
        return None
    if outputs["revenue"]["current"] <= 0 or outputs["revenue"]["prior"] <= 0:
        return None
    return outputs


def change_pct(current: float, prior: float) -> float | None:
    if prior <= 0:
        return None
    return (current - prior) / prior * 100


def money(value: float, unit: str = "USD") -> str:
    sign = "−" if value < 0 else ""
    abs_v = abs(value)
    prefix = "$" if unit == "USD" else ""
    if abs_v >= 1_000_000_000:
        return f"{sign}{prefix}{abs_v / 1e9:,.2f}bn"
    if abs_v >= 1_000_000:
        return f"{sign}{prefix}{abs_v / 1e6:,.2f}m"
    return f"{sign}{prefix}{abs_v:,.0f}"


def eps(value: float) -> str:
    return ("−" if value < 0 else "") + "$" + f"{abs(value):.2f}"


def period_label(filing: dict, metrics: dict) -> tuple[str, str]:
    revenue = metrics["revenue"]
    fy = revenue.get("fy")
    fp = revenue.get("fp")
    if not isinstance(fy, int) or fy < 2000 or fy > 2100:
        raise ValueError("A verifiable fiscal year is required")
    if filing["form"] == "10-K":
        return f"FY {fy} full-year", f"fy{fy}"
    if fp not in {"Q1", "Q2", "Q3"}:
        raise ValueError("10-Q fiscal period must be Q1, Q2 or Q3")
    return f"FY {fy} {fp}", f"fy{fy}-{fp.lower()}"


def filing_url(cik: int, filing: dict) -> str:
    accession = filing["accessionNumber"].replace("-", "")
    return f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filing["primaryDocument"]}'


def _comparison_note(label: str, now: float, prior: float, formatter) -> str:
    diff = change_pct(now, prior)
    movement = ("increased" if now > prior else "fell" if now < prior else "was unchanged")
    if diff is None:
        return f"{label} was {formatter(now)}, compared with {formatter(prior)} in the corresponding year-earlier period."
    return f"{label} {movement} from {formatter(prior)} to {formatter(now)} ({diff:+.1f}% year on year)."



def metric_history(facts: dict, filing: dict, metric: dict, *, unit: str, limit: int) -> list[dict]:
    """Use only SEC-reported matching-duration facts available as of this filing.

    Do not derive Q4 from annual/year-to-date values and never interpolate gaps.
    Quarterly history may therefore have fewer than eight observations.
    """
    annual = filing["form"] == "10-K"
    report_end = _iso(filing["reportDate"])
    as_of = filing["filingDate"]
    tagged = _metric_candidates(facts, metric["tag"], unit)
    selected: dict[str, dict] = {}
    for row in tagged:
        try:
            end = _iso(row["end"])
            submitted = str(row.get("filed") or "")
            value = row["val"]
            if row.get("form") != ("10-K" if annual else "10-Q"):
                continue
            if not submitted or submitted > as_of or end > report_end:
                continue
            if (report_end - end).days > (2400 if annual else 1150):
                continue
            if not _duration_ok(row, end, annual):
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            if not math.isfinite(value):
                continue
        except (KeyError, TypeError, ValueError):
            continue
        key = end.isoformat()
        existing = selected.get(key)
        score = (1 if row.get("accn") == filing["accessionNumber"] else 0,
                 1 if row.get("frame") else 0,
                 submitted)
        if existing is None or score > existing["score"]:
            selected[key] = {"end": key, "value": value, "score": score}
    points = sorted(selected.values(), key=lambda r: r["end"])[-limit:]
    # A final selected fact is sourced from the exact filing accession; always
    # align the latest chart observation with the verified article headline.
    verified_end = metric["end"]
    if verified_end not in {x["end"] for x in points}:
        points.append({"end": verified_end, "value": metric["current"]})
        points.sort(key=lambda r: r["end"])
        points = points[-limit:]
    else:
        for point in points:
            if point["end"] == verified_end:
                point["value"] = metric["current"]
    return [{"end": p["end"], "value": p["value"]} for p in points]


def build_article(ticker: str, company: str, cik: int, filing: dict, metrics: dict, today: date, facts: dict | None = None) -> tuple[str, str]:
    label, period_slug = period_label(filing, metrics)
    slug = f"{ticker.lower()}-earnings-{period_slug}"
    source = filing_url(cik, filing)
    safe_company = escape(company)
    safe_ticker = escape(ticker)
    period = "full financial year" if filing["form"] == "10-K" else "three-month quarter"
    rev = metrics["revenue"]
    net = metrics["net_income"]
    diluted = metrics["diluted_eps"]
    def delta(item: dict) -> str:
        change = change_pct(item["current"], item["prior"])
        return f"{change:+.1f}%" if change is not None else "not comparable"
    summary = (
        f"{company} ({ticker}) {label}: revenue {money(rev['current'])} ({delta(rev)} YoY), "
        f"net income {money(net['current'])} ({delta(net)}), "
        f"diluted GAAP EPS {eps(diluted['current'])} ({delta(diluted)})."
    )
    financial_snapshot = {
        "form": filing["form"], "report_end": filing["reportDate"],
        "period_label": label,
        "metrics": {
            key: {
                "current": item["current"], "prior": item["prior"],
                "history": metric_history(facts, filing, item,
                                          unit=item["unit"],
                                          limit=4 if filing["form"] == "10-K" else 8) if facts else [],
            }
            for key, item in metrics.items()
        },
    }
    meta = {
        "title": f"{company} ({ticker}) Earnings: {label} Revenue, Profit and EPS",
        "seo_title": f"{ticker} Earnings {label}: Revenue, EPS and Net Income | Compound",
        "slug": slug,
        "pillar": "wealth",
        "canonical_path": f"/wealth/earnings/{slug}/",
        "date": today.isoformat(),
        "reviewed": today.isoformat(),
        "draft": False,
        "publication_status": "published",
        "summary": summary,
        "meta_description": f"{ticker} {label}: revenue {money(rev['current'])} ({delta(rev)} YoY), net income {money(net['current'])}, diluted EPS {eps(diluted['current'])}. SEC filing data.",
        "tags": ["earnings", "automated-earnings", "stocks", "quarterly-results" if filing["form"] == "10-Q" else "annual-results", ticker.lower()],
        "earnings_snapshot": financial_snapshot,
        "sources": [
            {"title": f"SEC EDGAR: {company} {filing['form']} filed {filing['filingDate']}", "url": source},
            {"title": "SEC EDGAR XBRL company facts: comparable US GAAP results", "url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"},
        ],
        "filing_accession": filing["accessionNumber"],
        "automation": "SEC-reconciled deterministic financial summary; not AI-generated interpretation",
    }
    lines = [
        f"**{safe_company} ({safe_ticker})** filed its {escape(filing['form'])} for the {period} ending **{rev['end']}**.",
        "",
        "## What stands out", "",
        (f"Revenue {('increased' if rev['current'] > rev['prior'] else 'declined' if rev['current'] < rev['prior'] else 'was unchanged')} "
         f"year on year, while net income "
         f"{('increased' if net['current'] > net['prior'] else 'declined' if net['current'] < net['prior'] else 'was unchanged')}. "
         "The data above shows the direction and scale of all three GAAP metrics."),
        "",
        "## Filing and limitations", "",
        f"SEC {filing['form']} filed **{filing['filingDate']}** for the period ending **{filing['reportDate']}**. "
        f"[Read the original SEC filing]({source}).",
        "",
        "These are reported US GAAP figures, not analyst expectations, adjusted results or a share-price reaction. "
        "Year-on-year comparisons use the same financial-statement concept; missing quarters are omitted, not estimated. "
        "The report is not an investment recommendation.",
        "",
        "*Automated source-verified report, not individually reviewed before publication. "
        "This is general financial information, not investment advice. "
        "Corrections: [Compound](mailto:david@compound.ie).*",
        "",
    ]
    body = "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=120) + "---\n\n" + "\n".join(lines)
    return slug, body


def run(watchlist: Path, content_dir: Path, *, client: SECClient, now: date,
        lookback: int, max_new: int, dry_run: bool,
        registry_path: Path | None = None, shard_count: int = 1, shard_index: int = 0,
        extra_watchlist: Path | None = None) -> list[str]:
    if not 1 <= shard_count <= 24 or not 0 <= shard_index < shard_count:
        raise ValueError("Invalid SEC scan shard")
    # One JSON data file per company. Never create earnings article URLs.
    from earnings_consolidated import dashboard, store_update
    directory = content_dir / "earnings-profiles"
    registry_active = registry_path is not None and registry_path.is_file()
    if registry_active:
        # One SEC request per COMPANY, not per share class (GOOG/GOOGL etc).
        from importlib.util import module_from_spec, spec_from_file_location
        module_path = Path(__file__).with_name("sp500_registry.py")
        spec = spec_from_file_location("compound_sp500_registry", module_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        registry = module.load_registry(registry_path)
        if registry.get("company_count", 0) < 480:
            raise ValueError("S&P 500 registry is unexpectedly incomplete")
        members = [r for r in registry["members"] if r["active"]]
        resolved = {r["symbol"]: (r["name"], r["cik"]) for r in members}
        tickers = sorted(resolved)
    else:
        config = yaml.safe_load(watchlist.read_text(encoding="utf-8"))
        tickers = [str(s).upper() for s in config["tickers"]]
        if not tickers or len(tickers) != len(set(tickers)) or any(not re.fullmatch(r"[A-Z]{1,6}", t) for t in tickers):
            raise ValueError("Watchlist must contain distinct stock symbols")
        resolved = resolve_tickers(client.get_json(SEC_TICKERS), tickers)
        missing = sorted(set(tickers) - set(resolved))
        if missing:
            raise RuntimeError("Watchlist symbols not found in SEC ticker list: " + ", ".join(missing))
    # Add the confirmed US-reporting issuer from the ten extra public stocks.
    # Most overseas listings file 20-F/6-K or local-market accounts; they are
    # watched by the international disclosure monitor, NOT passed through the
    # US 10-Q / 10-K XBRL report generator.
    if extra_watchlist is not None and extra_watchlist.is_file():
        extras = json.loads(extra_watchlist.read_text(encoding="utf-8")).get("listed", [])
        domestic = [row for row in extras if row.get("slug") == "spcx"
                    and row.get("exchange", "").lower().startswith("nasdaq")]
        if domestic:
            try:
                mapping = resolve_tickers(client.get_json(SEC_TICKERS), [row["ticker"] for row in domestic])
            except RuntimeError as exc:
                LOG.warning("Extra SEC identity lookup unavailable; retaining core S&P scan: %s", exc)
                mapping = {}
            for row in domestic:
                issuer = mapping.get(row["ticker"])
                if not issuer or not re.search(r"space\s*(?:exploration|x)", issuer[0], re.I):
                    LOG.warning("SEC issuer verification missing for %s; skipping 10-Q/10-K monitoring",
                                row["ticker"])
                    continue
                if row["ticker"] not in resolved and issuer[1] not in {v[1] for v in resolved.values()}:
                    resolved[row["ticker"]] = (row["name"], issuer[1])
            tickers = sorted(resolved)
    # Every half-hour run examines one stable shard. Four sharded runs scan
    # the complete index in two hours, while remaining SEC-fair and cheap.
    total = len(tickers)
    tickers = [ticker for i, ticker in enumerate(tickers) if i % shard_count == shard_index]
    LOG.info("SEC scan %s/%s: %s of %s unique companies", shard_index + 1, shard_count, len(tickers), total)
    written = []
    failed = []
    for ticker in tickers:
        company, cik = resolved[ticker]
        try:
            submissions = client.get_json(f"{SEC_DATA}/submissions/CIK{cik:010d}.json")
            filings = recent_filings(submissions, now, lookback)
        except RuntimeError as exc:
            failed.append(ticker)
            LOG.warning("SEC submissions unavailable for %s: %s", ticker, exc)
            continue
        if not filings:
            continue
        # Never invent FY2027 Q3 just because a filing appears in 2026.
        # Form, fiscal year, and quarter are taken from that issuer's SEC facts.
        for filing in filings:
            if len(written) >= max_new:
                return written
            target = directory / f"{ticker.lower()}.json"
            previous = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else None
            accession = filing["accessionNumber"]
            if previous and any(p["accession"] == accession for p in previous["periods"]):
                continue
            try:
                facts = client.get_json(f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik:010d}.json")
            except RuntimeError as exc:
                failed.append(ticker)
                LOG.warning("SEC facts unavailable for %s: %s", ticker, exc)
                continue
            verified = dashboard(previous, ticker, company, cik, filing, submissions, facts,
                                 checked=now)
            if verified is None:
                continue
            result = store_update(directory, ticker, verified, dry_run=dry_run)
            if result:
                written.append(result)
                LOG.info("UPDATED %s: one canonical company report, SEC %s",
                         ticker, accession)
            # Revisit the rest of the company's filings on the next run.
            break
    if len(set(failed)) >= max(8, (len(tickers) + 4) // 5):
        raise RuntimeError(f"SEC unavailable for {len(set(failed))} of {len(tickers)} scanned companies: halt publishing")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Source-verified, single-page SEC company earnings updates")
    parser.add_argument("--watchlist", type=Path, default=Path("content/earnings-watchlist.yml"))
    parser.add_argument("--content-dir", type=Path, default=Path("content"))
    parser.add_argument("--lookback-days", type=int, default=5)
    parser.add_argument("--max-new", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--registry", type=Path, default=Path("content/earnings-sp500.json"))
    parser.add_argument("--extra-watchlist", type=Path, default=Path("content/company-watchlist.json"))
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    args = parser.parse_args(argv)
    if not 1 <= args.lookback_days <= 14 or not 1 <= args.max_new <= 10:
        parser.error("lookback-days must be 1–14 and max-new must be 1–10")
    logging.basicConfig(level=logging.INFO)
    client = SECClient(os.environ.get("SEC_USER_AGENT", ""))
    created = run(args.watchlist, args.content_dir, client=client,
                  now=datetime.now(timezone.utc).date(), lookback=args.lookback_days,
                  max_new=args.max_new, dry_run=args.dry_run,
                  registry_path=args.registry, shard_count=args.shard_count, shard_index=args.shard_index,
                  extra_watchlist=args.extra_watchlist)
    for f in created:
        print(f)
    print(f"Earnings checked: {len(created)} {'candidate updates' if args.dry_run else 'company profiles updated'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())