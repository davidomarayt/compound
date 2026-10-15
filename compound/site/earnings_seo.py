"""Search-first editorial presentation for twenty verified company earnings profiles.

This is intentionally a curated cohort, not a generator of extra quarterly URLs.
SEO titles only change when the underlying SEC-backed fiscal period changes.
All quantitative statements come from the verified company dashboard.
"""
from __future__ import annotations

from datetime import date
import re

PRIORITY = {
    "AAPL": ("Apple", "iPhone, Services and geographic segment disclosures", ("MSFT", "GOOGL", "NVDA")),
    "MSFT": ("Microsoft", "Azure, productivity software and segment-level margins", ("GOOGL", "AMZN", "ORCL")),
    "AMZN": ("Amazon", "AWS, online retail and non-operating investment gains", ("MSFT", "WMT", "GOOGL")),
    "GOOGL": ("Alphabet (Google)", "advertising, Google Cloud and capital spending", ("META", "MSFT", "AMZN")),
    "META": ("Meta Platforms", "advertising, Reality Labs and capital expenditure", ("GOOGL", "NVDA", "AAPL")),
    "NVDA": ("Nvidia", "data centre, gaming and gross-margin disclosures", ("AMD", "MSFT", "TSLA")),
    "TSLA": ("Tesla", "automotive, energy storage and regulatory-credit disclosures", ("UBER", "NVDA", "AAPL")),
    "AMD": ("AMD", "data centre, PC and gaming segment disclosures", ("NVDA", "AAPL", "MSFT")),
    "PLTR": ("Palantir", "US commercial, government and international revenue splits", ("MSFT", "ORCL", "CRM")),
    "NFLX": ("Netflix", "subscription revenue, operating margins and free cash flow", ("DIS", "META", "AMZN")),
    "ORCL": ("Oracle", "cloud infrastructure, software and remaining performance obligations", ("MSFT", "CRM", "AMZN")),
    "CRM": ("Salesforce", "subscription revenue, margins and remaining performance obligations", ("ORCL", "PLTR", "MSFT")),
    "UBER": ("Uber", "Mobility, Delivery and operating cash generation", ("TSLA", "AMZN", "META")),
    "COIN": ("Coinbase", "trading volume, transaction revenue and non-transaction income", ("HOOD", "META", "AMD")),
    "HOOD": ("Robinhood", "transaction revenue, net interest income and funded customers", ("COIN", "AAPL", "META")),
    "LLY": ("Eli Lilly", "medicine-level sales, volume and manufacturing investment", ("WMT", "AMZN", "AAPL")),
    "WMT": ("Walmart", "US comparable sales, ecommerce and international performance", ("COST", "AMZN", "AAPL")),
    "COST": ("Costco", "comparable sales, paid memberships and merchandise margins", ("WMT", "AMZN", "AAPL")),
    "ADBE": ("Adobe", "Digital Media subscriptions, remaining performance obligations and margins", ("CRM", "MSFT", "GOOGL")),
    "DIS": ("Disney", "Experiences, streaming and entertainment segment profits", ("NFLX", "META", "AMZN")),
}

ORDER = tuple(PRIORITY)

_PERIOD_PATTERN = re.compile(r"^FY(?P<year>\d{4}) (?P<period>Q[123]|FY)$")


def fiscal_period_display(report: dict) -> dict:
    """Keep the fiscal label accurate while supplying the actual calendar end."""
    match = _PERIOD_PATTERN.fullmatch(report["latest_label"])
    if not match:
        raise ValueError("Unrecognised verified fiscal period")
    end = date.fromisoformat(report["latest_end"])
    fy = int(match.group("year"))
    fp = match.group("period")
    annual = fp == "FY"
    display = f"FY{fy} Full-Year" if annual else f"{fp} FY{fy}"
    month_year = end.strftime("%B %Y")
    is_cross_year = fy != end.year
    readable_end = f"{end.day} {month_year}"
    filed = report.get("latest_filed") or ""
    filing_date = date.fromisoformat(filed) if filed else None
    filing_readable = f"{filing_date.day} {filing_date.strftime('%B %Y')}" if filing_date else ""
    filing_form = report.get("latest_form") or ("10-K" if annual else "10-Q")
    period_type = "Fiscal year" if annual else "Quarter"
    subtitle = f"{period_type} ended {readable_end}"
    if filing_readable:
        subtitle += f" · SEC {filing_form} filed {filing_readable}"
    return {
        "display": display, "month_year": month_year, "readable_end": readable_end,
        "filing_readable": filing_readable, "is_cross_year": is_cross_year,
        "title_calendar": f" ({month_year})" if is_cross_year else "",
        "subtitle": subtitle, "annual": annual,
    }


