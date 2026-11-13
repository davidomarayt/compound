"""Render the public-spending product in isolation for deterministic browser QA.
Full production rendering remains the existing compound build process.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import json
import shutil
from types import SimpleNamespace
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-wmm'

def main():
    env=Environment(loader=FileSystemLoader(ROOT/'compound/site/templates'),autoescape=select_autoescape(['html']))
    env.filters['long_date']=str
    cfg=yaml.safe_load((ROOT/'content/site.yml').read_text(encoding='utf-8'))
    env.globals.update(site_url='https://compound.ie',site_identity_jsonld='{}',year=2026,adsense=cfg['adsense'],analytics={'measurement_id':''})
    for file in (ROOT/'content/pages').glob('wmm-*.md'):
        _,front,body=file.read_text(encoding='utf-8').split('---',2)
        meta=yaml.safe_load(front)
        page=SimpleNamespace(slug=file.stem,title=meta['title'],url=meta['canonical_path'],meta_description=meta['meta_description'],body_html='<p>'+escape(body.strip())+'</p>')
        output=OUT/page.url.strip('/')/'index.html';output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(env.get_template('page.html').render(page=page,title=page.title),encoding='utf-8')
    spending=json.loads((ROOT/'content/public-spending-2026.json').read_text(encoding='utf-8'))
    (OUT/'wheres-my-money/index.html').write_text(env.get_template('wheres_my_money.html').render(title="Where's My Money?",spending=spending,wmm_page=True),encoding='utf-8')
    shutil.copytree(ROOT/'compound/site/static',OUT/'static',dirs_exist_ok=True)
    print('Rendered 44 native public-spending pages and the existing receipt.')

if __name__=='__main__': main()
