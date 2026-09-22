#!/usr/bin/env python3
"""
Publish article-specific social copy to X, LinkedIn and Instagram.

The script is intentionally conservative:
- Only articles with publication_status: published (or draft: false) are eligible.
- Automatic push runs post only when an article is newly published.
- Ordinary edits to an already-published article do not repost it.
- Manual workflow_dispatch can publish a specific article path.
- SOCIAL_DRY_RUN defaults to true.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

SITE_URL = "https://compound.ie"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}


def read_article(path: str) -> dict[str, Any]:
    return parse_frontmatter(Path(path).read_text(encoding="utf-8"))


def read_article_at(ref: str, path: str) -> dict[str, Any]:
    if not ref or set(ref) == {"0"}:
        return {}
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {}
    return parse_frontmatter(proc.stdout)


def published(meta: dict[str, Any]) -> bool:
    status = str(meta.get("publication_status", "")).lower()
    if status:
        return status == "published"
    return meta.get("draft") is False


def social_enabled(meta: dict[str, Any]) -> bool:
    social = meta.get("social") or {}
    return isinstance(social, dict) and is_true(social.get("enabled", False))


def article_url(meta: dict[str, Any]) -> str:
    social = meta.get("social") or {}
    explicit = str(social.get("url", "")).strip() if isinstance(social, dict) else ""
    if explicit:
        return explicit
    slug = str(meta.get("slug", "")).strip().strip("/")
    pillar = str(meta.get("pillar", "")).strip().strip("/")
    if not slug:
        raise ValueError("Article is missing slug")
    if pillar:
        return f"{SITE_URL}/{pillar}/{slug}/"
    return f"{SITE_URL}/{slug}/"


def changed_markdown_paths(base: str, head: str) -> list[str]:
    if not head:
        return []
    if not base or set(base) == {"0"}:
        proc = subprocess.run(["git", "rev-parse", f"{head}^"], text=True, capture_output=True, check=False)
        base = proc.stdout.strip() if proc.returncode == 0 else ""
    if not base:
        return []
    proc = subprocess.run(
        ["git", "diff", "--name-only", base, head, "--", "content/**/*.md"],
        text=True,
        capture_output=True,
        check=True,
    )
    return [p for p in proc.stdout.splitlines() if p.endswith(".md") and Path(p).exists()]


def should_auto_publish(path: str, current: dict[str, Any], base: str) -> bool:
    if not published(current) or not social_enabled(current):
        return False
    previous = read_article_at(base, path)
    # New file or article changed from unpublished to published.
    return not previous or not published(previous)


def platform_config(meta: dict[str, Any], name: str) -> dict[str, Any]:
    social = meta.get("social") or {}
    cfg = social.get(name) or {}
    return cfg if isinstance(cfg, dict) else {}


def text_with_url(text: str, url: str) -> str:
    text = (text or "").strip()
    if url in text:
        return text
    return f"{text}\n\n{url}".strip()


def post_x(meta: dict[str, Any], url: str, dry_run: bool) -> str:
    cfg = platform_config(meta, "x")
    if not is_true(cfg.get("enabled", True)):
        return "X disabled"
    copy = text_with_url(str(cfg.get("text", "")), url)
    if not copy:
        return "X skipped: no copy"
    if dry_run:
        print("[DRY RUN] X\n" + copy + "\n")
        return "X dry-run"
    token = env("X_ACCESS_TOKEN")
    if not token:
        return "X skipped: X_ACCESS_TOKEN missing"
    response = requests.post(
        "https://api.x.com/2/tweets",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"text": copy},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return f"X posted: {payload.get('data', {}).get('id', 'unknown id')}"


def post_linkedin(meta: dict[str, Any], url: str, dry_run: bool) -> str:
    cfg = platform_config(meta, "linkedin")
    if not is_true(cfg.get("enabled", True)):
        return "LinkedIn disabled"
    copy = text_with_url(str(cfg.get("text", "")), url)
    if not copy:
        return "LinkedIn skipped: no copy"
    if dry_run:
        print("[DRY RUN] LinkedIn\n" + copy + "\n")
        return "LinkedIn dry-run"
    token = env("LINKEDIN_ACCESS_TOKEN")
    author = env("LINKEDIN_AUTHOR_URN")
    version = env("LINKEDIN_VERSION")
    if not token or not author or not version:
        return "LinkedIn skipped: token, author URN or version missing"
    body = {
        "author": author,
        "commentary": copy,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    response = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Linkedin-Version": version,
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=body,
        timeout=30,
    )
    response.raise_for_status()
    post_id = response.headers.get("x-restli-id", "unknown id")
    return f"LinkedIn posted: {post_id}"


def post_instagram(meta: dict[str, Any], url: str, dry_run: bool) -> str:
    cfg = platform_config(meta, "instagram")
    if not is_true(cfg.get("enabled", True)):
        return "Instagram disabled"
    caption = str(cfg.get("caption", "")).strip()
    image_url = str(cfg.get("image_url") or meta.get("social_image") or meta.get("image") or "").strip()
    if not image_url and "news" in {str(x).lower() for x in (meta.get("tags") or [])}:
        slug = str(meta.get("slug") or "").strip()
        if slug:
            image_url = f"{SITE_URL}/static/images/news/{slug}-portrait.jpg"
    if image_url.startswith("/"):
        image_url = SITE_URL + image_url
    if not caption:
        return "Instagram skipped: no caption"
    if not image_url:
        return "Instagram skipped: no article/social image available"
    caption = text_with_url(caption, url)
    if dry_run:
        print(f"[DRY RUN] Instagram\nImage: {image_url}\n{caption}\n")
        return "Instagram dry-run"
    token = env("META_ACCESS_TOKEN")
    ig_user_id = env("INSTAGRAM_USER_ID")
    graph_version = env("META_GRAPH_VERSION")
    if not token or not ig_user_id or not graph_version:
        return "Instagram skipped: Meta token, Instagram user ID or graph version missing"

    base = f"https://graph.facebook.com/{graph_version}/{ig_user_id}"
    create = requests.post(
        f"{base}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token},
        timeout=60,
    )
    create.raise_for_status()
    creation_id = create.json()["id"]

    publish = requests.post(
        f"{base}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish.raise_for_status()
    return f"Instagram posted: {publish.json().get('id', 'unknown id')}"


def publish_path(path: str, dry_run: bool) -> None:
    meta = read_article(path)
    if not published(meta):
        print(f"Skip {path}: not published")
        return
    if not social_enabled(meta):
        print(f"Skip {path}: social.enabled is not true")
        return

    url = article_url(meta)
    print(f"Publishing social package for {path}")
    print(f"Article URL: {url}")

    failures: list[str] = []
    for name, fn in [
        ("X", post_x),
        ("LinkedIn", post_linkedin),
        ("Instagram", post_instagram),
    ]:
        try:
            result = fn(meta, url, dry_run)
            print(result)
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            print(f"{name} failed: {exc}", file=sys.stderr)

    if failures:
        raise RuntimeError(" | ".join(failures))


def main() -> int:
    dry_run = is_true(env("SOCIAL_DRY_RUN", "true"))
    manual_path = env("ARTICLE_PATH")
    base = env("BASE_SHA")
    head = env("HEAD_SHA")

    if manual_path:
        if not Path(manual_path).exists():
            raise FileNotFoundError(manual_path)
        publish_path(manual_path, dry_run)
        return 0

    paths = changed_markdown_paths(base, head)
    eligible = []
    for path in paths:
        current = read_article(path)
        if should_auto_publish(path, current, base):
            eligible.append(path)

    if not eligible:
        print("No newly published social-enabled articles in this push.")
        return 0

    for path in eligible:
        publish_path(path, dry_run)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Social publishing failed: {exc}", file=sys.stderr)
        raise
