"""Regression checks for fast editorial QA; no network access required."""
from pathlib import Path

from scripts.article_preflight import inspect


FRONT = """---
title: "Ireland's confirmed new grant: who qualifies?"
seo_title: "New Irish Grant 2026: Eligibility"
slug: new-grant-ireland
pillar: wealth
draft: false
publication_status: published
date: 2026-10-12
summary: "An accessible guide to the grant, eligibility rules and practical checks."
meta_description: "What the Irish grant covers, who qualifies and how to apply, with useful examples and trusted sources."
canonical_path: /news/new-grant-ireland/
tags: [news, grant, ireland]
news_image_query: "Irish home energy retrofit"
sources:
  - title: "SEAI official rules"
    url: https://www.seai.ie/grants/
  - title: "Government announcement"
    url: https://www.gov.ie/
charts:
  - title: "Illustrative annual costs"
    kind: bar
    unit: "euro"
    caption: "Illustrations, not forecasts."
    source_url: https://www.seai.ie/grants/
    items:
      - {label: "Example A", value: 300, text: "€300"}
      - {label: "Example B", value: 400, text: "€400"}
---
A clear explanation linked to [a relevant tool](/solar-payback-calculator/).
"""


def test_valid_published_article_passes(tmp_path: Path) -> None:
    article = tmp_path / "grant.md"
    article.write_text(FRONT, encoding="utf-8")
    errors, warnings = inspect(article)
    assert errors == []
    assert warnings == []


def test_missing_sources_fails_for_news(tmp_path: Path) -> None:
    article = tmp_path / "grant.md"
    article.write_text(FRONT.replace("sources:\n", "unrelated_key:\n"), encoding="utf-8")
    errors, _ = inspect(article)
    assert any("source" in error for error in errors)


def test_missing_metadata_fails(tmp_path: Path) -> None:
    article = tmp_path / "grant.md"
    article.write_text(FRONT.replace('meta_description: "What the Irish grant covers, who qualifies and how to apply, with useful examples and trusted sources."\n', ""), encoding="utf-8")
    errors, _ = inspect(article)
    assert any("meta_description" in error for error in errors)


def test_draft_skips_publishing_gates(tmp_path: Path) -> None:
    article = tmp_path / "draft.md"
    article.write_text(FRONT.replace("draft: false", "draft: true").replace("sources:\n", "unrelated_key:\n"), encoding="utf-8")
    errors, _ = inspect(article)
    assert not errors


def test_unresolved_placeholder_fails(tmp_path: Path) -> None:
    article = tmp_path / "grant.md"
    article.write_text(FRONT + "\nSource needed\n", encoding="utf-8")
    errors, _ = inspect(article)
    assert any("placeholder" in error for error in errors)
