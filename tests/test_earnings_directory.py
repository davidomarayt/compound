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
---

A sourced report.
''')
    build_site(settings)
    p=settings.public_dir
    hub=(p/'wealth'/'earnings'/'index.html').read_text()
    apple=(p/'wealth'/'earnings'/'company'/'aapl'/'index.html').read_text()
    alphabet=(p/'wealth'/'earnings'/'company'/'googl'/'index.html').read_text()
    sitemap=(p/'sitemap.xml').read_text()
    assert 'Example Apple' in hub and 'Example Alphabet' in hub
    assert '3 share classes' in hub and '2 active companies' in hub
    assert '/wealth/earnings/company/aapl/' in hub
    assert '/wealth/earnings/company/googl/' in hub
    assert 'Example Apple results' in apple
    assert 'name="robots" content="noindex,follow"' not in apple
    assert 'name="robots" content="noindex,follow"' in alphabet
    assert '<loc>https://example.test/wealth/earnings/company/aapl/</loc>' in sitemap
    assert '<loc>https://example.test/wealth/earnings/company/googl/</loc>' not in sitemap
    assert '/static/earnings-directory.js?v=1' in hub