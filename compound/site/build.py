"""Static site generator. Reads content/**/*.md (YAML front matter + markdown) and renders public/.

URL structure: evergreen articles live under their pillar; timely news may use /news/<slug>/ via canonical_path.
Previews render to /preview/<token>/ with noindex and are never listed anywhere.
"""
from __future__ import annotations

import json
import math
import re
from html import escape as html_escape, unescape as html_unescape
from urllib.parse import urlparse
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compound.config import Settings

PILLARS = ["health", "wealth", "happiness"]
PILLAR_LABELS = {"wealth": "Wealth", "health": "Health", "happiness": "Happiness"}

TOOL_SPONSORSHIP_CATEGORY_ORDER = [
    "Mortgages & Home Buying",
    "Pensions & Investing",
    "Home Energy",
    "Tax & Take-Home Pay",
    "Loans & Debt",
    "EV & Motoring",
    "Health",
    "Family & Life Planning",
]
TOOL_SPONSORSHIP_CATEGORY_BLURBS = {
    "Mortgages & Home Buying": "Mortgage, affordability, deposits, switching and home-buying costs.",
    "Pensions & Investing": "Long-term saving, pensions, retirement planning, net worth and investing.",
    "Home Energy": "Solar, electricity, BER, retrofit and home-energy planning.",
    "Tax & Take-Home Pay": "Irish income tax, take-home pay, USC, PRSI and other common taxes.",
    "Loans & Debt": "Repayment planning, debt payoff strategies and borrowing costs.",
    "EV & Motoring": "Driving costs, EV charging and car-finance comparisons.",
    "Health": "Evidence-based calculators for everyday health decisions.",
    "Family & Life Planning": "Childcare, pregnancy and longer-term household planning.",
}


TOOL_PRIMARY_RESULTS = {
    "mortgage-calculator": "monthly",
    "mortgage-overpayment-calculator": "interest_saved",
    "mortgage-borrowing-calculator": "purchase_price",
    "house-deposit-calculator": "deposit",
    "stamp-duty-calculator": "duty",
    "local-property-tax-calculator": "lpt",
    "loan-repayment-calculator": "monthly",
    "savings-goal-calculator": "time",
    "net-worth-calculator": "net_worth",
    "regular-savings-calculator": "final",
    "pension-tax-relief-calculator": "relief",
    "capital-gains-tax-calculator": "tax",
    "vat-calculator": "vat",
    "inflation-calculator": "future_cost",
    "emergency-fund-calculator": "target",
    "salary-hourly-rate-calculator": "hourly",
    "fuel-cost-calculator": "cost",
    "ev-charging-cost-calculator": "cost",
    "electricity-cost-calculator": "monthly",
    "take-home-pay-calculator": "monthly_net",
    "income-tax-calculator": "final_tax",
    "usc-calculator": "usc",
    "prsi-calculator": "annual",
    "inheritance-tax-calculator": "cat",
    "rent-tax-credit-calculator": "credit",
    "help-to-buy-calculator": "claim",
    "first-home-scheme-calculator": "gap",
    "dirt-calculator": "net",
    "contractor-vs-salary-calculator": "net_difference",
    "investment-fee-calculator": "fee_gap",
    "fire-number-calculator": "target",
    "retirement-income-calculator": "monthly_income",
    "pension-projection-calculator": "projected",
    "rent-vs-buy-calculator": "difference",
    "mortgage-affordability-calculator": "indicative_price",
    "house-buying-costs-calculator": "total_upfront",
    "solar-payback-calculator": "payback",
    "ber-energy-cost-calculator": "saving",
    "solar-ev-battery-optimiser": "best_scenario",
    "whole-house-retrofit-planner": "payback",
    "myfuturefund-calculator": "total_2026",
    "childcare-return-to-work-calculator": "household_gain",
    "mortgage-switch-calculator": "lifetime_difference",
    "lifetime-cost-calculator": "lifetime_today_money",
    "nutrition-needs-calculator": "maintenance",
    "pregnancy-due-date-calculator": "due_date",
    "alcohol-units-calories-cost-calculator": "standard_drinks",
}
PILLAR_BLURBS = {
    "wealth": "Irish tax credits, grants, pensions and money, explained for the person paying.",
    "health": "What the evidence actually says, without the hype.",
    "happiness": "Slower pieces on living well: relationships, habits, attention, and what the research says.",
}
HERE = Path(__file__).parent
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


@dataclass
class Article:
    title: str
    slug: str
    pillar: str
    date: date
    summary: str
    body_html: str
    tags: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    figures: list[dict] = field(default_factory=list)
    email_cta: str = ""
    meta_description: str = ""
    charts: list[dict] = field(default_factory=list)
    pinned: bool = False
    path: Path | None = None
    image_path: str = ""
    image_alt: str = ""
    image_credit: str = ""
    image_source: str = ""
    series_id: str = ""
    series_order: int = 0
    publication_status: str = "published"
    canonical_path: str = ""
    seo_title: str = ""
    reviewed: date | None = None
    related_tools: list[str] = field(default_factory=list)

    @property
    def body_with_charts(self) -> str:
        return place_charts(self.body_html, self.charts, self.pillar)

    @property
    def description(self) -> str:
        """Search-result description: the planned one, else the summary trimmed to ~155 chars."""
        d = (self.meta_description or self.summary or "").strip()
        return d if len(d) <= 160 else d[:157].rsplit(" ", 1)[0] + "…"

    @property
    def url(self) -> str:
        return self.canonical_path or f"/{self.pillar}/{self.slug}/"

    @property
    def pillar_label(self) -> str:
        return PILLAR_LABELS.get(self.pillar, self.pillar.title())

    @property
    def reading_minutes(self) -> int:
        return max(1, math.ceil(len(re.sub(r"<[^>]+>", " ", self.body_html).split()) / 220))

    @property
    def image(self) -> str:
        return self.image_path


