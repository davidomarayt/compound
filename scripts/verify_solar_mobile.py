"""Check every public Solar Hub route in a real Chromium mobile viewport.

Requires: python -m pip install playwright && python -m playwright install chromium
Run after `compound build`: python scripts/verify_solar_mobile.py
"""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ROUTES = [
    "/solar/",
    "/solar/compare-quotes/",
    "/solar/roof-direction/",
    "/solar/grants/",
    "/solar/costs/",
    "/solar/installers/",
    "/solar/get-quotes/",
    "/solar/for-installers/",
    "/solar/batteries/",
    "/solar/export-rates/",
    "/solar/equipment/",
    "/solar-payback-calculator/",
    "/solar-ev-battery-optimiser/",
    "/wealth/solar-panels-ireland/",
    "/wealth/solar-panels-vs-battery-ireland/",
]
WIDTHS = (320, 360, 390, 430, 768, 1024)
SCAN = r"""() => {
  const shell = document.querySelector('.sol-shell') || document.querySelector('main');
  if (!shell) return {error: 'No main page content'};
  const width = document.documentElement.clientWidth;
  const failures = [];
  const margin = 2;
  const pageWidth = document.documentElement.scrollWidth;
  if (pageWidth > width + margin) {
    failures.push({kind: 'page-width', pageWidth, width});
  }
  // Text can be visibly cropped even when overflow:hidden hides the page scroll.
  // Inspect individual rendered text-line rectangles, ignoring intentional
  // horizontal scrolling inside responsive comparison tables.
  const walker = document.createTreeWalker(shell, NodeFilter.SHOW_TEXT);
  let text;
  while ((text = walker.nextNode())) {
    if (!text.textContent.trim()) continue;
    const parent = text.parentElement;
    if (!parent || parent.closest('.sol-table-scroll, .tool-chart-scroll, .table-scroll, .table-responsive, .scroll-table, .responsive-table, script, style')) continue;
    const style = getComputedStyle(parent);
    if (style.display === 'none' || style.visibility === 'hidden') continue;
    const range = document.createRange();
    range.selectNodeContents(text);
    for (const rect of range.getClientRects()) {
      if (!rect.width || !rect.height) continue;
      if (rect.right > width + margin || rect.left < -margin) {
        failures.push({
          kind: 'clipped-text',
          element: parent.tagName.toLowerCase(),
          selector: parent.className && typeof parent.className === 'string' ? parent.className.slice(0,65) : '',
          snippet: text.textContent.trim().slice(0,80),
          left: Math.round(rect.left), right: Math.round(rect.right), width
        });
        break;
      }
    }
    if (failures.length >= 15) break;
  }
  const scrollBoxes = [...shell.querySelectorAll('.sol-table-scroll, .tool-chart-scroll')];
  for (const item of scrollBoxes) {
    const rect = item.getBoundingClientRect();
    if (rect.right > width + margin || rect.left < -margin) {
      failures.push({kind:'table-container-outside-viewport',left:rect.left,right:rect.right,width});
    }
    if (item.scrollWidth > item.clientWidth + margin &&
        !['auto','scroll'].includes(getComputedStyle(item).overflowX)) {
      failures.push({kind:'table-not-scrollable'});
    }
  }
  return {
    failures,
    width,
    pageWidth,
    tables: scrollBoxes.length,
    title: shell.querySelector('h1')?.innerText || ''
  };
}"""


