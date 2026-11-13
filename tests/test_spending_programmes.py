"""Where's My Money? granular 2026 budget allocation evidence and SEO."""
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import escape

from compound.site.spending_explorer import prepare_spending_explorer
from compound.site.spending_programmes import prepare_programmes, amount_display

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "compound/site/templates"
CONTENT = ROOT / "content"


def fixture():
    sectors = json.loads((CONTENT / "public-spending-2026.json").read_text(encoding="utf-8"))
    editorial = json.loads((CONTENT / "public-spending-sector-pages.json").read_text(encoding="utf-8"))
    register = json.loads((CONTENT / "public-spending-programmes-2026.json").read_text(encoding="utf-8"))
    return prepare_programmes(prepare_spending_explorer(sectors, editorial), register)


def context():
    return {
        "title":"Where's My Money?", "site_url":"https://compound.ie", "year":2026,
        "site_identity_jsonld":"{}", "adsense":{"client":""},
        "analytics":{"measurement_id":""}, "wmm_page":True,
    }


def jinja():
    return Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))


def test_register_has_49_official_2026_allocations_in_all_eight_sectors():
    d = fixture()
    assert d["programme_count"] == 49
    counts = Counter(p["sector"] for p in d["programmes"])
    assert set(counts) == {"social","health","education","housing","transport","justice","other","debt"}
    assert min(counts.values()) >= 3
    assert sum(counts.values()) == len({p["url"] for p in d["programmes"]})
    for p in d["programmes"]:
        assert p["source"].startswith("https://")
        assert p["url"].startswith("/wheres-my-money/spending/")
        assert p["url"].endswith("/")
        assert p["sector_url"] in [c["url"] for c in d["categories"]]
        assert len(p["description"]) > 100
        assert len(p["limitation"]) > 50
        assert "2026" in p["kind"] or p["year"] == 2026
        if p["parent_record"]:
            assert p["parent_record"]["url"] != p["url"]
        else:
            assert p["parent"] is None
    assert len(d["categories"]) == 8
    assert sum(c["billion"] for c in d["categories"]) == pytest.approx(133)
    assert sum(c["next_billion"] for c in d["categories"]) == pytest.approx(143)


def test_amount_qualifiers_preserve_uncertainty():
    assert amount_display(12000,"over") == "Over €12bn"
    assert amount_display(178,"under") == "Under €178m"
    assert amount_display(1600,"almost") == "Almost €1.6bn"
    assert amount_display(563.5,"exact") == "€563.5m"
    assert amount_display(2700,"approx") == "About €2.7bn"


def test_invalid_amount_missing_source_and_parent_are_rejected():
    base = json.loads((CONTENT / "public-spending-2026.json").read_text(encoding="utf-8"))
    editorial = json.loads((CONTENT / "public-spending-sector-pages.json").read_text(encoding="utf-8"))
    register = json.loads((CONTENT / "public-spending-programmes-2026.json").read_text(encoding="utf-8"))
    spending = prepare_spending_explorer(base, editorial)
    for mutation,match in (
        ({"amount_m": -1}, "Invalid programme amount"),
        ({"source":"https://example.com/fake"}, "Untrusted programme source"),
        ({"slug":"state-pension-payments"}, "Invalid or duplicate programme slug"),
        ({"parent":"non-existent-programme"}, "Invalid parent/component"),
    ):
        changed = deepcopy(register)
        item = changed["programmes"][1] if "slug" in mutation else changed["programmes"][0]
        item.update(mutation)
        with pytest.raises(ValueError, match=match):
            prepare_programmes(spending,changed)


def test_index_links_all_programmes_but_never_adds_amounts():
    d = fixture()
    html = jinja().get_template("spending_programmes_hub.html").render(
        **context(), spending=d, schema={"@type":"CollectionPage"}
    )
    assert 'href="https://compound.ie/wheres-my-money/spending/programmes/"' in html
    assert html.count('data-programme-card') == 49
    assert 'data-programme-search' in html
    assert "not be added together" in html
    for p in d["programmes"]:
        assert f'href="{p["url"]}"' in html
    for c in d["categories"]:
        assert f'href="{c["url"]}"' in html
    assert 'https://www.whereyourmoneygoes.gov.ie/en/' not in html  # interactive local charts


def test_49_programme_pages_render_unique_canonicals_sources_and_related_links():
    d = fixture()
    template = jinja().get_template("spending_programme.html")
    for p in d["programmes"]:
        html = template.render(**context(), programme=p, spending=d, schema={"@type":"WebPage"})
        assert f'<link rel="canonical" href="https://compound.ie{p["url"]}">' in html
        assert str(escape(p["title"])) in html
        assert p["amount_label"] in html
        assert str(escape(p["description"])) in html
        assert str(escape(p["limitation"])) in html
        assert p["source"] in html
        assert f'href="{p["sector_url"]}"' in html
        assert f'href="/wheres-my-money/spending/programmes/"' in html
        assert "cannot establish better results" in html
        if p["parent_record"]:
            assert f'href="{p["parent_record"]["url"]}"' in html


def test_sectors_render_nonadditive_inhouse_charts():
    d = fixture()
    template = jinja().get_template("spending_sector.html")
    for c in d["categories"]:
        html = template.render(**context(), spending=d, sector=c, sector_index=1, schema={"@type":"WebPage"})
        assert 'id="programmes"' in html
        assert "Do not add the bars together" in html
        assert html.count("wmex-programme-chart-row") == len(c["programmes"])
        for p in c["programmes"]:
            assert f'href="{p["url"]}"' in html
            assert p["amount_label"] in html


def test_no_external_chart_dependencies_or_sensitive_inputs_in_search():
    js = (ROOT / "compound/site/static/spending-explorer.js").read_text(encoding="utf-8")
    assert "data-programme-search" in js
    assert "fetch(" not in js
    assert "XMLHttpRequest" not in js
    assert "wmm-salary" not in js
    assert "gtag(" not in js
