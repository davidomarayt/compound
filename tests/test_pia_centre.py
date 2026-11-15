"""Regression tests for Compound's SEO-first PIA Centre."""
import json

from compound.site.build import build_site


def test_pia_centre_and_provider_routes_are_indexable(settings):
    tracker = settings.content_dir / "pia-providers.yml"
    tracker.write_text(
        """updated: '2026-10-10'
providers:
  - name: Example Provider
    slug: example-provider
    category: Bank
    stage: intent
    statement: Example publicly stated interest in launching a PIA.
    status: Plans to offer
    availability: Not open yet
    annual_fee: Not published
    dealing_fee: Not published
    fund_fee: Not published
    fx_fee: Not published
    minimum_investment: Not published
    transfer_terms: Not published
    investment_range: Not published
    checked: '2026-10-10'
    source_url: https://example.com/provider
    source_label: Example official source
    fee_model:
      verified: false
    referral:
      active: false
      approved: false
sponsorships: []
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
    assert "PIA Ireland: Personal Investment Account explained." in hub
    assert "/wealth/personal-investment-account-ireland/" in hub
    assert "/pia-calculator/" in hub
    assert 'href="/pia/vs-pension/"' in hub
    assert 'href="/pia/daily-valuation/"' in hub
    assert 'href="/pia/investment-eligibility/"' in hub
    assert 'href="/pia/compare-fee-quotes/"' in hub
    assert 'href="/pia/investment-eligibility/"' in compare
    assert 'href="/pia/compare-fee-quotes/"' in compare
    assert 'href="/pia/vs-pension/"' in compare
    assert 'aria-current="page">PIA</a>' in hub
    assert "Example Provider" in hub and "Example Provider" in compare
    assert "Not published" in compare and "https://example.com/provider" in compare
    assert "not currently available" not in compare  # No invented blanket claims.
    assert 'data-pia-comparison' in compare
    assert 'data-pia-provider-list' in compare
    assert 'data-pia-filter-search' in compare
    assert 'Awaiting verified fees' in compare
    assert 'data-fees-verified="false"' in compare
    assert 'href="/static/pia-centre.css?v=2"' in compare
    assert '/static/pia-providers.js?v=1' in compare
    assert 'rel="sponsored' not in compare
    assert 'Paid referral:' not in compare
    assert "/pia/" in wealth
    assert sitemap.count("<loc>https://example.test/pia/</loc>") == 1
    assert sitemap.count("<loc>https://example.test/pia/providers/</loc>") == 1
    assert {"/pia/", "/pia/providers/"}.issubset({entry["url"] for entry in search})


def test_pia_short_head_search_landing_and_intent_separation(settings):
    """Protect the PIA landing title, direct answers and distinct tool intent."""
    build_site(settings)
    hub = (settings.public_dir / "pia" / "index.html").read_text(encoding="utf-8")
    wealth = (settings.public_dir / "wealth" / "index.html").read_text(encoding="utf-8")
    assert "<title>PIA Ireland 2027: Tax Rules, Providers &amp; Calculator | Compound</title>" in hub or "PIA Ireland 2027: Tax Rules, Providers & Calculator | Compound" in hub
    assert "PIA Ireland: Personal Investment Account explained." in hub
    assert "What is a PIA in Ireland?" in hub
    assert "Individual Investment Account (IIA)" in hub
    assert "Personal Insolvency Arrangement" in hub
    assert "1% × (€75,000 − €50,000) = €250 for the year" in hub
    assert "PIA Ireland: frequently asked questions" in hub
    assert "When can I open a PIA in Ireland?" in hub
    assert "Finance (No. 2) Bill 2026 (as introduced)" in hub
    assert 'href="/pia-calculator/"' in hub
    assert 'href="/pia/vs-pension/"' in hub
    assert 'href="/pia/"' in wealth
    assert '<link rel="canonical" href="https://example.test/pia/">' in hub
