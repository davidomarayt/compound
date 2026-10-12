"""Fast, changed-file editorial checks before the more expensive site build.

Usage: python scripts/article_preflight.py --file-list /tmp/changed_articles.txt
       python scripts/article_preflight.py content/wealth/example.md

This intentionally does not attempt to 'verify' factual assertions or replace
source checking. It catches avoidable publication and SEO mistakes quickly.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

ARTICLE_FOLDERS = {"health", "wealth", "happiness", "life"}
PLACEHOLDERS = re.compile(
    r"(?i)\b(?:lorem ipsum|source needed|citation needed|insert link here|"
    r"todo:|tbd:)\b"
)
FRONT = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)", re.S)


def article_path(path: Path) -> bool:
    parts = path.parts
    return len(parts) >= 3 and parts[0] == "content" and parts[1] in ARTICLE_FOLDERS and path.suffix == ".md"


def inspect(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():  # Deleted pages are handled by the site build.
        return errors, warnings
    raw = path.read_text(encoding="utf-8")
    match = FRONT.match(raw)
    if not match:
        return ["missing YAML front matter"], warnings
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"invalid YAML front matter: {exc}"], warnings
    if not isinstance(meta, dict):
        return ["front matter must be a mapping"], warnings
    if meta.get("draft") is True or meta.get("publication_status") == "draft":
        return errors, warnings

    def require(key: str, minimum: int = 1) -> str:
        value = str(meta.get(key) or "").strip()
        if len(value) < minimum:
            errors.append(f"missing or too-short {key}")
        return value

    title = require("title", 12)
    slug = require("slug", 4)
    description = require("meta_description", 45)
    # Some older evergreen posts predate the current summary schema. Require
    # it for new news pieces; flag its absence on legacy guides instead.
    if str(meta.get("summary") or "").strip() == "":
        warnings.append("summary missing; add a concise search/social summary")
    date = require("date")
    if date:
        try:
            dt.date.fromisoformat(str(date))
        except ValueError:
            errors.append("date must be YYYY-MM-DD")
    if slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        errors.append("slug must use lowercase letters, digits and hyphens")
    if description and len(description) > 180:
        warnings.append(f"meta_description is {len(description)} chars; check search snippet")
    if title and len(title) > 100:
        warnings.append(f"title is {len(title)} chars; review readability")
    if not meta.get("seo_title"):
        warnings.append("seo_title missing; title will be used as fallback")
    canonical = str(meta.get("canonical_path") or "")
    if canonical and not (canonical.startswith("/") and canonical.endswith("/")):
        errors.append("canonical_path must start and end with '/'")

    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        errors.append("tags must be a YAML list")
        tags = []
    is_news = "news" in tags or canonical.startswith("/news/")
    sources = meta.get("sources") or []
    if not isinstance(sources, list):
        errors.append("sources must be a YAML list")
        sources = []
    if is_news and not sources:
        errors.append("published news article requires at least one traceable source")
    if is_news and len(sources) < 2:
        warnings.append("news article has fewer than two listed sources; independently corroborate claims")
    for idx, source in enumerate(sources, 1):
        if not isinstance(source, dict) or not str(source.get("title") or "").strip():
            errors.append(f"source {idx} needs a title")
            continue
        url = str(source.get("url") or "")
        if not (urlparse(url).scheme == "https" and urlparse(url).netloc):
            errors.append(f"source {idx} needs a valid https URL")

    charts = meta.get("charts") or []
    if not isinstance(charts, list):
        errors.append("charts must be a YAML list")
        charts = []
    for idx, chart in enumerate(charts, 1):
        if not isinstance(chart, dict):
            errors.append(f"chart {idx} must be a mapping")
            continue
        for field in ("title", "kind", "unit", "caption", "source_url"):
            if not str(chart.get(field) or "").strip():
                errors.append(f"chart {idx} missing {field}")
        items = chart.get("items") or []
        if not isinstance(items, list) or not items:
            errors.append(f"chart {idx} needs data items")
            continue
        for n, item in enumerate(items, 1):
            if not isinstance(item, dict) or not str(item.get("label") or "").strip():
                errors.append(f"chart {idx} item {n} needs a label")
            elif not isinstance(item.get("value"), (int, float)):
                errors.append(f"chart {idx} item {n} needs a numeric value")

    if PLACEHOLDERS.search(match.group(2)):
        errors.append("unresolved editorial placeholder in body")
    if not match.group(2).strip():
        errors.append("article body is empty")
    # Check News photos are at least specified. The publish build verifies
    # the actual image file and alt/credit after the image preparation step.
    if is_news and not any(meta.get(k) for k in
                           ("image", "hero_image_url", "pexels_photo_id", "news_image_query")):
        errors.append("news article needs a topic-specific cover image instruction")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Changed article Markdown paths")
    parser.add_argument("--file-list", type=Path, help="Newline-separated changed paths from git")
    args = parser.parse_args()
    raw_paths = list(args.files)
    if args.file_list:
        raw_paths.extend(args.file_list.read_text(encoding="utf-8").splitlines())
    paths = sorted({Path(p.strip()) for p in raw_paths if p.strip()})
    checked = 0
    failed = 0
    for path in paths:
        if not article_path(path):
            continue
        checked += 1
        errors, warnings = inspect(path)
        for issue in warnings:
            print(f"WARNING {path}: {issue}")
        for issue in errors:
            failed += 1
            print(f"ERROR {path}: {issue}")
    print(f"Editorial preflight: {checked} changed article(s), {failed} error(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
