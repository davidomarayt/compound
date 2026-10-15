"""Search-first editorial presentation for twenty verified company earnings profiles.

This is intentionally a curated cohort, not a generator of extra quarterly URLs.
SEO titles only change when the underlying SEC-backed fiscal period changes.
All quantitative statements come from the verified company dashboard.
"""
from __future__ import annotations

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
    fiscal = (period.replace(" FY", " Full-Year") if period.endswith(" FY") else period)
    title = f"{name} ({ticker}) {fiscal} Earnings: Revenue & EPS | Compound"
    headline = f"{name} ({ticker}) {fiscal} Earnings Results"
    description = (
        f"{name} ({ticker}) {fiscal} results, period ended {report['latest_end']}: "
        f"revenue {latest['revenue']}, diluted EPS {latest['diluted_eps']}. "
        "SEC filings, year-on-year growth and fiscal-quarter trends."
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
        "latest_end": report["latest_end"], "modified": report.get("updated") or report.get("latest_filed") or report["latest_end"],
        "latest_figures": latest, "movements": movements, "narrative": narrative,
        "caveat": caveat, "related": related_links, "source": report["latest_source"],
        "is_fy": period.endswith(" FY"),
    }
