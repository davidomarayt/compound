from datetime import date

from compound.site.build import Article


def make_article(**overrides):
    values = {
        "title": "Example Life Article",
        "slug": "example-life-article",
        "pillar": "happiness",
        "date": date(2026, 10, 3),
        "summary": "Example",
        "body_html": "<p>Example</p>",
    }
    values.update(overrides)
    return Article(**values)


def test_happiness_pillar_publishes_under_life_path():
    article = make_article()
    assert article.public_pillar_slug == "life"
    assert article.url == "/life/example-life-article/"


def test_explicit_canonical_path_still_overrides_pillar_route():
    article = make_article(canonical_path="/news/example-life-article/")
    assert article.url == "/news/example-life-article/"
