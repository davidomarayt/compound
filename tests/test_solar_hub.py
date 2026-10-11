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
