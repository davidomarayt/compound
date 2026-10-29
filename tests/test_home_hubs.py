"""Homepage evolution: specialist hubs remain connected to Health, Wealth and Life."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "compound/site/templates/home.html"
CSS = ROOT / "compound/site/static/home-hubs.css"
JS = ROOT / "compound/site/static/home-hubs.js"


def test_homepage_preserves_editorial_identity_and_promotes_four_hubs():
    page = HOME.read_text(encoding="utf-8")
    assert page.index('class="home-command-grid"') < page.index('id="explore-compound"') < page.index('id="pillars-title"')
    assert page.count('class="home-hub-card"') == 4
    assert page.count('data-home-hub=') == 8
    for route in ("/wealth/", "/compound-interest-calculator/", "/insurance/",
                  "/health-insurance-cost-comparison-calculator/", "/pia/",
                  "/wealth/how-to-start-investing-in-ireland/", "/stocks/", "/wealth/earnings/"):
        assert f'href="{route}"' in page
    for hub in ("wealth", "insurance", "pia", "stocks"):
        assert page.count(f'data-home-hub="{hub}"') == 2
    assert 'Finance &amp; Investing' in page
    assert '/solar/get-quotes/' not in page
    assert 'Popular tools' in page
    assert 'Explore our wider guides.' in page
    assert 'Worth your time.' in page
    assert 'home-hubs.css?v=1' in page and 'home-hubs.js?v=1' in page
    assert 'rel="canonical" href="{{ site_url }}/"' in page


def test_hub_tracking_is_opt_in_and_does_not_log_user_data():
    js = JS.read_text(encoding="utf-8")
    assert "homepage_hub_click" in js
    assert "compound_analytics_consent" in js
    assert "!== 'granted'" in js
    assert "data-home-hub" in js and "data-home-action" in js
    for forbidden in ("email", "phone", "eircode", "searchParams", "location.href", "input.value"):
        assert forbidden not in js
    css = CSS.read_text(encoding="utf-8")
    assert "grid-template-columns:repeat(4,minmax(0,1fr))" in css
    assert "grid-template-columns:repeat(2,minmax(0,1fr))" in css
    assert "grid-template-columns:minmax(0,1fr)" in css
    assert "min-height:44px" in css
    assert "prefers-reduced-motion" in css
