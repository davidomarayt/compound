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


# Company-specific diligence prompts: questions to verify in the cited 10-Q/10-K,
# not assertions about segment performance or unsourced figures.
INVESTOR_LENSES = {
    "AAPL": (("iPhone versus Services", "Compare hardware demand with recurring Services growth and gross margins."),
             ("Greater China and product mix", "Check geographic revenue and whether FX or mix changed the comparison."),
             ("Cash returns", "Contrast operating cash flow and repurchases with reported EPS growth.")),
    "MSFT": (("Azure and cloud capacity", "Separate Azure demand from AI infrastructure spending and capacity constraints."),
             ("Profit by segment", "Compare Intelligent Cloud margins with Productivity and More Personal Computing."),
             ("Cash conversion", "Check capital expenditure, depreciation and operating cash generation.")),
    "AMZN": (("AWS versus retail", "Compare AWS operating income with North American and international commerce."),
             ("Reported versus operating profit", "Reconcile other income, investment marks and tax with GAAP net income."),
             ("Free cash flow", "Review data-centre capital spending and cash generation separately from EPS.")),
    "GOOGL": (("Search versus Cloud", "Check Google Services advertising growth and Google Cloud profitability."),
              ("AI investment", "Compare capital expenditure with operating cash flow and depreciation."),
              ("Regulatory exposure", "Read litigation and antitrust contingencies before extrapolating margins.")),
    "META": (("Advertising yield", "Check impressions, price per ad and regional demand."),
             ("Reality Labs losses", "Separate core advertising income from Reality Labs operating losses."),
             ("AI investment", "Compare data-centre spending commitments with operating cash generation.")),
    "NVDA": (("Data Centre versus Gaming", "Identify which end markets contribute to revenue growth."),
             ("Gross margin and concentration", "Check product mix, supply constraints and customer concentration disclosures."),
             ("Cash and inventories", "Compare working-capital movements with reported revenue.")),
    "TSLA": (("Automotive profitability", "Separate vehicle margins from regulatory credits and other revenue."),
             ("Energy generation and storage", "Assess storage deployments and segment profitability."),
             ("Cash spending", "Review capital expenditure, inventory and operating cash flow.")),
    "AMD": (("Data Centre demand", "Contrast server and AI accelerator growth with client and gaming revenue."),
            ("Margins and mix", "Check product mix, gross margin and acquired-intangible amortisation."),
            ("Capacity and customers", "Examine supply commitments and concentration risks.")),
    "PLTR": (("US commercial adoption", "Separate US commercial growth from government and overseas contracts."),
             ("Contract economics", "Review remaining deal value, revenue recognition and customer concentration."),
             ("Dilution", "Check stock-based compensation and diluted share counts.")),
    "NFLX": (("Revenue drivers", "Separate membership, pricing, advertising and geographic mix."),
             ("Operating leverage", "Compare content amortisation and operating margin with revenue growth."),
             ("Free cash flow", "Review content cash spending and share repurchases against GAAP earnings.")),
    "ORCL": (("Cloud infrastructure", "Separate OCI growth from licence, support and other software revenue."),
             ("Backlog conversion", "Check remaining performance obligations and delivery timing."),
             ("Capital intensity", "Compare data-centre commitments, cash flow and financing needs.")),
    "CRM": (("Subscription growth", "Review constant-currency subscription revenue and business-line performance."),
            ("Remaining obligations", "Compare current RPO with recognised revenue growth."),
            ("Margins versus dilution", "Check restructuring, stock compensation and share repurchases.")),
    "UBER": (("Trips and gross bookings", "Contrast Mobility and Delivery volume with take rate and revenue."),
             ("Profit quality", "Separate core operating cash generation from investment revaluations."),
             ("Platform economics", "Check incentives, insurance expenses and regional profitability.")),
    "COIN": (("Trading activity", "Separate transaction fees from subscriptions and services revenue."),
             ("Crypto volatility", "Inspect fair-value movements and concentration in crypto assets."),
             ("Regulatory and custody risk", "Read custody disclosures, liabilities and regulatory contingencies.")),
    "HOOD": (("Trading versus interest income", "Review transaction-based revenue and net interest income separately."),
             ("Customer engagement", "Check funded customers, assets under custody and net deposits."),
             ("Crypto concentration", "Assess activity sensitivity to digital-asset prices and volumes.")),
    "LLY": (("Medicine-level growth", "Compare obesity and diabetes therapies with the rest of the portfolio."),
            ("Volume versus price", "Review realised pricing, rebates and manufacturing capacity."),
            ("Pipeline and cash", "Examine R&D costs, launch spending and supply investment.")),
    "WMT": (("Comparable sales", "Separate transaction growth, ticket size and international FX."),
            ("Ecommerce economics", "Compare ecommerce growth with fulfilment costs and operating margins."),
            ("Inventory", "Check stock turns and cash conversion as sales change.")),
    "COST": (("Membership economics", "Check fee income, renewal rates and warehouse openings."),
             ("Comparable sales", "Separate traffic, average transaction size and fuel/FX effects."),
             ("Retail margins", "Compare merchandise margin, labour costs and inventory.")),
    "ADBE": (("Digital Media ARR", "Review recurring subscription revenue, net new ARR and pricing."),
             ("AI monetisation", "Look for disclosed paid adoption rather than assuming usage equals revenue."),
             ("Revenue quality", "Compare cash flow, deferred revenue and remaining obligations.")),
    "DIS": (("Experiences versus entertainment", "Assess parks and cruises separately from studio results."),
            ("Streaming profitability", "Check direct-to-consumer operating income and content costs."),
            ("Cash needs", "Review parks capital spending and debt alongside earnings.")),
}


