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


def chart_svg(revenue: dict) -> str:
    """Two-period accessible inline graphic; sourced data also appears in HTML table."""
    a, b = float(revenue["prior"]), float(revenue["current"])
    top = max(a, b)
    prior_h = max(4, round(a / top * 126))
    now_h = max(4, round(b / top * 126))
    return (
        '<figure class="earnings-bars">'
        '<svg viewBox="0 0 560 190" width="560" height="190" role="img" '
        'aria-label="Reported revenue in US dollars: previous comparable period versus current filing">'
        '<rect x="85" y="' + str(148 - prior_h) + '" width="124" height="' + str(prior_h) + '" rx="4" fill="#9a8b91"/>'
        '<rect x="342" y="' + str(148 - now_h) + '" width="124" height="' + str(now_h) + '" rx="4" fill="#7d4b4e"/>'
        '<text x="147" y="167" text-anchor="middle" fill="#393139" font-size="14">Prior year</text>'
        '<text x="404" y="167" text-anchor="middle" fill="#393139" font-size="14">Current</text>'
        '<text x="147" y="' + str(139 - prior_h) + '" text-anchor="middle" fill="#393139" font-size="14">' + escape(money(a)) + '</text>'
        '<text x="404" y="' + str(139 - now_h) + '" text-anchor="middle" fill="#393139" font-size="14">' + escape(money(b)) + '</text>'
        '</svg><figcaption>Revenue for matched reporting periods; primary source: SEC filing.</figcaption></figure>'
    )


def build_article(ticker: str, company: str, cik: int, filing: dict, metrics: dict, today: date) -> tuple[str, str]:
    label, period_slug = period_label(filing, metrics)
    slug = f"{ticker.lower()}-earnings-{period_slug}"
    source = filing_url(cik, filing)
    safe_company = escape(company)
    safe_ticker = escape(ticker)
    period = "full financial year" if filing["form"] == "10-K" else "three-month quarter"
    rev = metrics["revenue"]
    net = metrics["net_income"]
    diluted = metrics["diluted_eps"]
    summary = (f"{company} ({ticker}) reported {money(rev['current'])} in revenue and "
               f"{eps(diluted['current'])} diluted GAAP EPS in its {label} SEC filing. "
               "Compare reported results with the year-earlier period.")
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
        "meta_description": f"{ticker} {label} reported earnings: revenue {money(rev['current'])}, diluted EPS {eps(diluted['current'])}. View verified SEC figures and year-on-year changes.",
        "tags": ["earnings", "automated-earnings", "stocks", "quarterly-results" if filing["form"] == "10-Q" else "annual-results", ticker.lower()],
        "related_tools": ["investment-fee-calculator"],
        "sources": [
            {"title": f"SEC EDGAR: {company} {filing['form']} filed {filing['filingDate']}", "url": source},
            {"title": "SEC EDGAR XBRL company facts: comparable US GAAP results", "url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"},
        ],
        "filing_accession": filing["accessionNumber"],
        "automation": "SEC-reconciled deterministic financial summary; not AI-generated interpretation",
    }
    metrics_table = [
        ("Revenue (US GAAP)", rev, money),
        ("Net income (US GAAP)", net, money),
        ("Diluted earnings per share (GAAP)", diluted, eps),
    ]
    lines = [
        f"**{safe_company} ({safe_ticker})** filed its {escape(filing['form'])} covering the {period} ending **{rev['end']}** on **{filing['filingDate']}**.",
        "",
        "> **Source-verified automated report:** Compound created this article from standardised figures in the cited SEC filing. This is a financial-data summary, not an earnings-call recap, analyst-consensus comparison or investment recommendation. Initial earnings announcements may precede the filing.",
        "",
        "## Earnings at a glance", "",
        "| Reported metric | Current period | Corresponding prior-year period | Change |",
        "|:---|---:|---:|---:|",
    ]
    for caption, item, fmt in metrics_table:
        pct = change_pct(item["current"], item["prior"])
        change = f"{pct:+.1f}%" if pct is not None else "Not meaningful"
        lines.append(f"| {caption} | {fmt(item['current'])} | {fmt(item['prior'])} | {change} |")
    lines.extend([
        "", "## Revenue and profit: what changed?", "",
        _comparison_note("Revenue", rev["current"], rev["prior"], money), "",
        _comparison_note("Net income", net["current"], net["prior"], money), "",
        _comparison_note("Diluted GAAP EPS", diluted["current"], diluted["prior"], eps), "",
        chart_svg(rev), "",
        "## How to interpret these results", "",
        "These figures are reported US GAAP results from the SEC's standardised company facts. They do not include management's full commentary, adjusted (non-GAAP) EPS, analyst estimates, guidance or the share-price reaction. Revenue growth does not by itself establish profitability or future returns.", "",
        "The comparison uses the same financial-statement concept and a corresponding period one year earlier; amended disclosures or accounting changes can affect comparability. Consult the source filing before relying on the figures.", "",
        "## When were the results filed?", "",
        f"The SEC received the **{filing['form']}** on **{filing['filingDate']}**, covering a period ending **{filing['reportDate']}**. [Read the original filing]({source}).", "",
        "For wider Irish investing context, see the [Compound PIA Centre](/pia/), our [Irish investing guide](/wealth/how-to-start-investing-in-ireland/) and the [earnings archive](/wealth/earnings/).", "",
        "*This report is automated and source-linked. It is not individually reviewed before publication; corrections can be sent to [Compound](mailto:david@compound.ie). It is general financial information, not investment advice.*", "",
    ])
    body = "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=120) + "---\n\n" + "\n".join(lines)
    return slug, body