@dataclass
class Page:
    title: str
    slug: str
    body_html: str


def parse_markdown_file(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(raw)
    if not m:
        return {}, raw
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, raw[m.end():]


def render_markdown(text: str) -> str:
    return markdown.markdown(text, extensions=["extra", "sane_lists", "smarty"], output_format="html5")


def render_tool_guide(text: str) -> tuple[str, list[dict]]:
    """Render calculator guidance with stable H2 anchors for a compact on-page contents nav."""
    html = render_markdown(text)
    toc: list[dict] = []
    used: dict[str, int] = {}

    def anchor_heading(match: re.Match) -> str:
        heading_html = match.group(1)
        title = html_unescape(re.sub(r"<[^>]+>", "", heading_html)).strip()
        base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
        used[base] = used.get(base, 0) + 1
        ident = base if used[base] == 1 else f"{base}-{used[base]}"
        toc.append({"id": ident, "title": title})
        return f'<h2 id="{ident}">{heading_html}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", anchor_heading, html, flags=re.DOTALL)
    return html, toc


def extract_tool_faq(text: str) -> list[dict]:
    """Extract displayed FAQ questions and plain-text answers from a calculator guide."""
    match = re.search(
        r"^##\s+Frequently asked questions\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return []
    section = match.group(1)
    parts = re.split(r"^###\s+", section, flags=re.MULTILINE)
    faq = []
    for part in parts[1:]:
        lines = part.strip().splitlines()
        if not lines:
            continue
        question = lines[0].strip()
        answer_md = "\n".join(lines[1:]).strip()
        if not question or not answer_md:
            continue
        answer_html = render_markdown(answer_md)
        answer = " ".join(html_unescape(re.sub(r"<[^>]+>", " ", answer_html)).split())
        if answer:
            faq.append({"question": question, "answer": answer})
    return faq[:10]


# --- charts: single-series inline SVG built only from verified figures ---------------------
CHART_W = 640
CHART_PLACEHOLDER = re.compile(r"<p>\s*\[chart:(\d+)\]\s*</p>|\[chart:(\d+)\]")


def _nice_max(v: float) -> float:
    if v <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return m * mag
    return 10 * mag


def _fmt(v: float) -> str:
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}"


def chart_svg(chart: dict, pillar: str) -> str:
    """Bar (horizontal) or line chart as inline SVG. One series in the pillar colour; text in ink
    tokens; hairline grid; value labelled selectively; a <title> per mark for hover."""
    items = chart.get("items") or []
    kind = chart.get("kind", "bar")
    unit = html_escape(chart.get("unit") or "")
    color = f"var(--{pillar})"
    if kind == "line":
        return _line_svg(items, color, unit)
    return _bar_svg(items, color, unit)


def _bar_svg(items: list[dict], color: str, unit: str) -> str:
    row, bar_h, label_w, pad = 34, 20, 170, 8
    vmax = _nice_max(max(float(i["value"]) for i in items))
    plot_w = CHART_W - label_w - 90
    h = row * len(items) + 12
    top = max(range(len(items)), key=lambda k: float(items[k]["value"]))
    out = [f'<svg class="chart-svg" viewBox="0 0 {CHART_W} {h}" width="100%" role="img" aria-hidden="true">']
    for i, it in enumerate(items):
        y = i * row + 6
        w = max(2.0, plot_w * float(it["value"]) / vmax)
        x0 = label_w
        label = html_escape(str(it["label"]))
        text = html_escape(str(it["text"]))
        out.append(f'<text x="{label_w - pad}" y="{y + bar_h / 2 + 4}" text-anchor="end" class="chart-label">{label}</text>')
        # square at the baseline, 4px rounded data-end
        path = f"M{x0},{y} h{w - 4:.1f} a4,4 0 0 1 4,4 v{bar_h - 8} a4,4 0 0 1 -4,4 H{x0} z"
        out.append(f'<path d="{path}" fill="{color}"><title>{label}: {text}</title></path>')
        cls = "chart-value" + (" chart-value-strong" if i == top else "")
        out.append(f'<text x="{x0 + w + pad}" y="{y + bar_h / 2 + 4}" class="{cls}">{text}</text>')
    out.append("</svg>")
    return "".join(out)


def _line_svg(items: list[dict], color: str, unit: str) -> str:
    w, h, left, right, top, bottom = CHART_W, 260, 56, 24, 18, 40
    vals = [float(i["value"]) for i in items]
    vmax = _nice_max(max(vals))
    vmin = 0.0 if min(vals) >= 0 else min(vals)
    n = len(items)
    px = lambda k: left + (w - left - right) * (k / max(1, n - 1))
    py = lambda v: top + (h - top - bottom) * (1 - (v - vmin) / (vmax - vmin or 1))
    out = [f'<svg class="chart-svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-hidden="true">']
    for g in range(5):  # hairline grid with clean ticks
        v = vmin + (vmax - vmin) * g / 4
        y = py(v)
        out.append(f'<line x1="{left}" x2="{w - right}" y1="{y:.1f}" y2="{y:.1f}" class="chart-grid"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" class="chart-tick">{_fmt(v)}</text>')
    pts = " ".join(f"{px(k):.1f},{py(v):.1f}" for k, v in enumerate(vals))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    for k, it in enumerate(items):
        label = html_escape(str(it["label"]))
        text = html_escape(str(it["text"]))
        out.append(f'<circle cx="{px(k):.1f}" cy="{py(vals[k]):.1f}" r="4" fill="{color}" stroke="var(--surface)" stroke-width="2"><title>{label}: {text}</title></circle>')
        out.append(f'<text x="{px(k):.1f}" y="{h - 14}" text-anchor="middle" class="chart-tick">{label}</text>')
    last = items[-1]
    out.append(f'<text x="{px(n - 1) - 6:.1f}" y="{py(vals[-1]) - 10:.1f}" text-anchor="end" class="chart-value chart-value-strong">{html_escape(str(last["text"]))}</text>')
    if unit:
        out.append(f'<text x="{left - 8}" y="{top - 6}" text-anchor="end" class="chart-tick">{unit}</text>')
    out.append("</svg>")
    return "".join(out)


def chart_figure(chart: dict, pillar: str) -> str:
    """Figure with the SVG, a plain table for screen readers and print, caption and source."""
    title = html_escape(chart.get("title") or "")
    caption = html_escape(chart.get("caption") or "")
    src = html_escape(chart.get("source_url") or "")
    unit = html_escape(chart.get("unit") or "")
    rows = "".join(f"<tr><th scope=\"row\">{html_escape(str(i['label']))}</th><td>{html_escape(str(i['text']))}</td></tr>" for i in chart.get("items") or [])
    return (
        f'<figure class="chart chart-{html_escape(chart.get("kind", "bar"))}">'
        f'<figcaption class="chart-title">{title}{f" <span class=chart-unit>({unit})</span>" if unit else ""}</figcaption>'
        f'<div class="chart-scroll">{chart_svg(chart, pillar)}</div>'
        f'<table class="chart-table"><caption class="sr-only">{title}</caption><tbody>{rows}</tbody></table>'
        f'<p class="chart-note">{caption}{" " if caption else ""}<a href="{src}" rel="noopener">Source</a></p>'
        f"</figure>"
    )


def place_charts(body_html: str, charts: list[dict], pillar: str) -> str:
    """Replace [chart:N] placeholders with rendered charts; append any the writer did not place."""
    if not charts:
        return CHART_PLACEHOLDER.sub("", body_html)
    used: set[int] = set()

    def sub(m):
        n = int(m.group(1) or m.group(2))
        if 1 <= n <= len(charts) and n not in used:
            used.add(n)
            return chart_figure(charts[n - 1], pillar)
        return ""

    out = CHART_PLACEHOLDER.sub(sub, body_html)
    for n in range(1, len(charts) + 1):
        if n not in used:
            out += chart_figure(charts[n - 1], pillar)
    return out


def _as_date(v) -> date:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str) and v:
        return datetime.fromisoformat(v[:19]).date()
    return date.today()


