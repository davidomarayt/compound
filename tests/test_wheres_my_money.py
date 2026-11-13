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
