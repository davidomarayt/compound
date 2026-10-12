"""Verify newly changed published articles after build and after deployment.

No individual article URLs need hardcoding in workflow YAML. The previous
publishing-branch commit determines the changed article set. Existing live
smoke tests remain in the independent nightly quality audit.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = os.getenv("SITE_BASE_URL", "https://compound.ie").rstrip("/")


def changed_articles() -> list[tuple[Path, str]]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD^", "HEAD", "--", "content/"],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Cannot compare publishing commits; avoid silently skipping new article verification.")
    items = []
    for line in result.stdout.splitlines():
        path = Path(line)
        if not (len(path.parts) == 3 and path.parts[0] == "content" and
                path.parts[1] in {"health", "wealth", "happiness", "life"} and path.suffix == ".md"):
            continue
        absolute = ROOT / path
        if not absolute.is_file():
            continue
        raw = absolute.read_text(encoding="utf-8")
        sections = raw.split("---", 2)
        if len(sections) < 3:
            raise RuntimeError(f"Missing front matter in {line}")
        meta = yaml.safe_load(sections[1]) or {}
        if not isinstance(meta, dict):
            raise RuntimeError(f"Invalid metadata in {line}")
        if meta.get("draft") or meta.get("publication_status") == "draft":
            continue
        # Automated earnings articles are deliberately consolidated under
        # /stocks/<ticker>/ and their legacy per-quarter URLs may be redirects.
        # Their SEC filing and canonical redirect checks run separately.
        if "automated-earnings" in (meta.get("tags") or []):
            continue
        slug = str(meta.get("slug") or path.stem)
        pillar = "life" if path.parts[1] == "happiness" else path.parts[1]
        url_path = str(meta.get("canonical_path") or f"/{pillar}/{slug}/")
        if not url_path.startswith("/") or not url_path.endswith("/") or ".." in url_path:
            raise RuntimeError(f"Unsafe article canonical path for {line}")
        items.append((path, url_path))
    return items


def fetch(url: str) -> str:
    error = None
    for attempt in range(5):
        try:
            with urlopen(Request(url, headers={"User-Agent": "CompoundReleaseCheck/1.0"}), timeout=20) as res:
                if res.status != 200:
                    raise RuntimeError(f"{url} returned HTTP {res.status}")
                return res.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            error = exc
            if attempt < 4:
                time.sleep(3)
    raise RuntimeError(f"Could not verify {url}: {error}")


def verify(path: Path, url_path: str, mode: str) -> None:
    canonical = SITE + url_path
    if mode == "built":
        html = (ROOT / "public" / url_path.strip("/") / "index.html").read_text(encoding="utf-8")
    else:
        html = fetch(canonical)
    # All generated article pages must expose their canonical on the live domain.
    if f'href="{canonical}"' not in html:
        raise RuntimeError(f"{path}: missing canonical {canonical}")
    if "<h1" not in html:
        raise RuntimeError(f"{path}: missing main headline")
    if "/news/" in url_path and 'property="og:image"' not in html:
        raise RuntimeError(f"{path}: missing article social image")
    print(f"PASS {mode}: {url_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("built", "live"))
    args = parser.parse_args()
    errors = []
    articles = changed_articles()
    for path, url_path in articles:
        try:
            verify(path, url_path, args.mode)
        except (RuntimeError, OSError) as exc:
            errors.append(str(exc))
    if args.mode == "live":
        try:
            html = fetch(SITE + "/")
            if "<html" not in html.lower():
                errors.append("Home page is not valid HTML")
        except RuntimeError as exc:
            errors.append(str(exc))
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    print(f"Release {args.mode} checks: {len(articles)} updated article(s); {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
