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
    assert 'image: "/static/images/evergreen/pickleball-ireland.jpg"' in updated


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
