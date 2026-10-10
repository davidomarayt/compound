"""Global stocks and private research watchlist: page types, links and SEO."""
import json
from pathlib import Path
import pytest

from compound.site.build import build_site
from compound.site.tradingview import render_tradingview_panel


def test_watchlist_registry_covers_requested_companies():
    root = Path(__file__).parents[1]
    data = json.loads((root / "content" / "company-watchlist.json").read_text())
    assert len(data["listed"]) == 10
    assert len(data["private"]) == 13
    assert {c["slug"] for c in data["listed"]} == {
        "spcx", "tsm", "asml", "005930-ks", "tm", "0700-hk",
        "1211-hk", "7974-t", "nvo", "mc-pa"
    }
    assert {c["slug"] for c in data["private"]} == {
        "openai", "anthropic", "bytedance", "databricks", "stripe",
        "revolut", "blue-origin", "anduril", "neuralink", "epic-games",
        "valve", "canva", "lego"
    }


def test_global_listed_and_private_pages_are_correctly_linked_and_gated(settings):
    listed = {
        "slug": "spcx", "name": "SpaceX", "ticker": "SPCX", "exchange": "Nasdaq",
        "market": "United States", "sector": "Aerospace",
        "summary": "Space launch and satellite connectivity.",
        "source": "https://example.test/spcx-listing",
        "tv_symbol": "NASDAQ:SPCX"
    }
    korean = {
        "slug": "005930-ks", "name": "Samsung Electronics",
        "ticker": "005930", "exchange": "KRX", "market": "South Korea",
        "sector": "Semiconductors", "summary": "Chips and phones.",
        "source": "https://example.test/krx",
        "tv_symbol": "KRX:005930"
    }
    private = {
        "slug": "openai", "name": "OpenAI", "sector": "AI",
        "summary": "AI research and products.", "website": "https://openai.com/"
    }
    private2 = {
        "slug": "canva", "name": "Canva", "sector": "Design software",
        "summary": "Visual design tools.", "website": "https://www.canva.com/"
    }
    (settings.content_dir / "company-watchlist.json").write_text(json.dumps({
        "checked": "2026-10-10", "listed": [listed, korean],
        "private": [private, private2]
    }), encoding="utf-8")
    wealth = settings.content_dir / "wealth"
    wealth.mkdir(parents=True, exist_ok=True)
    (wealth / "space-analysis.md").write_text("""---
title: SpaceX original research
slug: space-analysis
pillar: wealth
date: 2026-10-10
summary: Original notes about SpaceX.
tags: [stock-spcx, company-research]
---
Primary-source analysis of SpaceX.
""", encoding="utf-8")
    (wealth / "openai-analysis.md").write_text("""---
title: OpenAI original research
slug: openai-analysis
pillar: wealth
date: 2026-10-10
summary: Original notes about OpenAI.
tags: [company-openai, company-research]
---
Primary-source analysis of OpenAI.
""", encoding="utf-8")
    build_site(settings)
    root = settings.public_dir
    stocks = (root / "stocks/index.html").read_text(encoding="utf-8")
    companies = (root / "companies/index.html").read_text(encoding="utf-8")
    spcx = (root / "stocks/spcx/index.html").read_text(encoding="utf-8")
    samsung = (root / "stocks/005930-ks/index.html").read_text(encoding="utf-8")
    openai = (root / "companies/openai/index.html").read_text(encoding="utf-8")
    canva = (root / "companies/canva/index.html").read_text(encoding="utf-8")
    stock_article = (root / "wealth/space-analysis/index.html").read_text(encoding="utf-8")
    private_article = (root / "wealth/openai-analysis/index.html").read_text(encoding="utf-8")
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    search = json.loads((root / "search.json").read_text(encoding="utf-8"))

    assert "Global companies to watch" in stocks
    assert 'href="/stocks/spcx/"' in stocks
    assert 'href="/stocks/005930-ks/"' in stocks
    assert 'href="/companies/"' in stocks
    assert 'href="/companies/openai/"' in companies
    assert 'href="/companies/canva/"' in companies
    assert 'data-tv-symbol="NASDAQ:SPCX"' in spcx
    assert "SpaceX original research" in spcx
    assert 'name="robots" content="noindex,follow"' not in spcx
    assert 'data-tv-symbol="KRX:005930"' in samsung
    assert 'name="robots" content="noindex,follow"' in samsung
    assert "OpenAI original research" in openai
    assert "Privately held" in openai
    assert "tradingview-widget" not in openai
    assert 'name="robots" content="noindex,follow"' in canva
    assert 'href="/stocks/spcx/"' in stock_article
    assert 'href="/companies/openai/"' in private_article
    assert "OpenAI company news and research" in private_article
    assert '<loc>https://example.test/stocks/spcx/</loc>' in sitemap
    assert '<loc>https://example.test/companies/openai/</loc>' in sitemap
    assert '<loc>https://example.test/companies/</loc>' in sitemap
    assert '<loc>https://example.test/stocks/005930-ks/</loc>' not in sitemap
    assert '<loc>https://example.test/companies/canva/</loc>' not in sitemap
    assert any(x["url"] == "/companies/" for x in search)
    assert any(x["url"] == "/stocks/spcx/" for x in search)
    assert all(x["url"] != "/stocks/005930-ks/" for x in search)
    assert all(x["url"] != "/companies/canva/" for x in search)


def test_tradingview_accepts_exchange_qualified_tickers_and_rejects_injection():
    assert 'data-tv-symbol="NASDAQ:SPCX"' in render_tradingview_panel("NASDAQ:SPCX")
    assert 'data-tv-symbol="KRX:005930"' in render_tradingview_panel("KRX:005930")
    assert 'https://www.tradingview.com/symbols/KRX-005930/' in render_tradingview_panel("KRX:005930")
    assert render_tradingview_panel('NYSE:TSM"><script>') == ""


def test_watchlist_rejects_collisions_with_sp500_tickers(settings):
    (settings.content_dir / "earnings-sp500.json").write_text(json.dumps({
        "members": [{"cik":320193,"name":"Apple","sector":"IT",
                     "symbol":"AAPL","symbols":["AAPL"],"active": True}],
        "company_count":1,"security_count":1,"checked":"2026-10-10","source":"https://example.test"
    }), encoding="utf-8")
    (settings.content_dir / "company-watchlist.json").write_text(json.dumps({
        "listed": [{"slug": "aapl", "name": "Another Apple"}], "private": []
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate company slug"):
        build_site(settings)
