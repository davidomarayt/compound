"""Capture public, client-visible government chart data; never access private services.
Run explicitly during source verification. Output is an evidence artifact, not live content.
"""
from __future__ import annotations
import asyncio
import json
import re
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright

OUT = Path('wmm-source-evidence')
ROOT = 'https://www.whereyourmoneygoes.gov.ie'
START = ROOT + '/en/2026/'

CHARTS = r'''() => {
 if (!window.Highcharts) return [];
 return Highcharts.charts.filter(Boolean).map(c => ({
   title: c.title && c.title.textStr,
   subtitle: c.subtitle && c.subtitle.textStr,
   type: c.options.chart && c.options.chart.type,
   xAxes: c.xAxis.map(a => ({categories:a.categories,title:a.options.title})),
   yAxes: c.yAxis.map(a => ({title:a.options.title})),
   series: c.series.map(s => ({name:s.name,type:s.type,data:s.options.data})),
   drilldown: c.options.drilldown ? c.options.drilldown.series : [],
   credits:c.options.credits
 }));
}'''

async def main():
    OUT.mkdir(exist_ok=True)
    manifest = {'captured_at': datetime.now(timezone.utc).isoformat(), 'pages': []}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = await context.new_page()
        response = await page.goto(START, wait_until='networkidle', timeout=90000)
        if response is None or response.status >= 400:
            raise RuntimeError(f'Public source returned {response.status if response else "no response"}')
        links = await page.locator('a[href]').evaluate_all('(els) => els.map(e => ({href:e.href,text:e.textContent.trim()}))')
        (OUT / 'navigation.json').write_text(json.dumps(links, indent=2), encoding='utf-8')
        urls = [START]
        for link in links:
            url = link['href']
            if urlparse(url).netloc == urlparse(ROOT).netloc and re.search(r'/en/[^/]+/2026/?$', url) and url not in urls:
                urls.append(url)
        for url in urls[:15]:
            try:
                if page.url.rstrip('/') != url.rstrip('/'):
                    response = await page.goto(url, wait_until='networkidle', timeout=90000)
                    if response is None or response.status >= 400:
                        raise RuntimeError(f'HTTP {response.status if response else "unknown"}')
                try:
                    await page.wait_for_function('window.Highcharts && Highcharts.charts.filter(Boolean).length > 0', timeout=12000)
                except Exception:
                    pass
                key = url.strip('/').split('/')[-2]
                if key == 'en': key = 'national'
                charts = await page.evaluate(CHARTS)
                document = {'url':url,'title':await page.title(),'charts':charts,
                            'headings':await page.locator('h1,h2,h3,h4,h5,h6').all_text_contents(),
                            'tables':await page.locator('table').all_text_contents()}
                (OUT / f'{key}.json').write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
                (OUT / f'{key}.html').write_text(await page.content(), encoding='utf-8')
                await page.screenshot(path=str(OUT / f'{key}.png'), full_page=True)
                manifest['pages'].append({'key':key,'url':url,'chart_count':len(charts),
                    'charts':[{'title':c['title'],'series':len(c['series']),'drilldown_series':len(c.get('drilldown') or [])} for c in charts]})
                # Preserve only first-party source scripts for audit of units and labels.
                scripts = await page.locator('script[src]').evaluate_all('(els) => els.map(e => e.src)')
                for script in scripts:
                    if urlparse(script).netloc != urlparse(ROOT).netloc: continue
                    target = OUT / ('asset-' + re.sub(r'[^a-zA-Z0-9_.-]', '_', urlparse(script).path))
                    if target.exists(): continue
                    fetched = await context.request.get(script, timeout=30000)
                    if fetched.ok:
                        body = await fetched.body()
                        if len(body) < 4000000: target.write_bytes(body)
            except Exception as exc:
                manifest['pages'].append({'url':url,'error':str(exc)})
        about = await context.request.get(ROOT + '/en/about/', timeout=30000)
        if about.ok: (OUT / 'source-methodology.html').write_text(await about.text(), encoding='utf-8')
        await browser.close()
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))
    # Public committed application files only. Never include .git, .env or runner credentials.
    tracked = subprocess.check_output(['git','ls-files','-z']).decode().split('\0')
    with tarfile.open(OUT / 'repository-context.tar.gz', 'w:gz') as archive:
        for name in tracked:
            path = Path(name)
            if not name or not path.is_file() or path.is_symlink(): continue
            allowed = (name.startswith(('compound/','content/','tests/','scripts/','.github/workflows/'))
                       or name in ('AGENTS.md','EDITORIAL_TOPIC_INDEX.md','CONTENT_INVENTORY.md','pyproject.toml','README.md','data/content-inventory.json'))
            if allowed and path.suffix in ('.py','.js','.cjs','.html','.css','.yml','.yaml','.json','.md','.toml','.svg'):
                archive.add(path, arcname=name, recursive=False)

if __name__ == '__main__':
    asyncio.run(main())
