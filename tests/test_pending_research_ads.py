import json
from pathlib import Path

from compound.site.build import build_site


def test_pending_research_is_ad_free_on_article_and_company(settings):
    wealth = settings.content_dir / "wealth"
    wealth.mkdir()
    (wealth / "pending.md").write_text(
        "---\ntitle: Pending research\nslug: pending\npillar: wealth\n"
        "date: '2026-10-21'\nresearch_checked: '2026-11-11'\neditorial_review_status: pending\n"
        "image: /static/images/evergreen/meta-ai-app-earnings.jpg\n"
        "image_alt: Meta AI app\nimage_credit: Salvador Rios / Unsplash\n"
        "image_source: https://unsplash.com/photos/tkkOCi1Wgx0\n"
        "tags: [stocks, company-research, meta]\n---\nResearch awaiting editor review."
    )
    registry = json.loads(Path("content/earnings-sp500.json").read_text())
    registry["members"] = [c for c in registry["members"] if c["symbol"] == "META"]
    (settings.content_dir / "earnings-sp500.json").write_text(json.dumps(registry))
    (settings.content_dir / "site.yml").write_text(
        "adsense:\n  client: ca-pub-test\n  slots:\n"
        "    article_top: '1'\n    article_bottom: '2'\n"
        "    stock_mid: '3'\n    stock_lower: '4'\n"
    )
    build_site(settings)
    article = (settings.public_dir / "wealth/pending/index.html").read_text()
    company = (settings.public_dir / "stocks/meta/index.html").read_text()
    for html in [article, company]:
        assert "adsbygoogle" not in html
        assert "pagead2.googlesyndication.com" not in html
    assert '"datePublished": "2026-10-21"' in article
    assert '"dateModified": "2026-11-11"' in article
    assert '<meta property="article:published_time" content="2026-10-21">' in article
    assert '<meta property="article:modified_time" content="2026-11-11">' in article
    catalogue = json.loads((settings.public_dir / "finance/index.json").read_text())
    entry = next(e for e in catalogue["entries"] if e["url"].endswith("/wealth/pending/"))
    assert entry["published"] == "2026-10-21"
    assert entry["modified"] == "2026-11-11"
    assert "Compound Research" in article
    assert '"name": "David"' not in article
    assert "Every article is reviewed and approved" not in article
    assert "/wealth/pending/" in company
