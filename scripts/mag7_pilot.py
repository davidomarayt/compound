#!/usr/bin/env python3
"""28-day Mag 7 editorial research pilot: one review-only research packet per day.

The scheduled job NEVER edits content, publishes an article or invents a source.
With ANTHROPIC_API_KEY it may add an AI draft to the GitHub review issue.
Without that key, it still creates a useful SEC-backed commissioning brief.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import html
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 10, 16)
DAYS = 28
# One company per day; four full cycles, starting with the commissioned Tesla piece.
ROTATION = ("TSLA", "MSFT", "NVDA", "AAPL", "AMZN", "GOOGL", "META")
COMPANIES = {
    "TSLA": ("Tesla", "Roadster economics, auto margins, energy storage and the next earnings filing"),
    "MSFT": ("Microsoft", "Azure AI spending versus cloud revenue and operating cash flow"),
    "NVDA": ("Nvidia", "Data Centre demand, gross margins and customer concentration"),
    "AAPL": ("Apple", "iPhone demand, Services, free cash flow and capital returns"),
    "AMZN": ("Amazon", "AWS operating income, retail economics and AI capital expenditure"),
    "GOOGL": ("Alphabet", "Search advertising, Cloud profitability and AI infrastructure costs"),
    "META": ("Meta", "Advertising growth, Reality Labs losses and AI capital intensity"),
}
IR_PAGES = {
    "TSLA": "https://ir.tesla.com/",
    "MSFT": "https://www.microsoft.com/en-us/Investor",
    "NVDA": "https://investor.nvidia.com/",
    "AAPL": "https://investor.apple.com/",
    "AMZN": "https://ir.aboutamazon.com/",
    "GOOGL": "https://abc.xyz/investor/",
    "META": "https://investor.atmeta.com/",
}


def assignment(day: date) -> tuple[str, int] | None:
    n = (day - START).days
    return (ROTATION[n % 7], n // 7 + 1) if 0 <= n < DAYS else None


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", html.unescape(str(value or "")))).strip()


def latest_sec(ticker: str) -> dict:
    path = ROOT / "content" / "earnings-profiles" / (ticker.lower() + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    latest = data["latest"]
    source = str(latest.get("source") or "")
    if not source.startswith("https://www.sec.gov/Archives/"):
        raise ValueError(f"Missing verified source for {ticker}")
    metrics = latest["metrics"]
    lines = []
    for key, name, fmt in [
        ("revenue", "Revenue", "usd"),
        ("net_income", "Net income", "usd"),
        ("diluted_eps", "Diluted EPS", "eps"),
    ]:
        pair = metrics[key]
        a, b = pair["current"], pair.get("prior_year")
        if not isinstance(a, (float, int)) or not isinstance(b, (float, int)):
            continue
        if fmt == "usd":
            values = f"USD {a / 1e9:.3f}bn vs USD {b / 1e9:.3f}bn"
        else:
            values = f"USD {a:.2f}/share vs USD {b:.2f}/share"
        change = f"{((a / b) - 1) * 100:+.1f}%" if b > 0 else "not comparable"
        lines.append(f"- {name}: {values}; year-on-year {change}")
    return {
        "filing": source,
        "period": f"FY{latest['fy']} {latest['fp']}",
        "end": latest["period_end"],
        "filed": latest.get("filed", ""),
        "metrics": lines,
    }


def headlines(ticker: str, day: date, limit: int = 8) -> list[dict]:
    """RSS headlines are DISCOVERY ONLY: no article text is copied or verified."""
    company = COMPANIES[ticker][0]
    query = urllib.parse.quote(f'"{company}" stock earnings investor when:7d')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        import feedparser
        req = urllib.request.Request(url, headers={"User-Agent": "CompoundResearch/1.0 (editorial research)"})
        with urllib.request.urlopen(req, timeout=14) as resp:
            payload = resp.read(500_000)
        feed = feedparser.parse(payload)
        result = []
        for entry in feed.entries[:35]:
            published = entry.get("published") or entry.get("updated")
            if published:
                try:
                    stamp = parsedate_to_datetime(published).date()
                except (TypeError, ValueError, OverflowError):
                    continue
                if abs((day - stamp).days) > 7:
                    continue
            else:
                continue
            title, link = clean(entry.get("title")), str(entry.get("link", ""))
            if not title or not link.startswith("https://"):
                continue
            result.append({"title": title[:220], "url": link, "published": published[:45]})
            if len(result) >= limit:
                break
        return result
    except Exception as exc:
        print(f"News discovery unavailable for {ticker}: {type(exc).__name__}: {exc}")
        return []


def duplicates(ticker: str) -> list[str]:
    """Editorial catalogue is a sanity-check; the editor must assess search intent."""
    index = ROOT / "EDITORIAL_TOPIC_INDEX.md"
    if not index.is_file():
        return []
    names = {"GOOGL": ("alphabet", "google"), "META": ("meta",),
             "AAPL": ("apple",), "AMZN": ("amazon",), "NVDA": ("nvidia",),
             "TSLA": ("tesla",), "MSFT": ("microsoft",)}[ticker]
    return [line.strip()[:260] for line in index.read_text(encoding="utf-8").splitlines()
            if line.startswith("- [") and any(name in line.lower() for name in names)][:15]


def brief(day: date, ticker: str, week: int, sec: dict, news: list[dict], prior: list[str]) -> str:
    name, focus = COMPANIES[ticker]
    out = [
        f"# Mag 7 research pilot — {day.isoformat()} — {name} ({ticker})",
        "",
        f"**Week:** {week} of 4 · **Status:** Review required, not published",
        f"**Assignment:** One substantial, original article on {name}; target research theme: {focus}.",
        "**Editorial safeguard:** If no distinct, well-supported angle exists, recommend skipping rather than filler.",
        "",
        "## Verified historical financial baseline (SEC filing)",
        f"- Fiscal period: {sec['period']} ended {sec['end']}; filed {sec['filed']}",
        *sec["metrics"],
        f"- Primary filing: {sec['filing']}",
        f"- Company investor relations: {IR_PAGES[ticker]}",
        "- These data are a dated baseline, **not** the latest share price, consensus or forward guidance.",
        "",
        "## News discovery (headlines only; independently verify ALL material claims)",
    ]
    out.extend(f"- [{h['title']}]({h['url']}) — {h['published']}" for h in news)
    if not news:
        out.append("- No recent RSS headlines verified. Choose an evergreen earnings-economics angle or skip.")
    out.extend(["", "## Existing Compound content — check duplication", *prior])
    if not prior:
        out.append("- No obvious title-level match; manual subject and search-intent check still required.")
    out.extend([
        "", "## Article requirements",
        "1. A sharp, company-specific thesis that is not a rewritten press release.",
        "2. At least two independently checked reputable reports/primary documents; use company SEC filings for financial numbers.",
        "3. Explain what is confirmed, what is management guidance, and what is an assumption.",
        "4. One original calculation, visual or scenario table with assumptions and source attribution.",
        "5. Counter-argument, material risks, catalyst/next disclosure, and implications for long-term investors.",
        "6. Distinct SEO query, meaningful headline/description, no false certainty or price forecasts.",
        f"7. Internal link to https://compound.ie/stocks/{ticker.lower()}/ and https://compound.ie/wealth/earnings/.",
        "8. Use an authentic, properly licensed company photograph with photographer, dated context and source. NO AI-generated, synthetic, drawn or render-based hero or social images. Do not present archive photos as footage of current events.",
        "9. Run duplicate, fact, arithmetic, links, image, mobile, AdSense and build QA before publishing.",
        "10. Prepare a substantive X discussion post; article link should be in a reply.",
        "",
        "## Publication policy",
        "No auto-publish in the four-week pilot. Editor must approve; only then commit a"
        " new canonical article and its verified image to the existing publishing pipeline.",
    ])
    return "\n".join(out) + "\n"


def ai_draft(packet: str, ticker: str, day: date) -> str:
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        return "\n## Draft generation\n\n**Not configured:** ANTHROPIC_API_KEY GitHub Actions secret is missing. Research brief produced; awaiting editor or key setup.\n"
    try:
        from anthropic import Anthropic
        client = Anthropic(timeout=105.0)
        message = client.messages.create(
            model=os.getenv("MAG7_MODEL", "").strip() or "claude-sonnet-4-5",
            max_tokens=4400,
            temperature=0.25,
            # Server-side web search, when available to this API account.
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}],
            messages=[{"role": "user", "content": (
                "You are Compound.ie's rigorous financial research editor. Produce a"
                " REVIEW-ONLY article draft in Markdown, based on verified primary"
                " sources and independent current reporting. USE web_search to verify"
                " current facts; if unavailable or sources insufficient, explain gaps"
                " and mark NEEDS RESEARCH — do NOT manufacture details.\n"
                "Start with DRAFT ONLY, a title, and a 140-160 char SEO description."
                " Write 800-1300 useful words in focused sections with clear date"
                " context, first-principles financial analysis, evidence-based risks,"
                " plausible counterargument and next catalyst. Include an ORIGINAL,"
                " accurately calculated scenario table with stated hypothetical"
                " assumptions if it helps; never represent it as company guidance."
                " Cite every material current claim and number via direct Markdown"
                " links. Do not claim to have consulted any link not actually checked."
                " Keep the official fiscal-year label. Clearly distinguish revenue,"
                " GAAP net income, operating profit, and cash flow. Finish with"
                " 'Sources checked', 'Claims requiring human confirmation', and"
                " 'X post / reply link placeholder'. Do not repeat existing content."
                " No AI-generated, synthetic or illustrated cover images. Request a real"
                " appropriately licensed photo with attribution, date and original source."
                " If only an archival image is licensed, caption it as archival."
                " Never give personalised buy/sell advice. This is NOT permission"
                " to publish.\n\n" + packet)}],
        )
        content = "\n".join(block.text for block in message.content if getattr(block, "type", "") == "text")
        if len(content.split()) < 500 or len(re.findall(r"https?://", content)) < 2:
            return "\n## Draft generation\n\n**Needs manual research:** model response failed length/source safeguards. It has not been attached as a publication-ready draft.\n"
        return "\n## AI-assisted working draft — MUST BE VERIFIED BEFORE PUBLICATION\n\n" + content + "\n"
    except Exception as exc:
        # Do not hide failures, and never publish an incomplete response.
        return f"\n## Draft generation\n\n**Unavailable / needs review:** {type(exc).__name__}: {clean(exc)[:350]}\n"


def run(day: date, output: Path, no_ai: bool = False) -> int:
    slot = assignment(day)
    if slot is None:
        print(f"{day}: outside the 28-day pilot; no issue will be created.")
        return 3
    ticker, week = slot
    data = latest_sec(ticker)
    packet = brief(day, ticker, week, data, headlines(ticker, day), duplicates(ticker))
    if not no_ai:
        packet += ai_draft(packet, ticker, day)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(packet, encoding="utf-8")
    print(f"Research issue prepared for {ticker}, week {week}: {output}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    ap.add_argument("--output", default="mag7-review.md")
    ap.add_argument("--no-ai", action="store_true", help="Produce SEC-backed editorial brief only")
    args = ap.parse_args()
    return run(date.fromisoformat(args.date), Path(args.output), args.no_ai)


if __name__ == "__main__":
    raise SystemExit(main())
