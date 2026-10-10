"""Source-bound, accessible HTML charts for automated earnings articles.

No stock photographs, image assets, JS chart libraries, or speculative metrics.
The historical series always shows the periods actually available from SEC XBRL.
"""
from __future__ import annotations

from datetime import date
from html import escape
import math
import re
from typing import Any

METRICS = (("revenue", "Revenue", "USD"),
           ("net_income", "Net income", "USD"),
           ("diluted_eps", "Diluted EPS", "USD/shares"))


def _money(amount: float, unit: str = "USD") -> str:
    prefix = "−" if amount < 0 else ""
    v = abs(amount)
    if unit == "USD/shares":
        return f"{prefix}${v:,.2f}"
    if v >= 1e12:
        return f"{prefix}${v/1e12:,.2f}tn"
    if v >= 1e9:
        return f"{prefix}${v/1e9:,.2f}bn"
    if v >= 1e6:
        return f"{prefix}${v/1e6:,.2f}m"
    return f"{prefix}${v:,.0f}"


def _finite_num(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Earnings dashboard requires sourced, finite numerical data")
    return float(value)


def _change(now: float, prior: float) -> tuple[str, str, str]:
    if prior <= 0:
        return ("Not comparable", "neutral", "Prior period ≤ 0")
    pct = (now / prior - 1) * 100
    if abs(pct) < .05:
        return ("0.0%", "neutral", "Little change")
    return (f"{'+' if pct > 0 else '−'}{abs(pct):.1f}%", "up" if pct > 0 else "down", "Year on year")


def _point_label(row: dict) -> str:
    label = str(row.get("label") or "").strip()
    if label:
        return label[:32]
    try:
        d = date.fromisoformat(str(row["end"]))
        return d.strftime("%b '%y")
    except (KeyError, ValueError):
        return "Reported period"


def _history(rows: object, now: float, prior: float, quarter: bool) -> list[dict]:
    if not isinstance(rows, list):
        rows = []
    valid = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            value = _finite_num(row["value"])
        except (KeyError, ValueError):
            continue
        period_id = str(row.get("end") or row.get("label") or "")
        if not period_id or period_id in seen:
            continue
        seen.add(period_id)
        valid.append({"value": value, "label": _point_label(row), "end": str(row.get("end") or "")})
    if valid:
        valid.sort(key=lambda r: (r["end"] or "z", r["label"]))
        return valid[-(8 if quarter else 4):]
    return [{"label":"Year earlier", "value":prior, "end":""},
            {"label":"Latest filing", "value":now, "end":""}]


def _chart_html(key: str, label: str, unit: str, history: list[dict], quarter: bool) -> str:
    if len(history) < 2:
        return ""
    values = [item["value"] for item in history]
    # Chart axes include zero for positive-only values, and include losses for
    # signed EPS/profit values rather than clipping negative numbers.
    lo = min(0.0, min(values))
    hi = max(0.0, max(values))
    if hi == lo:
        hi = lo + 1
    spread = hi - lo
    top, height = 42, 148
    left, width = 60, 615
    xs = [left + (width * i / max(1, len(values) - 1)) for i in range(len(values))]
    ys = [top + height - (v - lo) / spread * height for v in values]
    tick_values = [hi, (hi + lo) / 2, lo]
    grids = []
    for tick in tick_values:
        y = top + height - (tick - lo) / spread * height
        grids.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" stroke="#e6e0dd" stroke-width="1"/>')
        grids.append(f'<text x="{left-9}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#766b71">{escape(_money(tick,unit))}</text>')
    points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs,ys))
    # Keep x-axis legible on mobile; omit alternating intermediate labels.
    labels=[]
    for i, (x,row) in enumerate(zip(xs, history)):
        if len(history)>5 and i%2 and i != len(history)-1:
            continue
        labels.append(f'<text x="{x:.1f}" y="218" text-anchor="middle" font-size="11" fill="#71656b">{escape(row["label"])}</text>')
    dots=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 if i < len(xs)-1 else 6}" fill="{("#2e6359" if key=="revenue" else "#7a514d")}" stroke="white" stroke-width="2"/>' for i,(x,y) in enumerate(zip(xs,ys)))
    color="#2e6359" if key=="revenue" else "#7a514d"
    line=f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    description=f'{label}: {len(values)} SEC-backed comparative data points ({"quarterly" if quarter else "annual"} context); latest {history[-1]["label"]}, {_money(values[-1],unit)}.'
    rows=''.join(f'<tr><th scope="row">{escape(row["label"])}</th><td>{escape(_money(row["value"],unit))}</td></tr>' for row in history)
    return (f'<section class="earnings-trend" aria-labelledby="trend-{key}">'
            f'<div class="earnings-trend-header"><h3 id="trend-{key}">{escape(label)}</h3>'
            f'<span>{len(values)} reported periods</span></div>'
            f'<svg role="img" aria-label="{escape(description,quote=True)}" viewBox="0 0 720 238" '
            f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet" class="earnings-trend-plot">'
            +''.join(grids)+line+dots+''.join(labels)+'</svg>'
            f'<details class="earnings-trend-data"><summary>View underlying {escape(label.lower())} values</summary>'
            f'<table><thead><tr><th scope="col">Period</th><th scope="col">Reported value</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></details></section>')


