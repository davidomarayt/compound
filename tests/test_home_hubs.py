"""Homepage evolution: specialist hubs remain connected to Health, Wealth and Life."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "compound/site/templates/home.html"
CSS = ROOT / "compound/site/static/home-hubs.css"
JS = ROOT / "compound/site/static/home-hubs.js"


def test_homepage_preserves_editorial_identity_and_promotes_four_hubs():
    page = HOME.read_text(encoding="utf-8")
    assert page.index('class="home-command-grid"') < page.index('id="explore-compound"') < page.index('id="finance-desk-title"')
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
    assert 'Research. Invest. Build.' in page
    assert 'pillar-tile' not in page
    assert 'journal-column-happiness' not in page
    assert all(title in page for title in ('Stock research','Investing in Ireland','Personal finance'))
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


def test_home_finance_panel_shows_newest_wealth_articles_from_every_publisher():
    from datetime import date
    from types import SimpleNamespace

    from compound.site.build import select_latest_finance_articles

    def article(slug, day, pillar="wealth", tags=()):
        return SimpleNamespace(slug=slug, date=date(2026, 11, day), pillar=pillar, tags=tags)

    articles = [
        article("old-news", 13, tags=("news",)),
        article("health-news", 16, pillar="health", tags=("news",)),
        article("private-company", 16, tags=("private-company",)),
        article("stock-analysis", 15, tags=("company-research",)),
        article("personal-finance", 14, tags=("investing",)),
        article("obsolete-quarter", 16, tags=("automated-earnings",)),
    ]
    selected = select_latest_finance_articles(articles)
    assert [item.slug for item in selected] == [
        "private-company", "stock-analysis", "personal-finance"
    ]

    page = HOME.read_text(encoding="utf-8")
    assert "for a in home_finance_articles" in page
    assert "for a in news_articles[:3]" not in page
    assert 'href="/finance/">Explore finance' in page
