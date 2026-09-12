"""Revenue.ie eBriefs.

Revenue publishes eBriefs at /en/tax-professionals/ebrief/<year>/no-<NNN><YYYY>.aspx and lists
them on an index page. If an RSS URL is configured it is used first; otherwise the index page is
polled and every eBrief link is extracted. New links = new items.

NOTE: the live page could not be reached from the build sandbox, so the HTML parsing is written
defensively (any anchor whose href matches the eBrief URL pattern) and tested against a fixture.
Run `compound poll --dry-run` once on a real network to confirm it sees the current eBriefs.
"""
from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

import feedparser

from compound.sources.base import Source, SourceItem, collect_links, http_get

EBRIEF_HREF = re.compile(r"/ebrief/(?P<year>\d{4})/(?P<slug>no-\d+)\.aspx$", re.IGNORECASE)
DATE_IN_TEXT = re.compile(r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})")


class RevenueEbriefs(Source):
    key = "revenue_ebrief"
    name = "Revenue eBriefs"
    pillar = "wealth"

    def __init__(self, index_url: str, rss_url: str = ""):
        self.index_url = index_url
        self.rss_url = rss_url

    def fetch(self) -> list[SourceItem]:
        if self.rss_url:
            items = self._fetch_rss()
            if items:
                return items
        return parse_index(http_get(self.index_url), base_url=self.index_url)

    def _fetch_rss(self) -> list[SourceItem]:
        feed = feedparser.parse(self.rss_url)
        out: list[SourceItem] = []
        for e in feed.entries:
            link = getattr(e, "link", "") or ""
            title = (getattr(e, "title", "") or "").strip()
            if not link or not title:
                continue
            m = EBRIEF_HREF.search(link)
            ext = f"{m.group('year')}/{m.group('slug')}".lower() if m else link
            published = None
            if getattr(e, "published_parsed", None):
                published = datetime(*e.published_parsed[:3]).date().isoformat()
            out.append(SourceItem(external_id=ext, title=title, url=link,
                                  summary=(getattr(e, "summary", "") or "")[:500], published_at=published))
        return out


def parse_index(html: str, base_url: str) -> list[SourceItem]:
    """Extract eBrief items from the index HTML. Order preserved (site lists newest first)."""
    seen: set[str] = set()
    items: list[SourceItem] = []
    for href, text in collect_links(html):
        if not href:
            continue
        m = EBRIEF_HREF.search(href)
        if not m:
            continue
        ext = f"{m.group('year')}/{m.group('slug')}".lower()
        if ext in seen:
            continue
        seen.add(ext)
        title = text or ext
        dm = DATE_IN_TEXT.search(text)
        published = None
        if dm:
            try:
                published = datetime.strptime(" ".join(dm.groups()), "%d %B %Y").date().isoformat()
            except ValueError:
                published = None
        items.append(SourceItem(external_id=ext, title=title, url=urljoin(base_url, href), published_at=published))
    return items
