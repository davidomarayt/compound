#!/usr/bin/env python3
"""Automatic, source-gated Magnificent Seven publisher; never use generated covers."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from html import unescape
from io import BytesIO
import json
import os
from pathlib import Path
import re

import httpx
from PIL import Image, ImageOps
import yaml
import mag7_pilot as pilot

ROOT = Path(__file__).resolve().parents[1]
ANGLES = {
 "TSLA": ("roadster-economics", "Roadster and vehicle economics", "Autonomy economics", "Energy cash conversion", "Automotive profit resilience"),
 "MSFT": ("azure-ai-economics", "Azure AI capital expenditure and returns", "Microsoft 365 subscription economics", "Cloud margin durability", "AI cash-flow conversion"),
 "NVDA": ("ai-gpu-margins", "Data Centre and GPU profitability", "Customer concentration", "Supply chain economics", "Revenue and profit durability"),
 "AAPL": ("iphone-services-profit", "iPhone versus Services profitability", "Geographic demand", "Cash returns versus EPS", "Device replacement economics"),
 "AMZN": ("aws-retail-profit", "AWS versus retail economics", "AI capex and cash flow", "Retail operating margins", "Non-operating gains"),
 "GOOGL": ("ai-search-economics", "Search advertising versus AI cost", "Cloud profits", "Capital intensity", "Ad revenue concentration"),
 "META": ("ai-advertising-roi", "Advertising and AI investment returns", "Reality Labs losses", "Impressions and ad pricing", "Cash flow sustainability"),
}
HEADINGS = ["What changed", "What the numbers say", "The investment case",
            "Risks and counterarguments", "What to watch", "Sources and methodology"]


def photo_for(ticker: str, week: int) -> dict:
    library = json.loads((ROOT / "content/mag7-photo-library.json").read_text("utf-8"))
    pictures = library["photos"][ticker]
    photo = pictures[(week - 1) % len(pictures)]
    if not photo["source"].startswith("https://unsplash.com/photos/"):
        raise ValueError("Photo not approved from free Unsplash library")
    if not photo["credit"].endswith("/ Unsplash"):
        raise ValueError("Photo missing verified attribution")
    return photo


def fetch_real_photo(photo: dict, target: Path) -> None:
    """Download approved authentic picture. Never use search/fallback imagery."""
    page_url = photo["source"].rstrip("/")
    headers = {"User-Agent": "Mozilla/5.0 (Compound.ie documentary photo fetch)", "Accept": "*/*"}
    with httpx.Client(timeout=45, follow_redirects=True, headers=headers) as client:
        response = client.get(page_url + "/download?force=true&w=1800")
        if not response.headers.get("content-type", "").lower().startswith("image/"):
            page = client.get(page_url, headers={"User-Agent": headers["User-Agent"], "Accept": "text/html"})
            page.raise_for_status()
            match = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', page.text)
            if match:
                url = unescape(match.group(1))
            else:
                match = re.search(r'https://images\.unsplash\.com/photo-[A-Za-z0-9-]+',page.text)
                if not match:
                    raise ValueError("Approved photo page did not expose an image")
                url = match.group(0)
            if not url.startswith("https://images.unsplash.com/"):
                raise ValueError("Photo download was not from Unsplash CDN")
            response = client.get(url)
        response.raise_for_status()
        if len(response.content) < 65000:
            raise ValueError("Approved real photo payload too small")
        with Image.open(BytesIO(response.content)) as original:
            if original.width < 1200 or original.height < 675:
                raise ValueError("Photo resolution too small")
            image = ImageOps.fit(original.convert("RGB"), (1600, 900), method=Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, format="JPEG", quality=89, progressive=True, optimize=True)


def model_text(message) -> str:
    return "\n".join(part.text for part in message.content if getattr(part, "type", "") == "text").strip()


def model_json(raw: str) -> dict:
    raw = raw.strip()
    if not raw.startswith("{"):
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("AI response was not structured JSON")
        raw = raw[start:end+1]
    return json.loads(raw)


def research(ai, ticker: str, week: int, day: date, sec: dict) -> dict:
    note = pilot.brief(day,ticker,week,sec,pilot.headlines(ticker,day),pilot.duplicates(ticker))
    instructions = (
        "You are the independent financial research desk at Compound.ie. "
        "Use web_search to VERIFY current claims and read official reporting. "
        "The supplied SEC numbers are historical and filing-backed. "
        "Never invent segment results, quotes, dates, prices, analyst expectations "
        "or recent developments. Never mistake fiscal-year labels for calendar years. "
        "Produce thoughtful ORIGINAL investment research, not a press release rewrite. "
        "Use one transparent numerical scenario or calculation grounded in the filing, "
        "distinguish facts from explicit assumptions and explain both bull and bear cases. "
        "If a new event is not source-confirmed, analyse evergreen business economics instead. "
        "Skip publication if it would repeat an existing Compound article. "
        "Return ONLY one valid JSON object with: publish (boolean), title, seo_title, "
        "meta_description (130-160 characters), summary (110-230 characters), "
        "body_markdown (850-1500 words), sources (array of >=3 objects with title and url "
        "for sources actually checked), blockers (array), and x_post (short). "
        "In body use these H2 headings: " + ", ".join(HEADINGS) + ". "
        "Cite exact sources inline as Markdown links. Always include original SEC URL "
        "from brief, https://compound.ie/stocks/" + ticker.lower() +
        "/ and https://compound.ie/wealth/earnings/. "
        "Separate audited/reported numbers from forecasts. No investment advice. "
        "Do not fabricate data to fill missing historical quarters. "
        "Decline rather than invent an assertion. Never produce images."
    )
    message = ai.messages.create(
        model=(os.getenv("MAG7_MODEL") or "claude-sonnet-4-5"),max_tokens=6800,temperature=0.15,
        tools=[{"type":"web_search_20250305","name":"web_search","max_uses":7}],
        system=instructions,
        messages=[{"role":"user","content":
            f"Assignment: {pilot.COMPANIES[ticker][0]} ({ticker}), {day}, "
            f"pilot week {week}, unique thesis: {ANGLES[ticker][week]}. "
            "The proposed article must be distinct from these existing titles. "
            "Commissioning brief follows:\n"+note}],
    )
    return model_json(model_text(message))


def validate(data: dict, ticker: str, sec: dict) -> None:
    if data.get("publish") is not True or data.get("blockers"):
        raise ValueError("Model could not verify publishable original research")
    body = data.get("body_markdown","")
    if not 780 <= len(body.split()) <= 1800:
        raise ValueError("Article too short, long, or empty")
    for heading in HEADINGS:
        if not re.search(r"(?mi)^##\s+"+re.escape(heading)+r"\s*$",body):
            raise ValueError("Missing research heading: "+heading)
    bad = ["DRAFT ONLY","TODO","TBD","[citation needed]","not verified",
           "claims requiring human confirmation","lorem ipsum"]
    if any(term.lower() in body.lower() for term in bad):
        raise ValueError("Draft contains unresolved editorial blockers")
    if f"/stocks/{ticker.lower()}/" not in body or "/wealth/earnings/" not in body:
        raise ValueError("Missing crosslinks to company and earnings")
    sources=data.get("sources") or []
    urls=[entry.get("url","") for entry in sources if isinstance(entry,dict)]
    if len(set(urls)) < 3 or sec["filing"] not in urls or sec["filing"] not in body:
        raise ValueError("Insufficient verified references, including actual SEC filing")
    if len({url.split("/")[2] for url in urls}) < 2 or not all(url.startswith("https://") for url in urls):
        raise ValueError("Sources not independent HTTPS references")
    if sum(1 for url in urls if url in body) < 3:
        raise ValueError("Body does not cite research references")
    if not 100 <= len(data.get("summary","")) <= 260:
        raise ValueError("Missing useful article description")
    if not 110 <= len(data.get("meta_description","")) <= 175:
        raise ValueError("Invalid search description")
    if not 15 <= len(data.get("title","")) <= 105:
        raise ValueError("Invalid article headline")


def independent_review(ai, data: dict, sec: dict) -> None:
    prompt = (
        "Act as a strict second independent publication editor. Use web_search to check "
        "multiple current material assertions in this financial report, sources, "
        "chronology and any scenario arithmetic. Reject if material facts are "
        "unsupported, sources cannot be confirmed, calculations are inconsistent, "
        "the writing is generic/duplicated, or financial terminology is misleading. "
        "Do not grant publication unless clearly justified. "
        "Respond ONLY as JSON: {\"pass\":boolean,\"problems\":[strings]}. "
        "Review input:\n"+json.dumps({"sec":sec,"article":data},ensure_ascii=False)[:26000]
    )
    response=ai.messages.create(
        model=(os.getenv("MAG7_EDITOR_MODEL") or os.getenv("MAG7_MODEL") or "claude-sonnet-4-5"),
        max_tokens=1300,temperature=0,
        tools=[{"type":"web_search_20250305","name":"web_search","max_uses":4}],
        messages=[{"role":"user","content":prompt}],
    )
    verdict=model_json(model_text(response))
    if verdict.get("pass") is not True or verdict.get("problems"):
        raise ValueError("Independent review failed: "+str(verdict.get("problems"))[:450])


def article(day: date,ticker: str,week: int,data: dict,photo: dict) -> tuple[Path,Path,str]:
    topic=ANGLES[ticker][0] if week == 1 else re.sub(r"[^a-z0-9]+","-",ANGLES[ticker][week].lower()).strip("-")[:36]
    slug=f"{ticker.lower()}-{topic}-{day.isoformat()}"
    path=ROOT/"content/wealth"/(slug+".md")
    image=ROOT/"compound/site/static/images/evergreen"/(slug+".jpg")
    if path.exists():
        raise ValueError("Canonical article already exists; duplicate publication forbidden")
    fetch_real_photo(photo,image)
    image_url="/static/images/evergreen/"+slug+".jpg"
    metadata={
        "title":data["title"],"seo_title":data.get("seo_title",data["title"]),
        "slug":slug,"canonical_path":"/wealth/"+slug+"/","pillar":"wealth",
        "draft":False,"publication_status":"published",
        "date":day.isoformat(),"reviewed":day.isoformat(),
        "approved_by":"Automatic evidence-checked Mag7 research publication",
        "summary":data["summary"],"meta_description":data["meta_description"],
        "tags":["wealth","stocks","company-research","mag7-research",
                ticker.lower(),"investor-research"],
        "image":image_url,"social_image":image_url,
        "image_alt":photo["alt"],
        "image_credit":photo["credit"]+" ("+photo["year"]+"; Unsplash License)",
        "image_source":photo["source"],"require_pinned_hero":True,
        "sources":[{"title":item["title"],"url":item["url"]} for item in data["sources"]],
    }
    caption=(
        "*Cover: authentic archival photograph by "+photo["credit"]+
        " ("+photo["year"]+"). [Original photo and licence]("+photo["source"]+
        "). This image does not depict today's event.*\n\n"
    )
    path.write_text("---\n"+yaml.safe_dump(metadata,allow_unicode=True,sort_keys=False,width=120)+
                    "---\n\n"+caption+data["body_markdown"].strip()+
                    "\n\n*This article was automatically published following AI-assisted source and editorial checks. "
                    "It is informational analysis, not personal investment advice.*\n",encoding="utf-8")
    return path,image,slug


def run(day: date,output: Path) -> int:
    slot=pilot.assignment(day)
    if slot is None:
        print("Pilot ended; nothing created")
        return 3
    ticker,week=slot
    report=[f"# Mag 7 {day.isoformat()} {ticker} review record",""]
    try:
        # The first day was already written and published in the existing workflow.
        if day == pilot.START and ticker == "TSLA":
            raise ValueError("16 October Tesla Roadster article already published")
        sec=pilot.latest_sec(ticker)
        photo=photo_for(ticker,week)
        from anthropic import Anthropic
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY GitHub Actions secret missing")
        ai=Anthropic(timeout=140)
        data=research(ai,ticker,week,day,sec)
        validate(data,ticker,sec)
        independent_review(ai,data,sec)
        page,image,slug=article(day,ticker,week,data,photo)
        report.extend(["**Status: accepted for automatic publication**",
                       f"**URL:** https://compound.ie/wealth/{slug}/",
                       f"**Title:** {data['title']}","",
                       "## Sources",*("- "+x["url"] for x in data["sources"]),
                       "","## Approved real photograph",
                       photo["source"],photo["credit"],"",
                       "## X post draft",data.get("x_post","")])
    except Exception as exc:  # Every fault fails closed; write audit status instead of an unsafe page.
        report.extend(["**Status: skipped — nothing automatically published**",
                       f"Reason: {type(exc).__name__}: {str(exc)[:500]}",
                       "No filler article and no synthetic image permitted."])
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text("\n".join(report)+"\n",encoding="utf-8")
    return 0


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--date",default=datetime.now(timezone.utc).date().isoformat())
    p.add_argument("--output",default="mag7-review.md")
    args=p.parse_args()
    return run(date.fromisoformat(args.date),Path(args.output))


if __name__=="__main__":
    raise SystemExit(main())
