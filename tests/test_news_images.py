import pytest
from pathlib import Path

from scripts import news_images


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _Client:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, *args, **kwargs):
        return _Response(self.payload)


def test_explicit_image_query_preserves_pexels_relevance_order(monkeypatch):
    photos = [{"id": 101}, {"id": 202}, {"id": 303}]
    monkeypatch.setattr(news_images.httpx, "Client", lambda **kwargs: _Client({"photos": photos}))
    news_images.USED_PEXELS_PHOTO_IDS.clear()

    photo = news_images.pexels_photo(
        "pickleball paddle ball court",
        "fake-key",
        "pickleball-ireland",
        prefer_ranked=True,
    )

    assert photo["id"] == 101


def test_evergreen_explicit_query_never_gets_generic_fallback(tmp_path, monkeypatch):
    article = tmp_path / "pickleball-ireland.md"
    article.write_text(
        """---
title: "Pickleball in Ireland"
slug: pickleball-ireland
pillar: happiness
draft: false
publication_status: published
news_image_query: "pickleball paddle ball on court"
---

Body.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(news_images, "pexels_photo", lambda *args, **kwargs: None)

    result = news_images.process(article, "fake-key")
    updated = article.read_text(encoding="utf-8")

    assert result.startswith("skip:evergreen-topic-image-unavailable:")
    assert "\nimage:" not in updated
    assert "image_credit:" not in updated


def test_failed_pinned_evergreen_does_not_substitute_generic_photo(tmp_path, monkeypatch):
    article = tmp_path / "pickleball-ireland.md"
    article.write_text(
        """---
title: "Pickleball in Ireland"
slug: pickleball-ireland
pillar: happiness
draft: false
publication_status: published
news_image_query: "pickleball paddle ball on court"
pexels_photo_id: "38208389"
---

Body.
""",
        encoding="utf-8",
    )

    def fail(*args, **kwargs):
        raise RuntimeError("temporary Pexels failure")

    monkeypatch.setattr(news_images, "pexels_photo_by_id", fail)
    monkeypatch.setattr(news_images, "download", fail)

    result = news_images.process(article, "fake-key")
    updated = article.read_text(encoding="utf-8")

    assert result == "skip:pinned-fetch-failed-no-image"
    assert "\nimage:" not in updated


def test_pinned_evergreen_recovers_same_photo_from_cdn_if_api_rate_limited(tmp_path, monkeypatch):
    article = tmp_path / "pickleball-ireland.md"
    article.write_text(
        '''---
title: "Pickleball in Ireland"
slug: pickleball-ireland
pillar: happiness
draft: false
publication_status: published
pexels_photo_id: "38208389"
---

Body.
''',
        encoding="utf-8",
    )

    def api_failed(*args, **kwargs):
        raise RuntimeError("Pexels API 429")

    downloads = []

    def fake_download(url, dest):
        downloads.append(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"fake jpeg test bytes")

    monkeypatch.setattr(news_images, "pexels_photo_by_id", api_failed)
    monkeypatch.setattr(news_images, "download", fake_download)
    monkeypatch.setattr(news_images, "STATIC", tmp_path / "static")

    result = news_images.process(article, "fake-key")
    updated = article.read_text(encoding="utf-8")

    assert result == "pexels-pinned-direct:38208389"
    assert "https://images.pexels.com/photos/38208389/pexels-photo-38208389.jpeg" in downloads[0]
    assert news_images.parse(article)[0]["image"] == "/static/images/evergreen/pickleball-ireland.jpg"


def test_automated_earnings_never_receive_images_even_when_forced(tmp_path, monkeypatch):
    article = tmp_path / "len-earnings-fy2026-q3.md"
    original = """---
title: 'Lennar (LEN) Earnings'
slug: len-earnings-fy2026-q3
pillar: wealth
publication_status: published
tags: [earnings, automated-earnings, stocks]
hero_image_url: https://example.com/some-kitchen.jpg
---

Earnings text only.
"""
    article.write_text(original, encoding="utf-8")

    def unexpected(*args, **kwargs):
        raise AssertionError("Image lookup/download must not run for automated earnings")

    monkeypatch.setattr(news_images, "download", unexpected)
    monkeypatch.setattr(news_images, "pexels_photo", unexpected)
    monkeypatch.setattr(news_images, "fallback_image", unexpected)

    assert news_images.process(article, "fake-key", force=False) == "skip:automated-earnings-text-only"
    assert news_images.process(article, "fake-key", force=True) == "skip:automated-earnings-text-only"
    assert article.read_text(encoding="utf-8") == original


def test_stock_article_requires_company_photo(tmp_path, monkeypatch):
    doc = tmp_path / "merger.md"
    doc.write_text(
        "---\ntitle: Will Tesla and SpaceX merge?\nslug: merger\n"
        "pillar: wealth\ntags: [stocks, tesla, spacex]\n"
        "publication_status: published\n---\nResearch.",
        encoding="utf-8",
    )
    monkeypatch.setattr(news_images, "STATIC", tmp_path / "static")
    with pytest.raises(ValueError, match="company-specific photograph"):
        news_images.process(doc, "")
    assert "image:" not in doc.read_text(encoding="utf-8")


def test_stock_article_pinned_image_and_no_inheritance_keyword(tmp_path, monkeypatch):
    meta = {"title": "Will Tesla and SpaceX Merge in 2027?", "slug": "merger", "pillar": "wealth", "tags": ["stocks"]}
    assert news_images._local_photo_for(meta)["file"] != "tax-paperwork.jpg"
    doc = tmp_path / "merger.md"
    doc.write_text(
        "---\ntitle: Will Tesla and SpaceX merge?\nslug: merger\n"
        "pillar: wealth\ntags: [stocks, tesla, spacex]\n"
        "publication_status: published\n"
        "hero_image_url: https://www.nasa.gov/test-image.jpg\n"
        "hero_image_alt: SpaceX rocket photographed in flight\n"
        "hero_image_credit: NASA photographer\n"
        "hero_image_source: https://www.nasa.gov/\n"
        "---\nResearch.",
        encoding="utf-8",
    )
    monkeypatch.setattr(news_images, "STATIC", tmp_path / "static")
    def stub_download(url, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"sample-jpeg")
    monkeypatch.setattr(news_images, "download", stub_download)
    assert news_images.process(doc, "") == "pinned-url"
    assert "/static/images/evergreen/merger.jpg" in doc.read_text(encoding="utf-8")
    assert "NASA photographer" in doc.read_text(encoding="utf-8")


def test_inject_fields_replaces_wrapped_and_block_scalars(tmp_path):
    p = tmp_path / 'story.md'
    p.write_text('---\ntitle: Story\nimage_alt: old text\n  continued text\nimage_credit: |\n  Old credit\n  second line\nsources:\n- url: https://example.com\n---\nBody stays exactly.\n')
    _, raw, match = news_images.parse(p)
    news_images.inject_fields(p, raw, match, {'image_alt': 'New alt', 'image_credit': 'New credit'})
    meta, updated, _ = news_images.parse(p)
    assert meta['image_alt'] == 'New alt'
    assert meta['image_credit'] == 'New credit'
    assert meta['sources'] == [{'url': 'https://example.com'}]
    assert updated.endswith('Body stays exactly.\n')


def test_cache_restores_assets_without_network_and_invalidates_source(tmp_path, monkeypatch):
    from PIL import Image
    static = tmp_path / 'static'
    monkeypatch.setattr(news_images, 'STATIC', static)
    cache = tmp_path / 'cache'
    p = tmp_path / 'story.md'
    original = '---\ntitle: Story\nslug: story\nhero_image_url: https://example.com/one.jpg\n---\nBody.\n'
    p.write_text(original)
    calls = []
    def processor(path, api_key, force=False):
        calls.append(path.read_text())
        asset = static / 'images/story.jpg'
        asset.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (30, 20), 'blue').save(asset)
        _, raw, match = news_images.parse(path)
        news_images.inject_fields(path, raw, match, {'image': '/static/images/story.jpg', 'social_image': '/static/images/story.jpg'})
        return 'pinned-url'
    monkeypatch.setattr(news_images, 'process', processor)
    assert news_images.process_cached(p, '', cache) == 'pinned-url'
    processed = p.read_text()
    (static / 'images/story.jpg').unlink()
    p.write_text(original)
    assert news_images.process_cached(p, '', cache) == 'skip:cached-images'
    assert len(calls) == 1 and p.read_text() == processed
    assert (static / 'images/story.jpg').is_file()
    p.write_text(original.replace('one.jpg', 'two.jpg'))
    assert news_images.process_cached(p, '', cache) == 'pinned-url'
    assert len(calls) == 2
    # A corrupt cached blob cannot pass as a successfully reused photograph.
    import json
    record = json.loads(next(cache.glob('*.json')).read_text())
    for entry in cache.glob('*.json'):
        for asset in json.loads(entry.read_text())['assets']:
            (cache / asset['sha']).write_bytes(b'corrupt')
    p.write_text(original)
    assert news_images.process_cached(p, '', cache) == 'pinned-url'
    assert len(calls) == 3
