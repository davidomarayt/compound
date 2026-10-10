"""Regression tests for one canonical company earnings report and fiscal-quarter math."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import earnings_consolidated as consolidated
from compound.site.earnings_view import load_company_report
from compound.site.build import build_site


def record(fy, fp, period_end, filed, accession, revenue, net, eps, start):
    return {
        "fy":fy,"fp":fp,"period_end":period_end,"filed":filed,
        "accession":accession,"form":"10-Q","source":"https://www.sec.gov/Archives/example.htm",
        "metrics":{
            "revenue":{"current":revenue,"prior_year":revenue*.9,"unit":"USD","tag":"Revenues"},
            "net_income":{"current":net,"prior_year":net*.9,"unit":"USD","tag":"NetIncomeLoss"},
            "diluted_eps":{"current":eps,"prior_year":eps*.9,"unit":"USD/shares","tag":"EarningsPerShareDiluted"},
        }
    }


def test_fiscal_q3_q2_and_verified_ytd(tmp_path):
    records=[
        record(2026,"Q1","2026-03-31","2026-05-09","accn1",10e9,2e9,1.00,"2026-01-01"),
        record(2026,"Q2","2026-06-30","2026-08-08","accn2",12e9,2.2e9,1.15,"2026-04-01"),
        record(2026,"Q3","2026-09-30","2026-10-09","accn3",15e9,3e9,1.40,"2026-07-01"),
    ]
    folder=tmp_path/"earnings-profiles"
    folder.mkdir()
    (folder/"aapl.json").write_text(json.dumps({
        "ticker":"AAPL","company":"Apple","cik":320193,"periods":records,
        "latest":records[-1],"updated":"2026-10-10"
    }))
    report=load_company_report(tmp_path,"AAPL")
    assert report["fy"] == 2026
    assert report["latest_label"]=="FY2026 Q3"
    assert report["q3q2"]["revenue"]==25.0
    assert report["q3q2"]["net_income"]==36.4
    assert report["total_revenue"]=="$37.00bn"
    assert report["ytd_complete"]
    assert len(report["quarters"])==3
    assert all(row["source"].startswith("https://www.sec.gov") for row in records)


def test_fiscal_2027_q1_ended_2026_is_not_wrong_q3(tmp_path):
    folder=tmp_path/"earnings-profiles"; folder.mkdir()
    data=record(2027,"Q1","2026-08-31","2026-10-08","accn",3000000000,100000000,0.8,"2026-06-01")
    data["metrics"]["revenue"]["current"]=3000000000
    data["metrics"]["net_income"]["current"]=100000000
    (folder/"ctas.json").write_text(json.dumps({
        "ticker":"CTAS","company":"Cintas","cik":723254,
        "periods":[data],"latest":data,"updated":"2026-10-10"
    }))
    report=load_company_report(tmp_path,"CTAS")
    assert report["latest_label"]=="FY2027 Q1"
    assert report["latest_end"]=="2026-08-31"
    assert report["quarters"][0]["available"]
    assert not report["quarters"][2]["available"]
    assert report["q3q2"]["revenue"] is None


def test_no_pre_2026_historical_quarters(tmp_path):
    folder=tmp_path/"earnings-profiles"; folder.mkdir()
    valid=record(2026,"Q2","2026-06-30","2026-08-08","accn2",10e9,2e9,1,"2026-04-01")
    old=record(2026,"Q1","2025-12-31","2026-02-08","accn1",9e9,1e9,.5,"2025-10-01")
    (folder/"ex.json").write_text(json.dumps({
        "ticker":"EX","company":"Example","cik":101,
        "periods":[old,valid],"latest":valid
    }))
    view=load_company_report(tmp_path,"EX")
    assert not view["quarters"][0]["available"]
    assert not view["ytd_complete"]
    assert view["total_revenue"] is None


def test_legacy_article_redirects_to_one_company_url(settings):
    import yaml
    (settings.content_dir/"earnings-sp500.json").write_text(json.dumps({
       "source":"https://sec.example.test","checked":"2026-10-10",
       "company_count":1,"security_count":1,
       "members":[{"name":"Cintas","symbol":"CTAS","symbols":["CTAS"],
                   "cik":723254,"active":True,"sector":"Industrials"}]
    }))
    d=settings.content_dir/"wealth";d.mkdir(parents=True,exist_ok=True)
    (d/"ctas-earnings-fy2027-q1.md").write_text("""---
title: Cintas fiscal FY2027 Q1 results
slug: ctas-earnings-fy2027-q1
pillar: wealth
canonical_path: /wealth/earnings/ctas-earnings-fy2027-q1/
date: 2026-10-10
summary: Cintas SEC 10-Q
tags: [earnings,automated-earnings,ctas]
earnings_snapshot:
  form: 10-Q
  report_end: '2026-08-31'
  period_label: FY 2027 Q1
  metrics:
    revenue: {current: 3000000000, prior: 2600000000}
    net_income: {current: 300000000, prior: 250000000}
    diluted_eps: {current: 1.20, prior: 1.00}
