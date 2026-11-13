"""Exact 2026 Vote 30 gross/current programme and expenditure subhead accounting.

Amounts from February 25 Oireachtas committee submission are in €000. Only
programmes A/B/C have complete subhead tables; D deliberately has no invented
subheads. A-in-A is subtracted to form the net grant, not an expenditure line.
"""
from __future__ import annotations
import math
import re
from copy import deepcopy
from urllib.parse import urlparse

EXPECTED = {"A":(5,495695,513929),"B":(16,1132652,1152675),"C":(13,436004,470272),"D":(0,173570,180090)}

def prepare_vote30_subheads(spending:dict, register:dict)->dict:
    if register.get("year")!=2026 or register.get("vote")!=30 or register.get("unit")!="EUR thousands":
        raise ValueError("Unexpected Vote 30 accounting period, vote or unit")
    src=urlparse(str(register.get("source") or ""))
    if src.scheme!="https" or src.hostname!="data.oireachtas.ie":
        raise ValueError("Vote 30 must cite a primary Oireachtas source")
    groups=deepcopy(register.get("programmes") or [])
    if [x.get("code") for x in groups] != list(EXPECTED):
        raise ValueError("Incomplete Vote 30 programme order")
    path="/wheres-my-money/spending/votes/vote-30-agriculture-food-and-the-marine-2026/"
    seen=set()
    all_subheads=[]
    for group in groups:
        n,prev,total=EXPECTED[group["code"]]
        rows=group.get("rows") or []
        if len(rows)!=n or group["total_2025"]!=prev or group["total_2026"]!=total:
            raise ValueError("Vote 30 programme figures or row count differ from the published table")
        if sum(v["amount_2025"] for v in rows)!=prev and n:
            raise ValueError("2025 subheads do not reconcile")
        if sum(v["amount_2026"] for v in rows)!=total and n:
            raise ValueError("2026 subheads do not reconcile")
        group["difference_000"]=total-prev
        group["amount_label"]="€{:,.3f}m".format(total/1000)
        group["url"]=path+"subheads/#programme-"+group["code"].lower()
        max_value=max((v["amount_2026"] for v in rows),default=1)
        for item in rows:
            code=item["code"]
            if not re.fullmatch(r"[ABC]\.\d{1,2}",code) or not code.startswith(group["code"]+".") or code in seen:
                raise ValueError("Invalid or duplicate subhead code")
            seen.add(code)
            if not item.get("title") or any(not isinstance(item[y],int) or item[y]<0 or not math.isfinite(item[y]) for y in ("amount_2025","amount_2026")):
                raise ValueError("Invalid subhead figure")
            item["programme_code"]=group["code"]
            item["programme_title"]=group["title"]
            item["amount_label"]="€{:,.3f}m".format(item["amount_2026"]/1000)
            item["delta_000"]=item["amount_2026"]-item["amount_2025"]
            item["delta_pct"]=100*(item["delta_000"]/item["amount_2025"]) if item["amount_2025"] else None
            item["bar_width"]=100*item["amount_2026"]/max_value if max_value else 0
            item["slug"]="subhead-"+code.lower().replace(".","-")
            item["url"]=path+item["slug"]+"/"
            all_subheads.append(item)
    totals=register["totals"]
    for year in (2025,2026):
        if sum(g["total_"+str(year)] for g in groups)!=totals["gross_"+str(year)]:
            raise ValueError("Vote 30 programme gross does not reconcile")
        if totals["gross_"+str(year)]-totals["appropriations_"+str(year)]!=totals["net_"+str(year)]:
            raise ValueError("Vote 30 gross minus Appropriations-in-Aid does not equal net")
    matching=next((v for v in spending["votes"] if v["number"]==30),None)
    if not matching or matching["net_supply_eur"]!=totals["net_2026"]*1000:
        raise ValueError("Vote 30 net supply must match the Dáil vote record")
    matching["detail"]=True
    matching["vote30_subheads_url"]=path+"subheads/"
    matching["url"]=path
    matching["related_subhead_count"]=len(all_subheads)
    for category in spending["categories"]:
        if category["id"]=="other":
            category["vote30_subheads_url"]=path+"subheads/"
    return {**spending,"vote30_account":{**register,"programmes":groups,"subheads":all_subheads,
        "url":path+"subheads/","vote_url":path,"subhead_count":len(all_subheads),
        "gross_2026_eur":totals["gross_2026"]*1000}}
