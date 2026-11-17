"""The caffeine tool has a canonical SEO page, accessible source and licence."""
from pathlib import Path
from compound.site.build import load_pages

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "compound/site/static"


def test_caffeine_page_and_linked_entry_points():
    pages = load_pages(ROOT / "content")
    page = next(p for p in pages if p.slug == "caffeine-calculator")
    assert page.url == "/caffeine-calculator/"
    assert "caffeine" in page.meta_description.lower()
    assert "HSE" in page.body_html and "EFSA" in page.body_html
    template = (ROOT / "compound/site/templates/page.html").read_text(encoding="utf-8")
    assert 'data-caffeine-chart' in template
    assert 'application/ld+json' in template
    assert '/static/caffeine-page.js?v=1' in template
    for file in ("tools.html", "pillar.html"):
        assert '/caffeine-calculator/' in (ROOT / "compound/site/templates" / file).read_text(encoding="utf-8")


def test_licenced_chart_source_and_model_are_local():
    chart = (STATIC / "caffeine-day.js").read_text(encoding="utf-8")
    licence = (STATIC / "caffeine-day-LICENSE.txt").read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Charles Postiaux" in licence
    assert "MIT License" in licence
    assert "export function mount" in chart
    assert "export const HALF_LIFE = 5;" in chart
    assert "if (!h || !h.includes('~bed.')) return null;" in chart
    assert (STATIC / "caffeine-page.css").is_file()
    assert (STATIC / "caffeine-page.js").is_file()