def article_from_file(path: Path, *, include_drafts: bool = False) -> Article | None:
    meta, body = parse_markdown_file(path)
    status = str(meta.get("publication_status") or ("draft" if meta.get("draft") else "published"))
    if not meta.get("title") or (not include_drafts and (meta.get("draft") or status != "published")):
        return None
    if meta.get("draft"):
        status = "draft"
    canonical_path = str(meta.get("canonical_path") or "")
    if canonical_path and not re.fullmatch(r"/(?:[a-z0-9]+(?:-[a-z0-9]+)*/)+", canonical_path):
        raise ValueError(f"Invalid canonical path in {path}")
    if meta.get("series_id") and status == "published" and not meta.get("date"):
        raise ValueError(f"Set the actual publication date before publishing {path}")
    pillar = str(meta.get("pillar") or path.parent.name)
    if pillar not in PILLARS:
        return None
    return Article(
        title=str(meta["title"]),
        slug=str(meta.get("slug") or path.stem),
        pillar=pillar,
        date=_as_date(meta.get("date") or meta.get("reviewed")),
        summary=str(meta.get("summary") or ""),
        body_html=render_markdown(body),
        tags=[str(t) for t in (meta.get("tags") or [])],
        sources=list(meta.get("sources") or []),
        figures=list(meta.get("figures") or []),
        email_cta=str(meta.get("email_cta") or ""),
        meta_description=str(meta.get("meta_description") or ""),
        charts=list(meta.get("charts") or []),
        pinned=bool(meta.get("pinned")),
        path=path,
        image_path=str(meta.get("image") or ""),
        image_alt=str(meta.get("image_alt") or ""),
        image_credit=str(meta.get("image_credit") or ""),
        image_source=str(meta.get("image_source") or ""),
        series_id=str(meta.get("series_id") or ""),
        series_order=int(meta.get("series_order") or 0),
        publication_status=status,
        canonical_path=canonical_path,
        seo_title=str(meta.get("seo_title") or ""),
        reviewed=_as_date(meta["reviewed"]) if meta.get("reviewed") else None,
        related_tools=[str(t) for t in (meta.get("related_tools") or [])],
    )


