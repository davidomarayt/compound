"""Watch the ten additional public companies for verified financial disclosures.

The SEC 10-Q/10-K generator cannot accurately normalise local-market IFRS
statements and foreign-issuer 20-F/6-K releases. Instead, collect dated,
source-linked REVIEW candidates. Nothing here becomes a published earnings
article without proper issuer-specific financial extraction and validation.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
import logging
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from earnings import SECClient, SEC_DATA, SEC_TICKERS, filing_rows, resolve_tickers

LOG = logging.getLogger("compound.global_earnings")
KEYWORDS = re.compile(r"\b(quarterly|annual|interim|earnings|financial[- ]?results|"
                      r"financial[- ]?statements|financial[- ]?report|results[- ]?centre|"
                      r"results[- ]?center|full[- ]?year|half[- ]?year|"
                      r"20-f|6-k|10-k|10-q)\b", re.I)
SEC_NAMES = {
    "spcx": re.compile(r"space\s*(exploration|x)", re.I),
    "tsm": re.compile(r"taiwan\s*semiconductor", re.I),
    "asml": re.compile(r"asml", re.I),
    "tm": re.compile(r"toyota", re.I),
    "nvo": re.compile(r"novo\s*nordisk", re.I),
}
FORMS = {"10-Q", "10-K", "20-F", "6-K"}

# Verified company / exchange pages specialising in financial results.
# Keep the trading-listing URLs in company-watchlist.json unchanged.
OFFICIAL_RESULTS_PAGES = {
    "tsm": "https://investor.tsmc.com/english/financial-calendar",
    "asml": "https://www.asml.com/en/investors/financial-results",
    "005930-ks": "https://www.samsung.com/global/ir/financial-information/earnings-release/",
    "tm": "https://global.toyota/en/ir/library/",
    "0700-hk": "https://www.tencent.com/investors/results/",
    "1211-hk": "https://www1.hkexnews.hk/search/titlesearch.xhtml?category=0&lang=EN&market=SEHK&stockId=2696",
    "7974-t": "https://www.nintendo.co.jp/ir/en/events/index.html",
    "nvo": "https://www.novonordisk.com/investors/financial-results.html",
    "mc-pa": "https://www.lvmh.com/publications",
}



class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.url = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.url = dict(attrs).get("href", "")
            self.text = []

    def handle_data(self, data):
        if self.url is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.url is not None:
            self.links.append((self.url, " ".join(" ".join(self.text).split())))
            self.url = None
            self.text = []


def financial_links(html: str, source_url: str) -> list[dict]:
    """Limit to primary-source links; never accept external promotional links."""
    parser = AnchorParser()
    parser.feed(html[:2_000_000])
    root = urlparse(source_url)
    items = {}
    for href, title in parser.links:
        target = urljoin(source_url, href)
        parsed = urlparse(target)
        if parsed.scheme != "https" or parsed.hostname != root.hostname:
            continue
        if not KEYWORDS.search(title + " " + parsed.path.replace("/", " ")):
            continue
        # Exclude static header/footer categories without any useful context.
        if len(title) < 7 or len(title) > 220:
            continue
        clean = parsed._replace(fragment="").geturl()
        items[clean] = {"title": title, "url": clean}
    return list(items.values())[:160]


def fetch_page(url: str) -> str:
    if not url.startswith("https://"):
        raise ValueError("Investor relations source must use HTTPS")
    req = Request(url, headers={"User-Agent": "Compound.ie Earnings Research david@compound.ie",
                                "Accept": "text/html"})
    with urlopen(req, timeout=24) as response:
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("Source is not an HTML investor-relations page")
        return response.read(2_000_001).decode("utf-8", errors="replace")


def sec_candidates(client, listed: list[dict], today: date) -> tuple[dict[str, list[dict]], dict[str, str]]:
    matched = [row for row in listed if row["slug"] in SEC_NAMES]
    found: dict[str, list[dict]] = {row["slug"]: [] for row in matched}
    status: dict[str, str] = {}
    if not matched:
        return found, status
    try:
        mapping = resolve_tickers(client.get_json(SEC_TICKERS), [row["ticker"] for row in matched])
    except RuntimeError as exc:
        return found, {row["slug"]: f"SEC index unavailable: {exc}" for row in matched}
    for row in matched:
        slug, symbol = row["slug"], row["ticker"]
        issuer = mapping.get(symbol)
        if not issuer or not SEC_NAMES[slug].search(issuer[0]):
            status[slug] = "No SEC issuer identity confirmed for listing"
            continue
        name, cik = issuer
        try:
            submissions = client.get_json(f"{SEC_DATA}/submissions/CIK{cik:010d}.json")
        except RuntimeError as exc:
            status[slug] = f"SEC submissions unavailable: {exc}"
            continue
        status[slug] = f"SEC verified issuer: {name} ({cik})"
        seen = set()
        for filing in filing_rows(submissions):
            try:
                filed = date.fromisoformat(filing["filingDate"])
                accession = filing["accessionNumber"]
                form = filing["form"]
                if (form not in FORMS or filed > today or filed < today - timedelta(days=40)
                        or not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession)):
                    continue
            except (KeyError, TypeError, ValueError):
                continue
            ident = f"sec:{cik}:{accession}"
            if ident in seen:
                continue
            seen.add(ident)
            found[slug].append({
                "id": ident, "company": row["name"], "slug": slug,
                "title": f"{row['name']} SEC {form} filed {filed}",
                "filed": filed.isoformat(), "form": form,
                "url": f"https://www.sec.gov/edgar/browse/?CIK={cik}",
                "source": "SEC EDGAR (requires review; not a verified earnings article)",
            })
            if len(found[slug]) >= 6:
                break
    return found, status


def run(watchlist: Path, snapshot: Path, *, today: date, client=None,
        fetch=fetch_page, dry_run=False) -> dict:
    listed = json.loads(watchlist.read_text(encoding="utf-8")).get("listed", [])
    if len(listed) != 10 or len({row["slug"] for row in listed}) != 10:
        raise ValueError("Expected the ten additional publicly listed companies")
    previous = json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists() else {}
    old_links = previous.get("observed_links", {})
    observed = dict(old_links)
    pending = list(previous.get("pending_review", []))
    pending_ids = {item["id"] for item in pending}
    checks = {}
    sec, sec_status = sec_candidates(client, listed, today) if client else ({}, {})
    added = []
    for row in listed:
        slug = row["slug"]
        results_page = OFFICIAL_RESULTS_PAGES.get(slug, row["source"])
        status = {"company": row["name"], "official_source": results_page,
                  "regulatory": sec_status.get(slug, "Local-market / non-SEC disclosures")}
        try:
            links = financial_links(fetch(results_page), results_page)
            status["official_source_status"] = f"Checked {len(links)} relevant investor links"
            current = {item["url"]: item for item in links}
            prior = set(old_links.get(slug, []))
            # First scan is a baseline rather than retroactive proof of a new result.
            new = set(current) - prior if slug in old_links else set()
            for url in sorted(new)[:6]:
                item = current[url]
                ident = f"ir:{slug}:{url}"
                if ident not in pending_ids:
                    added.append({"id": ident, "company": row["name"], "slug": slug,
                                  "title": item["title"], "url": url,
                                  "source": "Official investor page (review before publication)",
                                  "discovered": today.isoformat()})
                    pending_ids.add(ident)
            observed[slug] = sorted(current)
        except (OSError, ValueError) as exc:
            status["official_source_status"] = f"Unavailable; retry next run: {str(exc)[:150]}"
        for filing in sec.get(slug, []):
            if filing["id"] not in pending_ids:
                added.append(filing)
                pending_ids.add(filing["id"])
        checks[slug] = status
    pending = (added + pending)[:150]
    state = {"checked": today.isoformat(), "companies_checked": len(listed),
             "companies": checks, "observed_links": observed,
             "new_review_candidates": len(added), "pending_review": pending,
             "note": ("A discovery queue, not published financial analysis. Source pages can be blocked "
                      "or JavaScript-rendered; a successful HTTP request does not guarantee full coverage.")}
    if not dry_run:
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    for row in added:
        LOG.info("NEW financial-disclosure candidate: %s | %s", row["company"], row["url"])
    for slug, status in checks.items():
        LOG.info("%s: %s; %s", slug, status["regulatory"], status["official_source_status"])
    return state


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--watchlist", type=Path, default=Path("content/company-watchlist.json"))
    p.add_argument("--snapshot", type=Path, default=Path("monitoring/global-earnings-review.json"))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO)
    client = SECClient(os.getenv("SEC_USER_AGENT", ""))
    state = run(args.watchlist, args.snapshot, today=datetime.now(timezone.utc).date(),
                client=client, dry_run=args.dry_run)
    # Surface discoveries prominently on the scheduled GitHub Actions run.
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = [
            "## International company earnings watch",
            "",
            f"Checked **{state['companies_checked']}** additional public companies; "
            f"**{state['new_review_candidates']}** new review candidates.",
            "",
            "| Company | Primary source status |",
            "|---|---|",
        ]
        for entry in state["companies"].values():
            lines.append(f"| {entry['company']} | {entry['official_source_status'].replace('|', ' ')} |")
        for row in state["pending_review"][:state["new_review_candidates"]]:
            lines.append(f"- **{row['company']}**: [{row['title']}]({row['url']}) — review only")
        lines.append("")
        lines.append("Review queue: monitoring/global-earnings-review.json. "
                     "No unverified foreign-market results are auto-published.")
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write("\n".join(lines) + "\n")
    print(f"Global financial-disclosure watch: {state['companies_checked']} companies, "
          f"{state['new_review_candidates']} new items for review, "
          f"{len(state['pending_review'])} pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
