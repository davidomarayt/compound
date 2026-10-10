"""Integration regression tests for the S&P 500 public directory and company profiles."""
import json
from compound.site.build import build_site


def test_sp500_directory_profiles_and_nonindexing(settings):
    registry={
        'source':'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        'checked':'2026-10-10', 'company_count':2, 'security_count':3,
        'members':[
            {'cik':320193,'name':'Example Apple', 'sector':'Information Technology',
             'symbol':'AAPL','symbols':['AAPL'],'active':True},
            {'cik':1652044,'name':'Example Alphabet','sector':'Communication Services',
             'symbol':'GOOGL','symbols':['GOOG','GOOGL'],'active':True},
        ]
    }
    (settings.content_dir/'earnings-sp500.json').write_text(json.dumps(registry),encoding='utf-8')
    folder=settings.content_dir/'wealth'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'aapl-earnings-fy2026-q3.md').write_text('''---
title: Example Apple results
slug: aapl-earnings-fy2026-q3
pillar: wealth
canonical_path: /wealth/earnings/aapl-earnings-fy2026-q3/
date: 2026-10-10
summary: Verifiable filing summary.
tags: [earnings, automated-earnings, aapl]
earnings_snapshot:
  form: 10-Q
  report_end: '2026-09-30'
  period_label: FY 2026 Q3
  metrics:
    revenue: {current: 10000000000, prior: 9000000000}
    net_income: {current: 2000000000, prior: 1800000000}
    diluted_eps: {current: 1.5, prior: 1.2}
sources:
  - title: SEC Apple 10-Q filed 2026-10-09
    url: https://www.sec.gov/Archives/edgar/data/320193/example.htm
---

A sourced report.
''')
    build_site(settings)
    p=settings.public_dir
    hub=(p/'wealth'/'earnings'/'index.html').read_text()
    apple=(p/'stocks'/'aapl'/'index.html').read_text()
    alphabet=(p/'stocks'/'googl'/'index.html').read_text()
    sitemap=(p/'sitemap.xml').read_text()
    assert 'Example Apple' in hub and 'Example Alphabet' in hub
    assert '3 share classes' in hub and '2 active companies' in hub
    assert '/stocks/aapl/' in hub
    assert '/stocks/googl/' in hub
    assert 'FY2026 Q3' in apple
    assert '2026-09-30' in apple
    assert 'name="robots" content="noindex,follow"' not in apple
    assert 'name="robots" content="noindex,follow"' in alphabet
    assert 'Verified FY2026' not in alphabet
    assert 'Awaiting a verified SEC filing' in alphabet
    assert 'one report per business' in hub.lower() or 'one live report per company' in hub.lower()
    assert 'summaryies' not in apple
    assert 'summaryies' not in alphabet
    assert '<loc>https://example.test/stocks/aapl/</loc>' in sitemap
    assert '<loc>https://example.test/stocks/googl/</loc>' not in sitemap
    assert '/static/earnings-directory.js?v=1' in hub
    stocks=(p/'stocks'/'index.html').read_text()
    assert '<link rel="canonical" href="https://example.test/stocks/">' in stocks
    assert '/stocks/aapl/' in stocks and '/stocks/googl/' in stocks
    assert 'Showing 2 of 2 companies' in stocks
    assert '2 companies' in stocks
    assert 'S&amp;P 500' not in stocks
    assert '<loc>https://example.test/stocks/</loc>' in sitemap
    legacy=(p/'wealth'/'earnings'/'company'/'aapl'/'index.html').read_text()
    assert 'http-equiv="refresh"' in legacy
    assert '<link rel="canonical" href="https://example.test/stocks/aapl/">' in legacy
    assert 'name="robots" content="noindex,follow"' in legacy
    assert '<loc>https://example.test/wealth/earnings/company/aapl/</loc>' not in sitemap
    assert "https://example.test/stocks/aapl/" in apple
    search=json.loads((p/'search.json').read_text())
    assert any(x['url']=='/stocks/' for x in search)
    assert any(x['url']=='/stocks/aapl/' for x in search)
    assert not any(x['url']=='/stocks/googl/' for x in search)

def test_earnings_profile_is_one_report_not_a_quarterly_article_list():
    from pathlib import Path
    template=(Path(__file__).resolve().parents[1] /
              "compound/site/templates/earnings_company.html").read_text()
    assert 'include "_company_quarters.html"' in template
    assert "published summaries" not in template
    assert "quarterly report cards" not in template
