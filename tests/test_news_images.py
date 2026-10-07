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

    result = news_images.process(article, "fake-key")
    updated = article.read_text(encoding="utf-8")

    assert result == "skip:pinned-fetch-failed-no-image"
    assert "\nimage:" not in updated