def run(watchlist: Path, content_dir: Path, *, client: SECClient, now: date,
        lookback: int, max_new: int, dry_run: bool,
        registry_path: Path | None = None, shard_count: int = 1, shard_index: int = 0) -> list[str]:
    if not 1 <= shard_count <= 24 or not 0 <= shard_index < shard_count:
        raise ValueError("Invalid SEC scan shard")
    directory = content_dir / "wealth"
    if not dry_run:
        directory.mkdir(parents=True, exist_ok=True)

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
            filings = recent_filings(client.get_json(f"{SEC_DATA}/submissions/CIK{cik:010d}.json"), now, lookback)
        except RuntimeError as exc:
            failed.append(ticker)
            LOG.warning("SEC submission unavailable for %s: %s", ticker, exc)
            continue
        for filing in filings:
            # Pull only if a new, recent complete SEC financial filing exists.
            # Annual 10-K is annual reporting, never mislabelled as Q4 earnings.
            if len(written) >= max_new:
                LOG.info("Article cap reached (%d). Remaining filings held for next scheduled scan", max_new)
                return written
            # Path identity is ticker + fiscal period (derived from XBRL), so fact fetch is needed.
            accession = filing["accessionNumber"]
            if any(accession in p.read_text(encoding="utf-8")
                   for p in directory.glob(f"{ticker.lower()}-earnings-*.md")):
                continue
            try:
                facts = client.get_json(f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik:010d}.json")
            except RuntimeError as exc:
                failed.append(ticker)
                LOG.warning("SEC XBRL facts unavailable for %s: %s", ticker, exc)
                continue
            metrics = extract_metrics(facts, filing)
            if metrics is None:
                continue
            try:
                slug, content = build_article(ticker, company, cik, filing, metrics, now)
            except ValueError as exc:
                LOG.warning("Skipping %s %s: %s", ticker, filing["accessionNumber"], exc)
                continue
            target = directory / f"{slug}.md"
            if target.exists():
                LOG.info("Existing article for %s %s; leaving published URL stable", ticker, slug)
                continue
            LOG.info("NEW %s: %s", ticker, slug)
            if not dry_run:
                target.write_text(content, encoding="utf-8", newline="\n")
            written.append(str(target))
    if len(set(failed)) >= max(8, (len(tickers) + 4) // 5):
        raise RuntimeError(f"SEC unavailable for {len(set(failed))} of {len(tickers)} scanned companies: halt publishing")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Source-verified, deterministic SEC earnings publication")
    parser.add_argument("--watchlist", type=Path, default=Path("content/earnings-watchlist.yml"))
    parser.add_argument("--content-dir", type=Path, default=Path("content"))
    parser.add_argument("--lookback-days", type=int, default=5)
    parser.add_argument("--max-new", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--registry", type=Path, default=Path("content/earnings-sp500.json"))
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
                  registry_path=args.registry, shard_count=args.shard_count, shard_index=args.shard_index)
    for f in created:
        print(f)
    print(f"Earnings checked: {len(created)} new {'candidates' if args.dry_run else 'articles'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())