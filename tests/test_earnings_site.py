"""Earnings hub integration with Compound's existing static-site generator."""
import json

from compound.site.build import build_site


def test_earnings_archive_is_indexable_and_linked(settings):
    build_site(settings)
    public = settings.public_dir
    html = (public / "wealth" / "earnings" / "index.html").read_text(encoding="utf-8")
    sitemap = (public / "sitemap.xml").read_text(encoding="utf-8")
    search = json.loads((public / "search.json").read_text(encoding="utf-8"))
    assert '<link rel="canonical" href="https://example.test/wealth/earnings/">' in html
    assert 'Earnings Reports' in html
    assert 'not individually reviewed before publication' in html
    assert sitemap.count('<loc>https://example.test/wealth/earnings/</loc>') == 1
    assert '/wealth/earnings/' in (public / "wealth" / "index.html").read_text(encoding="utf-8")
    assert any(x["url"] == "/wealth/earnings/" for x in search)


def test_legacy_quarterly_urls_are_redirected_and_removed_from_sitemaps(settings):
    folder=settings.content_dir/"wealth"
    folder.mkdir(exist_ok=True,parents=True)
    (folder/"unknown-earnings-fy2026-q3.md").write_text("""---
title: Unknown legacy earnings
slug: unknown-earnings-fy2026-q3
pillar: wealth
canonical_path: /wealth/earnings/unknown-earnings-fy2026-q3/
date: 2026-10-10
tags: [earnings, automated-earnings]
image: /static/images/wealth.jpg
---
Legacy quarterly article.
""")
    build_site(settings)
    root=settings.public_dir
    old=(root/"wealth/earnings/unknown-earnings-fy2026-q3/index.html").read_text()
    sitemap=(root/"sitemap.xml").read_text()
    search=json.loads((root/"search.json").read_text())
    assert 'http-equiv="refresh"' in old
    assert '<link rel="canonical" href="https://example.test/wealth/earnings/">' in old
    assert 'name="robots" content="noindex,follow"' in old
    assert "wealth.jpg" not in old
    assert '/wealth/earnings/unknown-earnings-fy2026-q3/' not in sitemap
    assert not any(x["url"].endswith("/unknown-earnings-fy2026-q3/") for x in search)


def test_earnings_company_history_and_pia_links_replace_tool_banner(settings):
    """Existing legacy related_tools cannot interrupt earnings numbers."""
    registry = {
        "source": "https://example.test/membership",
        "checked": "2026-10-10", "company_count": 1, "security_count": 1,
        "members": [{
            "cik": 920760, "name": "Lennar", "sector": "Consumer Discretionary",
            "symbol": "LEN", "symbols": ["LEN"], "active": True,
        }],
    }
    (settings.content_dir / "earnings-sp500.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )
    # The tool exists so the old auto-banner WOULD be added to a normal article.
    (settings.content_dir / "tools.yml").write_text(
        """tools:
  - slug: investment-fee-calculator
    title: Investment Fee Impact Calculator
    formula: investment_fees
    updated: 2026-10-10
    category: Pensions & Investing
    summary: Compare investment fee structures.
""",
        encoding="utf-8",
    )
    folder = settings.content_dir / "wealth"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "len-test-earnings.md").write_text(
        """---
title: Lennar filing report
slug: len-test-earnings
pillar: wealth
canonical_path: /wealth/earnings/len-test-earnings/
date: 2026-10-10
summary: Filing-backed data.
tags: [automated-earnings, earnings, len]
related_tools: [investment-fee-calculator]
---

## Earnings at a glance

Revenue was $8bn.

Net income was $200m.

Diluted earnings per share was $1.20.

Compare historical performance.

Source filing linked below.
""",
        encoding="utf-8",
    )
    (folder / "regular-investing-guide.md").write_text(
        """---
title: Regular investing guide
slug: regular-investing-guide
pillar: wealth
date: 2026-10-10
tags: [investing]
related_tools: [investment-fee-calculator]
---

First paragraph about investment costs.

Second paragraph explains percentage fees.

Third paragraph discusses compounding.

Fourth paragraph discusses fixed fees.

Fifth paragraph discusses financial choices.
""",
        encoding="utf-8",
    )
    build_site(settings)
    normal = (settings.public_dir / "wealth" /
              "regular-investing-guide" / "index.html").read_text(encoding="utf-8")
    assert 'class="article-tool-banner' in normal
    article = (settings.public_dir / "wealth" / "earnings" /
               "len-test-earnings" / "index.html").read_text(encoding="utf-8")
    assert 'http-equiv="refresh"' in article
    assert 'https://example.test/stocks/len/' in article
    assert 'class="article-tool-banner' not in article
    assert "Investment Fee Impact Calculator" not in article
