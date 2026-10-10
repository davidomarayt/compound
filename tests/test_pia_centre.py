"""Regression tests for Compound's SEO-first PIA Centre."""
import json

from compound.site.build import build_site


def test_pia_centre_and_provider_routes_are_indexable(settings):
    tracker = settings.content_dir / "pia-providers.yml"
    tracker.write_text(
        """updated: '2026-10-10'
providers:
  - name: Example Provider
    statement: Example publicly stated interest in launching a PIA.
    status: Plans to offer
    availability: Not open yet
    annual_fee: Not published
    dealing_fee: Not published
    investment_range: Not published
    source_url: https://example.com/provider
    source_label: Example official source
""",
        encoding="utf-8",
    )

    build_site(settings)
    hub = (settings.public_dir / "pia" / "index.html").read_text(encoding="utf-8")
    compare = (settings.public_dir / "pia" / "providers" / "index.html").read_text(encoding="utf-8")
    wealth = (settings.public_dir / "wealth" / "index.html").read_text(encoding="utf-8")
    sitemap = (settings.public_dir / "sitemap.xml").read_text(encoding="utf-8")
    search = json.loads((settings.public_dir / "search.json").read_text(encoding="utf-8"))

    assert '<link rel="canonical" href="https://example.test/pia/">' in hub
    assert '<link rel="canonical" href="https://example.test/pia/providers/">' in compare
    assert 'name="description"' in hub and 'name="description"' in compare
    assert '"@type":"BreadcrumbList"' in hub
    assert "Personal Investment Accounts in Ireland" in hub
    assert "/wealth/personal-investment-account-ireland/" in hub
    assert "/pia-calculator/" in hub
    assert 'aria-current="page">PIA</a>' in hub
    assert "Example Provider" in hub and "Example Provider" in compare
    assert "Not published" in compare and "https://example.com/provider" in compare
    assert "not currently available" not in compare  # No invented blanket claims.
    assert "/pia/" in wealth
    assert sitemap.count("<loc>https://example.test/pia/</loc>") == 1
    assert sitemap.count("<loc>https://example.test/pia/providers/</loc>") == 1
    assert {"/pia/", "/pia/providers/"}.issubset({entry["url"] for entry in search})
