"""A deliberately bounded discovery catalogue, derived from published content.

This is navigation/provenance, not a new source of financial facts or an AI
ranking protocol. Dates describe content/filings, never the build clock.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from urllib.parse import urlsplit

GUIDES = (
    'how-to-start-investing-in-ireland', 'before-you-invest-ireland',
    'pension-vs-investing-ireland', 'shares-etfs-funds-ireland',
    'investment-tax-ireland', 'diversification-portfolio-ireland',
    'choose-investment-broker-ireland', 'investment-fees-ireland',
    'how-much-to-invest-per-month-ireland', 'maintain-investment-portfolio-ireland',
    'personal-investment-account-ireland', 'pensions-in-ireland',
    'saving-for-your-child-ireland',
)
FINANCE_CATEGORIES = {
    'Pensions & Investing', 'Mortgages & Home Buying', 'Loans & Debt',
    'Tax & Take-Home Pay',
}
GROUPS = ('Investing guides', 'Stock profiles', 'Company analysis', 'Financial calculators')
GUIDANCE = (
    'Read and cite the canonical page, then follow its original sources for financial claims. '
    'Publication dates, review dates, filing dates and fiscal period ends are distinct. '
    'Company analysis contains interpretation; reported results are not forecasts. '
    'Calculator outputs are scenarios based on user inputs and stated assumptions, not advice or quotes. '
    'Check current Irish tax rules and dated source coverage before relying on a result. '
    'This catalogue is selective; omission does not mean a page is unavailable.'
)


def source_links(sources):
    """Preserve declared provenance without asserting it was independently verified."""
    result = []
    for source in sources:
        url = str(source.get('url') or '')
        if urlsplit(url).scheme not in {'https', 'http'} or not urlsplit(url).netloc:
            continue
        if not any(s['url'] == url for s in result):
            result.append({'url': url, 'title': str(source.get('title') or source.get('name') or url)})
    return result


def catalogue(base, articles, tools, stocks, has_calculator):
    base = base.rstrip('/')
    entries = []
    published = [a for a in articles if a.publication_status == 'published'
                 and a.pillar == 'wealth' and 'automated-earnings' not in a.tags]
    by_slug = {a.slug: a for a in published}
    def add_article(a, group):
        entries.append({'kind': group, 'title': a.title, 'url': base + a.url,
                        'description': a.description, 'published': a.date.isoformat(),
                        'modified': (getattr(a, "research_checked", None) or a.reviewed or a.date).isoformat(),
                        'sources': source_links(a.sources)})
    for slug in GUIDES:
        if slug in by_slug:
            add_article(by_slug[slug], GROUPS[0])
    for stock in stocks:
        entries.append({'kind': GROUPS[1], **stock, 'url': base + stock['url']})
    stories = [a for a in published if a.slug not in GUIDES and
               {'stocks', 'company-research', 'stock-analysis', 'earnings'} & set(a.tags)]
    for a in sorted(stories, key=lambda a: (getattr(a, "research_checked", None) or a.reviewed or a.date, a.slug), reverse=True)[:30]:
        add_article(a, GROUPS[2])
    for tool in tools:
        if tool.get('category') not in FINANCE_CATEGORIES and tool['slug'] != 'car-finance-calculator':
            continue
        entries.append({'kind': GROUPS[3], 'title': tool['title'], 'url': base + tool['url'],
                        'description': tool.get('summary') or tool.get('meta_description') or '',
                        'modified': str(tool.get('updated') or '') or None,
                        'sources': source_links(tool.get('sources', [])),
                        'requires_javascript_for_calculation': True})
    if has_calculator:
        entries.append({'kind': GROUPS[3], 'title': 'Compound Interest Calculator Ireland',
                        'url': base + '/compound-interest-calculator/',
                        'description': 'Model compound growth using contributions, time and an assumed return.',
                        'sources': [], 'requires_javascript_for_calculation': True})
    urls = [entry['url'] for entry in entries]
    if len(urls) != len(set(urls)):
        raise ValueError('Duplicate finance discovery canonical URL')
    return {'version': 1, 'title': 'Compound finance directory',
            'url': base + '/finance/', 'language': 'en-IE',
            'guidance': GUIDANCE, 'entries': entries}


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False
        self.redirect = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta':
            if attrs.get('name', '').lower() in {'robots', 'googlebot'}:
                self.noindex |= 'noindex' in attrs.get('content', '').lower()
            self.redirect |= attrs.get('http-equiv', '').lower() == 'refresh'


def validate_targets(data, out, sitemap_urls):
    """Fail publication if navigation drifts to a missing, alias or private page."""
    base = data['url'].removesuffix('/finance/')
    for entry in data['entries']:
        url = entry['url']
        path = urlsplit(url).path
        if not url.startswith(base + '/') or not path.endswith('/') or path.startswith('/preview/'):
            raise ValueError(f'Invalid finance discovery URL: {url}')
        page = out / path.lstrip('/') / 'index.html'
        if not page.is_file() or url not in sitemap_urls:
            raise ValueError(f'Finance discovery target missing from build/sitemap: {url}')
        metadata = PageMetadata()
        metadata.feed(page.read_text(encoding='utf-8'))
        if metadata.canonicals != [url] or metadata.noindex or metadata.redirect:
            raise ValueError(f'Finance discovery target is not indexable/canonical: {url}')


def write_discovery(base, out, env, data, sitemap_urls):
    base = base.rstrip('/')
    validate_targets(data, out, sitemap_urls)
    schema = {'@context': 'https://schema.org', '@type': 'CollectionPage',
              '@id': data['url'], 'url': data['url'], 'name': data['title'],
              'inLanguage': 'en-IE', 'isPartOf': {'@id': base + '/#website'},
              'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(data['entries']),
                             'itemListElement': [
                                 {'@type': 'ListItem', 'position': i, 'name': e['title'], 'url': e['url']}
                                 for i, e in enumerate(data['entries'], 1)]}}
    (out / 'finance').mkdir(parents=True, exist_ok=True)
    (out / 'finance/index.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'finance/index.html').write_text(env.get_template('finance.html').render(
        title='Finance directory', catalogue=data, groups=GROUPS, schema=schema,
        pillar='wealth'), encoding='utf-8')
    lines = ['# Compound.ie', '', '> Independent investing guides, company earnings analysis and financial calculators for readers in Ireland.',
             '', GUIDANCE, '', '## Navigation',
             f'- [Finance directory]({base}/finance/): Curated resources with dates and source links.',
             f'- [Machine-readable finance index]({base}/finance/index.json): Versioned JSON catalogue; canonical URLs and provenance.',
             f'- [Stock directory]({base}/stocks/): All public company profiles; coverage varies.',
             f'- [Earnings]({base}/wealth/earnings/): Consolidated company results.',
             f'- [All tools]({base}/tools/): Calculator assumptions and methodology.',
             f'- [Editorial policy]({base}/editorial-policy/): Editorial standards and limitations.',
             f'- [Sitemap]({base}/sitemap.xml): Full public URL inventory.', '',
             '## Selected starting points']
    for group in GROUPS:
        lines += ['', '### ' + group]
        lines += [f"- [{e['title']}]({e['url']}): {e['description']}".replace('\n', ' ')
                  for e in [e for e in data['entries'] if e['kind'] == group][:5]]
    lines += ['', 'This optional navigation file does not guarantee crawling, indexing, citations or recommendations. robots.txt controls crawler access.', '']
    (out / 'llms.txt').write_text('\n'.join(lines), encoding='utf-8')
