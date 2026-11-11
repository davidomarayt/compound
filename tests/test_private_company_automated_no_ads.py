"""Private-company monetization requires genuine recorded human editorial approval."""
import json
from pathlib import Path

import pytest
from PIL import Image
from scripts.normalise_private_company_images import normalise_pinned_photo

from compound.site.build import _env, article_context, article_from_file, article_jsonld


ROOT = Path(__file__).resolve().parents[1]
SLUGS = {
    "openai": "openai-businesses-chatgpt-agent-commerce-trust-2026",
    "anthropic": "anthropic-fable-mythos-52-pricing-routing-economics",
    "databricks": "databricks-european-sovereign-cloud-expansion-economics",
}


def test_private_company_articles_have_neutral_attribution_and_no_unreviewed_ads(settings, monkeypatch):
    # Real site settings enable an AdSense client; test the exact non-audit render.
    monkeypatch.delenv("COMPOUND_AUDIT_MODE", raising=False)
    (settings.content_dir / "site.yml").write_text("""
adsense:
  client: ca-pub-test-123
  slots:
    article_top: 111
    article_bottom: 222
""")
    env = _env(settings)
    for company, slug in SLUGS.items():
        article_path = ROOT / "content" / "wealth" / f"{slug}.md"
        article = article_from_file(article_path)
        assert article is not None
        assert "private-company" in article.tags and "unreviewed-ai" not in article.tags
        assert f"company-{company}" in article.tags
        context = article_context(env, settings, article, False)
        assert context["ads_allowed"] is False
        html = env.get_template("article.html").render(**context, related=[], linked_tools=[])
        assert "pagead2.googlesyndication.com" not in html
        assert "adsbygoogle" not in html
        assert 'data-ad-client="' not in html
        assert 'By <a href="/editorial-policy/">Compound Research</a>' in html
        assert "AI-assisted" not in html and "awaiting human review" not in html
        assert "Every article is reviewed and approved before publication" not in html
        assert f'href="/companies/{company}/"' in html
        assert f'<link rel="canonical" href="https://example.test/wealth/{slug}/">' in html
        social_url = f"https://example.test/static/discover/{slug}-16x9.webp"
        assert f'property="og:image" content="{social_url}"' in html
        assert f'name="twitter:image" content="{social_url}"' in html
        schema = json.loads(article_jsonld(article, "https://compound.ie"))
        assert schema["author"] == {
            "@type": "Organization",
            "name": "Compound Research",
            "url": "https://compound.ie/editorial-policy/",
        }
        assert schema["image"][-1] == f"https://compound.ie/static/discover/{slug}-16x9.webp"


def test_ads_default_unchanged_for_preexisting_reviewed_articles(settings, monkeypatch):
    monkeypatch.delenv("COMPOUND_AUDIT_MODE", raising=False)
    (settings.content_dir / "site.yml").write_text("adsense:\n  client: ca-pub-test-123\n")
    env = _env(settings)
    article = article_from_file(ROOT / "content" / "wealth" / "amazon-advertising-prime-day-timing.md")
    assert article is not None
    assert "unreviewed-ai" not in article.tags
    context = article_context(env, settings, article, False)
    assert context["ads_allowed"] is True
    html = env.get_template("article.html").render(**context, related=[], linked_tools=[])
    assert "pagead2.googlesyndication.com" in html


def test_private_company_hub_gates_ads_on_human_review():
    # Linked unreviewed articles must not silently monetize the hub.
    build = (ROOT / "compound" / "site" / "build.py").read_text()
    assert "ads_allowed=bool(stories) and all(a.human_reviewed_by and a.human_reviewed_at for a in stories)))" in build


def test_approved_pinned_photo_is_reencoded_as_a_real_jpeg(tmp_path):
    # Wikimedia JPEGs with an MPF segment may be detected as MPO.
    # A non-JPEG raster container must not be served unchanged with .jpg.
    cover = tmp_path / "licensed-cover.jpg"
    Image.new("RGB", (1200, 800), "white").save(cover, format="PNG")
    normalise_pinned_photo(cover)
    with Image.open(cover) as converted:
        assert converted.format == "JPEG"
        assert converted.size == (1200, 800)
        converted.verify()


def test_pinned_photo_rejects_small_source_instead_of_upscaling(tmp_path):
    cover = tmp_path / "tiny.jpg"
    Image.new("RGB", (500, 400), "white").save(cover, format="PNG")
    with pytest.raises(ValueError, match="too small"):
        normalise_pinned_photo(cover)


def test_verified_manual_review_enables_private_company_ads(settings, monkeypatch):
    """A dated, named editorial approval enables ad serving after an actual review."""
    from dataclasses import replace

    monkeypatch.delenv("COMPOUND_AUDIT_MODE", raising=False)
    (settings.content_dir / "site.yml").write_text(
        "adsense:\n  client: ca-pub-test-123\n  slots:\n    article_top: 111\n"
    )
    env = _env(settings)
    source = article_from_file(ROOT / "content" / "wealth" /
                               "openai-businesses-chatgpt-agent-commerce-trust-2026.md")
    assert source is not None
    reviewed = replace(source, human_reviewed_by="Editor", human_reviewed_at="2026-11-11T14:00:00Z")
    context = article_context(env, settings, reviewed, False)
    assert context["ads_allowed"] is True
    html = env.get_template("article.html").render(**context, related=[], linked_tools=[])
    assert "pagead2.googlesyndication.com" in html
    assert "adsbygoogle" in html
