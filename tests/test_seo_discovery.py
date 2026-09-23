from datetime import date

from compound.site.build import build_site


def test_discovery_and_news_seo_output(settings):
    wealth = settings.content_dir / "wealth"
    wealth.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    (wealth / "seo-news.md").write_text(
        f"""---
title: SEO News Test
slug: seo-news-test
pillar: wealth
canonical_path: /news/seo-news-test/
date: {today}
reviewed: {today}
summary: Test news article for discovery markup.
meta_description: Test news article for discovery markup.
tags: [news, ireland]
image: /static/images/home-wealth.webp
image_alt: Irish wealth illustration.
sources:
- title: Example source
  url: https://example.com/source
---

Visible FAQ content stays.

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}}
</script>

## Frequently asked questions

### Does visible FAQ content remain?

Yes.
""",
        encoding="utf-8",
    )

    build_site(settings)

    html = (settings.public_dir / "news" / "seo-news-test" / "index.html").read_text(encoding="utf-8")
    news_hub = (settings.public_dir / "news" / "index.html").read_text(encoding="utf-8")
    robots = (settings.public_dir / "robots.txt").read_text(encoding="utf-8")
    news_sitemap = (settings.public_dir / "news-sitemap.xml").read_text(encoding="utf-8")

    assert '"@type": "NewsArticle"' in html
    assert '"@type": "BreadcrumbList"' in html
    assert '"@type": "Organization"' in html
    assert '"@type": "WebSite"' in html
    assert 'max-image-preview:large' in html
    assert 'FAQPage' not in html
    assert 'Frequently asked questions' in html
    assert 'google-add-preferred-source-btn' in html
    assert 'google-add-preferred-source-btn' in news_hub

    assert "news-sitemap.xml" in robots
    assert "/news/seo-news-test/" in news_sitemap
    assert "<news:publication_date>" in news_sitemap

    discover = settings.public_dir / "static" / "discover"
    assert (discover / "seo-news-test-1x1.webp").exists()
    assert (discover / "seo-news-test-4x3.webp").exists()
    assert (discover / "seo-news-test-16x9.webp").exists()
    assert "/static/discover/seo-news-test-16x9.webp" in html
