"""Research packs: the source text an article is written from and verified against.

Health and happiness pieces draw on PubMed (free NCBI E-utilities; no key needed). Wealth pieces draw
on official Irish pages. A pack is a list of sources, each with a title, URL and plain text; the
draft may only use figures it can quote verbatim from one of them, and the verifier checks each
figure against the text of the source it cites.
"""
from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

log = logging.getLogger(__name__)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
# Only strong study designs, in humans, recent. Appended to every PubMed query.
PUBMED_FILTER = (
    ' AND (meta-analysis[pt] OR "systematic review"[pt] OR "randomized controlled trial"[pt] OR review[pt])'
    ' AND humans[mh] AND ("2015"[dp] : "3000"[dp]) AND hasabstract[text]'
)
STRONG_TYPES = ("Meta-Analysis", "Systematic Review", "Randomized Controlled Trial")

# Pages on these hosts count as trustworthy sources for wealth (and general Irish) pieces.
TRUSTED_HOSTS = {
    "revenue.ie", "citizensinformation.ie", "gov.ie", "cso.ie", "centralbank.ie", "pensionsauthority.ie",
    "mabs.ie", "ccpc.ie", "hse.ie", "seai.ie", "esri.ie", "oecd.org", "who.int", "nice.org.uk",
    "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov", "cochranelibrary.com", "bmj.com", "thelancet.com", "nhs.uk",
}
MAX_SOURCE_CHARS = 6_000
MAX_PACK_CHARS = 40_000
TIMEOUT = 30.0
USER_AGENT = "compound.ie research (+https://compound.ie; contact: hello@compound.ie)"


@dataclass
class Source:
    title: str
    url: str
    text: str
    kind: str = "page"  # page | pubmed
    meta: dict = field(default_factory=dict)  # journal, year, pubtypes, pmid


@dataclass
class ResearchPack:
    sources: list[Source] = field(default_factory=list)

    def source_text(self) -> str:
        """What the drafting model reads: every source, clearly delimited, capped in size."""
        parts: list[str] = []
        used = 0
        for i, s in enumerate(self.sources, start=1):
            head = f"### Source {i}: {s.title}\nURL: {s.url}\n"
            if s.kind == "pubmed":
                m = s.meta
                head += f"{m.get('journal', '')} {m.get('year', '')} · {', '.join(m.get('pubtypes', []))}\n"
            body = s.text.strip()[:MAX_SOURCE_CHARS]
            chunk = head + body + "\n"
            if used + len(chunk) > MAX_PACK_CHARS:
                break
            parts.append(chunk)
            used += len(chunk)
        return "\n".join(parts)

    def page_texts(self) -> dict[str, str]:
        """url -> text, for figure verification against the exact source cited."""
        return {s.url: s.text for s in self.sources}

    def refs(self) -> list[dict]:
        return [{"title": s.title, "url": s.url} for s in self.sources]

    def to_json(self) -> str:
        return json.dumps([s.__dict__ for s in self.sources], ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str | None) -> "ResearchPack":
        if not raw:
            return cls()
        return cls(sources=[Source(**d) for d in json.loads(raw)])


def is_trusted(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in TRUSTED_HOSTS)


# --- PubMed -------------------------------------------------------------------
def _get(url: str, params: dict) -> httpx.Response:
    with httpx.Client(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as c:
        r = c.get(url, params=params)
        r.raise_for_status()
        return r


def pubmed_search_ids(query: str, max_results: int = 5) -> list[str]:
    r = _get(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "term": query + PUBMED_FILTER, "retmax": max_results,
                                        "sort": "relevance", "retmode": "json"})
    return list(r.json().get("esearchresult", {}).get("idlist", []))


def pubmed_fetch(pmids: list[str]) -> list[Source]:
    if not pmids:
        return []
    r = _get(f"{EUTILS}/efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    return parse_pubmed_xml(r.text)


def parse_pubmed_xml(xml_text: str) -> list[Source]:
    """Turn efetch XML into Sources. Abstract sections (Background/Results/...) are kept with labels."""
    out: list[Source] = []
    root = ET.fromstring(xml_text)
    for art in root.iter("PubmedArticle"):
        pmid = (art.findtext(".//PMID") or "").strip()
        title = " ".join((art.findtext(".//ArticleTitle") or "").split())
        journal = (art.findtext(".//Journal/Title") or "").strip()
        year = (art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//PubDate/MedlineDate") or "")[:4]
        pubtypes = [pt.text.strip() for pt in art.findall(".//PublicationTypeList/PublicationType") if pt.text]
        parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            text = " ".join("".join(ab.itertext()).split())
            parts.append(f"{label}: {text}" if label else text)
        abstract = "\n".join(parts).strip()
        if not pmid or not abstract:
            continue
        out.append(Source(
            title=title or f"PubMed {pmid}", url=PUBMED_URL.format(pmid=pmid), text=abstract, kind="pubmed",
            meta={"pmid": pmid, "journal": journal, "year": year, "pubtypes": pubtypes},
        ))
    # strongest designs first
    out.sort(key=lambda s: (0 if any(t in s.meta.get("pubtypes", []) for t in STRONG_TYPES) else 1))
    return out


def pubmed_search(query: str, max_results: int = 5) -> list[Source]:
    try:
        return pubmed_fetch(pubmed_search_ids(query, max_results))
    except Exception:  # noqa: BLE001 - research is best effort; the pack size gate decides
        log.exception("pubmed search failed for %r", query)
        return []


# --- search-demand signal ----------------------------------------------------------
SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


def suggestions(seed: str, region: str = "ie") -> list[str]:
    """What people type after `seed` into Google (unofficial autocomplete endpoint). [] on any failure."""
    try:
        r = _get(SUGGEST_URL, {"client": "firefox", "hl": "en", "gl": region, "q": seed})
        data = r.json()
        return [s for s in data[1] if isinstance(s, str)][:10]
    except Exception:  # noqa: BLE001
        log.warning("autocomplete failed for %r", seed)
        return []


# --- assembly -------------------------------------------------------------------------
def build_pack(*, pubmed_queries: list[str], urls: list[str], fetch_page, pubmed_max: int = 5,
               max_sources: int = 8) -> ResearchPack:
    """Run the PubMed queries and fetch the trusted URLs; dedupe; keep at most max_sources."""
    pack = ResearchPack()
    seen: set[str] = set()
    for q in pubmed_queries:
        for s in pubmed_search(q, pubmed_max):
            if s.url not in seen:
                seen.add(s.url)
                pack.sources.append(s)
    for u in urls:
        u = u.strip()
        if not u or u in seen or not is_trusted(u):
            if u and not is_trusted(u):
                log.info("dropping untrusted source url %s", u)
            continue
        try:
            text = fetch_page(u)
        except Exception:  # noqa: BLE001
            log.warning("could not fetch source %s", u)
            continue
        if len(text.strip()) < 200:
            continue
        seen.add(u)
        pack.sources.append(Source(title=_title_from_text(text) or u, url=u, text=text, kind="page"))
    pack.sources = pack.sources[:max_sources]
    return pack


def _title_from_text(text: str) -> str:
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return re.sub(r"\s+", " ", first)[:120]
