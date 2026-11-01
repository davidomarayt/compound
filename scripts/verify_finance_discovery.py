#!/usr/bin/env python3
"""Check deployed discovery delivery, not Google indexing. Standard library only."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
import re
import time
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

GROUPS = ('Investing guides', 'Stock profiles', 'Company analysis', 'Financial calculators')

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.canonicals, self.links, self.directives, self.schemas = [], [], [], []
        self.refresh = False
        self.script = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href'))
        if tag == 'a':
            self.links.append(a.get('href', ''))
        if tag == 'meta':
            if a.get('name', '').lower() in ('robots', 'googlebot'):
                self.directives.append(a.get('content', ''))
            self.refresh |= a.get('http-equiv', '').lower() == 'refresh'
        if tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self.script = ''

    def handle_data(self, data):
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.schemas.append(json.loads(self.script))
            self.script = None


def check_directives(values):
    for value in values:
        assert not re.search(r'\b(noindex|none|nofollow)\b', value, re.I), value


def schema_types(value):
    if isinstance(value, dict):
        t = value.get('@type', [])
        yield from ([t] if isinstance(t, str) else t)
        for child in value.values():
            yield from schema_types(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_types(child)


def fetch(url, mime, agent='Compound-Deployment-Check/1.0'):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': agent}), timeout=30) as r:
                assert r.status == 200, (url, r.status)
                assert r.url == url, (url, 'unexpected redirect', r.url)
                assert r.headers.get_content_type() == mime, (url, r.headers.get('Content-Type'))
                check_directives(r.headers.get_all('X-Robots-Tag', []))
                return r.read().decode('utf-8')
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def audit(base, all_targets=False):
    directory = base + '/finance/'
    paths = [('/finance/', 'text/html'), ('/finance/index.json', 'application/json'),
             ('/llms.txt', 'text/plain'), ('/robots.txt', 'text/plain'), ('/sitemap.xml', 'application/xml')]
    with ThreadPoolExecutor(max_workers=5) as pool:
        bodies = dict(zip((p for p, _ in paths), pool.map(lambda p: fetch(base+p[0], p[1]), paths)))
    robots = RobotFileParser()
    robots.parse(bodies['/robots.txt'].splitlines())
    sitemap = ET.fromstring(bodies['/sitemap.xml'])
    assert sitemap.tag.endswith('urlset'), 'Expected current flat URL sitemap'
    locations = {e.text for e in sitemap.iter() if e.tag.endswith('}loc')}
    assert base + '/sitemap.xml' in (robots.site_maps() or []), 'Sitemap not advertised in robots'
    catalogue = json.loads(bodies['/finance/index.json'])
    assert catalogue['version'] == 1 and catalogue['url'] == directory
    entries = catalogue['entries']
    counts = Counter(e['kind'] for e in entries)
    assert set(counts) == set(GROUPS), counts
    urls = [e['url'] for e in entries]
    assert len(set(urls)) == len(urls), 'Duplicate catalogue URLs'
    for e in entries:
        assert urlsplit(e['url']).netloc == urlsplit(base).netloc
        assert e['url'].startswith(base + '/') and e['url'].endswith('/')
        assert e['url'] in locations, ('Missing from sitemap', e['url'])
        assert isinstance(e['sources'], list)
        for source in e['sources']:
            assert urlsplit(source['url']).scheme in ('http', 'https')
    for url in [directory, base+'/finance/index.json', base+'/llms.txt', *urls]:
        assert robots.can_fetch('Googlebot', url), ('Blocked Googlebot', url)
    assert not robots.can_fetch('Googlebot', base+'/preview/test/'), 'Preview protection lost'

    def html_check(url, html):
        page = Page(html)
        assert page.canonicals == [url], (url, page.canonicals)
        check_directives(page.directives)
        assert not page.refresh, ('Meta redirect', url)
        assert url in locations, ('Sitemap missing', url)
        assert page.schemas, ('No JSON-LD', url)
        return page

    page = html_check(directory, bodies['/finance/'])
    links = {urljoin(directory, x) for x in page.links}
    assert set(urls) <= links, 'Directory missing visible catalogue links'
    assert base+'/finance/index.json' in links
    assert base+'/llms.txt' in bodies['/robots.txt']
    collection = next(s for s in page.schemas if s.get('@type') == 'CollectionPage')
    assert collection['url'] == directory
    items = collection['mainEntity']
    assert items['@type'] == 'ItemList' and items['numberOfItems'] == len(entries)
    assert [e['url'] for e in items['itemListElement']] == urls
    assert directory in bodies['/llms.txt'] and base+'/finance/index.json' in bodies['/llms.txt']
    home = Page(fetch(base+'/', 'text/html'))
    assert directory in {urljoin(base+'/', x) for x in home.links}, 'Home/footer link missing'
    # A user-agent probe is delivery evidence, not an actual Googlebot crawl.
    for path, mime in paths[:3]:
        fetch(base+path, mime, 'Googlebot')
    selected = entries if all_targets else [e for group in GROUPS for e in [x for x in entries if x['kind'] == group][:2]]
    def target(e):
        page = html_check(e['url'], fetch(e['url'], 'text/html'))
        types = set(schema_types(page.schemas))
        expected = {'Investing guides': {'Article', 'NewsArticle'}, 'Company analysis': {'Article', 'NewsArticle'},
                    'Stock profiles': {'WebPage'}, 'Financial calculators': {'WebApplication', 'SoftwareApplication'}}
        assert types & expected[e['kind']], (e['url'], types)
        return {'url': e['url'], 'kind': e['kind'], 'status': 200, 'canonical': page.canonicals[0],
                'schema_types': sorted(types), 'googlebot_allowed': True, 'in_sitemap': True}
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(target, selected))
    return {'catalogue_counts': dict(counts), 'targets_checked': len(results), 'results': results,
            'discovery_endpoints': 'PASS: 200, MIME, robots/header directives, links and catalogue consistency',
            'google_indexing': 'Not measured by this HTTP check'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='https://compound.ie')
    parser.add_argument('--all-targets', action='store_true')
    args = parser.parse_args()
    print(json.dumps(audit(args.base_url.rstrip('/'), args.all_targets), indent=2))
