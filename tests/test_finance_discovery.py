import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from urllib.robotparser import RobotFileParser

import pytest
from compound.site.finance_discovery import catalogue, validate_targets, source_links, PageMetadata


def article(**overrides):
    values = dict(slug='before-you-invest-ireland', title='Before investing',
                  publication_status='published', pillar='wealth', tags=[],
                  url='/wealth/before-you-invest-ireland/', description='Start here',
                  date=date(2026, 9, 1), reviewed=None,
                  sources=[{'url': 'https://www.revenue.ie/', 'title': 'Revenue'}])
    return SimpleNamespace(**(values | overrides))


def test_selection_dates_and_source_provenance():
    data = catalogue('https://example.test/', [article(), article(slug='draft', publication_status='draft', tags=['stocks']),
        article(slug='legacy', tags=['automated-earnings', 'stocks']),
        article(slug='health', pillar='health', tags=['stocks'])], [], [], False)
    assert len(data['entries']) == 1
    entry = data['entries'][0]
    assert entry['url'] == 'https://example.test/wealth/before-you-invest-ireland/'
    assert entry['published'] == entry['modified'] == '2026-09-01'
    assert entry['sources'] == [{'url': 'https://www.revenue.ie/', 'title': 'Revenue'}]
    assert source_links([{'url': 'javascript:alert(1)'}, {'url': '/preview/foo/'}]) == []


@pytest.mark.parametrize('bad', ['missing', 'noindex', 'alias', 'redirect', 'not-in-sitemap'])
def test_bad_targets_block_discovery(tmp_path, bad):
    data = catalogue('https://example.test', [article()], [], [], False)
    url = data['entries'][0]['url']
    page = tmp_path / 'wealth/before-you-invest-ireland/index.html'
    page.parent.mkdir(parents=True)
    canonical = 'https://example.test/other/' if bad == 'alias' else url
    content = f'<link rel="canonical" href="{canonical}">'
    if bad == 'noindex':
        content += '<meta name="robots" content="noindex,follow">'
    if bad == 'redirect':
        content += '<meta http-equiv="refresh" content="0; url=/other/">'
    if bad != 'missing':
        page.write_text(content)
    with pytest.raises(ValueError):
        validate_targets(data, tmp_path, [] if bad == 'not-in-sitemap' else [url])


def test_built_discovery_and_crawler_access(settings):
    from compound.site.build import build_site
    build_site(settings)
    out = settings.public_dir
    data = json.loads((out / 'finance/index.json').read_text())
    page = (out / 'finance/index.html').read_text()
    assert data['url'] == 'https://example.test/finance/'
    metadata = PageMetadata(); metadata.feed(page)
    assert metadata.canonicals == [data['url']]
    assert not metadata.noindex
    assert 'CollectionPage' in page and 'ItemList' in page
    assert '/finance/' in (out / 'index.html').read_text()
    assert data['url'] in (out / 'sitemap.xml').read_text()
    assert '/finance/index.json' in (out / 'llms.txt').read_text()
    robots = RobotFileParser(); robots.parse((out / 'robots.txt').read_text().splitlines())
    for bot in ('OAI-SearchBot', 'ChatGPT-User', 'Claude-SearchBot', 'Claude-User', 'Googlebot', 'Google-Extended', 'bingbot', 'GPTBot', '*'):
        for path in ('/finance/', '/finance/index.json', '/llms.txt', '/stocks/aapl/', '/compound-interest-calculator/'):
            assert robots.can_fetch(bot, 'https://example.test' + path)
        assert not robots.can_fetch(bot, 'https://example.test/preview/private/')


def test_recent_company_limit_and_finance_tool_selection():
    stories = [article(slug=f'story-{i:02}', url=f'/wealth/story-{i:02}/', tags=['stocks']) for i in range(35)]
    tools = [dict(slug='mortgage', url='/mortgage/', title='Mortgage', category='Mortgages & Home Buying', updated='2026-10-01'),
             dict(slug='bmi', url='/bmi/', title='BMI', category='Health')]
    data = catalogue('https://example.test', stories, tools, [], True)
    assert len(data['entries']) == 32
    assert sum(e['kind'] == 'Company analysis' for e in data['entries']) == 30
    assert not any(e['url'].endswith('/bmi/') for e in data['entries'])
    assert next(e for e in data['entries'] if e['title'] == 'Mortgage')['modified'] == '2026-10-01'


def test_populated_render_matches_schema_and_escapes_text(tmp_path):
    from compound.config import load_settings
    from compound.site.build import _env
    from compound.site.finance_discovery import write_discovery
    data = catalogue('https://example.test', [article(title='Safe </script> & title')], [], [], False)
    target = tmp_path / 'wealth/before-you-invest-ireland/index.html'
    target.parent.mkdir(parents=True)
    target.write_text(f'<link rel="canonical" href="{data["entries"][0]["url"]}">')
    write_discovery('https://example.test', tmp_path, _env(load_settings()), data, [data['entries'][0]['url']])
    page = (tmp_path / 'finance/index.html').read_text()
    import re
    schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]
    collection = next(s for s in schemas if s.get('@type') == 'CollectionPage')
    assert collection['mainEntity']['numberOfItems'] == 1
    assert collection['mainEntity']['itemListElement'][0]['url'] == data['entries'][0]['url']
    assert 'Safe </script>' not in page
    assert 'https://www.revenue.ie/' in page
