"""Rebuild the title/URL register used to prevent duplicate Compound content."""
from __future__ import annotations
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://compound.ie"
PILLARS = (("health", "Health"), ("wealth", "Wealth"), ("happiness", "Life"))
HUBS = (
    ("Home", "/"), ("Health", "/health/"), ("Wealth", "/wealth/"), ("Life", "/life/"),
    ("News", "/news/"), ("Tools and Calculators", "/tools/"), ("Stocks Directory", "/stocks/"),
    ("Company Earnings and Financial Results", "/wealth/earnings/"),
    ("Private Company Research Directory", "/companies/"), ("PIA Centre", "/pia/"),
    ("PIA Providers", "/pia/providers/"), ("Search", "/search/"),
    ("Live to 100 Series", "/live-to-100/"),
)

def frontmatter(path):
    raw = path.read_text(encoding="utf-8-sig")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", raw, re.S)
    return (yaml.safe_load(match.group(1)) or {}) if match else {}

def item(title, url, source, kind, **rest):
    return dict(title=str(title), url=str(url), source=str(source), kind=kind, **rest)

def ordered(rows):
    return sorted(rows, key=lambda r: (r["title"].casefold(), r["url"]))

def link(row):
    label = row["title"].replace("[", "\\[").replace("]", "\\]")
    return "[" + label + "](" + HOST + row["url"] + ")"

