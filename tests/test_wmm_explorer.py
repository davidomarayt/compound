"""Source-backed native public spending library: reconciliation, routes and rendering."""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from types import SimpleNamespace
from urllib.parse import urlsplit
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'content/public-spending-detail-2026.json').read_text(encoding='utf-8'))

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.links=[]; self.ids=set(); self.canonicals=[]; self.descriptions=[]; self.h1=0; self.ad_count=0; self.svg=0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate element ID '+a['id']
            self.ids.add(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag=='h1': self.h1+=1
        if tag=='svg': self.svg+=1
        if tag=='link' and a.get('rel')=='canonical': self.canonicals.append(a['href'])
        if tag=='meta' and a.get('name')=='description': self.descriptions.append(a['content'])
        if 'data-wmm-ad-position' in a: self.ad_count+=1

def pages():
    result=[]
    for file in sorted((ROOT/'content/pages').glob('wmm-*.md')):
        _,front,body=file.read_text(encoding='utf-8').split('---',2)
        meta=yaml.safe_load(front)
        result.append(SimpleNamespace(slug=file.stem,title=meta['title'],url=meta['canonical_path'],meta_description=meta['meta_description'],body_html='<p>'+escape(body.strip())+'</p>'))
    return result

def environment(ads=True):
    env=Environment(loader=FileSystemLoader(ROOT/'compound/site/templates'),autoescape=select_autoescape(['html']))
    env.filters['long_date']=str
    cfg=yaml.safe_load((ROOT/'content/site.yml').read_text(encoding='utf-8'))
    env.globals.update(site_url='https://compound.ie',year=2026,site_identity_jsonld='{}',adsense=cfg['adsense'] if ads else {'client':'','slots':{}},analytics={'measurement_id':''})
    return env

def test_exact_source_snapshot_and_reporting_scope():
    assert DATA['year']==2026 and DATA['total']==132996715000
    assert len(DATA['sectors'])==8
    assert sum(len(s['programmes']) for s in DATA['sectors'])==57
    assert sum(len(p['lines']) for s in DATA['sectors'] for p in s['programmes'])==228
    assert DATA['total']==sum(s['total'] for s in DATA['sectors'])
    debt=next(s for s in DATA['sectors'] if s['key']=='debt')
    assert DATA['current']+DATA['capital']+debt['total']==DATA['total']
    assert debt['gap']==-1000
    assert DATA['years']==list(range(2016,2027))
    for s in DATA['sectors']:
        assert len(s['history'])==len(s['years'])
        assert s['history'][-1]==s['total'] and s['years'][-1]==2026
        assert s['gap']==s['total']-sum(p['total'] for p in s['programmes'])
        if s['key']!='debt': assert s['current']+s['capital']==s['total']
        assert len({p['slug'] for p in s['programmes']})==len(s['programmes'])
        for p in s['programmes']:
            assert p['history'][-1]==p['total'] and len(p['history'])==3
            assert p['gap']==p['total']-sum(v for _,v in p['lines'])
            assert all(isinstance(v,int) and v>=0 for _,v in p['lines'])
    housing=next(s for s in DATA['sectors'] if s['key']=='housing')
    assert housing['years'][0]==2020
    social=next(s for s in DATA['sectors'] if s['key']=='socialprotection')
    gaps={p['slug']:p['gap'] for p in social['programmes'] if p['gap']}
    assert gaps['illness-disability-and-carers']==1747635000
    assert len(gaps)==4

def test_generated_templates_and_data_are_identical():
    from scripts.sync_wmm_views import outputs
    for relative,expected in outputs(ROOT).items():
        assert (ROOT/relative).read_bytes().decode('utf-8')==expected, relative
    module=environment(False).get_template('_wmm_spending_data.html').module
    assert module.wmm_data==DATA

def test_all_native_routes_have_unique_metadata_and_server_rendered_evidence():
    ps=pages();assert len(ps)==44
    assert len({p.url for p in ps})==44
    assert len({p.title for p in ps})==44
    assert len({p.meta_description for p in ps})==44
    env=environment(); rendered={}
    for p in ps:
        text=env.get_template('page.html').render(page=p,title=p.title)
        doc=Document(text); rendered[p.url]=(text,doc)
        assert doc.h1==1 and doc.canonicals==['https://compound.ie'+p.url]
        assert doc.descriptions==[p.meta_description]
        assert 'noindex' not in text
        assert '2026' in text and 'source' in text.lower()
        assert doc.ad_count==(0 if p.slug=='wmm-methodology' else 2)
        if p.slug!='wmm-methodology':
            assert doc.svg==1 and '<table>' in text and 'data-wx-value=' in text
            assert 'estimate' in text.lower() and 'nominal' in text.lower()
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S): json.loads(block)
    summary=json.loads((ROOT/'content/public-spending-2026.json').read_text(encoding='utf-8'))
    home=env.get_template('wheres_my_money.html').render(title="Where's My Money?",spending=summary,wmm_page=True)
    rendered['/wheres-my-money/']=(home,Document(home))
    for origin,(_,doc) in rendered.items():
        for href in doc.links:
            path=urlsplit(href).path or origin; fragment=urlsplit(href).fragment
            if path.startswith('/wheres-my-money/'):
                assert path in rendered,(origin,href)
                if fragment: assert fragment in rendered[path][1].ids,(origin,href)
    assert 'Explore this sector on Compound' in home
    assert 'Read official sector figures' not in home and 'View the source data' not in home

