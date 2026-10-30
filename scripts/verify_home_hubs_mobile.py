"""Browser smoke test for the homepage specialist hub directory.
Run after `compound build` and installing Playwright Chromium.
"""
from __future__ import annotations

import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ROUTES = (
    "/solar/", "/solar/get-quotes/", "/insurance/",
    "/health-insurance-cost-comparison-calculator/", "/pia/",
    "/wealth/how-to-start-investing-in-ireland/", "/stocks/", "/wealth/earnings/",
)
WIDTHS = (320, 360, 390, 430, 768, 1024, 1440)


def main():
    for route in ROUTES:
        path = PUBLIC / route.lstrip("/") / "index.html"
        if not path.is_file() or not path.stat().st_size:
            raise SystemExit(f"Homepage hub destination missing: {route}")
    handler = partial(SimpleHTTPRequestHandler, directory=str(PUBLIC))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    failures = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for width in WIDTHS:
                    context = browser.new_context(
                        viewport={"width": width, "height": 850},
                        device_scale_factor=1,
                        is_mobile=width <= 430,
                        has_touch=width <= 430,
                    )
                    page = context.new_page()
                    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    try:
                        response = page.goto(origin + "/", wait_until="domcontentloaded", timeout=30000)
                        if not response or response.status != 200:
                            failures.append(f"{width}px: homepage HTTP error")
                            continue
                        hub = page.locator("#explore-compound")
                        hub.scroll_into_view_if_needed()
                        result = page.evaluate("""() => {
                            const root=document.getElementById('explore-compound');
                            if(!root)return {error:'missing specialist section'};
                            const cards=[...root.querySelectorAll('.home-hub-card')];
                            const width=document.documentElement.clientWidth;
                            const failures=[];
                            for(const card of cards){
                                const rect=card.getBoundingClientRect();
                                if(rect.width<180 || rect.left < -2 || rect.right>width+2)
                                    failures.push('card outside viewport');
                                for(const link of card.querySelectorAll('a')){
                                    const r=link.getBoundingClientRect();
                                    if(r.width<70 || r.height<32 || r.right>width+2 || r.left< -2)
                                        failures.push('link clipped or too small: '+link.textContent.trim());
                                }
                                const walker=document.createTreeWalker(card,NodeFilter.SHOW_TEXT);
                                let node;
                                while((node=walker.nextNode())){
                                    if(!node.textContent.trim())continue;
                                    const range=document.createRange();range.selectNodeContents(node);
                                    for(const r of range.getClientRects())
                                        if(r.width && (r.right>width+2 || r.left< -2))
                                            failures.push('text clipped: '+node.textContent.trim().slice(0,30));
                                }
                            }
                            return {count:cards.length,width,failures};
                        }""")
                        if result.get("error") or result.get("count") != 4 or result.get("failures"):
                            failures.append(f"{width}px: {result}")
                        if errors:
                            failures.append(f"{width}px JS error: {errors[-1][:140]}")
                        if width == 390:
                            tracked = page.evaluate("""() => {
                                const root=document.getElementById('explore-compound');
                                const anchor=root.querySelector('a[data-home-hub="stocks"][data-home-action="earnings"]');
                                if(!anchor)throw new Error('Missing company earnings hub link');
                                root.addEventListener('click',e=>e.preventDefault(),true);
                                const data=[];window.gtag=(...args)=>data.push(args);
                                localStorage.setItem('compound_analytics_consent','denied');
                                anchor.click();
                                const before=data.length;
                                localStorage.setItem('compound_analytics_consent','granted');
                                anchor.click();
                                return {before,after:data.length,params:data[0]||null};
                            }""")
                            # The earnings link emits one consented homepage_hub_click event.
                            # It is not part of the solar journey funnel.
                            if tracked["before"] != 0 or tracked["after"] != 1 or tracked["params"][1] != "homepage_hub_click":
                                failures.append(f"{width}px consent tracking failed: {tracked}")
                            elif tracked["params"][2].get("hub") != "stocks":
                                failures.append(f"{width}px wrong hub attribution: {tracked}")
                        print(f"{width}px homepage specialist cards: {result}", flush=True)
                    finally:
                        page.close()
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    if failures:
        raise SystemExit("\n".join(failures))
    print("Homepage specialist hub mobile layout, link targets and consent checks passed.")


if __name__ == "__main__":
    main()
