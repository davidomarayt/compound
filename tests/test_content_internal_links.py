"""Root-relative Markdown links in content must reach a real canonical route.

Guards two defects found on 26 Nov 2026: links to the legacy /happiness/<slug>/
redirect stubs (noindex client redirects kept only for old external links), and
links to /tools/glp-1-cost/ and /wealth/investing-in-ireland/, routes the site
never builds.

27 Nov 2026: extended to raw HTML href="/..." links inside Markdown, which the
first version missed (three hub/article links pointed at routes never built).
"""
import re
from pathlib import Path

from compound.site.build import load_articles, load_pages, load_tools

CONTENT = Path(__file__).parents[1] / "content"
LINK = re.compile(r"\]\((/[^)\s#?]*)|href=[\"'](/[^\"'\s#?]*)")
# Hubs and directories built from data rather than from a Markdown file.
GENERATED_HUBS = {
    "/", "/finance/", "/search/", "/tools/", "/news/", "/pia/", "/pia/providers/",
    "/wealth/earnings/", "/stocks/", "/companies/", "/life/", "/health/",
    "/health/medicines/", "/wheres-my-money/", "/wealth/",
    "/compound-interest-calculator/", "/bmi-calculator/",
}
GENERATED_PREFIXES = ("/stocks/", "/companies/", "/health/", "/pia/", "/wheres-my-money/")


def _links():
    for path in sorted(CONTENT.rglob("*.md")):
        for match in LINK.finditer(path.read_text(encoding="utf-8")):
            target = match.group(1) or match.group(2)
            if "." in target.rsplit("/", 1)[-1]:
                continue  # static asset such as an image or PDF
            yield path.relative_to(CONTENT), target.rstrip("/") + "/"


def _known_routes():
    routes = set(GENERATED_HUBS)
    routes |= {a.url for a in load_articles(CONTENT)}
    routes |= {p.url for p in load_pages(CONTENT)}
    routes |= {t["url"] for t in load_tools(CONTENT)}
    return routes


def test_content_does_not_link_to_legacy_happiness_redirects():
    legacy = [(str(f), t) for f, t in _links() if t.startswith("/happiness/")]
    assert legacy == []


def test_root_relative_content_links_resolve_to_built_routes():
    known = _known_routes()
    broken = sorted(
        (str(f), t) for f, t in _links()
        if t not in known and not t.startswith(GENERATED_PREFIXES)
    )
    assert broken == []


def test_glp1_link_points_at_the_real_calculator():
    text = (CONTENT / "wealth/eli-lilly-foundayo-europe-approval-glp1-2026.md").read_text()
    assert "](/glp1-cost-calculator-ireland/)" in text
    assert "/tools/glp-1-cost/" not in text
    urls = {t["url"] for t in load_tools(CONTENT)}
    assert "/glp1-cost-calculator-ireland/" in urls


def test_young_savers_links_to_the_beginner_investing_guide():
    text = (CONTENT / "wealth/irish-young-savers-investing-survey-2026.md").read_text()
    assert "](/wealth/how-to-start-investing-in-ireland/)" in text
    assert "](/wealth/investing-in-ireland/)" not in text


def test_kickstartsaver_article_links_savings_calculators():
    path = CONTENT / "wealth/bank-of-ireland-5-percent-savings-account.md"
    text = path.read_text(encoding="utf-8")
    tools = {t["slug"]: t["url"] for t in load_tools(CONTENT)}
    for slug in ("dirt-calculator", "regular-savings-calculator", "emergency-fund-calculator"):
        assert f"]({tools[slug]})" in text
        assert slug in text.split("---", 2)[1]  # listed in related_tools front matter
    assert "date: 2026-11-25" in text  # original publication date preserved
