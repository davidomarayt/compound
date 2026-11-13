"""Regression checks for Where's My Money? source-backed spending atlas."""
import json
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compound.site.spending_explorer import prepare_spending_explorer

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "compound" / "site" / "templates"


def load_spending():
    base = json.loads((ROOT / "content/public-spending-2026.json").read_text(encoding="utf-8"))
    extra = json.loads((ROOT / "content/public-spending-sector-pages.json").read_text(encoding="utf-8"))
    return prepare_spending_explorer(base, extra)


def env():
    return Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))


def common_context():
    return dict(
        site_url="https://compound.ie",
        year=2026,
        site_identity_jsonld="{}",
        adsense={"client": ""},
        analytics={"measurement_id": ""},
        title="Irish spending",
        wmm_page=True,
    )


def test_sector_totals_reconcile_without_invented_subcategory_amounts():
    spending = load_spending()
    sectors = spending["categories"]
    assert len(sectors) == 8
    assert len(set(x["url"] for x in sectors)) == len(sectors)
    assert sum(x["billion"] for x in sectors) == pytest.approx(133)
    assert sum(x["next_billion"] for x in sectors) == pytest.approx(143)
    assert sum(x["share_2026"] for x in sectors) == pytest.approx(100)
    assert sum(x["share_2027"] for x in sectors) == pytest.approx(100)
    for s in sectors:
        assert s["url"].startswith("/wheres-my-money/spending/")
        assert s["url"].endswith("/")
        assert len(s["themes"]) == len(s["theme_notes"])
        assert all(s["theme_notes"])
        assert len(s["questions"]) >= 3
        assert s["source"].startswith("https://www.whereyourmoneygoes.gov.ie/")
        assert s["series"][-1]["year"] == 2027
        assert s["series"][-2]["year"] == 2026
    assert spending["comparison_kind"].startswith("Budget 2027")


def test_fail_closed_on_unreconciled_year():
    b = json.loads((ROOT / "content/public-spending-2026.json").read_text(encoding="utf-8"))
    e = json.loads((ROOT / "content/public-spending-sector-pages.json").read_text(encoding="utf-8"))
    e["sectors"][0]["next_billion"] += 1
    with pytest.raises(ValueError, match="2027 sectors do not reconcile"):
        prepare_spending_explorer(b, e)


def test_hub_contains_original_charts_and_sector_links():
    d = load_spending()
    markup = env().get_template("spending_hub.html").render(
        **common_context(), spending=d, max_billion=max(c["billion"] for c in d["categories"]),
        schema={"@type": "CollectionPage"},
    )
    assert '<link rel="canonical" href="https://compound.ie/wheres-my-money/spending/">' in markup
    assert "€133.0bn" in markup and "€143.0bn" in markup
    assert "2027 estimate" in markup
    assert "wmex-sector-track" in markup and "<table" in markup
    assert 'data-spending-personal' in markup
    assert 'pagead2.googlesyndication.com' not in markup
    for sector in d["categories"]:
        assert f'href="{sector["url"]}"' in markup
    assert "whereyourmoneygoes.gov.ie" in markup  # sources, not off-site charts


def test_each_sector_page_is_unique_linked_and_sourced():
    d = load_spending()
    template = env().get_template("spending_sector.html")
    for position, sector in enumerate(d["categories"], 1):
        html = template.render(
            **common_context(), spending=d, sector=sector, sector_index=position,
            schema={"@type": "WebPage"},
        )
        assert f'href="https://compound.ie{sector["url"]}"' in html
        assert f'{sector["name"]} spending in Ireland' in html
        assert f'€{sector["billion"]:.1f}bn' in html
        assert f'€{sector["next_billion"]:.1f}bn' in html
        assert "wmex-history" in html
        assert "<table" in html
        assert sector["theme_notes"][0] in html
        assert 'href="/wheres-my-money/spending/"' in html
        assert "Source" in html
        assert html.count('class="wmex-topic"') == len(sector["themes"])
        for other in d["categories"]:
            if other["id"] != sector["id"]:
                assert f'href="{other["url"]}"' in html


def test_flagship_spending_section_links_to_local_atlas():
    d = load_spending()
    html = env().get_template("wheres_my_money.html").render(
        **common_context(), spending=d,
    )
    assert 'href="/wheres-my-money/spending/"' in html
    assert 'Detailed charts on Compound' in html
    assert 'data-wmm-ad-position="' not in html