def _premium_dashboard(ticker: str, report: dict) -> dict:
    """Use only the latest SEC filing's same-period prior-year comparatives."""
    comparison = report.get("latest_comparison") or {}
    mapping = (("revenue", "Revenue"), ("net_income", "Net income"),
               ("diluted_eps", "Diluted EPS"))
    rows = []
    for key, label in mapping:
        pair = comparison.get(key)
        if not pair:
            continue
        current, prior = pair["current"], pair["prior"]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (current, prior)):
            continue
        scale = max(abs(current), abs(prior))
        rows.append({
            "key": key, "label": label,
            "current": pair["current_display"], "prior": pair["prior_display"],
            "current_width": round(100 * abs(current) / scale, 1) if scale else 0,
            "prior_width": round(100 * abs(prior) / scale, 1) if scale else 0,
            "current_negative": current < 0, "prior_negative": prior < 0,
            "growth": report.get("yoy", {}).get(key),
        })
    margin = report.get("margin_comparison")
    insights = []
    rev_growth = report.get("yoy", {}).get("revenue")
    eps_growth = report.get("yoy", {}).get("diluted_eps")
    if isinstance(rev_growth, (int, float)):
        direction = "higher" if rev_growth > 0 else "lower" if rev_growth < 0 else "unchanged"
        insights.append(f"Revenue was {abs(rev_growth):.1f}% {direction} than the same fiscal period a year earlier.")
    if margin and all(isinstance(margin.get(k), (int, float)) for k in ("current", "prior", "change_pp")):
        movement = margin["change_pp"]
        word = "widened" if movement > 0 else "narrowed" if movement < 0 else "was unchanged"
        suffix = f" by {abs(movement):.1f} percentage points" if movement else ""
        insights.append(
            f"GAAP net profit margin {word}{suffix}, from {margin['prior']:.1f}% to {margin['current']:.1f}%. "
            "Net margin can be affected by non-operating items and taxes."
        )
    if isinstance(rev_growth, (int, float)) and isinstance(eps_growth, (int, float)):
        gap = round(eps_growth - rev_growth, 1)
        if abs(gap) >= 5:
            comparison_word = "outpaced" if gap > 0 else "lagged"
            insights.append(
                f"Diluted EPS growth {comparison_word} revenue growth by {abs(gap):.1f} percentage points. "
                "Review share count, expenses and non-operating gains or losses before attributing the gap."
            )
    return {
        "rows": rows, "margin": margin, "insights": insights,
        "lenses": [{"title": title, "question": question}
                   for title, question in INVESTOR_LENSES[ticker]],
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
    premium = _premium_dashboard(ticker, report)
    return {
        "premium": premium,
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
