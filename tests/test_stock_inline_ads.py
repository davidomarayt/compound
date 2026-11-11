"""Stock-profile ad placements must be opt-in, clearly labelled and away from charts."""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from compound.site.build import load_site_config

TEMPLATES = Path(__file__).resolve().parents[1] / "compound" / "site" / "templates"


def render_stock_ad(*, allowed=True, client="ca-pub-example", slot="123"):
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    return env.get_template("_stock_inline_ad.html").render(
        ads_allowed=allowed,
        adsense={"client": client},
        slot=slot,
        name="stock-mid",
    )


def test_stock_ad_is_labelled_and_responsive():
    html = render_stock_ad()
    assert html.count("Advertisement") == 2  # visible label + accessible name
    assert 'data-ad-slot="123"' in html
    assert 'data-ad-format="auto"' in html
    assert html.count("adsbygoogle") >= 1


def test_stock_ad_is_opt_in_and_never_appears_on_disallowed_page():
    assert not render_stock_ad(allowed=False).strip()
    assert not render_stock_ad(client="").strip()
    assert not render_stock_ad(slot="").strip()


def test_stock_ads_stay_below_chart_and_require_substantive_coverage():
    main = (TEMPLATES / "earnings_company.html").read_text()
    watchlist = (TEMPLATES / "watchlist_stock.html").read_text()
    assert main.index("{{ tradingview_panel|safe }}") < main.index('name="stock-mid"')
    assert main.index('name="stock-mid"') < main.index('name="stock-lower"')
    assert "ads_allowed and report and (seo or earnings_analysis)" in main
    assert "ads_allowed and report and seo and (news or research)" in main
    assert watchlist.index("{{ tradingview_panel|safe }}") < watchlist.index('name="stock-mid"')
    assert "ads_allowed and report and (news or research)" in watchlist
    assert 'name="stock-lower"' not in watchlist


def test_configured_stock_slot_uses_existing_adsense_client():
    config = load_site_config(Path(__file__).resolve().parents[1] / "content")
    assert config["adsense"]["client"] == "ca-pub-6115783809711785"
    assert config["adsense"]["slots"]["stock_mid"] == "2138650464"
    assert config["adsense"]["slots"]["stock_lower"] == ""
    assert "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in (TEMPLATES / "_stock_inline_ad.html").read_text()
