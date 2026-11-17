"""Reader-facing stock research layout guards.

The full register and existing company reports must survive a visual redesign.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stocks_directory_keeps_complete_accessible_register(settings):
    from compound.site.build import build_site

    build_site(settings)
    out = settings.public_dir
    html = (out / "stocks/index.html").read_text(encoding="utf-8")

    assert "Understand the business" in html
    assert 'id="sr-featured"' in html
    assert 'id="stocks-companies"' in html
    # Empty-registry test fixtures intentionally render a setup message instead of controls.
    if 'data-earnings-row' in html:
        assert 'data-earnings-search' in html
        assert 'data-earnings-sector' in html
        assert 'data-earnings-count' in html
    else:
        assert 'Company register being prepared' in html
    assert "Browse stocks by company or ticker." in html
    assert "Price is not" in html
    assert 'rel="canonical"' in html
    assert '/static/earnings-directory.js?v=2' in html
    assert '/static/stocks-research.css?v=1' in html
    assert (out / "static/stocks-research.css").is_file()
    assert (out / "static/earnings-directory.js").is_file()


def test_company_template_keeps_filing_provenance_and_single_chart():
    page = (ROOT / "compound/site/templates/earnings_company.html").read_text(encoding="utf-8")
    assert 'id="sr-company-overview"' in page
    assert 'class="sr-company-metrics"' in page
    assert '{{ seo.latest_figures.revenue }}' in page
    assert '{{ seo.latest_figures.net_income }}' in page
    assert '{{ seo.latest_figures.diluted_eps }}' in page
    assert 'seo.fiscal_display' in page
    assert 'Official SEC filings' in page
    assert page.count("{{ tradingview_panel|safe }}") == 1
    assert page.index('id="sr-company-overview"') < page.index("{{ tradingview_panel|safe }}")
    assert page.index("{{ tradingview_panel|safe }}") < page.index('id="earnings-investor-lens"')
    assert 'id="stocks-company-coverage"' in page
    assert 'include "_company_quarters.html"' in page
    assert 'rel="canonical"' in page
    assert '/static/stocks-research.css?v=1' in page


def test_directory_search_keeps_existing_controls_and_sector_chips():
    script = (ROOT / "compound/site/static/earnings-directory.js").read_text(encoding="utf-8")
    assert "[data-earnings-row]" in script
    assert "[data-earnings-search]" in script
    assert "[data-earnings-sector]" in script
    assert "[data-stock-sector]" in script
    assert "aria-pressed" in script
    assert "row.hidden" in script
    assert "visible" in script
