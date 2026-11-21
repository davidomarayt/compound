from pathlib import Path
from types import SimpleNamespace

from compound.site.incremental import ArticleRenderCache, hash_inputs, render_key


def _article(slug="first", title="First", body="Original body"):
    return SimpleNamespace(
        slug=slug, title=title, url=f"/wealth/{slug}/",
        body=body, tags=["investing"], related_tools=[],
    )


def test_cache_reuses_unchanged_article_and_invalidates_changed_body(tmp_path):
    cache = ArticleRenderCache(tmp_path / "cache", "site-code-v1")
    article = _article()
    recommendations = [_article("recommended", "Related")]
    key = render_key(base=cache.base, article=article,
                     recommendations=recommendations, tools=[], profile=None)
    output = tmp_path / "public" / "wealth" / "first" / "index.html"
    assert not cache.reuse(article.url, key, output)
    output.parent.mkdir(parents=True)
    output.write_text("<html>First</html>", encoding="utf-8")
    cache.store(article.url, key, output)
    output.unlink()
    assert cache.reuse(article.url, key, output)
    assert output.read_text(encoding="utf-8") == "<html>First</html>"
    assert cache.hits == 1
    assert cache.misses == 1
    article.body = "Changed article"
    changed = render_key(base=cache.base, article=article,
                         recommendations=recommendations, tools=[], profile=None)
    assert changed != key
    assert not cache.reuse(article.url, changed, output)


def test_recommendation_change_and_code_change_invalidate(tmp_path):
    original = _article()
    related = [_article("related", "Old related title")]
    a = render_key(base="template-v1", article=original,
                   recommendations=related, tools=[], profile=None)
    related[0].title = "New related title"
    b = render_key(base="template-v1", article=original,
                   recommendations=related, tools=[], profile=None)
    c = render_key(base="template-v2", article=original,
                   recommendations=related, tools=[], profile=None)
    assert len({a, b, c}) == 3
    source = tmp_path / "template.html"
    source.write_text("one")
    first = hash_inputs([source])
    source.write_text("two")
    assert hash_inputs([source]) != first


def test_disabled_cache_and_invalid_urls_fall_back(tmp_path):
    disabled = ArticleRenderCache(None, "version")
    out = tmp_path / "out.html"
    assert not disabled.reuse("/wealth/first/", "hash", out)
    enabled = ArticleRenderCache(tmp_path / "cache", "version")
    assert not enabled.reuse("/../../private/", "hash", out)
    assert not out.exists()


def test_mixed_numeric_and_string_keys_in_article_metadata(tmp_path):
    """Regression: real article charts include nested int and string keys."""
    article = _article()
    article.charts = [{"values": {1: "point a", "2": "point b"}}]
    first = render_key(base="site", article=article,
                       recommendations=[], tools=[], profile=None)
    again = render_key(base="site", article=article,
                       recommendations=[], tools=[], profile=None)
    assert first == again
    article.charts[0]["values"][1] = "changed"
    changed = render_key(base="site", article=article,
                         recommendations=[], tools=[], profile=None)
    assert changed != first
