"""Tests for the Dáil-approved 2026 net voted Exchequer grants layer."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compound.site.spending_explorer import prepare_spending_explorer
from compound.site.spending_programmes import prepare_programmes
from compound.site.spending_votes import prepare_votes, EXPECTED_NUMBERS

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "compound/site/templates"


def load_registers():
    base = json.loads((CONTENT / "public-spending-2026.json").read_text(encoding="utf-8"))
    editorial = json.loads((CONTENT / "public-spending-sector-pages.json").read_text(encoding="utf-8"))
    programmes = json.loads((CONTENT / "public-spending-programmes-2026.json").read_text(encoding="utf-8"))
    votes = json.loads((CONTENT / "public-spending-votes-2026.json").read_text(encoding="utf-8"))
    return prepare_programmes(prepare_spending_explorer(base, editorial), programmes), votes


def data():
    spending, register = load_registers()
    return prepare_votes(spending, register)


def env():
    return Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))


def kwargs():
    return {
        "site_url":"https://compound.ie", "title":"Irish Voted Estimates",
        "year":2026, "site_identity_jsonld":"{}",
        "adsense":{"client":""}, "analytics":{"measurement_id":""},
        "wmm_page":True,
    }


def test_exact_37_votes_bounded_by_original_dail_resolution():
    d = data()
    assert d["vote_count"] == 37
    assert [v["number"] for v in d["votes"]] == EXPECTED_NUMBERS
    assert len(d["vote_details"]) == 17
    assert d["vote_grant_sum"] == 84598988000
    assert sum(v["net_supply_eur"] for v in d["votes"]) == d["vote_grant_sum"]
    assert d["vote_grant_sum"] != d["total_billion"] * 1_000_000_000
    assert d["vote_source"].startswith("https://data.oireachtas.ie/")
    assert len({v["url"] for v in d["votes"]}) == 37
    assert all(v["amount_display"].startswith("€") for v in d["votes"])
    assert all(v["estimate_type"] == "net Exchequer supply grant" for v in d["votes"])
    assert all(v["sector_record"]["url"].startswith("/wheres-my-money/spending/") for v in d["votes"])
    assert all(0 < v["bar_percent"] <= 100 for v in d["votes"])
    assert all(0 < v["bar_percent"] <= 100 for vote in d["votes"] for v in vote["other_votes"])
    assert any(v["number"] == 37 and v["net_supply_eur"] == 14066335000 for v in d["votes"])


def test_invalid_or_truncated_vote_register_rejected():
    spending, register = load_registers()
    cases = [
        ("short",lambda r:r["votes"].pop(), "Incomplete or out-of-order"),
        ("wrong grant",lambda r:r["votes"][0].update({"net_supply_eur":0}), "Invalid exact net grant"),
        ("untrusted source",lambda r:r.update({"source":"https://example.com/false.pdf"}), "official Oireachtas"),
        ("year",lambda r:r.update({"year":2027}), "must match 25 March 2026"),
        ("wrong numbering",lambda r:r["votes"][10].update({"number":11}), "Incomplete or out-of-order"),
    ]
    for label,mutate,error in cases:
        copy = deepcopy(register)
        mutate(copy)
        with pytest.raises(ValueError,match=error), pytest.MonkeyPatch.context():
            prepare_votes(spending,copy)


def test_vote_hub_has_local_charts_source_and_exact_numbered_rows():
    d = data()
    html = env().get_template("spending_votes_hub.html").render(
        **kwargs(),spending=d,schema={"@type":"CollectionPage"}
    )
    assert '<link rel="canonical" href="https://compound.ie/wheres-my-money/spending/votes/">' in html
    assert "37 exact 2026 net Exchequer supply-grant" in html
    assert "€14.066bn" in html
    assert 'data-vote-search' in html
    assert html.count('data-vote-row') == 37
    assert 'href="/wheres-my-money/spending/programmes/"' in html
    assert 'href="/wheres-my-money/spending/"' in html
    assert "supply-grant authorisations, not actual 2026 expenditure" in html
    assert "Vote 37" in html
    for vote in d["vote_details"]:
        assert f'href="{vote["url"]}"' in html


def test_all_17_detailed_votes_are_canonical_and_internally_linked():
    d = data()
    template = env().get_template("spending_vote_detail.html")
    for vote in d["vote_details"]:
        html = template.render(
            **kwargs(),spending=d,vote=vote,schema={"@type":"WebPage"}
        )
        assert f'<link rel="canonical" href="https://compound.ie{vote["url"]}">' in html
        assert f'Vote {vote["number"]}:' in html
        assert vote["amount_display"] in html
        assert "2026 Dáil-approved net supply-grant ceiling" in html
        assert "The 2026 Dáil-approved net supply-grant ceiling" in html
        assert "https://data.oireachtas.ie/" in html
        assert f'href="{vote["sector_record"]["url"]}"' in html
        assert 'href="/wheres-my-money/spending/votes/"' in html
        assert 'href="/wheres-my-money/spending/programmes/"' in html
        for p in vote["related_programmes"]:
            assert f'href="{p["url"]}"' in html


def test_vote_crosslink_present_in_eight_sector_templates():
    d = data()
    template = env().get_template("spending_sector.html")
    for sector in d["categories"]:
        html = template.render(
            **kwargs(),spending=d,sector=sector,sector_index=1,schema={"@type":"WebPage"}
        )
        assert 'id="votes"' in html
        assert 'href="/wheres-my-money/spending/votes/"' in html
        for vote in d["vote_details"]:
            if vote["sector"] == sector["id"]:
                assert f'href="{vote["url"]}"' in html


def test_search_js_is_local_and_input_safe():
    src = (ROOT / "compound/site/static/spending-explorer.js").read_text(encoding="utf-8")
    assert "data-vote-search" in src and "data-vote-row" in src
    assert "fetch(" not in src and "XMLHttpRequest" not in src and "gtag(" not in src