def main() -> None:
    if not (PUBLIC / "solar" / "index.html").exists():
        raise SystemExit("Build the site before running this browser audit.")

    handler = partial(SimpleHTTPRequestHandler, directory=str(PUBLIC))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    failures: list[str] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for width in WIDTHS:
                    context = browser.new_context(
                        viewport={"width": width, "height": 860},
                        device_scale_factor=1,
                        is_mobile=width <= 430,
                        has_touch=width <= 430,
                    )
                    page = context.new_page()
                    errors: list[str] = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                    try:
                        for path in ROUTES:
                            response = page.goto(origin + path, wait_until="domcontentloaded", timeout=35000)
                            if response is None or response.status != 200:
                                failures.append(f"{width}px {path}: HTTP error")
                                continue
                            page.wait_for_selector("main", timeout=5000)
                            page.wait_for_timeout(70)
                            result = page.evaluate(SCAN)
                            if result.get("error") or result.get("failures"):
                                failures.append(f"{width}px {path}: {json.dumps(result, ensure_ascii=False)}")
                            print(f"{width:4d}px {path:<29} page={result.get('pageWidth')} "
                                  f"tables={result.get('tables')} errors={len(result.get('failures',[]))}", flush=True)
                            if path == "/solar/export-rates/" and width <= 430:
                                cards = page.locator("[data-ex-card]")
                                if cards.count() != 2:
                                    failures.append(f"{width}px {path}: expected two tariff result cards")
                                else:
                                    measurements = page.evaluate("""() => [...document.querySelectorAll('[data-ex-card]')].map(card => {
                                      const box = card.getBoundingClientRect();
                                      const amount = card.querySelector('.sol-export-amount');
                                      const credit = card.querySelector('.sol-export-credit strong');
                                      return {width: box.width, left: box.left, right: box.right,
                                        amountWhiteSpace: getComputedStyle(amount).whiteSpace,
                                        amountWidth: amount.getBoundingClientRect().width,
                                        creditWhiteSpace: getComputedStyle(credit).whiteSpace};
                                    })""")
                                    for item in measurements:
                                        if (item["width"] < 185 or item["left"] < -2 or
                                            item["right"] > width + 2 or
                                            item["amountWhiteSpace"] != "nowrap" or
                                            item["creditWhiteSpace"] != "nowrap"):
                                            failures.append(f"{width}px {path}: unreadable result card {item}")
                            if path == "/solar/roof-direction/" and width == 390:
                                before = page.locator('[data-or="percent"]').inner_text()
                                south_yield = page.locator('[data-or="total"]').inner_text()
                                page.locator('[data-or-preset="90"]').click()
                                east_percent = page.locator('[data-or="percent"]').inner_text()
                                east_yield = page.locator('[data-or="total"]').inner_text()
                                if before != "100%" or not south_yield.strip() or east_percent == "100%" or east_yield == south_yield:
                                    failures.append(f"{width}px {path}: direction change did not update estimated output")
                                page.locator('[data-or-preset="180"]').click()
                                # Native HTML bars must be painted and interactive on mobile;
                                # no reliance on a browser's Canvas 2D context.
                                chart = page.locator('[data-or="chart"]')
                                month = page.locator('[data-or="chart-amount"]')
                                if not chart.is_visible() or "kWh" not in month.inner_text():
                                    failures.append(f"{width}px {path}: chart or kWh reading missing")
                                else:
                                    checks = chart.evaluate("""el => {
                                        const bars=[...el.querySelectorAll('[data-sor-month]')];
                                        const drawn=bars.filter(b => {
                                          const fill=b.querySelector('.sor-canvas-fill');
                                          if(!fill)return false;
                                          const r=fill.getBoundingClientRect();
                                          return r.width>=3 && r.height>=3 && getComputedStyle(fill).visibility!=='hidden';
                                        });
                                        return {bars:bars.length,drawn:drawn.length,
                                          selected:bars.filter(b=>b.getAttribute('aria-pressed')==='true').length};
                                    }""")
                                    if checks["bars"] != 12 or checks["drawn"] != 12 or checks["selected"] != 1:
                                        failures.append(f"{width}px {path}: monthly HTML bars missing {checks}")
                            if errors:
                                failures.append(f"{width}px {path}: JS exception: {errors[-1][:180]}")
                                errors.clear()
                            # Smoke-test the feature JS after layout is stable.
                            if width == 390:
                                selector = {
                                    "/solar/compare-quotes/": "[data-sq-rows] tr",
                                    "/solar/grants/": "[data-sg-total]",
                                    "/solar/costs/": "[data-ss-size]",
                                    "/solar/installers/": "[data-sol-check-count]",
                                    "/solar/get-quotes/": "[data-sb-output]",
                                    "/solar/batteries/": "[data-bat-out=annual]",
                                    "/solar/export-rates/": "[data-ex-out=difference]",
                                    "/solar/equipment/": "[data-eq-out=kwp]",
                                }.get(path)
                                if selector:
                                    page.wait_for_selector(selector, timeout=5000)
                                    if path in ("/solar/batteries/", "/solar/export-rates/", "/solar/equipment/"):
                                        tool_result = page.locator(selector).inner_text()
                                        if not tool_result or tool_result.strip() == "—":
                                            failures.append(f"{width}px {path}: calculator did not populate")
                                    if path == "/solar/get-quotes/":
                                        profile = page.locator("[data-solar-project]")
                                        if profile.count() != 1:
                                            failures.append(f"{width}px {path}: homeowner project form missing")
                                        if page.locator('[data-sp="county"]').count() != 1 or page.locator('[data-sp="email"]').count() != 1:
                                            failures.append(f"{width}px {path}: required homeowner location or contact fields missing")
                                        if page.locator("[data-orientation-embedded]").count()!=1:
                                            failures.append(f"{width}px {path}: inline 360 compass missing")
                                        if page.locator(".sol-project-photo-guide").count()!=0 or page.locator('[data-sp="photoRoof"]').count()!=0:
                                            failures.append(f"{width}px {path}: removed photo section still present")
                                        page.locator('[data-sp="area"]').fill("Kells")
                                        compass = page.locator('[data-orientation-embedded]')
                                        compass.locator('[data-or-preset="225"]').click()
                                        if "225°" not in page.locator("[data-sb-output]").input_value():
                                            failures.append(f"{width}px {path}: primary compass direction not copied into project brief")
                                        page.locator('[data-sp="faces"]').select_option("2")
                                        face_buttons = page.locator('[data-sp-face-switch]')
                                        if not face_buttons.is_visible():
                                            failures.append(f"{width}px {path}: dual roof selector hidden")
                                        page.locator('[data-sp-face-button="2"]').click()
                                        compass.locator('[data-or-preset="90"]').click()
                                        combined = page.locator("[data-sb-output]").input_value()
                                        if "Primary direction (clockwise from north): 225°" not in combined or "Second direction: 90°" not in combined:
                                            failures.append(f"{width}px {path}: two independent roof faces not captured")
                                        page.locator('[data-sp-face-button="1"]').click()
                                        if compass.locator('[data-or="angle"]').inner_text() != "225°":
                                            failures.append(f"{width}px {path}: first roof angle not restored")
                                        chart = compass.locator('[data-or="chart"]')
                                        if not chart.is_visible() or "kWh" not in compass.locator('[data-or="chart-amount"]').inner_text():
                                            failures.append(f"{width}px {path}: embedded monthly chart missing or not calculated")
                                        else:
                                            painted = chart.evaluate("""el => {
                                                const bars=[...el.querySelectorAll('[data-sor-month]')];
                                                return bars.length===12 && bars.every(b => {
                                                    const fill=b.querySelector('.sor-canvas-fill');
                                                    if(!fill)return false;
                                                    const rect=fill.getBoundingClientRect();
                                                    return rect.width>=3 && rect.height>=3;
                                                });
                                            }""")
                                            if not painted:
                                                failures.append(f"{width}px {path}: embedded monthly bars are blank")
                                        page.locator('[data-sp="faces"]').select_option("1")
                                        output = page.locator("[data-sb-output]").input_value()
                                        if "SOLAR INSTALLATION QUOTE REQUEST" not in output:
                                            failures.append(f"{width}px {path}: quote request generator did not populate output")
                    finally:
                        page.close()
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    if failures:
        print("\nFAILURES (" + str(len(failures)) + "):")
        for failure in failures:
            print(failure, flush=True)
        raise SystemExit(1)
    print(f"PASS: {len(ROUTES)} solar routes × {len(WIDTHS)} viewport sizes; no horizontal overflow or clipped text.")


if __name__ == "__main__":
    main()
