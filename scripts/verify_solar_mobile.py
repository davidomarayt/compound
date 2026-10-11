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
    "/solar/grants/",
    "/solar/costs/",
    "/solar/installers/",
    "/solar/get-quotes/",
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
                                }.get(path)
                                if selector:
                                    page.wait_for_selector(selector, timeout=5000)
                                    if path == "/solar/get-quotes/":
                                        output = page.locator("[data-sb-output]").input_value()
                                        if "itemised domestic solar PV quotation" not in output:
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