def load_articles(content_dir: Path) -> list[Article]:
    arts: list[Article] = []
    for pillar in PILLARS:
        d = content_dir / pillar
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            a = article_from_file(p)
            if a:
                arts.append(a)
    arts.sort(key=lambda a: (a.date, a.slug), reverse=True)
    return arts


def load_pages(content_dir: Path) -> list[Page]:
    pages: list[Page] = []
    d = content_dir / "pages"
    if not d.exists():
        return pages
    for p in sorted(d.glob("*.md")):
        meta, body = parse_markdown_file(p)
        pages.append(Page(title=str(meta.get("title") or p.stem.title()), slug=p.stem, body_html=render_markdown(body)))
    return pages


def load_tools(content_dir: Path) -> list[dict]:
    """Load the scalable calculator catalogue from content/tools.yml."""
    path = content_dir / "tools.yml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = []
    seen = set()
    for raw in data.get("tools") or []:
        tool = dict(raw)
        slug = str(tool.get("slug") or "").strip()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid tool slug: {slug!r}")
        if slug in seen:
            raise ValueError(f"Duplicate tool slug: {slug}")
        seen.add(slug)
        if not tool.get("title") or not tool.get("formula"):
            raise ValueError(f"Tool {slug} needs title and formula")
        tool["slug"] = slug
        tool["url"] = f"/{slug}/"
        guide_path = content_dir / "tool-guides" / f"{slug}.md"
        if guide_path.is_file():
            tool["guide"] = guide_path.read_text(encoding="utf-8")
        tool["guide_html"], tool["guide_toc"] = render_tool_guide(str(tool.get("guide") or ""))
        tool["faq"] = extract_tool_faq(str(tool.get("guide") or ""))
        tool["fields"] = list(tool.get("fields") or [])
        tool["results"] = list(tool.get("results") or [])
        tool["sources"] = list(tool.get("sources") or [])
        tool["primary_result"] = TOOL_PRIMARY_RESULTS.get(slug, (tool["results"][0]["id"] if tool["results"] else ""))
        source_section = str(tool.get("guide") or "").split("### Useful sources", 1)
        if len(source_section) == 2:
            seen_urls = {str(source.get("url") or "") for source in tool["sources"]}
            for title, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", source_section[1]):
                if url not in seen_urls:
                    tool["sources"].append({"title": title.strip(), "url": url.strip()})
                    seen_urls.add(url)
        items.append(tool)
    return items


def tool_catalogue(content_dir: Path, tools: list[dict]) -> dict[str, dict]:
    """All linkable tools, including the two bespoke legacy calculator pages."""
    items = {tool["slug"]: tool for tool in tools}
    if (content_dir / "compound-calculator-guide.md").is_file():
        items["compound-interest-calculator"] = {
            "slug": "compound-interest-calculator",
            "title": "Compound Interest Calculator Ireland",
            "url": "/compound-interest-calculator/",
            "category": "Pensions & Investing",
            "summary": "Model contributions, growth, inflation, fees and long-term savings scenarios.",
        }
    if (content_dir / "bmi-guide.md").is_file():
        items["bmi-calculator"] = {
            "slug": "bmi-calculator",
            "title": "BMI Calculator Ireland",
            "url": "/bmi-calculator/",
            "category": "Health",
            "summary": "Calculate adult BMI, explore waist-to-height ratio and put the result in context.",
        }
    return items


def linked_articles(tool_slug: str, articles: list[Article], n: int = 4) -> list[Article]:
    """Articles that explicitly nominate this tool, newest first."""
    matches = [a for a in articles if tool_slug in a.related_tools]
    matches.sort(key=lambda a: (a.date, a.slug), reverse=True)
    return matches[:n]


def insert_article_tool_cta(body: str, tool: dict, env: Environment, pillar: str) -> str:
    """Insert one contextual tool CTA into an article without requiring manual HTML.

    Writers can place it precisely with a standalone [tool-cta] paragraph. Otherwise
    it is inserted near the middle of the prose at a paragraph boundary. The full
    related-tools module still appears after the article.
    """
    if not body or not tool:
        return body
    banner = env.get_template("_article_tool_banner.html").render(tool=tool, pillar=pillar)
    placeholder = re.compile(r"<p>\s*\[tool-cta\]\s*</p>", re.IGNORECASE)
    if placeholder.search(body):
        return placeholder.sub(banner, body, count=1)

    paragraph_ends = [m.end() for m in re.finditer(r"</p>", body, re.IGNORECASE)]
    if len(paragraph_ends) < 4:
        return body + banner

    target = len(body) * 0.46
    candidates = [pos for pos in paragraph_ends if len(body) * 0.30 <= pos <= len(body) * 0.68]
    insert_at = min(candidates or paragraph_ends, key=lambda pos: abs(pos - target))
    return body[:insert_at] + banner + body[insert_at:]