def test_related_guides_are_real_canonical_routes():
    inv=json.loads((ROOT/'data/content-inventory.json').read_text(encoding='utf-8'))
    known={'/tools/','/health/','/wealth/','/solar/','/wheres-my-money/','/wheres-my-money/methodology/'}
    for section in inv['sections'].values():
        if isinstance(section,list): known.update(x.get('url','') for x in section if isinstance(x,dict))
    for s in DATA['sectors']:
        for item in s['related']: assert urlsplit(item['url']).path in known,item

def test_ads_and_personal_input_privacy():
    env=environment(False);p=pages()[0]
    text=env.get_template('page.html').render(page=p,title=p.title)
    assert 'data-wmm-ad-position=' not in text
    js=(ROOT/'compound/site/static/wmm-explorer.js').read_text(encoding='utf-8')
    for token in ['fetch(', 'XMLHttpRequest', 'sendBeacon(', 'localStorage.', 'sessionStorage.', 'gtag(', 'location.search']: assert token not in js,token
    assert 'amount / national * contribution' in js
    assert 'Number.isFinite' in js and "el.textContent = invalid ? '—'" in js
    assert 'innerHTML' not in js

def test_receipt_preserves_legacy_api_and_uses_native_links():
    summary=json.loads((ROOT/'content/public-spending-2026.json').read_text(encoding='utf-8'))
    assert summary['total_billion']==133.0 and summary['exact_total_eur']==DATA['total']
    assert all(c['url'].startswith('/wheres-my-money/spending/') for c in summary['categories'])
    assert all(c['source'].startswith('https://www.whereyourmoneygoes.gov.ie/') for c in summary['categories'])
    assert sum(c['exact_eur'] for c in summary['categories'])==DATA['total']

def test_normalised_numbers_match_archived_primary_source():
    import hashlib
    base=ROOT/'content/public-spending-sources/2026'
    for key,digest in DATA['source_hashes'].items():
        assert hashlib.sha256((base/(key+'.json')).read_bytes()).hexdigest()==digest
    for sector in DATA['sectors']:
        source=json.loads((base/(sector['key']+'.json')).read_text(encoding='utf-8'))
        chart=source['charts'][1]
        parents={p['name']:p['y'] for p in chart['series'][0]['data']}
        detail={p['id']:p['data'] for p in chart['drilldown']}
        for programme in sector['programmes']:
            assert programme['total']==parents[programme['original']]
            assert [v for _,v in programme['lines']]==[v for _,v in detail[programme['original']]]
