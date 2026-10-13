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
    "solar-batteries": "/solar/batteries/",
    "solar-export-rates": "/solar/export-rates/",
    "solar-equipment": "/solar/equipment/",
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
        assert 'solar-research.js' in page
        assert 'application/ld+json' in page
        assert 'pagead2.googlesyndication.com' not in page  # fixture has no AdSense client
    assert len(urls) == 9
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
    assert 'There is no live paid referral marketplace' in installer
    assert 'href="/solar/for-installers/"' in installer
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
    assert "/static/solar-hub.css?v=6" in page_template


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
    assert ".tool-chart-scroll" in script  # charts intentionally scroll within the viewport
    assert "python scripts/verify_solar_mobile.py" in workflow
    assert "overflow-wrap:anywhere" in css
    assert "solar-hub.css?v=6" in template
    assert "solar-hub.js?v=5" in template
    assert "solar-research.js?v=2" in template
    assert "node --check compound/site/static/solar-research.js" in workflow
    solar_paths = "solar solar/compare-quotes solar/grants solar/costs solar/installers solar/get-quotes solar/for-installers solar/batteries solar/export-rates solar/equipment; do"
    assert "for path in " + solar_paths in workflow  # generated pages
    assert "for slug in " + solar_paths in workflow  # public deployed pages
    assert 'brief.querySelector("[data-sb-output]")' in (ROOT / "compound/site/static/solar-hub.js").read_text(encoding="utf-8")
    for route in ("/solar-payback-calculator/", "/solar-ev-battery-optimiser/", "/wealth/solar-panels-ireland/", "/wealth/solar-panels-vs-battery-ireland/"):
        assert f'"{route}"' in script

def test_solar_research_calculators_and_sources():
    battery = (ROOT / "content/pages/solar-batteries.md").read_text(encoding="utf-8")
    export = (ROOT / "content/pages/solar-export-rates.md").read_text(encoding="utf-8")
    equipment = (ROOT / "content/pages/solar-equipment.md").read_text(encoding="utf-8")
    js = (ROOT / "compound/site/static/solar-research.js").read_text(encoding="utf-8")
    assert "data-solar-battery" in battery and "round-trip efficiency" in battery.lower()
    assert "data-solar-export" in export and "standing charge" in export.lower()
    assert "data-solar-equipment" in equipment and "nameplate" in equipment.lower()
    assert "data-bat-out" in battery and "data-ex-out" in export and "data-eq-out" in equipment
    assert "data-solar-battery" in js and "data-solar-export" in js and "data-solar-equipment" in js
    assert "Number.isFinite" in js
    assert "document.querySelector(\"[data-solar-battery]\")" in js
    for url in ("/solar/batteries/", "/solar/export-rates/", "/solar/equipment/"):
        assert url in (ROOT / "content/pages/solar.md").read_text(encoding="utf-8")


def test_solar_hub_connects_home_energy_tools_and_guides():
    hub = (ROOT / "content/pages/solar.md").read_text(encoding="utf-8")
    tools_page = (ROOT / "compound/site/templates/tools.html").read_text(encoding="utf-8")
    for path in (
        "/solar-payback-calculator/",
        "/solar-ev-battery-optimiser/",
        "/electricity-cost-calculator/",
        "/ber-energy-cost-calculator/",
        "/whole-house-retrofit-planner/",
        "/wealth/average-home-electricity-use-ireland/",
        "/wealth/electricity-tariffs-ireland/",
        "/wealth/heat-pumps-ireland/",
        "/wealth/insulation-grants-ireland/",
    ):
        assert f'href="{path}"' in hub
    assert "category == 'Home Energy'" in tools_page
    assert 'href="/solar/"' in tools_page
    for slug in (
        "electricity-cost-calculator",
        "solar-payback-calculator",
        "ber-energy-cost-calculator",
        "solar-ev-battery-optimiser",
        "whole-house-retrofit-planner",
    ):
        body = (ROOT / "content/tool-guides" / f"{slug}.md").read_text(encoding="utf-8")
        assert "](/solar/)" in body


def test_tariff_result_cards_are_readable_on_mobile():
    page = (ROOT / "content/pages/solar-export-rates.md").read_text(encoding="utf-8")
    css = (ROOT / "compound/site/static/solar-hub.css").read_text(encoding="utf-8")
    js = (ROOT / "compound/site/static/solar-research.js").read_text(encoding="utf-8")
    audit = (ROOT / "scripts/verify_solar_mobile.py").read_text(encoding="utf-8")
    assert 'class="sol-export-breakdown"' in page
    for key in ('a-bill', 'a-credit', 'b-bill', 'b-credit'):
        assert f'data-ex-out="{key}"' in page
    assert 'class="sol-minirows"' not in page  # not a four-column minirow layout
    assert '[data-solar-export] .sol-export-amount' in css
    assert "white-space:nowrap;" in css
    assert 'setBetter(gap<.005?null:' in js
    assert 'unreadable result card' in audit


def test_solar_quote_project_brief_is_private_and_comprehensive():
    page = (ROOT / "content/pages/solar-get-quotes.md").read_text(encoding="utf-8")
    js = (ROOT / "compound/site/static/solar-project.js").read_text(encoding="utf-8")
    template = (ROOT / "compound/site/templates/page.html").read_text(encoding="utf-8")
    compass = (ROOT / "compound/site/static/solar-orientation.js").read_text(encoding="utf-8")
    assert 'data-solar-project' in page and 'data-solar-brief' in page
    assert 'data-sb-output' in page and 'data-sb-copy' in page
    for field in ("county", "role", "building", "timing", "azimuth", "pitch", "faces",
                  "shade", "roofCondition", "material", "demand", "phase", "smartMeter",
                  "kwp", "battery", "grant", "installerCount", "email", "phone", "eircode"):
        assert f'data-sp="{field}"' in page
    assert "Compound does not receive, save, sell or send" in page
    assert "not consent for data sharing" in page
    assert 'solar-project.css?v=1' in template and 'solar-project.js?v=1' in template
    assert "sessionStorage.getItem('compound_solar_project_compass_v1')" in js
    assert "sessionStorage.setItem('compound_solar_project_compass_v1'" in compass
    # No remote submission or local persistence of contact data.
    assert "fetch(" not in js and "localStorage.setItem" not in js
    assert '<form' not in page
    assert '/solar/roof-direction/' in page and '/solar/compare-quotes/' in page
