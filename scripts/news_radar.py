#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
import yaml


@dataclass
class Item:
    title: str
    link: str
    source: str
    published: dt.datetime
    summary: str
    categories: list[str]
    score: int
    source_type: str


def clean(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_date(entry: Any, now: dt.datetime) -> dt.datetime:
    for attr in ("published_parsed", "updated_parsed"):
        value = getattr(entry, attr, None)
        if value:
            return dt.datetime(*value[:6], tzinfo=dt.timezone.utc)
    for attr in ("published", "updated"):
        value = getattr(entry, attr, None)
        if value:
            try:
                parsed = parsedate_to_datetime(value)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=dt.timezone.utc)
                return parsed.astimezone(dt.timezone.utc)
            except Exception:
                pass
    return now


def contains(text: str, term: str) -> bool:
    return term.casefold() in text.casefold()


def classify(text: str, cfg: dict[str, Any], defaults: list[str]) -> tuple[list[str], int]:
    categories: list[str] = []
    score = 0

    for category, terms in (cfg.get("topics") or {}).items():
        matches = sum(1 for term in terms if contains(text, str(term)))
        if matches:
            categories.append(category)
            score += matches * 3

    for tag in defaults:
        if tag in {"wealth", "health", "happiness"} and tag not in categories:
            categories.append(tag)
            score += 2

    for term in cfg.get("priority_terms") or []:
        if contains(text, str(term)):
            score += 2

    return categories, score


def item_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.casefold())[:120]


def fetch(config_path: Path, hours: int, limit: int) -> list[Item]:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=hours)
    seen: set[str] = set()
    items: list[Item] = []

    for feed_cfg in cfg.get("feeds") or []:
        parsed = feedparser.parse(feed_cfg["url"])
        source = str(feed_cfg.get("name") or parsed.feed.get("title") or feed_cfg["url"])
        defaults = [str(x) for x in (feed_cfg.get("default_tags") or [])]
        weight = int(feed_cfg.get("weight") or 0)
        source_type = str(feed_cfg.get("source_type") or "publisher")

        for entry in parsed.entries:
            title = clean(getattr(entry, "title", ""))
            link = str(getattr(entry, "link", "")).strip()
            summary = clean(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            if not title or not link:
                continue

            published = parse_date(entry, now)
            if published < cutoff:
                continue

            key = item_key(title)
            if key in seen:
                continue
            seen.add(key)

            text = f"{title} {summary}"
            categories, score = classify(text, cfg, defaults)
            if not categories:
                continue

            age_hours = max(0, int((now - published).total_seconds() // 3600))
            freshness = max(0, 8 - age_hours // 4)
            score += weight + freshness

            items.append(
                Item(
                    title=title,
                    link=link,
                    source=source,
                    published=published,
                    summary=summary,
                    categories=categories,
                    score=score,
                    source_type=source_type,
                )
            )

    items.sort(key=lambda x: (x.score, x.published), reverse=True)
    return items[:limit]


def build_markdown(items: list[Item], hours: int) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    lines = [
        "# Compound News Radar",
        "",
        f"_Updated {now:%Y-%m-%d %H:%M UTC}. Looking back {hours} hours._",
        "",
        "**Discovery only.** A feed item is not enough to publish a story. Before publication, verify the development against primary/authoritative sources and independently confirm every material figure, date and claim.",
        "",
    ]

    if not items:
        lines += ["No relevant feed items found in the current window.", ""]
        return "\n".join(lines)

    for idx, item in enumerate(items, 1):
        category = " / ".join(x.title() for x in item.categories)
        stamp = item.published.astimezone(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC")
        source_marker = "PRIMARY" if item.source_type == "primary" else "PUBLISHER"
        lines += [
            f"## {idx}. {item.title}",
            "",
            f"**{category} · Score {item.score} · {source_marker} · {item.source} · {stamp}**",
            "",
        ]
        if item.summary:
            summary = item.summary[:500].rstrip()
            if len(item.summary) > 500:
                summary += "…"
            lines += [summary, ""]
        lines += [
            f"Source: {item.link}",
            "",
            "Suggested Compound treatment: identify the practical Irish consequence, verify the underlying facts, then connect the news story to the most relevant evergreen guide or tool.",
            "",
        ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/news-feeds.yml")
    parser.add_argument("--hours", type=int, default=36)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output", default="news-radar.md")
    args = parser.parse_args()

    items = fetch(Path(args.config), args.hours, args.limit)
    Path(args.output).write_text(build_markdown(items, args.hours), encoding="utf-8")
    print(f"Wrote {len(items)} items to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
