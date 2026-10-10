"""Stock hub URL, indexing, cross-linking and share-class regression coverage."""
import json
from compound.site.build import build_site


def test_company_editorial_tags_attach_to_a_permanent_stock_hub(settings):
    registry = {
        "source": "https://example.test/company-register",
        "checked": "2026-10-10", "company_count": 2, "security_count": 3,
        "members": [
            {"cik": 1652044, "name": "Alphabet Inc.", "sector": "Communication Services",
             "symbol": "GOOGL", "symbols": ["GOOG", "GOOGL"], "active": True},
            {"cik": 320193, "name": "Apple Inc.", "sector": "Information Technology",
             "symbol": "AAPL", "symbols": ["AAPL"], "active": True},
        ],
    }
    (settings.content_dir / "earnings-sp500.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )
    wealth = settings.content_dir / "wealth"
    wealth.mkdir(parents=True, exist_ok=True)
    (wealth / "alphabet-research.md").write_text("""---
title: Alphabet independent research note
slug: alphabet-research
pillar: wealth
date: 2026-10-10
summary: Research about Alphabet.
tags: [goog, company-research]
---

Independent financial analysis, with company-specific source references.
""", encoding="utf-8")
    (wealth / "generic-investing.md").write_text("""---
title: How to invest in shares
slug: generic-investing
pillar: wealth
date: 2026-10-10
summary: Overview.
tags: [stocks, investing]
---

General advice, not about Alphabet or Apple.
""", encoding="utf-8")
    build_site(settings)
    root = settings.public_dir
    profile = (root / "stocks/googl/index.html").read_text(encoding="utf-8")
    apple = (root / "stocks/aapl/index.html").read_text(encoding="utf-8")
    alias = (root / "stocks/goog/index.html").read_text(encoding="utf-8")
    old = (root / "wealth/earnings/company/googl/index.html").read_text(encoding="utf-8")
    article = (root / "wealth/alphabet-research/index.html").read_text(encoding="utf-8")
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    search = json.loads((root / "search.json").read_text(encoding="utf-8"))

    assert '<link rel="canonical" href="https://example.test/stocks/googl/">' in profile
    assert 'Alphabet independent research note' in profile
    assert 'name="robots" content="noindex,follow"' not in profile
    assert 'href="/stocks/googl/"' in article
    assert "Alphabet Inc." in article
    assert 'name="robots" content="noindex,follow"' in apple
    assert 'Alphabet independent research note' not in apple
    assert 'How to invest in shares' not in profile
    assert 'name="robots" content="noindex,follow"' in alias
    assert 'content="0; url=/stocks/googl/"' in alias
    assert 'href="https://example.test/stocks/googl/"' in old
    assert '<loc>https://example.test/stocks/googl/</loc>' in sitemap
    assert '<loc>https://example.test/stocks/aapl/</loc>' not in sitemap
    assert '<loc>https://example.test/stocks/goog/</loc>' not in sitemap
    assert '<loc>https://example.test/wealth/earnings/company/googl/</loc>' not in sitemap
    assert any(x["url"] == "/stocks/" for x in search)
    assert any(x["url"] == "/stocks/googl/" for x in search)
    assert all(x["url"] not in ("/stocks/goog/", "/stocks/aapl/") for x in search)
