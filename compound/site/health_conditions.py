"""Build Compound's Irish conditions directory from checked-in source records."""

import json
from collections import defaultdict
from urllib.parse import urlsplit

import yaml


CONDITIONS_URL = "/health/conditions/"
MEASURES = {
    "prevalence": "Prevalence estimate",
    "registry": "Registry or care count",
    "notifications": "Infectious disease notifications",
    "procedure": "Procedures reported",
    "diagnoses": "New diagnoses",
    "hospital": "Hospital activity",
    "service": "Service activity",
    "genetic": "Genetic frequency",
    "mortality": "Deaths",
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
PROCEDURE_SECTIONS = (
    ("symptoms", "Why it is offered"),
    ("causes", "What it involves"),
    ("diagnosis", "How to prepare"),
    ("care", "What happens on the day"),
    ("complications", "Risks and recovery"),
    ("help", "Follow-up and getting help"),
)
SERVICE_SECTIONS = (
    ("symptoms", "Who the service is for"),
    ("causes", "How it works"),
    ("diagnosis", "What to consider"),
    ("care", "What to expect"),
    ("complications", "Support and follow-up"),
    ("help", "Where to get advice"),
)
SYMPTOM_SECTIONS = (
    ("symptoms", "What you may notice"),
    ("causes", "Possible causes"),
    ("diagnosis", "How it is assessed"),
    ("care", "Care and follow-up"),
    ("complications", "What can happen next"),
    ("help", "When to get help"),
)
TOPIC_SECTIONS = (
    ("symptoms", "What to look out for"),
    ("causes", "What to know"),
    ("diagnosis", "Assessment and practical checks"),
    ("care", "Practical next steps"),
    ("complications", "Support and follow-up"),
    ("help", "When to get help"),
)
CONTRACEPTION_SECTIONS = (
    ("symptoms", "When this option may suit you"),
    ("causes", "How it works"),
    ("diagnosis", "What to consider"),
    ("care", "How to use or access it"),
    ("complications", "Side effects and practical considerations"),
    ("help", "Where to get advice"),
)
TREATMENT_SECTIONS = (
    ("symptoms", "When it may be used"),
    ("causes", "How it works"),
    ("diagnosis", "What to consider before starting"),
    ("care", "What to expect during treatment"),
    ("complications", "Side effects and follow-up"),
    ("help", "When to get advice"),
)
VACCINATION_SECTIONS = (
    ("symptoms", "Who is offered the vaccine"),
    ("causes", "What it protects against"),
    ("diagnosis", "What to know before vaccination"),
    ("care", "What to expect"),
    ("complications", "Side effects and follow-up"),
    ("help", "Where to get advice"),
)
GUIDE_FORMATS = {
    "condition": (SECTIONS, "How common is it in Ireland?", "MedicalCondition"),
    "symptom": (SYMPTOM_SECTIONS, "Irish data on this symptom", "MedicalSymptom"),
    "topic": (TOPIC_SECTIONS, "Irish data and evidence", "Thing"),
    "contraception": (CONTRACEPTION_SECTIONS, "Irish contraception figures", "Thing"),
    "treatment": (TREATMENT_SECTIONS, "Irish treatment figures", "MedicalTherapy"),
    "vaccination": (VACCINATION_SECTIONS, "Irish vaccination figures", "MedicalProcedure"),
    "test": (TEST_SECTIONS, "Irish testing figures", "MedicalTest"),
    "procedure": (PROCEDURE_SECTIONS, "Irish procedure figures", "MedicalProcedure"),
    "service": (SERVICE_SECTIONS, "Irish service figures", "Service"),
}


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
            measure_label = MEASURES[record["measure"]]
            records.append({**record, "label": record.get("label", measure_label), "citation": source})
        guide = guides.get(slug)
        if guide:
            has_evidence_gap = bool(guide.get("evidence_gap", "").strip() and guide.get("sources"))
            if (not records and not has_evidence_gap) or not guide.get("summary") or any(
                not guide.get(key) for key, _ in SECTIONS
            ):
                raise ValueError(f"Incomplete condition guide: {slug}")
            for links_key in ("links", "care_links"):
                for label, target in guide.get(links_key, {}).items():
                    if target not in article_urls:
                        raise ValueError(f"Unknown related article for {slug}: {label} ({target})")
        kind = guide.get("kind", "condition") if guide else "condition"
        if kind not in GUIDE_FORMATS:
            raise ValueError(f"Unknown condition guide type for {slug}: {kind}")
        sections, evidence_heading, schema_type = GUIDE_FORMATS[kind]
        if guide and (headings := guide.get("headings")):
            sections = tuple((key, headings.get(key, label)) for key, label in sections)
        entry = {
            "name": name,
            "official_url": official_url,
            "url": f"{CONDITIONS_URL}{slug}/" if guide else official_url,
            "guide": guide,
            "records": records,
            "sections": sections,
            "evidence_heading": evidence_heading,
            "schema_type": schema_type,
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
