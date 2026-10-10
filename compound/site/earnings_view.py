"""Presentation adapter for one canonical earnings report per public company.

Legacy quarter articles are used as a temporary data source until a monitor
ingests the exact SEC filings; legacy URLs redirect to /stocks/<ticker>/.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import re
import yaml

METRICS = ("revenue", "net_income", "diluted_eps")


def _from_legacy(article):
    if not article.path or not article.path.is_file():
        return None
    raw = article.path.read_text(encoding="utf-8")
    chunks = raw.split("---", 2)
    if len(chunks) < 3:
        return None
    meta = yaml.safe_load(chunks[1]) or {}
    snapshot = meta.get("earnings_snapshot") or {}
    label = snapshot.get("period_label", "")
    matched = re.search(r"FY\s*(\d{4})\s*(Q[123]|full-year)", label, re.I)
    if not matched:
        return None
    fiscal_year, quarter = int(matched.group(1)), matched.group(2).upper()
    if quarter == "FULL-YEAR":
        quarter = "FY"
    end = snapshot.get("report_end", "")
    if not end or end < "2026-01-01":
        return None
    facts = snapshot.get("metrics") or {}
    if any(k not in facts for k in METRICS):
        return None
    sources = meta.get("sources") or []
    url = sources[0].get("url", "") if sources else ""
    filing_date = ""
    if sources:
        mo = re.search(r"filed\s*(\d{4}-\d{2}-\d{2})",sources[0].get("title",""))
        filing_date = mo.group(1) if mo else ""
    return {
        "fy": fiscal_year, "fp": quarter, "period_end": end, "filed": filing_date,
        "form": snapshot.get("form",""),
        "accession": meta.get("filing_accession", ""),
        "source": url, "metrics": {
            key: {"current": facts[key].get("current"), "prior_year": facts[key].get("prior"),
                  "unit": "USD/shares" if key == "diluted_eps" else "USD",
                  "tag": "SEC XBRL"} for key in METRICS
        },
    }


def load_company_report(content_dir: Path, ticker: str, legacy_articles=()):
    target = content_dir / "earnings-profiles" / (ticker.lower() + ".json")
    data = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
    periods = [p for p in (data.get("periods") or []) if p.get("period_end","") >= "2026-01-01"]
    seen = {(p["fy"],p["fp"]) for p in periods}
    for article in legacy_articles:
        if ticker.lower() not in article.tags:
            continue
        p = _from_legacy(article)
        if p and (p["fy"], p["fp"]) not in seen:
            periods.append(p)
            seen.add((p["fy"], p["fp"]))
    if not periods:
        return None
    latest = max(periods, key=lambda p: (p["period_end"], p.get("filed","")))
    fy = latest["fy"]
    current = {p["fp"]:p for p in periods if p["fy"] == fy}
    rows = [current.get(f"Q{i}") for i in (1,2,3)]
    def money(v,key):
        if v is None:
            return "—"
        if key == "diluted_eps":
            return f"${v:,.2f}"
        val = abs(v)
        sign = "−" if v<0 else ""
        return f"{sign}${val/1e9:,.2f}bn" if val>=1e9 else (
            f"{sign}${val/1e6:,.2f}m" if val>=1e6 else f"{sign}${val:,.0f}")
    def percent(a,b,key):
        if not a or not b:
            return None
        curr=a["metrics"][key]["current"]
        prev=b["metrics"][key]["current"]
        if not isinstance(curr,(float,int)) or not isinstance(prev,(float,int)) or prev<=0:
            return None
        return round((curr / prev-1)*100,1)
    q3q2={k:percent(rows[2],rows[1],k) for k in METRICS}
    end_at=max([i for i,x in enumerate(rows) if x],default=-1)
    contiguous=end_at>=0 and all(rows[i] for i in range(end_at+1))
    totals={key:sum(x["metrics"][key]["current"] for x in rows[:end_at+1])
            for key in ("revenue","net_income")} if contiguous else {}
    totals_prior={}
    if contiguous:
        for key in ("revenue","net_income"):
            comparable=[r["metrics"][key].get("prior_year") for r in rows[:end_at+1]]
            if all(isinstance(v,(int,float)) for v in comparable):
                totals_prior[key]=sum(comparable)
    ytd_yoy={
        key:round((totals[key]/totals_prior[key]-1)*100,1)
        if key in totals and totals_prior.get(key,0)>0 else None
        for key in ("revenue","net_income")
    }
    chart_max={key:max((abs(x["metrics"][key]["current"]) for x in rows if x),default=0)
               for key in METRICS}
    display=[]
    for i,r in enumerate(rows):
        if not r:
            display.append({"label":f"Q{i+1}","available":False})
            continue
        vals={key:money(r["metrics"][key]["current"],key) for key in METRICS}
        bars={key: round(abs(r["metrics"][key]["current"])/chart_max[key]*100)
              if chart_max[key] else 0 for key in METRICS}
        display.append({"label":f"Q{i+1}","available":True,"period_end":r["period_end"],
                        "filed":r.get("filed",""),"source":r.get("source",""),
                        "figures":vals,"bars":bars,"fiscal_year":r["fy"]})
    yoy={k: percent({"metrics":{k:{"current":latest["metrics"][k]["current"]}}},
                    {"metrics":{k:{"current":latest["metrics"][k].get("prior_year")}}},k)
         for k in METRICS}
    data_out={"fy":fy,"latest_label":f"FY{fy} {latest['fp']}",
              "latest_end":latest["period_end"],"latest_filed":latest.get("filed",""),
              "latest_source":latest.get("source",""),"latest_form":latest.get("form",""),
              "quarters":display,"q3q2":q3q2,"yoy":yoy,
              "total_revenue":money(totals["revenue"],"revenue") if totals else None,
              "total_net":money(totals["net_income"],"net_income") if totals else None,
              "ytd_complete":bool(totals),"ytd_yoy":ytd_yoy,"through":f"Q{end_at+1}" if end_at>=0 else "",
              "summary":("All three fiscal quarters are available" if all(rows)
                         else "Only SEC-verified, available quarters are shown"),
              "period_count":len(periods)}
    return data_out
