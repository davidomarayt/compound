"""Pages with front-matter descriptions render them; stock labels meet WCAG AA contrast."""
import re
from pathlib import Path

from compound.config import load_settings
from compound.site.build import _env, load_pages

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = "Independent investing research, company earnings, personal finance guides and financial tools for readers in Ireland."


def _descriptions(page):
    html = _env(load_settings()).get_template("page.html").render(page=page, title=page.title, ads_allowed=True, ads_configured=False)
    return re.findall(r'<meta name="description" content="([^"]*)"', html)


def test_every_page_with_meta_description_renders_its_own():
    pages = [p for p in load_pages(ROOT / "content") if p.meta_description]
    assert pages
    for page in pages:
        found = _descriptions(page)
        assert len(found) == 1, page.url
        assert found[0] != DEFAULT, page.url


def test_map_and_sun_tools_no_longer_use_sitewide_default():
    by_url = {p.url: p for p in load_pages(ROOT / "content")}
    for url in ("/ireland-rent-map/", "/rent-commute-map/", "/sun-path-explorer/"):
        page = by_url[url]
        assert _descriptions(page) == [page.meta_description.replace("'", "&#39;")]


def _lum(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _ratio(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_small_stock_labels_meet_aa_contrast():
    css = (ROOT / "compound/site/static/stocks-research.css").read_text(encoding="utf-8")
    rules = {
        r"\.stocks-company \.sr-kicker,\.stocks-research-hub \.sr-eyebrow\{[^}]*color:(#[0-9a-f]{6})": "kicker",
        r"\.sr-aside-no\{[^}]*color:(#[0-9a-f]{6})": "aside number",
        r"\.sr-jump>span\{[^}]*color:(#[0-9a-f]{6})": "jump label",
        r"\.sr-company-symbol\{[^}]*color:(#[0-9a-f]{6})": "symbol",
        r"\.sr-company-metrics small\{[^}]*color:(#[0-9a-f]{6})": "metric period",
    }
    # Lightest and darkest page backgrounds these labels were measured on (axe, 28 Nov 2026).
    backgrounds = ["#fffdfa", "#fcf9f4", "#f8f6f1", "#f4f1eb", "#ecede6", "#e7ede6"]
    for pattern, name in rules.items():
        colour = re.search(pattern, css).group(1)
        for bg in backgrounds:
            assert _ratio(colour, bg) >= 4.5, (name, colour, bg)


def test_calculator_guide_scroll_tables_are_keyboard_reachable():
    build = (ROOT / "compound/site/build.py").read_text(encoding="utf-8")
    assert '<div class="guide-table-scroll" tabindex="0" role="region" aria-label="Scrollable table"><table>' in build