sources:
  - title: SEC EDGAR Cintas 10-Q filed 2026-10-08
    url: https://www.sec.gov/Archives/edgar/data/723254/fake.htm
---
Legacy article content.
""")
    build_site(settings)
    root=settings.public_dir
    old=(root/"wealth/earnings/ctas-earnings-fy2027-q1/index.html").read_text()
    hub=(root/"wealth/earnings/index.html").read_text()
    profile=(root/"stocks/ctas/index.html").read_text()
    sitemap=(root/"sitemap.xml").read_text()
    assert 'http-equiv="refresh"' in old
    assert 'https://example.test/stocks/ctas/' in old
    assert "one constantly updated earnings dashboard" in hub
    assert "FY2027 Q1" in profile
    assert "2026-08-31" in profile
    assert '<loc>https://example.test/wealth/earnings/ctas-earnings-fy2027-q1/</loc>' not in sitemap
    assert '<loc>https://example.test/stocks/ctas/</loc>' in sitemap
    assert "Cintas fiscal FY2027 Q1 results" not in hub


def test_q3_sec_trigger_hydrates_q1_and_q2_from_exact_same_fiscal_year():
    accns = ["0000000001-26-000111", "0000000001-26-000222", "0000000001-26-000333"]
    ends = ["2026-03-31","2026-06-30","2026-09-30"]
    starts = ["2026-01-01","2026-04-01","2026-07-01"]
    pends = ["2025-03-31","2025-06-30","2025-09-30"]
    pstarts = ["2025-01-01","2025-04-01","2025-07-01"]
    filed = ["2026-05-10","2026-08-10","2026-10-09"]
    forms = []
    for i in range(3):
        forms.append({"form":"10-Q","filingDate":filed[i],"reportDate":ends[i],
                      "accessionNumber":accns[i],"primaryDocument":f"q{i+1}.htm"})
    keys=("accessionNumber","form","filingDate","reportDate","primaryDocument")
    submissions={"filings":{"recent":{k:[f[k] for f in forms] for k in keys}}}
    facts={"facts":{"us-gaap":{}}}
    for tag,unit,multiplier in [
        ("RevenueFromContractWithCustomerExcludingAssessedTax","USD",1e9),
        ("NetIncomeLoss","USD",1e8),
        ("EarningsPerShareDiluted","USD/shares",0.3),
    ]:
        rows=[]
        for i in range(3):
            base={"form":"10-Q","filed":filed[i],
                  "fy":2026,"fp":f"Q{i+1}","accn":accns[i]}
            rows.extend([
                {**base,"start":starts[i],"end":ends[i],
                 "val":(10+2*i+(1 if i==2 else 0))*multiplier},
                {**base,"start":pstarts[i],"end":pends[i],
                 "val":(9+2*i)*multiplier},
            ])
        facts["facts"]["us-gaap"][tag]={"units":{unit:rows}}
    result=consolidated.dashboard(
        None,"AAPL","Apple",320193,forms[2],submissions,facts,
        checked=date(2026,10,10))
    assert result is not None
    assert [(p["fy"],p["fp"]) for p in result["periods"]] == [
        (2026,"Q1"),(2026,"Q2"),(2026,"Q3")]
    assert [p["period_end"] for p in result["periods"]] == ends
    view=consolidated.summary(result)
    assert view["comparisons"]["revenue"] == 25.0
    assert view["complete_ytd"] is True
    assert view["totals"]["revenue"] == 37e9
    assert result["latest"]["period_end"] == "2026-09-30"
    assert all(p["source"].startswith("https://www.sec.gov") for p in result["periods"])


def test_fy2027_q1_filed_2026_remains_fiscal_q1():
    filing={"form":"10-Q","filingDate":"2026-10-08",
            "reportDate":"2026-08-31","accessionNumber":"0000723254-26-000047",
            "primaryDocument":"fy27q1.htm"}
    metrics={key:{"current":100 if key!="diluted_eps" else 1.0,
                  "prior":90 if key!="diluted_eps" else 0.9,
                  "unit":"USD/shares" if key=="diluted_eps" else "USD",
                  "tag":key,"start":"2026-06-01","end":"2026-08-31",
                  "fy":2027,"fp":"Q1"} for key in ("revenue","net_income","diluted_eps")}
    quarter=consolidated.verified_period(filing,metrics,723254)
    assert quarter["fy"] == 2027
    assert quarter["fp"] == "Q1"
    assert quarter["period_end"] == "2026-08-31"
