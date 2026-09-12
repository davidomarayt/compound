"""Base types for pollable sources plus shared HTML helpers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

import httpx

USER_AGENT = "compound.ie poller (+https://compound.ie; contact: hello@compound.ie)"
TIMEOUT = 30.0


@dataclass(frozen=True)
class SourceItem:
    external_id: str
    title: str
    url: str
    summary: str = ""
    published_at: str | None = None  # ISO date if known


class Source:
    """A pollable source. Subclasses set key/name/pillar and implement fetch()."""

    key: str = ""
    name: str = ""
    pillar: str = "wealth"

    def fetch(self) -> list[SourceItem]:
        """Return the items currently listed by the source, newest first."""
        raise NotImplementedError

    def fetch_text(self, url: str) -> str:
        """Fetch the item page and reduce it to readable text for the LLM."""
        html = http_get(url)
        return html_to_text(html)


BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IE,en;q=0.9",
}


def http_get(url: str) -> str:
    """GET a page as text. Identifies itself honestly first; if the site refuses that (403/406/429,
    typical of bot-blocking front ends on government sites), retries once as a plain browser."""
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=_HEADERS) as client:
        r = client.get(url, headers={"User-Agent": USER_AGENT})
        if r.status_code in (403, 406, 429):
            r = client.get(url, headers={"User-Agent": BROWSER_UA})
        r.raise_for_status()
        return r.text


class _TextExtractor(HTMLParser):
    """Turn an HTML page into plain text, skipping chrome (nav/header/footer/script/style).

    If the page has a <main> element, only its contents are kept.
    """

    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "svg", "form", "aside"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br", "section", "article", "table", "ul", "ol", "dd", "dt"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.main_parts: list[str] = []
        self._skip_depth = 0
        self._in_main = 0
        self._cell = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip_depth += 1
        elif tag == "main":
            self._in_main += 1
        elif tag in self.BLOCK:
            self._emit("\n")
        elif tag in {"td", "th"}:
            self._emit(" | ")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "main":
            self._in_main = max(0, self._in_main - 1)
        elif tag in self.BLOCK:
            self._emit("\n")

    def handle_data(self, data):
        if self._skip_depth:
            return
        self._emit(data)

    def _emit(self, s: str) -> None:
        self.parts.append(s)
        if self._in_main:
            self.main_parts.append(s)

    def text(self) -> str:
        raw = "".join(self.main_parts) if self.main_parts else "".join(self.parts)
        raw = unescape(raw)
        lines = [re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in raw.splitlines()]
        out: list[str] = []
        for ln in lines:
            if ln:
                out.append(ln)
            elif out and out[-1] != "":
                out.append("")
        return "\n".join(out).strip()


def html_to_text(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    p.close()
    return p.text()


class _LinkCollector(HTMLParser):
    """Collect (href, text) pairs for every anchor in a page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            self._href = href
            self._buf = []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self.links.append((self._href, text))
            self._href = None
            self._buf = []


def collect_links(html: str) -> list[tuple[str, str]]:
    p = _LinkCollector()
    p.feed(html)
    p.close()
    return p.links