def _move(label: str, value: float | None, kind: str) -> str | None:
    if value is None:
        return None
    if value == 0:
        return f"{label} was unchanged {kind}."
    direction = "rose" if value > 0 else "fell"
    return f"{label} {direction} {abs(value):.1f}% {kind}."


def build_earnings_seo(company: dict, report: dict | None) -> dict | None:
    """Only upgrade the selected, already-covered companies with verified figures."""
    if not report:
        return None
    ticker = company["symbol"].upper()
    if ticker not in PRIORITY:
        return None
    name, focus, related = PRIORITY[ticker]
    period = report["latest_label"]
    latest = report.get("latest_figures") or {}
    if not latest.get("revenue") or not latest.get("diluted_eps") or not report.get("latest_source"):
        return None
    fiscal = fiscal_period_display(report)
    label = fiscal["display"]
    if fiscal["is_cross_year"]:
        title = f"{name} {label} Earnings{fiscal['title_calendar']} | {ticker} Results"
    else:
        title = f"{name} {label} Earnings: Revenue & EPS | {ticker}"
    headline = f"{name} {label} Earnings Results"
    description = (
        f"{name} ({ticker}) {label} earnings, {fiscal['subtitle']}. "
        f"Revenue {latest['revenue']}; diluted EPS {latest['diluted_eps']}. "
        "SEC filings and growth comparisons."
    )
    # Retain precise reporting dates instead of presenting FY2027 as a future event.
    narrative = [
        f"In {period}, ending {report['latest_end']}, {name} reported "
        f"revenue of {latest['revenue']}, net income of {latest['net_income']} "
        f"and diluted earnings per share of {latest['diluted_eps']}. "
        "These are reported financial-statement amounts, not market forecasts."
    ]
    metrics = (
        ("Revenue", "revenue"),
        ("Diluted EPS", "diluted_eps"),
        ("Net income", "net_income"),
    )
    movements = []
    for label, key in metrics:
        m = _move(label, report.get("yoy", {}).get(key), "versus the comparable year-earlier reporting period")
        if m:
            movements.append(m)
    prev = report.get("latest_prev_label")
    if prev:
        for label, key in metrics:
            m = _move(label, report.get("latest_qoq", {}).get(key), f"from {prev} to {period}")
            if m:
                movements.append(m)
    if not movements:
        movements.append("Some growth comparisons are unavailable because matching verified periods are missing.")
    caveat = (
        f"To understand what drove these consolidated results, examine {focus} in the "
        "linked original filing; the summary figures alone cannot establish which business "
        "segments or one-off items caused a change."
    )
    # Filing-specific editorial qualification; never carry this forward to a future quarter.
    if ticker == "AMZN" and period == "FY2026 Q2" and report["latest_end"] == "2026-06-30":
        caveat = (
            "Amazon reported $53.4bn of non-operating pre-tax other income in "
            "Q2 2026, primarily related to its Anthropic investments. Reported net "
            "income and EPS therefore do not represent operating-profit growth alone. "
            "See the linked Amazon 10-Q before interpreting the headline increase."
        )
    related_links = [
        {"ticker": t, "name": PRIORITY[t][0], "url": f"/stocks/{t.lower()}/"}
        for t in related if t in PRIORITY
    ]
    return {
        "title": title, "headline": headline, "description": description[:240],
        "name": name, "ticker": ticker, "period": period,
        "fiscal_display": fiscal["display"], "calendar_period": fiscal["month_year"],
        "period_subtitle": fiscal["subtitle"], "readable_end": fiscal["readable_end"],
        "calendar_year_differs": fiscal["is_cross_year"],
        "hub_period": f"{fiscal['display']}{fiscal['title_calendar']}",
        "latest_end": report["latest_end"], "modified": report.get("updated") or report.get("latest_filed") or report["latest_end"],
        "latest_figures": latest, "movements": movements, "narrative": narrative,
        "caveat": caveat, "related": related_links, "source": report["latest_source"],
        "is_fy": period.endswith(" FY"),
    }
