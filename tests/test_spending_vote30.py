"""Vote 30 agriculture subheads: source figures, rendered charts, and canonical links."""
import json
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape
from compound.site.spending_vote30 import prepare_vote30_subheads

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/"content"
TEMPLATES=ROOT/"compound"/"site"/"templates"

def register():
    return json.loads((CONTENT/"public-spending-vote30-subheads-2026.json").read_text())

def fake_spending():
    sectors=[{"id":x} for x in ("social","health","education","housing","transport","justice","other","debt")]
    votes=[{"number":30,"net_supply_eur":1817835000,"title":"Agriculture","detail":True}]
    return {"votes":votes,"categories":sectors}

def data():
    return prepare_vote30_subheads(fake_spending(),register())["vote30_account"]

def env():
    return Environment(loader=FileSystemLoader(str(TEMPLATES)),autoescape=select_autoescape(["html"]))

def context():
    return dict(site_url="https://compound.ie",title="Agriculture REV 2026",
        site_identity_jsonld="{}",year=2026,adsense={"client":""},analytics={"measurement_id":""})

def test_all_programmes_reconcile_and_net_matches_approved_grant():
    a=data()
    assert a["subhead_count"]==34
    assert [p["code"] for p in a["programmes"]]==list("ABCD")
    assert [len(p["rows"]) for p in a["programmes"]]==[5,16,13,0]
    for p in a["programmes"][:3]:
        assert sum(i["amount_2025"] for i in p["rows"])==p["total_2025"]
        assert sum(i["amount_2026"] for i in p["rows"])==p["total_2026"]
    assert sum(p["total_2026"] for p in a["programmes"])==2316966
    assert a["totals"]["gross_2026"]-a["totals"]["appropriations_2026"]==a["totals"]["net_2026"]==1817835
    assert len({i["url"] for i in a["subheads"]})==34
    assert next(i for i in a["subheads"] if i["code"]=="B.17")["amount_2026"]==0
    assert next(i for i in a["subheads"] if i["code"]=="B.14")["amount_2026"]==280000

def test_corrupt_subhead_or_net_fails_closed():
    import copy
    for operation,expected in [
       (lambda x:x["programmes"][0]["rows"][0].update({"amount_2026":0}),"do not reconcile"),
       (lambda x:x["totals"].update({"net_2026":1}),"gross minus"),
       (lambda x:x["programmes"][1]["rows"][2].update({"code":"B.1"}),"duplicate"),
    ]:
       x=copy.deepcopy(register());operation(x)
       with pytest.raises(ValueError,match=expected):
          prepare_vote30_subheads(fake_spending(),x)

def test_hub_has_local_source_backed_charts_and_inhouse_links():
    a=data()
    html=env().get_template("spending_subheads_vote30.html").render(
       **context(),account=a,spending={},schema={"@type":"CollectionPage"})
    assert 'href="https://compound.ie'+a["url"]+'"' in html
    assert html.count('class="wmex-programme-chart-row"')==34
    assert "Appropriations-in-Aid" in html
    assert "€2.317bn" in html
    assert "34" in html
    for i in a["subheads"]:
       assert f'href="{i["url"]}"' in html

def test_all_subhead_pages_have_correct_sources_canonicals_and_original_text():
    a=data()
    tpl=env().get_template("spending_subhead_detail.html")
    for i in a["subheads"]:
       html=tpl.render(**context(),item=i,account=a,spending={},schema={"@type":"WebPage"})
       assert f'href="https://compound.ie{i["url"]}"' in html
       assert i["title"] in html
       assert i["amount_label"] in html
       assert "Supplementary Estimate" in html
       assert "Revised Estimate" in html
       assert a["source"] in html

def test_article_remains_single_canonical_microsoft_news():
    text=(CONTENT/"wealth"/"microsoft-365-outage-outlook-teams-november-13-2026.md").read_text()
    assert text.count("canonical_path: /news/microsoft-365-outage-outlook-teams-november-13-2026/")==1
    assert "Latest verified update" in text
    assert "EX1550543" in text
    assert "require_pinned_hero: true" in text