def build():
    articles, earnings, drafts, errors = [], [], [], []
    for pillar, category in PILLARS:
        for path in sorted((ROOT / "content" / pillar).glob("*.md")):
            meta = frontmatter(path)
            if not meta.get("title"):
                errors.append("Missing title: " + str(path.relative_to(ROOT)))
                continue
            slug = str(meta.get("slug") or path.stem)
            public_pillar = "life" if pillar == "happiness" else pillar
            url = str(meta.get("canonical_path") or ("/" + public_pillar + "/" + slug + "/"))
            tags = list(meta.get("tags") or [])
            is_earnings = "automated-earnings" in tags or bool(re.search(r"earnings-fy20\d\d", slug))
            status = "draft" if meta.get("draft") or meta.get("publication_status", "published") != "published" else "published"
            row = item(meta["title"], url, path.relative_to(ROOT),
                       "Earnings source file" if is_earnings else "Editorial article / guide",
                       category=category, slug=slug, date=str(meta.get("date") or ""),
                       reviewed=str(meta.get("reviewed") or ""), tags=tags, status=status)
            (drafts if status == "draft" else earnings if is_earnings else articles).append(row)
    catalogue = yaml.safe_load((ROOT / "content" / "tools.yml").read_text(encoding="utf-8")) or {}
    tools = []
    for tool in catalogue.get("tools", []):
        slug = tool["slug"]
        guide = ROOT / "content" / "tool-guides" / (slug + ".md")
        tools.append(item(tool.get("title") or slug, "/" + slug + "/", "content/tools.yml",
                          "Calculator", category=tool.get("category") or "Other", slug=slug,
                          embedded_guide=str(guide.relative_to(ROOT)) if guide.exists() else ""))
    tools.extend([
        item("Compound Interest Calculator Ireland", "/compound-interest-calculator/",
             "content/compound-calculator-guide.md", "Calculator", category="Pensions & Investing",
             slug="compound-interest-calculator", embedded_guide="content/compound-calculator-guide.md"),
        item("BMI Calculator Ireland", "/bmi-calculator/", "content/bmi-guide.md",
             "Calculator", category="Health", slug="bmi-calculator",
             embedded_guide="content/bmi-guide.md"),
    ])
    by_slug = {r["slug"]: r for r in tools}
    guide_files = sorted((ROOT / "content" / "tool-guides").glob("*.md"))
    guides = [item(by_slug.get(p.stem, {}).get("title") or p.stem,
                   "/" + p.stem + "/", p.relative_to(ROOT),
                   "Embedded calculator guide") for p in guide_files]
    pages = []
    for path in sorted((ROOT / "content" / "pages").glob("*.md")):
        meta = frontmatter(path)
        pages.append(item(meta.get("title") or path.stem.title(), "/" + path.stem + "/",
                          path.relative_to(ROOT), "Information / policy page"))
    hubs = [item(title, url, "compound/site/build.py", "Hub / landing page") for title, url in HUBS]
    stock = json.loads((ROOT / "content" / "earnings-sp500.json").read_text(encoding="utf-8"))
    watch = json.loads((ROOT / "content" / "company-watchlist.json").read_text(encoding="utf-8"))
    listed = []
    for co in stock.get("members", []):
        symbol = co.get("symbol")
        if symbol:
            listed.append(item(str(co["name"]) + " (" + symbol + ") Stock",
                               "/stocks/" + symbol.lower() + "/",
                               "content/earnings-sp500.json", "Public-company profile",
                               ticker=symbol, origin="S&P reference list"))
    for co in watch.get("listed", []):
        listed.append(item(str(co["name"]) + " (" + co["ticker"] + ") Stock Research",
                           "/stocks/" + co["slug"] + "/", "content/company-watchlist.json",
                           "Public-company profile", ticker=co["ticker"],
                           origin="Additional listed company"))
    private = [item(co["name"] + " Private Company Research",
                    "/companies/" + co["slug"] + "/", "content/company-watchlist.json",
                    "Private-company profile") for co in watch.get("private", [])]
    public = [*articles, *earnings, *tools, *pages, *hubs, *listed, *private]
    conflicts = [path for path, n in Counter(x["url"] for x in public).items() if n > 1]
    if conflicts:
        errors.append("Repeated canonical routes across groups: " + ", ".join(conflicts))
    sections = dict(articles=ordered(articles), earnings_source_files=ordered(earnings),
                    tools=ordered(tools), embedded_tool_guides=ordered(guides), pages=ordered(pages),
                    hubs=ordered(hubs), public_company_profiles=ordered(listed),
                    private_company_profiles=ordered(private), drafts=ordered(drafts))
    catalogue = dict(snapshot_date=date.today().isoformat(),
                     source="Compound.ie GitHub publishing files", sections=sections, warnings=errors,
                     caveat="Source inventory, not proof of live HTTP 200 or Google indexation. Legacy earnings URLs may redirect.")
    lines = [
        "# Compound.ie — Master Content and Title Register", "",
        "Snapshot: " + catalogue["snapshot_date"] + " | Source: publishing branch", "",
        "PURPOSE: Check this register before creating a new article, guide or calculator. Search by exact title, keyword, synonym and reader intent. If the topic is already answered, update its canonical page instead of publishing an SEO duplicate.", "",
        "Coverage: editorial content, all configured calculators, their embedded explanations, information pages, hubs and generated company profiles. Does not separately list tag pages, share-class redirects or unpublished preview links.", "",
        "## Summary", "",
        f"- Published editorial articles and guides: {len(articles)}",
        f"- Existing automated/legacy earnings source files: {len(earnings)}",
        f"- Tools and calculators: {len(tools)}",
        f"- Embedded tool-guide files: {len(guides)}",
        f"- Information and policy pages: {len(pages)}",
        f"- Main hubs: {len(hubs)}",
        f"- Public-company directory profiles: {len(listed)}",
        f"- Private-company directory profiles: {len(private)}",
        f"- Draft or unpublished editorial files: {len(drafts)}", "",
    ]
    for pillar in ("Health", "Wealth", "Life"):
        subset = ordered(x for x in articles if x["category"] == pillar)
        lines += [f"## {pillar} articles and guides — {len(subset)}", ""]
        lines += ["- " + link(x) for x in subset] + [""]
    lines += [f"## Automated / legacy earnings source files — {len(earnings)}", "",
              "Some old quarterly article routes are now redirects to continuous company profiles. Do not create quarterly article spam; consolidate company results into the single company page.", ""]
    lines += ["- " + link(x) + " | source: " + x["source"] for x in ordered(earnings)] + [""]
    lines += [f"## Interactive calculators and tools — {len(tools)}", ""]
    for cat in sorted(set(x["category"] for x in tools)):
        subset = ordered(x for x in tools if x["category"] == cat)
        lines += [f"### {cat} — {len(subset)}", ""]
        lines += ["- " + link(x) + (" | includes embedded guide" if x["embedded_guide"] else "") for x in subset] + [""]
    lines += [f"## Supporting tool explainer files — {len(guides)}", "",
              "Each entry lives within its corresponding calculator page; it is not a second standalone article.", ""]
    lines += ["- " + x["title"] + " | source: " + x["source"] for x in guides] + [""]
    for key, title in (("pages", "Information and policy pages"), ("hubs", "Site hubs and directories")):
        rows = sections[key]
        lines += [f"## {title} — {len(rows)}", ""] + ["- " + link(x) for x in rows] + [""]
    lines += [f"## Listed company stock research profiles — {len(listed)}", "",
              "These are generated directory profiles, not individually written evergreen articles.", ""]
    lines += ["- " + link(x) for x in ordered(listed)] + [""]
    lines += [f"## Private-company research profiles — {len(private)}", ""]
    lines += ["- " + link(x) for x in ordered(private)] + [""]
    if drafts:
        lines += [f"## Draft / unpublished content — {len(drafts)}", "",
                  "Excluded from the published count.", ""]
        lines += ["- " + x["title"] + " | " + x["source"] for x in ordered(drafts)] + [""]
    if errors:
        lines += ["## Inventory warnings", ""] + ["- " + x for x in errors] + [""]
    lines += ["## Duplicate-prevention procedure", "",
              "1. Search article titles for exact keywords and closely related questions.",
              "2. Search calculators, embedded tool guides and existing series chapters.",
              "3. For earnings, update the existing company profile rather than creating another quarterly URL.",
              "4. If existing coverage matches the search intent, refresh it, preserve its URL and add internal links.",
              "5. Only create a new URL for a genuinely distinct reader question.",
              "6. Update this register after a publishing batch; the machine-readable JSON is also available in data/content-inventory.json.", ""]
    (ROOT / "CONTENT_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "content-inventory.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Inventory generated:", ", ".join(k + "=" + str(len(v)) for k, v in sections.items()))
    if errors:
        print("Warnings:", errors)

if __name__ == "__main__":
    build()
