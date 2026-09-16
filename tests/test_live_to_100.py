"""Draft isolation, canonical routing and honest metadata for the longevity series."""
import json
import re
import shutil
from pathlib import Path

import pytest

from compound.site.build import (
    article_from_file, build_site, render_file_preview, series_context,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def series_draft(settings):
    (settings.content_dir / "health").mkdir()
    (settings.content_dir / "series").mkdir()
    draft = settings.content_dir / "health" / "live-to-100.md"
    source = (ROOT / "content/health/live-to-100.md").read_text()
    source = re.sub(r"^date:.*\n", "", source, flags=re.MULTILINE)
    draft.write_text(source.replace("draft: false", "draft: true").replace("publication_status: published", "publication_status: draft"))
    shutil.copy(ROOT / "content/series/live-to-100.yml", settings.content_dir / "series/live-to-100.yml")
    manifest = settings.content_dir / "series/live-to-100.yml"
    manifest.write_text(manifest.read_text().replace("status: published", "status: planned"))
    return draft


def test_draft_cannot_enter_public_discovery(settings, series_draft):
    assert article_from_file(series_draft) is None
    build_site(settings)
    for filename in ("index.html", "search.json", "feed.xml", "sitemap.xml", "health/index.html"):
        assert "live-to-100" not in (settings.public_dir / filename).read_text()
    assert not (settings.public_dir / "live-to-100/index.html").exists()
    assert not (settings.public_dir / "health/live-to-100/index.html").exists()


def test_local_review_has_content_but_no_publication_claims(settings, series_draft, tmp_path):
    result = render_file_preview(settings, series_draft, tmp_path / "review")
    html = result.read_text()
    assert 'content="noindex,nofollow,noarchive"' in html
    assert html.count("<h1>") == 1
    assert "datePublished" not in html
    assert 'rel="canonical"' not in html
    assert "googletagmanager.com/gtag" not in html
    assert "adsbygoogle.js" not in html
    assert "[live100:" not in html
    assert '<strong>70</strong>' in html and '<strong>35</strong>' in html
    assert html.count('class="chapter-panel"') == 5
    assert html.count("Coming next") == 6
    assert '/wealth/wealth-for-a-100-year-life/' not in html
    assert not settings.public_dir.exists()
    # The independently selected ages are not submitted by an HTML form.
    assert '<form' not in html


def test_future_parts_have_no_link_even_if_manifest_accidentally_says_published(settings, series_draft):
    article = article_from_file(series_draft, include_drafts=True)
    manifest = settings.content_dir / "series/live-to-100.yml"
    manifest.write_text(manifest.read_text().replace("status: planned", "status: published"))
    nav = series_context(article, settings.content_dir)
    assert len(nav["parts"]) == 4
    assert all(not part["url"] for part in nav["parts"])


def test_publication_requires_actual_date_and_has_one_canonical_route(settings, series_draft):
    text = series_draft.read_text().replace("draft: true", "draft: false").replace("publication_status: draft", "publication_status: published")
    series_draft.write_text(text)
    with pytest.raises(ValueError, match="actual publication date"):
        build_site(settings)
    series_draft.write_text(text.replace("reviewed: 2026-09-16", "reviewed: 2026-09-16\ndate: 2026-09-17"))
    build_site(settings)
    html = (settings.public_dir / "live-to-100/index.html").read_text()
    assert '<link rel="canonical" href="https://example.test/live-to-100/">' in html
    assert not (settings.public_dir / "health/live-to-100/index.html").exists()
    schemas = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
    assert {s["@type"] for s in schemas} == {"Article", "BreadcrumbList"}
    article_schema = next(s for s in schemas if s["@type"] == "Article")
    assert article_schema["datePublished"] == "2026-09-17"
    assert 'Live to 100 in Ireland: Planning a 100-Year Life | Compound' in html
    assert (settings.public_dir / "sitemap.xml").read_text().count("/live-to-100/") == 1


def test_canonical_conflicts_and_unsafe_preview_destinations_fail(settings, series_draft, tmp_path):
    with pytest.raises(ValueError, match="production build"):
        render_file_preview(settings, series_draft, settings.public_dir)
    with pytest.raises(ValueError, match="source files"):
        render_file_preview(settings, series_draft, settings.content_dir)
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("Keep me")
    with pytest.raises(ValueError, match="must be empty"):
        render_file_preview(settings, series_draft, occupied)
    assert (occupied / "keep.txt").read_text() == "Keep me"
    text = series_draft.read_text().replace("draft: true", "draft: false").replace("publication_status: draft", "publication_status: published").replace("canonical_path: /live-to-100/", "canonical_path: /search/")
    series_draft.write_text(text.replace("reviewed: 2026-09-16", "reviewed: 2026-09-16\ndate: 2026-09-16"))
    with pytest.raises(ValueError, match="route conflicts"):
        build_site(settings)
