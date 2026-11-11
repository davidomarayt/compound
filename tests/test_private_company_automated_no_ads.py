"""Unreviewed private-company research must not monetise or misstate human approval."""
from pathlib import Path

from compound.site.build import _env, article_context, article_from_file


ROOT = Path(__file__).resolve().parents[1]
SLUGS = {
    "openai": "openai-businesses-chatgpt-agent-commerce-trust-2026",
    "anthropic": "anthropic-fable-mythos-52-pricing-routing-economics",
    "databricks": "databricks-european-sovereign-cloud-expansion-economics",
}


def test_automated_private_company_articles_never_load_adsense_or_claim_human_editor(settings, monkeypatch):
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
        assert "unreviewed-ai" in article.tags
        assert f"company-{company}" in article.tags
        context = article_context(env, settings, article, False)
        assert context["ads_allowed"] is False
        html = env.get_template("article.html").render(**context, related=[], linked_tools=[])
        assert "pagead2.googlesyndication.com" not in html
        assert "adsbygoogle" not in html
        assert 'data-ad-client="' not in html
        assert "awaiting human review" in html
        assert "not received human editorial approval" in html
        assert "Every article is reviewed and approved before publication" not in html
        assert f'href="/companies/{company}/"' in html
        assert f'<link rel="canonical" href="https://example.test/wealth/{slug}/">' in html
        assert "og:image" in html and "twitter:image" in html


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


def test_private_company_hub_disables_ads_if_it_contains_unreviewed_research():
    # The production generator must keep hub ads off where a linked story is unreviewed.
    build = (ROOT / "compound" / "site" / "build.py").read_text()
    assert 'ads_allowed=bool(stories) and not any("unreviewed-ai" in a.tags for a in stories)' in build
