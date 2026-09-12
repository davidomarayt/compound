"""Static site generator. Reads content/**/*.md (YAML front matter + markdown) and renders public/.

URL structure (fixed, do not change): /wealth/<slug>/, /health/<slug>/, /happiness/<slug>/, /tag/<topic>/
Previews render to /preview/<token>/ with noindex and are never listed anywhere.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compound.config import Settings

PILLARS = ["wealth", "health", "happiness"]
PILLAR_LABELS = {"wealth": "Wealth", "health": "Health", "happiness": "Happiness"}
PILLAR_BLURBS = {
    "wealth": "Irish grants, tax and money news, explained for the person paying.",
    "health": "What the evidence actually says, without the hype.",
    "happiness": "Slower pieces on living well, written between shifts.",
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
    pinned: bool = False
    path: Path | None = None

    @property
    def url(self) -> str:
        return f"/{self.pillar}/{self.slug}/"

    @property
    def pillar_label(self) -> str:
        return PILLAR_LABELS.get(self.pillar, self.pillar.title())


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


def _as_date(v) -> date:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str) and v:
        return datetime.fromisoformat(v[:19]).date()
    return date.today()


def article_from_file(path: Path) -> Article | None:
    meta, body = parse_markdown_file(path)
    if not meta.get("title") or meta.get("draft"):
        return None
    pillar = str(meta.get("pillar") or path.parent.name)
    if pillar not in PILLARS:
        return None
    return Article(
        title=str(meta["title"]),
        slug=str(meta.get("slug") or path.stem),
        pillar=pillar,
        date=_as_date(meta.get("date")),
        summary=str(meta.get("summary") or ""),
        body_html=render_markdown(body),
        tags=[str(t) for t in (meta.get("tags") or [])],
        sources=list(meta.get("sources") or []),
        figures=list(meta.get("figures") or []),
        email_cta=str(meta.get("email_cta") or ""),
        pinned=bool(meta.get("pinned")),
        path=path,
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


def long_date(d: date) -> str:
    """'3 September 2026' without relying on strftime('%-d'), which Windows rejects."""
    return f"{d.day} {d.strftime('%B %Y')}"


def _env(settings: Settings) -> Environment:
    env = Environment(loader=FileSystemLoader(str(HERE / "templates")), autoescape=select_autoescape(["html"]))
    env.filters["long_date"] = long_date
    env.globals.update(
        site_url=settings.site_base_url,
        email_form_action=settings.email_form_action,
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

    # Wipe rendered output except previews (they belong to the pending queue, not the content dir).
    if out.exists():
        for child in out.iterdir():
            if child.name == "preview":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HERE / "static", out / "static", dirs_exist_ok=True)

    by_pillar = {p: [a for a in articles if a.pillar == p] for p in PILLARS}
    columns = {}
    for p in PILLARS:
        arts = by_pillar[p]
        pinned = next((a for a in arts if a.pinned), None)
        feed = [a for a in arts if a is not pinned]
        columns[p] = {"pinned": pinned, "feed": feed[:8]}

    _write(out / "index.html", env.get_template("home.html").render(columns=columns, title="Compound"))

    for p in PILLARS:
        _write(out / p / "index.html", env.get_template("pillar.html").render(pillar=p, articles=by_pillar[p], title=PILLAR_LABELS[p]))

    tag_map: dict[str, list[Article]] = {}
    for a in articles:
        _write(out / a.pillar / a.slug / "index.html",
               env.get_template("article.html").render(article=a, related=related(a, articles), title=a.title, preview=False))
        for t in a.tags:
            tag_map.setdefault(t, []).append(a)
    for t, arts in tag_map.items():
        _write(out / "tag" / t / "index.html", env.get_template("tag.html").render(tag=t, articles=arts, title=f"#{t}"))

    for pg in pages:
        _write(out / pg.slug / "index.html", env.get_template("page.html").render(page=pg, title=pg.title))

    index = [
        {"title": a.title, "url": a.url, "pillar": a.pillar_label, "date": a.date.isoformat(),
         "summary": a.summary, "tags": a.tags}
        for a in articles
    ]
    _write(out / "search.json", json.dumps(index, ensure_ascii=False))
    _write(out / "search" / "index.html", env.get_template("search.html").render(title="Search"))
    _write(out / "feed.xml", env.get_template("feed.xml").render(articles=articles[:30]))
    _write(out / "robots.txt", f"User-agent: *\nDisallow: /preview/\nSitemap: {settings.site_base_url}/sitemap.xml\n")
    urls = [settings.site_base_url + "/"] + [settings.site_base_url + f"/{p}/" for p in PILLARS] + [settings.site_base_url + a.url for a in articles]
    _write(out / "sitemap.xml", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
           + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    return {"articles": len(articles), "tags": len(tag_map), "pages": len(pages)}


def render_preview(settings: Settings, token: str, article: Article) -> Path:
    """Render one draft to /preview/<token>/index.html. Not linked from anywhere, noindex."""
    env = _env(settings)
    out = settings.public_dir / "preview" / token / "index.html"
    if not (settings.public_dir / "static").exists():
        shutil.copytree(HERE / "static", settings.public_dir / "static", dirs_exist_ok=True)
    _write(out, env.get_template("article.html").render(article=article, related=[], title=f"PREVIEW: {article.title}", preview=True))
    return out


def remove_preview(settings: Settings, token: str) -> None:
    d = settings.public_dir / "preview" / token
    if d.exists():
        shutil.rmtree(d)
