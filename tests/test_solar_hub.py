"""Solar hub: SEO route generation, no duplicates and grant references."""
import json
from pathlib import Path
from shutil import copyfile

from compound.site.build import build_site

ROOT = Path(__file__).resolve().parents[1]
SOLAR_PAGES = {
    "solar": "/solar/",
    "solar-compare-quotes": "/solar/compare-quotes/",
    "solar-grants": "/solar/grants/",
    "solar-costs": "/solar/costs/",
    "solar-installers": "/solar/installers/",
    "solar-get-quotes": "/solar/get-quotes/",
}


def test_solar_canonical_routes_are_indexable_and_interlinked(settings):
    for slug in SOLAR_PAGES:
        copyfile(ROOT / "content" / "pages" / f"{slug}.md",
                 settings.content_dir / "pages" / f"{slug}.md")

    build_site(settings)
    urls = set()
    for slug, url in SOLAR_PAGES.items():
        page = (settings.public_dir / url.strip("/") / "index.html").read_text(encoding="utf-8")
        urls.add(url)
        assert f'<link rel="canonical" href="https://example.test{url}">' in page
        assert 'name="description"' in page
        assert 'solar-hub.css' in page
        assert 'solar-hub.js' in page
        assert 'application/ld+json' in page
        assert 'pagead2.googlesyndication.com' not in page  # fixture has no AdSense client
    assert len(urls) == 6
    hub = (settings.public_dir / "solar" / "index.html").read_text(encoding="utf-8")
    for url in SOLAR_PAGES.values():
        if url != "/solar/":
            assert f'href="{url}"' in hub
    assert '/solar-payback-calculator/' in hub
    assert '/solar-ev-battery-optimiser/' in hub
    grant = (settings.public_dir / "solar" / "grants" / "index.html").read_text(encoding="utf-8")
    assert 'before 2025' in grant
    assert 'before 2021' not in grant
    sitemap = (settings.public_dir / "sitemap.xml").read_text(encoding="utf-8")
    for url in urls:
        assert sitemap.count(f"<loc>https://example.test{url}</loc>") == 1
    search = json.loads((settings.public_dir / "search.json").read_text(encoding="utf-8"))
    assert urls.issubset({entry["url"] for entry in search})


def test_solar_installer_conversion_is_private():
    installer = (ROOT / "content/pages/solar-installers.md").read_text(encoding="utf-8")
    comparison = (ROOT / "content/pages/solar-compare-quotes.md").read_text(encoding="utf-8")
    js = (ROOT / "compound/site/static/solar-hub.js").read_text(encoding="utf-8")
    assert installer.count('data-sol-check>') == 8
    assert 'data-sol-check-progress' in installer
    assert 'There is no active lead marketplace' in installer
    assert 'mailto:david@compound.ie?subject=Compound%20Solar%20installer%20pilot' in installer
    assert 'data-sq-print' in comparison
    assert "compound_analytics_consent" in js and "==='granted'" in js
    for event in ("quote_comparison_used", "quote_brief_copied", "seai_register_opened", "installer_checklist_completed"):
        assert event in js


def test_solar_quote_mobile_containment_rules():
    css = (ROOT / "compound/site/static/solar-hub.css").read_text(encoding="utf-8")
    quote = (ROOT / "content/pages/solar-compare-quotes.md").read_text(encoding="utf-8")
    page_template = (ROOT / "compound/site/templates/page.html").read_text(encoding="utf-8")
    assert "grid-template-columns:minmax(0,1fr)" in css
    assert ".sol-shell > *," in css
    assert ".sol-results,.sol-table-scroll" in css
    assert "overflow-x:auto" in css
    assert "grid-template-columns:minmax(0,1fr)" in css.split("@media screen and (max-width:730px)")[1]
    assert "sol-scroll-hint" in quote
    assert 'aria-label="Solar quote comparison table;' in quote
    assert "/static/solar-hub.css?v=3" in page_template


def test_mobile_browser_audit_covers_every_solar_route():
    script = (ROOT / "scripts/verify_solar_mobile.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/site.yml").read_text(encoding="utf-8")
    css = (ROOT / "compound/site/static/solar-hub.css").read_text(encoding="utf-8")
    template = (ROOT / "compound/site/templates/page.html").read_text(encoding="utf-8")
    for path in SOLAR_PAGES.values():
        assert f'"{path}"' in script
    for width in ("320", "360", "390", "430", "768", "1024"):
        assert width in script
    assert "clipped-text" in script and "page-width" in script
    assert "python scripts/verify_solar_mobile.py" in workflow
    assert "overflow-wrap:anywhere" in css
    assert "solar-hub.css?v=4" in template
