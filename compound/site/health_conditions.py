"""Build Compound's Irish conditions directory from checked-in source records."""

import json
from collections import defaultdict
from urllib.parse import urlsplit

import yaml


CONDITIONS_URL = "/health/conditions/"
MEASURES = {
    "prevalence": "Prevalence estimate",
    "registry": "Registry or care count",
    "notifications": "Disease notifications",
    "diagnoses": "New diagnoses",
    "hospital": "Hospital activity",
    "service": "Service activity",
}
SECTIONS = (
    ("symptoms", "Symptoms and signs"),
    ("causes", "What happens in the body"),
    ("diagnosis", "How it is diagnosed"),
    ("care", "Treatment and follow-up"),
    ("complications", "Complications and outlook"),
    ("help", "When to get help"),
)
TEST_SECTIONS = (
    ("symptoms", "Why you might have the test"),
    ("causes", "What the test measures"),
    ("diagnosis", "Preparing for the appointment"),
    ("care", "What happens on the day"),
    ("complications", "After the test"),
    ("help", "Getting your results and advice"),
)


def load_conditions(content, article_urls):
    index_path = content / "health-conditions-index.json"
    if not index_path.is_file():
        return None

    with index_path.open(encoding="utf-8") as index_file:
        rows = json.load(index_file)
    editorial = yaml.safe_load((content / "health-conditions.yml").read_text(encoding="utf-8"))
    sources = editorial["sources"]
    evidence = editorial["evidence"]
    guides = editorial["guides"]
    checked = editorial["checked"].isoformat()
    grouped = defaultdict(list)
    by_slug = {}
    seen_urls = {}
    for letter, name, official_url in rows:
        url = urlsplit(official_url)
        if url.scheme != "https" or url.hostname != "www2.hse.ie" or not name or letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            raise ValueError(f"Invalid HSE catalogue entry: {name}")
        slug = url.path.rstrip("/").split("/")[-1]
        if official_url in seen_urls:
            grouped[letter].append({**seen_urls[official_url], "name": name})
            continue
        if slug in by_slug:
            raise ValueError(f"Duplicate condition slug: {slug}")
        records = []
        for record in evidence.get(slug, []):
            if not all(record.get(key) for key in ("value", "period", "population", "note", "locator")):
                raise ValueError(f"Incomplete Irish evidence: {slug}")
            source = sources[record["source"]]
            if urlsplit(source["url"]).scheme != "https":
                raise ValueError(f"Invalid evidence source: {slug}")
            records.append({**record, "label": MEASURES[record["measure"]], "citation": source})
        guide = guides.get(slug)
        if guide:
            has_evidence_gap = bool(guide.get("evidence_gap", "").strip() and guide.get("sources"))
            if (not records and not has_evidence_gap) or not guide.get("summary") or any(
                not guide.get(key) for key, _ in SECTIONS
            ):
                raise ValueError(f"Incomplete condition guide: {slug}")
            for label, target in guide.get("links", {}).items():
                if target not in article_urls:
                    raise ValueError(f"Unknown related article for {slug}: {label} ({target})")
        entry = {
            "name": name,
            "official_url": official_url,
            "url": f"{CONDITIONS_URL}{slug}/" if guide else official_url,
            "guide": guide,
            "records": records,
            "sections": TEST_SECTIONS if guide and guide.get("kind") == "test" else SECTIONS,
        }
        by_slug[slug] = entry
        seen_urls[official_url] = entry
        grouped[letter].append(entry)

    unknown = (set(guides) | set(evidence)) - set(by_slug)
    if unknown:
        raise ValueError(f"Condition slugs missing from HSE catalogue: {sorted(unknown)}")
    return {
        "groups": dict(sorted(grouped.items())),
        "featured": sorted((entry for entry in by_slug.values() if entry["guide"]), key=lambda entry: entry["name"]),
        "topic_count": len(by_slug),
        "evidence_count": sum(bool(entry["records"]) for entry in by_slug.values()),
        "checked": checked,
    }


def condition_search_entries(directory):
    checked = directory["checked"]
    items = [(CONDITIONS_URL, "Health Conditions A–Z", "Find HSE topics, Compound guides and Irish health statistics.")]
    items.extend((entry["url"], entry["name"], entry["guide"]["summary"]) for entry in directory["featured"])
    return [
        {
            "title": title, "url": url, "pillar": "Health", "date": checked,
            "summary": description, "description": description, "image": "",
            "tags": ["health conditions", "irish health"], "reading_minutes": 4,
            "date_label": "Health reference",
        }
        for url, title, description in items
    ]
