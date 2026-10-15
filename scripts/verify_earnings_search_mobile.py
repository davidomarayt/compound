"""Browser smoke-test: ten latest SEC filings and a functional full-archive search."""
from __future__ import annotations

import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

PUBLIC = Path(__file__).resolve().parents[1] / "public"


def main() -> None:
    if not (PUBLIC / "wealth/earnings/index.html").is_file():
        raise SystemExit("Build the site before running the earnings browser audit")
    handler = partial(SimpleHTTPRequestHandler, directory=str(PUBLIC))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for width in (390, 1024):
                    context = browser.new_context(viewport={"width": width, "height": 850})
                    page = context.new_page()
                    page.route("**/*", lambda route: route.continue_()
                               if route.request.url.startswith(origin) else route.abort())
                    response = page.goto(origin + "/wealth/earnings/", wait_until="domcontentloaded")
                    assert response and response.status == 200
                    recent = page.locator("[data-earnings-recent]")
                    results = page.locator("[data-earnings-report-results]")
                    search = page.locator("[data-earnings-report-search]")
                    assert recent.locator("[data-earnings-recent-card]").count() == 10
                    assert recent.is_visible()
                    assert not results.is_visible()
                    search.fill("nvda")
                    assert results.is_visible() and not recent.is_visible()
                    assert results.locator('a[href="/stocks/nvda/"]').count() >= 1
                    assert results.locator("article").count() == 1
                    search.fill("this-company-does-not-exist")
                    assert results.locator("article").count() == 0
                    assert "No verified earnings reports found" in page.locator(
                        "[data-earnings-report-status]").inner_text()
                    search.fill("")
                    assert recent.is_visible() and not results.is_visible()
                    assert recent.locator("[data-earnings-recent-card]").count() == 10
                    print(f"PASS: {width}px earnings digest and complete archive search", flush=True)
                    context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
