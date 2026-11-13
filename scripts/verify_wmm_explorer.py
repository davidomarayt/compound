"""Desktop/mobile functional checks. Third-party requests are blocked during QA."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wmm-qa'
PATHS=['/wheres-my-money/', '/wheres-my-money/spending/', '/wheres-my-money/spending/health/', '/wheres-my-money/spending/social-protection/illness-disability-and-carers/', '/wheres-my-money/spending/education/', '/wheres-my-money/spending/debt-and-eu/', '/wheres-my-money/methodology/']

def main():
    OUT.mkdir(exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'review-wmm')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    checks=[]
    try:
        with sync_playwright() as engine:
            browser=engine.chromium.launch()
            for width in [390,1440]:
                page=browser.new_page(viewport={'width':width,'height':950})
                page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort())
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                for path in PATHS:
                    response=page.goto(base+path,wait_until='networkidle')
                    assert response.status==200,(path,response.status)
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),(path,width,'horizontal overflow')
                    assert page.locator('h1').count()==1
                    page.screenshot(path=str(OUT/(path.strip('/').replace('/','-')+f'-{width}.png')))
                    if page.locator('#wx-mode').count():
                        page.select_option('#wx-mode','share')
                        assert '%' in page.locator('[data-wx-value]').first.inner_text()
                        page.select_option('#wx-mode','personal');page.fill('#wx-contribution','37035.245')
                        assert '€' in page.locator('[data-wx-value]').first.inner_text()
                        page.fill('#wx-contribution','-1')
                        assert page.locator('[data-wx-value]').first.inner_text()=='—'
                        page.select_option('#wx-mode','national')
                    if page.locator('#wx-search').count():
                        page.fill('#wx-search','pension')
                        assert page.locator('[data-wx-search-item]:visible').count()>0
                        page.fill('#wx-search','not-a-real-programme')
                        assert page.locator('[data-wx-search-item]:visible').count()==0
                    if path=='/wheres-my-money/':
                        page.fill('#wmm-salary','103000')
                        assert '37,035' in page.locator('#wmm-total').inner_text()
                        assert page.locator('#wmm-sector-source').get_attribute('href')=='/wheres-my-money/spending/health/'
                    assert not errors,(path,errors)
                    checks.append({'path':path,'width':width,'status':'pass'})
                page.close()
            context=browser.new_context(java_script_enabled=False)
            page=context.new_page()
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort())
            page.goto(base+'/wheres-my-money/spending/education/')
            assert page.locator('.wx-bar-row').count()==16
            assert page.locator('.wx-history svg').count()==1
            assert page.locator('a[href="/wheres-my-money/spending/"]').count()>0
            browser.close()
    finally: server.shutdown()
    (OUT/'results.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print('PASS: native graphs, receipt regression, mobile, desktop, no-JS and personal input validation.')

if __name__=='__main__':main()
