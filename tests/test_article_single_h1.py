"""Article bodies must not render their own <h1>.

The article template already renders the page title as the single <h1>. On
27 Nov 2026 a sitemap crawl found seven pages with extra <h1> elements because
the Markdown body used level-one `# ` headings: six pension course chapters
repeated the title, and the Manchester City explainer used `# ` for twelve
section headings (13 <h1> elements in total). One <h1> per page keeps the
heading outline usable for screen-reader navigation and gives search engines
an unambiguous page heading.
"""
import re
from pathlib import Path

from compound.site.build import load_articles

CONTENT = Path(__file__).parents[1] / "content"
H1 = re.compile(r"<h1[\s>]", re.I)


def test_no_article_body_renders_an_h1():
    offenders = [a.slug for a in load_articles(CONTENT) if H1.search(a.body_html)]
    assert offenders == []


def test_manchester_city_sections_are_h2():
    article = next(
        a for a in load_articles(CONTENT)
        if a.slug == "manchester-city-114-financial-rule-breaches-explained"
    )
    assert "<h2>The deeper issue: what counts as real revenue?</h2>" in article.body_html
    assert "<h2>The bottom line</h2>" in article.body_html


def test_pension_chapter_keeps_question_heading_as_h2():
    article = next(
        a for a in load_articles(CONTENT)
        if a.slug == "changing-jobs-transfer-pension-ireland"
    )
    assert "<h2>What happens to your pension when you change jobs?</h2>" in article.body_html
