"""Where's My Money: source and rendering integrity."""
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
SPENDING = ROOT / "content" / "public-spending-2026.json"
TEMPLATES = ROOT / "compound" / "site" / "templates"


def test_2026_public_spending_reconciles():
    data = json.loads(SPENDING.read_text(encoding="utf-8"))
    assert data["year"] == 2026
    assert data["kind"] == "estimated expenditure"
    assert data["total_billion"] == 133.0
    categories = data["categories"]
    assert len(categories) == 8
    assert len({c["id"] for c in categories}) == len(categories)
    assert abs(sum(c["billion"] for c in categories) - data["total_billion"]) < 0.001
    assert all(c["themes"] and c["source"].startswith("https://") for c in categories)


def test_flagship_template_renders_with_privacy_and_sources():
    data = json.loads(SPENDING.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))
    html = env.get_template("wheres_my_money.html").render(
        title="Where's My Money?",
        site_url="https://compound.ie",
        spending=data,
        adsense={"client":""},
        analytics={"measurement_id":""},
        site_identity_jsonld="{}",
        year=2026,
    )
    assert 'href="https://compound.ie/wheres-my-money/"' in html
    assert 'id="wmm-salary"' in html
    assert 'id="wmm-spending-data"' in html
    assert 'wheres-my-money.js' in html
    assert 'Calculations stay on your device' in html
    assert "€133.0bn" in html
    assert "not earmarked payments" in html
    assert "https://www.whereyourmoneygoes.gov.ie/en/2026/" in html
    assert "chatbot" not in html.lower()



def test_flagship_ads_have_three_desktop_slots_and_two_mobile_slots():
    data = json.loads(SPENDING.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))
    slots = {
        "wmm_receipt": "2138650464",
        "wmm_spending": "8512487125",
        "wmm_budget": "2138650464",
    }
    html = env.get_template("wheres_my_money.html").render(
        title="Where's My Money?",
        site_url="https://compound.ie",
        spending=data,
        adsense={"client":"ca-pub-6115783809711785", "slots":slots},
        analytics={"measurement_id":""},
        site_identity_jsonld="{}",
        year=2026,
    )
    assert html.count('class="wmm-ad') == 3
    assert html.count('aria-label="Advertisement"') == 3
    assert html.count('data-wmm-ad-slot="2138650464"') == 2
    assert html.count('data-wmm-ad-slot="8512487125"') == 1
    assert html.count("wmm-ad-desktop-only") == 1
    assert html.count("wheres-my-money-ads.js") == 1
    assert html.count("pagead2.googlesyndication.com/pagead/js/adsbygoogle.js") == 1
    assert html.index('id="your-receipt"') < html.index('data-wmm-ad-position="after-receipt"') < html.index('id="spending"')
    assert html.index('id="spending"') < html.index('data-wmm-ad-position="after-spending"') < html.index('id="what-if"')
    assert html.index('id="budget"') < html.index('data-wmm-ad-position="after-budget"') < html.index('id="reliefs"')
    css = (ROOT / "compound/site/static/wheres-my-money.css").read_text(encoding="utf-8")
    script = (ROOT / "compound/site/static/wheres-my-money-ads.js").read_text(encoding="utf-8")
    assert ".wmm-ad-desktop-only{display:none!important}" in css
    assert "matchMedia('(min-width: 761px)')" in script
    assert "IntersectionObserver" in script
    assert "data-ad-full-width-responsive" not in script  # use Google's full-width-responsive key
    assert "data-full-width-responsive" in script
    assert "wmm-salary" not in script and "wmm-pension" not in script


def test_flagship_ads_respect_disabled_site_config():
    data = json.loads(SPENDING.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))
    html = env.get_template("wheres_my_money.html").render(
        title="Where's My Money?",
        site_url="https://compound.ie",
        spending=data,
        adsense={"client":"", "slots":{"wmm_receipt":"2138650464"}},
        analytics={"measurement_id":""},
        site_identity_jsonld="{}",
        year=2026,
    )
    assert 'data-wmm-ad-position="' not in html
    assert 'class="wmm-ad' not in html