def long_date(d: date) -> str:
    """'3 September 2026' without relying on strftime('%-d'), which Windows rejects."""
    return f"{d.day} {d.strftime('%B %Y')}"


def article_jsonld(a: Article, site_url: str) -> str:
    """schema.org Article markup for search engines."""
    data = {
        "@context": "https://schema.org", "@type": "Article", "headline": a.title, "description": a.description,
        "datePublished": a.date.isoformat(), "dateModified": a.date.isoformat(),
        "author": {"@type": "Person", "name": "David", "url": f"{site_url}/about/"},
        "publisher": {"@type": "Organization", "name": "Compound", "url": site_url},
        "mainEntityOfPage": f"{site_url}{a.url}", "image": f"{site_url}{a.image}" if a.image else None,
        "articleSection": (f"News / {PILLAR_LABELS.get(a.pillar, a.pillar)}" if "news" in a.tags else PILLAR_LABELS.get(a.pillar, a.pillar)),
        "keywords": ", ".join(a.tags),
        "citation": [s.get("url") for s in a.sources if s.get("url")],
    }
    if a.publication_status != "published":
        data.pop("datePublished", None)
        data["creativeWorkStatus"] = "Draft"
    if a.reviewed:
        data["dateModified"] = a.reviewed.isoformat()
    if a.series_id:
        data["isPartOf"] = {"@type": "CreativeWorkSeries", "name": "Live to 100"}
    return json.dumps(data, ensure_ascii=False)


def article_template(article: Article) -> str:
    return "series_article.html" if article.series_id == "live-to-100" else "article.html"


def series_context(article: Article, content_dir: Path) -> dict:
    """Series identity is independent of pillars. Only published articles receive links."""
    if not article.series_id:
        return {}
    if not re.fullmatch(r"[a-z0-9-]+", article.series_id):
        raise ValueError("Invalid series identifier")
    path = content_dir / "series" / f"{article.series_id}.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    published = {(a.series_id, a.series_order): a for a in load_articles(content_dir)}
    parts = []
    for part in data["parts"]:
        item = dict(part)
        item["current"] = int(item["order"]) == article.series_order
        live_article = published.get((article.series_id, int(item["order"])))
        item["url"] = live_article.url if live_article and item.get("status") == "published" else ""
        parts.append(item)
    return {"id": data["id"], "title": data["title"], "parts": parts}


def article_context(env: Environment, settings: Settings, article: Article, preview: bool) -> dict:
    body = article.body_with_charts
    series = series_context(article, settings.content_dir)
    if article.series_id == "live-to-100":
        for block in ("figures", "horizon", "timeline"):
            fragment = env.get_template(f"_live100_{block}.html").render()
            body = body.replace(f"<p>[live100:{block}]</p>", fragment)
    crumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": settings.site_base_url + "/"},
        {"@type": "ListItem", "position": 2, "name": "Live to 100", "item": settings.site_base_url + "/live-to-100/"},
    ]
    if article.series_order > 1:
        crumb_items.append({"@type": "ListItem", "position": 3, "name": article.title,
                            "item": settings.site_base_url + article.url})
    toc = [{"id": ident, "title": html_unescape(re.sub(r"<[^>]+>", "", heading))}
           for ident, heading in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.DOTALL)]
    breadcrumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumb_items
    }
    return dict(article=article, preview=preview, series=series, article_body=body, article_toc=toc,
                title=article.seo_title or article.title,
                article_jsonld=article_jsonld(article, settings.site_base_url),
                breadcrumb_jsonld=json.dumps(breadcrumbs, ensure_ascii=False))


def load_site_config(content_dir: Path) -> dict:
    """content/site.yml: committed, non-secret site settings (ads). Missing file = defaults."""
    f = content_dir / "site.yml"
    data = {}
    if f.exists():
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    ads = data.get("adsense") or {}
    analytics = data.get("analytics") or {}
    slots = ads.get("slots") or {}
    return {
        "adsense": {
            "client": str(ads.get("client") or "").strip(),
            "slots": {k: str(slots.get(k) or "").strip() for k in ("article_top", "article_bottom", "feed")},
        },
        "analytics": {"measurement_id": str(analytics.get("measurement_id") or "").strip()},
        "email_form_action": str(data.get("email_form_action") or "").strip(),
    }


def _env(settings: Settings) -> Environment:
    env = Environment(loader=FileSystemLoader(str(HERE / "templates")), autoescape=select_autoescape(["html"]))
    env.filters["long_date"] = long_date
    site_cfg = load_site_config(settings.content_dir)
    env.globals.update(adsense=site_cfg["adsense"])
    env.globals.update(analytics=site_cfg["analytics"])
    env.globals.update(
        site_url=settings.site_base_url,
        email_form_action=site_cfg["email_form_action"] or settings.email_form_action,
        pillars=PILLARS,
        pillar_labels=PILLAR_LABELS,
        pillar_blurbs=PILLAR_BLURBS,
        year=date.today().year,
    )
    return env


def _write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def related(article: Article, all_articles: list[Article], n: int = 3) -> list[Article]:
    tags = set(article.tags)
    scored = []
    for a in all_articles:
        if a.slug == article.slug and a.pillar == article.pillar:
            continue
        score = len(tags & set(a.tags)) * 2 + (1 if a.pillar == article.pillar else 0)
        if score:
            scored.append((score, a.date, a))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [a for _, _, a in scored[:n]]


