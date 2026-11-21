"""Conservative content-addressed cache for rendered article HTML.

A cache miss never changes correctness: callers render normally. Shared indexes,
sitemaps, directories, and other site pages are intentionally rebuilt each run.
The cache is immutable per digest; never trust a path by itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path


def hash_inputs(paths: list[Path], *, extras: object = None) -> str:
    """Hash ordered file contents, including names and missing-file markers."""
    h = hashlib.sha256()
    for path in sorted(paths, key=str):
        h.update(str(path).encode("utf-8"))
        h.update(b"\x00")
        if path.is_file():
            h.update(hashlib.sha256(path.read_bytes()).digest())
        else:
            h.update(b"<missing>")
    h.update(json.dumps(extras, sort_keys=True, default=str).encode("utf-8"))
    return h.hexdigest()


def render_key(*, base: str, article: object, recommendations: list[object],
               tools: list[dict], profile: object) -> str:
    """Include all mutable article inputs and linked recommendations.

    Conservatively hashing the complete article objects is intentional: a
    new metadata field cannot silently bypass invalidation.
    """
    payload = {
        "base": base,
        "article": vars(article),
        "recommendations": [vars(item) for item in recommendations],
        "linked_tools": tools,
        "profile": profile,
    }
    return hashlib.sha256(
        # Preserve source insertion order: trial tables and other metadata can
        # contain mixed integer/string keys, which JSON cannot sort together.
        # A different order causes a safe cache miss rather than stale output.
        json.dumps(payload, sort_keys=False, default=str, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


class ArticleRenderCache:
    def __init__(self, directory: Path | None, base: str):
        self.directory = directory
        self.base = base
        self.hits = 0
        self.misses = 0

    @classmethod
    def from_environment(cls, *, site_root: Path, content_dir: Path,
                         site_base_url: str, email_form_action: str = "") -> "ArticleRenderCache":
        raw = os.environ.get("COMPOUND_ARTICLE_CACHE_DIR", "").strip()
        directory = Path(raw).resolve() if raw else None
        code = sorted((site_root / "templates").rglob("*.html"))
        # Include all Python modules used to assemble pages, not only the
        # site module: changes to imports must invalidate cached HTML.
        code += sorted(site_root.parent.rglob("*.py"))
        code += [content_dir / "site.yml"]
        # All article pages use the same year; audit and production cannot share.
        base = hash_inputs(code, extras={
            "site_base_url": site_base_url,
            "email_form_action": email_form_action,
            "audit": os.environ.get("COMPOUND_AUDIT_MODE", ""),
            "year": date.today().year,
        })
        return cls(directory, base)

    def _path(self, url: str, key: str) -> Path | None:
        # Never interpret canonical URLs as filesystem traversal.
        if self.directory is None or not re.fullmatch(r"/[a-zA-Z0-9/_-]+/", url):
            return None
        return self.directory / key[:2] / (key + ".html")

    def reuse(self, url: str, key: str, destination: Path) -> bool:
        source = self._path(url, key)
        if source is None or not source.is_file():
            self.misses += 1
            return False
        # A valid cache object must be non-empty regular HTML. All other
        # validation (article metadata, links, images) runs before this point.
        if source.stat().st_size == 0:
            self.misses += 1
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        self.hits += 1
        return True

    def store(self, url: str, key: str, source: Path) -> None:
        path = self._path(url, key)
        if path is None or not source.is_file():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            shutil.copyfile(source, path)
