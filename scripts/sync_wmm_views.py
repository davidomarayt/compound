"""Render versioned public-spending data into static Jinja views, page routes and CSV.
The JSON snapshot is the source of truth. Use --check in CI. Source updates
require review of reporting basis and labels before regenerating the views.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

def outputs(root: Path) -> dict[Path, str]:
    data = json.loads((root / 'content/public-spending-detail-2026.json').read_text(encoding='utf-8'))
    assert data['year'] == 2026 and data['total'] > 0
    assert data['total'] == sum(s['total'] for s in data['sectors'])
    result = {}
    packed = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    result[Path('compound/site/templates/_wmm_spending_data.html')] = (
        '{# Generated from content/public-spending-detail-2026.json. Do not edit independently. #}\n'
        '{% set wmm_data = ' + packed + ' %}\n')
    def page(slug: str, title: str, url: str, description: str, body: str) -> None:
        if not re.fullmatch(r'wmm-[a-z0-9-]+', slug) or not re.fullmatch(r'/wheres-my-money/(?:[a-z0-9-]+/)+', url):
            raise ValueError('Unsafe or invalid public spending route')
        meta = {'title':title, 'canonical_path':url, 'meta_description':description}
        result[Path(f'content/pages/{slug}.md')] = '---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' + body + '\n'
    page('wmm-spending','Irish Government Spending Breakdown 2026','/wheres-my-money/spending/',
         'Explore Ireland’s 2026 public spending with native charts, sector and programme breakdowns, 2016–2026 trends and transparent source data. Where’s My Money by Compound.',
         'Explore the public spending behind your tax receipt. Start with a sector, open a programme, or compare the historical series — without leaving Compound.')
    page('wmm-methodology','How We Explain Irish Public Spending','/wheres-my-money/methodology/',
         'How Compound’s Where’s My Money spending charts work: sources, estimates versus actuals, gross expenditure, data gaps and personal tax allocation assumptions.',
         'A public spending chart is only useful when its boundaries are clear. This page explains what the figures include, which years are estimates, and how to read gaps and comparisons.')
    for s in data['sectors']:
        page('wmm-'+s['slug'],s['name']+' Spending in Ireland — 2026',s['url'],
             f"Explore Ireland’s {s['name'].lower()} spending: published 2026 programmes, detailed allocations and historical trends. Native charts and tables on Compound.",s['intro'])
        for p in s['programmes']:
            if p['detail']:
                page('wmm-'+s['slug']+'-'+p['slug'],p['name']+' Spending — Ireland 2026',p['url'],
                     f"Explore the 2026 {p['name'].lower()} allocation, its published component lines and 2024–2026 comparison. Part of Compound’s Irish public spending explorer.",
                     p['note'] or f"Explore the published {p['name'].lower()} allocation inside {s['name'].lower()}. Read its component lines alongside the historical comparison and reporting notes.")
    csvfile = io.StringIO()
    writer = csv.writer(csvfile)
    writer.writerow(['year','level','sector','programme','line','eur','status','source_url','note'])
    for s in data['sectors']:
        writer.writerow([2026,'sector',s['name'],'','',s['total'],'estimate',s['source'],'Do not add parent and child rows'])
        for p in s['programmes']:
            writer.writerow([2026,'programme',s['name'],p['original'],'',p['total'],'estimate',s['source'],'Do not add parent and child rows'])
            for label,value in p['lines']:
                if label.startswith(('=','+','-','@')): label = "'" + label
                writer.writerow([2026,'component',s['name'],p['original'],label,value,'estimate',s['source'],'Published component; coverage can be incomplete'])
    result[Path('compound/site/static/wmm/public-spending-2026.csv')] = csvfile.getvalue()
    overview = json.loads((root/'content/public-spending-2026.json').read_text(encoding='utf-8'))
    overview['exact_total_eur'] = data['total']
    mapping = {'social':'socialprotection','health':'health','education':'education','housing':'housing','justice':'justice','transport':'transport','debt':'debt','other':'other'}
    for category in overview['categories']:
        s = next(s for s in data['sectors'] if s['key']==mapping[category['id']])
        category.update(url=s['url'], exact_eur=s['total'], detail_links=[{'name':p['name'],'url':p['url']} for p in s['programmes']])
    result[Path('content/public-spending-2026.json')] = json.dumps(overview,ensure_ascii=False,indent=2)+'\n'
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale=[]
    for relative, expected in outputs(ROOT).items():
        path=ROOT/relative
        if args.check:
            actual=path.read_bytes().decode('utf-8') if path.is_file() else None
            if actual!=expected: stale.append(str(relative))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(expected.encode('utf-8'))
    if stale: raise SystemExit('Generated public spending views are stale: '+', '.join(stale))
    print('Public spending derived views are current.' if args.check else 'Public spending derived views generated.')
    return 0

if __name__=='__main__': raise SystemExit(main())