def build_site(settings: Settings) -> dict:
    """Render the whole site. Returns a small stats dict. Preview pages are left untouched."""
    env = _env(settings)
    out = settings.public_dir
    articles = load_articles(settings.content_dir)
    pages = load_pages(settings.content_dir)
    tools = load_tools(settings.content_dir)
    tools_by_slug = tool_catalogue(settings.content_dir, tools)
    for article in articles:
        if len(article.related_tools) > 4:
            raise ValueError(f"Keep related_tools to four or fewer on {article.slug}")
        if tools_by_slug:
            unknown = [slug for slug in article.related_tools if slug not in tools_by_slug]
            if unknown:
                raise ValueError(f"Unknown related_tools on {article.slug}: {unknown}")
    reserved = {"/", "/search/", "/tools/", "/news/", "/compound-interest-calculator/", "/bmi-calculator/"}
    reserved.update(tool["url"] for tool in tools)
    reserved.update(f"/{p}/" for p in PILLARS)
    reserved.update(f"/{pg.slug}/" for pg in pages)
    seen_urls = set(reserved)
    for article in articles:
        if article.url in seen_urls or article.url.startswith(("/preview/", "/static/", "/tag/")):
            raise ValueError(f"Article route conflicts with another page: {article.url}")
        seen_urls.add(article.url)
    image_owners = {}
    for article in articles:
        is_news = "news" in article.tags or article.url.startswith("/news/")
        if is_news and not article.image_path:
            raise ValueError(f"Published News article needs an image: {article.slug}")
        if not article.image_path:
            continue  # Evergreen articles may render without a generic cover.
        if not article.image_alt:
            raise ValueError(f"Add cover alt text for {article.slug}")
        if article.image in image_owners:
            raise ValueError(f"Cover image reused by {article.slug} and {image_owners[article.image]}")
        image_owners[article.image] = article.slug
        if not article.image.startswith("/static/images/") or not (HERE / article.image.lstrip("/")).is_file():
            raise ValueError(f"Missing local cover image for {article.slug}")

    # Wipe rendered output except previews (they belong to the pending queue, not the content dir).
    if out.exists():
        for child in out.iterdir():
            if child.name == "preview":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HERE / "static", out / "static", dirs_exist_ok=True)

    news_articles = [a for a in articles if "news" in a.tags or a.url.startswith("/news/")]
    news_articles.sort(key=lambda a: (a.date, a.slug), reverse=True)
    by_pillar = {p: [a for a in articles if a.pillar == p and a not in news_articles] for p in PILLARS}
    columns = {}
    for p in PILLARS:
        arts = by_pillar[p]
        pinned = next((a for a in arts if a.pinned), None)
        feed = [a for a in arts if a is not pinned]
        columns[p] = {"pinned": pinned, "feed": feed[:8]}

    # Balance the first row across the three pillars, retaining date order within each.
    home_articles = []
    for i in range(max((len(items) for items in by_pillar.values()), default=0)):
        for p in PILLARS:
            if i < len(by_pillar[p]):
                home_articles.append(by_pillar[p][i])
    preferred_home_tools = [
        "compound-interest-calculator",
        "solar-payback-calculator",
        "mortgage-overpayment-calculator",
        "savings-goal-calculator",
        "bmi-calculator",
    ]
    home_tools = [tools_by_slug[s] for s in preferred_home_tools if s in tools_by_slug]
    _write(out / "index.html", env.get_template("home.html").render(
        columns=columns, articles=articles, home_articles=home_articles,
        news_articles=news_articles[:4], home_tools=home_tools, title="Compound"))

    _write(out / "news" / "index.html", env.get_template("news.html").render(
        articles=news_articles, title="Latest News for Ireland", news=True, ads_allowed=False))

    for p in PILLARS:
        _write(out / p / "index.html", env.get_template("pillar.html").render(pillar=p, articles=by_pillar[p], title=PILLAR_LABELS[p]))

    tag_map: dict[str, list[Article]] = {}
    for a in articles:
        linked_tools = [tools_by_slug[s] for s in a.related_tools if s in tools_by_slug]
        context = article_context(env, settings, a, False)
        if linked_tools:
            context["article_body"] = insert_article_tool_cta(
                context["article_body"], linked_tools[0], env, a.pillar
            )
        _write(out / a.url.strip("/") / "index.html",
               env.get_template(article_template(a)).render(
                   **context, related=related(a, articles), linked_tools=linked_tools))
        for t in a.tags:
            tag_map.setdefault(t, []).append(a)
    for t, arts in tag_map.items():
        _write(out / "tag" / t / "index.html", env.get_template("tag.html").render(tag=t, articles=arts, title=f"#{t}", ads_allowed=False))

    for pg in pages:
        _write(out / pg.slug / "index.html", env.get_template("page.html").render(page=pg, title=pg.title))

    if tools:
        hub_tools = list(tools)
        if (settings.content_dir / "compound-calculator-guide.md").is_file():
            hub_tools.append({
                "slug": "compound-interest-calculator",
                "title": "Compound Interest Calculator Ireland",
                "url": "/compound-interest-calculator/",
                "category": "Pensions & Investing",
                "summary": "Model contributions, growth, inflation, fees and long-term savings scenarios.",
            })
        if (settings.content_dir / "bmi-guide.md").is_file():
            hub_tools.append({
                "slug": "bmi-calculator",
                "title": "BMI Calculator Ireland",
                "url": "/bmi-calculator/",
                "category": "Health",
                "summary": "Calculate adult BMI, explore waist-to-height ratio and put the result in context.",
            })

        grouped_tools = {}
        for category in TOOL_SPONSORSHIP_CATEGORY_ORDER:
            grouped_tools[category] = [tool for tool in hub_tools if tool.get("category") == category]
        for tool in hub_tools:
            category = str(tool.get("category") or "Other")
            if category not in grouped_tools:
                grouped_tools.setdefault(category, []).append(tool)

        _write(out / "tools" / "index.html", env.get_template("tools.html").render(
            title="Free Calculators & Tools for Ireland", grouped_tools=grouped_tools, tools=hub_tools,
            category_blurbs=TOOL_SPONSORSHIP_CATEGORY_BLURBS,
            pillar="wealth", tools_page=True))
        for tool in tools:
            related_tools = [t for t in tools if t["slug"] != tool["slug"] and t.get("category") == tool.get("category")][:3]
            if len(related_tools) < 3:
                related_tools += [t for t in tools if t["slug"] != tool["slug"] and t not in related_tools][:3-len(related_tools)]
            app_category = (
                "HealthApplication" if tool.get("category") == "Health"
                else "UtilitiesApplication" if tool.get("category") in {"Home Energy", "EV & Motoring"}
                else "LifestyleApplication" if tool.get("category") == "Family & Life Planning"
                else "FinanceApplication"
            )
            app_data = {
                "@type": "WebApplication",
                "name": tool["title"], "url": settings.site_base_url + tool["url"],
                "description": tool.get("meta_description") or tool.get("summary") or "",
                "applicationCategory": app_category, "operatingSystem": "Any",
                "browserRequirements": "Requires JavaScript", "inLanguage": "en-IE",
                "isAccessibleForFree": True,
                "dateModified": str(tool.get("updated") or ""),
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
                "publisher": {"@type": "Organization", "name": "Compound", "url": settings.site_base_url},
                "citation": [source.get("url") for source in tool.get("sources", []) if source.get("url")],
            }
            graph = [
                app_data,
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": settings.site_base_url + "/"},
                        {"@type": "ListItem", "position": 2, "name": "Tools", "item": settings.site_base_url + "/tools/"},
                        {"@type": "ListItem", "position": 3, "name": tool["title"], "item": settings.site_base_url + tool["url"]},
                    ],
                },
            ]
            if tool.get("faq"):
                graph.append({
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": item["question"],
                            "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
                        }
                        for item in tool["faq"]
                    ],
                })
            tool_jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
            tool_template = "debt_repayment.html" if tool["slug"] == "debt-repayment-calculator" else "tool.html"
            _write(out / tool["slug"] / "index.html", env.get_template(tool_template).render(
                title=tool["title"], tool=tool, related_tools=related_tools,
                related_articles=linked_articles(tool["slug"], articles),
                tool_jsonld=tool_jsonld, pillar="wealth", tools_page=True))

    calculator_path = "/compound-interest-calculator/"
    has_calculator = (settings.content_dir / "compound-calculator-guide.md").is_file()
    if has_calculator:
        calculator_guide = render_markdown((settings.content_dir / "compound-calculator-guide.md").read_text(encoding="utf-8"))
        _write(out / "compound-interest-calculator" / "index.html", env.get_template("calculator.html").render(
            title="Compound Interest Calculator Ireland", pillar="wealth", tools_page=True, ads_allowed=False,
            related_articles=linked_articles("compound-interest-calculator", articles),
            calculator_guide=calculator_guide.replace("<table>", '<div class="guide-table-scroll"><table>').replace("</table>", "</table></div>")))

    bmi_path = "/bmi-calculator/"
    has_bmi = (settings.content_dir / "bmi-guide.md").is_file()
    if has_bmi:
        bmi_guide = render_markdown((settings.content_dir / "bmi-guide.md").read_text(encoding="utf-8"))
        _write(out / "bmi-calculator" / "index.html", env.get_template("bmi.html").render(
            title="BMI Calculator Ireland", pillar="health", tools_page=True, ads_allowed=False,
            related_articles=linked_articles("bmi-calculator", articles),
            bmi_guide=bmi_guide.replace("<table>", '<div class="bmi-table"><table>').replace("</table>", "</table></div>")))

    index = [
        {"title": a.title, "url": a.url, "pillar": ("News" if "news" in a.tags else a.pillar_label), "date": a.date.isoformat(),
         "summary": a.summary, "tags": a.tags, "description": a.description,
         "image": a.image, "reading_minutes": a.reading_minutes, "date_label": long_date(a.date)}
        for a in articles
    ]
    if has_calculator:
        index.insert(0, {"title": "Compound Interest Calculator Ireland", "url": calculator_path,
                        "pillar": "Wealth", "date": "2026-09-15", "summary": "Explore growth, compare plans, set goals and model inflation, fees and supported Irish tax.",
                        "tags": ["saving", "investing", "calculator"], "description": "Free interactive compound interest calculator for Ireland.",
                        "image": "", "reading_minutes": 10, "date_label": "15 September 2026"})
    if has_bmi:
        index.insert(0, {"title": "BMI Calculator Ireland", "url": bmi_path,
                         "pillar": "Health", "date": "2026-09-15", "summary": "Calculate adult BMI in kg or stones, explore waist-to-height ratio and read sourced Irish guidance.",
                         "tags": ["BMI", "health", "calculator", "weight"], "description": "Free BMI calculator with HSE guidance for Ireland.",
                         "image": "", "reading_minutes": 7, "date_label": "15 September 2026"})
    for tool in reversed(tools):
        index.insert(0, {"title": tool["title"], "url": tool["url"], "pillar": "Tools",
                         "date": str(tool.get("updated") or "2026-09-21"), "summary": str(tool.get("summary") or ""),
                         "tags": ["calculator", str(tool.get("category") or "").lower().replace(" ", "-")],
                         "description": str(tool.get("meta_description") or tool.get("summary") or ""),
                         "image": "", "reading_minutes": 3, "date_label": "21 September 2026"})
    _write(out / "search.json", json.dumps(index, ensure_ascii=False))
    _write(out / "search" / "index.html", env.get_template("search.html").render(title="Search", search_index=index, ads_allowed=False))
    _write(out / "feed.xml", env.get_template("feed.xml").render(articles=articles[:30]))
    _write(out / "robots.txt", f"User-agent: *\nDisallow: /preview/\nSitemap: {settings.site_base_url}/sitemap.xml\n")
    host = urlparse(settings.site_base_url).hostname or ""
    if host and host not in {"localhost", "127.0.0.1"}:
        _write(out / "CNAME", host + "\n")  # custom domain for GitHub Pages; harmless elsewhere
    _write(out / ".nojekyll", "")  # tell GitHub Pages to serve files as-is
    client = load_site_config(settings.content_dir)["adsense"]["client"]
    if client.startswith("ca-pub-"):
        # AdSense checks this file to confirm the site is allowed to show your ads.
        _write(out / "ads.txt", f"google.com, {client.removeprefix('ca-')}, DIRECT, f08c47fec0942fa0\n")
    urls = ([settings.site_base_url + "/"]
            + [settings.site_base_url + "/news/"]
            + ([settings.site_base_url + "/tools/"] if tools else [])
            + [settings.site_base_url + tool["url"] for tool in tools]
            + ([settings.site_base_url + bmi_path] if has_bmi else [])
            + ([settings.site_base_url + calculator_path] if has_calculator else [])
            + [settings.site_base_url + f"/{p}/" for p in PILLARS]
            + [settings.site_base_url + a.url for a in articles]
            + [settings.site_base_url + f"/{pg.slug}/" for pg in pages])
    _write(out / "sitemap.xml", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
           + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    return {"articles": len(articles), "tags": len(tag_map), "pages": len(pages), "tools": len(tools)}


def render_preview(settings: Settings, token: str, article: Article) -> Path:
    """Render one draft to /preview/<token>/index.html. Not linked from anywhere, noindex."""
    env = _env(settings)
    out = settings.public_dir / "preview" / token / "index.html"
    if not (settings.public_dir / "static").exists():
        shutil.copytree(HERE / "static", settings.public_dir / "static", dirs_exist_ok=True)
    catalogue = tool_catalogue(settings.content_dir, load_tools(settings.content_dir))
    linked_tools = [catalogue[s] for s in article.related_tools if s in catalogue]
    context = article_context(env, settings, article, True)
    if linked_tools:
        context["article_body"] = insert_article_tool_cta(
            context["article_body"], linked_tools[0], env, article.pillar
        )
    _write(out, env.get_template(article_template(article)).render(
        **context, related=[], linked_tools=linked_tools))
    return out


def render_file_preview(settings: Settings, source: Path, destination: Path) -> Path:
    """Build a review tree outside deployment output; never calls the publishing pipeline."""
    from dataclasses import replace

    destination = destination.resolve()
    protected = (settings.content_dir.resolve(), HERE.resolve(), Path(__file__).resolve())
    if any(destination == p or destination in p.parents for p in protected):
        raise ValueError("Review output must not contain project source files")
    if destination == settings.public_dir.resolve() or settings.public_dir.resolve() in destination.parents:
        raise ValueError("Review output must be outside the production build directory")
    marker = destination / ".compound-review"
    if destination.exists() and any(destination.iterdir()) and not marker.is_file():
        raise ValueError("Review output must be empty or a previously generated review tree")
    article = article_from_file(source, include_drafts=True)
    if not article or article.publication_status != "draft":
        raise ValueError("preview-file requires a draft article")
    preview_settings = replace(settings, public_dir=destination, deploy_command="")
    build_site(preview_settings)
    marker.write_text("Local review output; not for deployment.\n", encoding="utf-8")
    return render_preview(preview_settings, article.slug, article)


def remove_preview(settings: Settings, token: str) -> None:
    d = settings.public_dir / "preview" / token
    if d.exists():
        shutil.rmtree(d)