def render_earnings_dashboard(snapshot: dict) -> str:
    """Render charts only from validated snapshots, never from guesses or estimates."""
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get("metrics"),dict):
        raise ValueError("Missing earnings financial data")
    metrics=snapshot["metrics"]
    quarter = str(snapshot.get("form") or "10-Q") == "10-Q"
    cards=[]; table=[]; charts=[]; numbers={}
    for key,label,unit in METRICS:
        datum=metrics.get(key)
        if not isinstance(datum,dict):
            raise ValueError(f"Earnings data missing {key}")
        current=_finite_num(datum.get("current"))
        prior=_finite_num(datum.get("prior"))
        if key=="revenue" and (current <= 0 or prior <= 0):
            raise ValueError("Revenue must be positive in both periods")
        change, status, note=_change(current,prior)
        if datum.get("reported_change") is not None:
            # Legacy reports contain rounded display amounts; preserve the
            # SEC-verified YoY percentage rather than recalculating from rounding.
            provided=str(datum["reported_change"]).strip().replace("-", "−")
            if not re.fullmatch(r"[+−]?\d+(?:\.\d+)?%", provided):
                raise ValueError("Invalid legacy year-on-year percentage")
            change=provided
            status="down" if provided.startswith("−") else "up" if provided.startswith("+") else "neutral"
        numbers[key]=(current,prior,change,status)
        cards.append(f'<div class="earnings-kpi earnings-kpi-{key}">'
          f'<div class="earnings-kpi-label">{escape(label)}</div>'
          f'<strong class="earnings-kpi-value">{escape(_money(current,unit))}</strong>'
          f'<div class="earnings-kpi-foot"><span class="earnings-change earnings-change-{status}">{escape(change)}</span>'
          f'<span class="earnings-kpi-prior">vs {escape(_money(prior,unit))} previous year</span></div></div>')
        table.append(f'<tr><th scope="row">{escape(label)}</th><td>{escape(_money(current,unit))}</td>'
                     f'<td>{escape(_money(prior,unit))}</td><td><span class="earnings-change earnings-change-{status}">{escape(change)}</span></td></tr>')
        series=_history(datum.get("history"),current,prior,quarter)
        charts.append(_chart_html(key,label,unit,series,quarter))
    rev,profit,eps=numbers["revenue"],numbers["net_income"],numbers["diluted_eps"]
    def verb(pair):return "rose" if pair[0]>pair[1] else "fell" if pair[0]<pair[1] else "was unchanged"
    # Avoid misleading "rose +X" or "fell -X" phrasing.
    headline=(f'Revenue {verb(rev)} to {_money(rev[0])} ({rev[2]} YoY). '
              f'Net income: {_money(profit[0])} ({profit[2]}); diluted EPS: {_money(eps[0],"USD/shares")} ({eps[2]}).')
    period=str(snapshot.get("period_label") or "SEC filing")
    summary=f'<p class="earnings-dashboard-takeaway"><strong>The headline:</strong> {escape(headline)}</p>'
    return (f'<section class="earnings-dashboard" aria-label="Financial results dashboard">'
            f'<p class="earnings-dashboard-eyebrow">SEC DATA SNAPSHOT · {escape(period)}</p>'
            +summary
            +'<div class="earnings-kpi-grid">'+''.join(cards)+'</div>'
            +'<div class="earnings-table-section"><div class="earnings-section-heading"><h2>Results at a glance</h2><p>US GAAP · matched reporting periods</p></div>'
            +'<div class="earnings-data-scroll"><table class="earnings-results-table"><thead><tr><th scope="col">Metric</th><th scope="col">Current</th><th scope="col">Year earlier</th><th scope="col">YoY</th></tr></thead><tbody>'
            +''.join(table)+'</tbody></table></div></div>'
            +'<div class="earnings-charts"><div class="earnings-section-heading"><h2>Reported trends</h2><p>Only periods confirmed in SEC data</p></div>'
            +'<div class="earnings-trend-grid">'+''.join(charts)+'</div>'
            +'<p class="earnings-dashboard-source">Trend points are SEC XBRL financial facts. Older reports may show only two matched annual-comparison points. Non-GAAP estimates and missing quarters are never interpolated. Values are rounded for display.</p>'
            +'</div></section>')


def from_existing_markdown(markdown: str, meta: dict) -> dict | None:
    """Back-compat: use only already published displayed values as rounded input.

    This does NOT invent 8-quarter history for pre-upgrade articles.
    """
    if "automated-earnings" not in (meta.get("tags") or []):
        return None
    metrics={}
    for key,label,unit in METRICS:
        prefix={"revenue": "Revenue (US GAAP)","net_income":"Net income (US GAAP)",
                "diluted_eps":"Diluted earnings per share (GAAP)"}[key]
        match=re.search(r"^\|\s*"+re.escape(prefix)+r"\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",markdown,re.M)
        if not match:
            return None
        def parse_money(text:str)->float:
            s=text.strip().replace(',','').replace('−','-')
            m=re.fullmatch(r'(-?)\$([\d.]+)(bn|m|tn)?',s)
            if not m:raise ValueError(f"Cannot parse sourced figure {text!r}")
            factor={None:1,"m":1e6,"bn":1e9,"tn":1e12}[m.group(3)]
            return float(m.group(1)+m.group(2))*factor
        pct=re.search(r"^\|\s*"+re.escape(prefix)+r"\s*\|\s*[^|]+\|\s*[^|]+\|\s*([+−-]?[\d.]+%)",markdown,re.M)
        metrics[key]={"current":parse_money(match[1]),"prior":parse_money(match[2]),
                      **({"reported_change":pct[1]} if pct else {})}
    period_match=re.search(r'FY\s+(20\d{2})\s+(Q[123]|full-year)',str(meta.get('title') or ''))
    label=f'FY {period_match[1]} {period_match[2]}' if period_match else 'SEC filing'
    return {"period_label":label,"form":"10-K" if 'full-year' in label else '10-Q',"metrics":metrics}