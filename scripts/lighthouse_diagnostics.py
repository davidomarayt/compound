"""Print actionable Lighthouse audit failures from LHCI JSON reports."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".lighthouseci")
    reports = sorted(root.glob("*.json"))
    if not reports:
        print("No Lighthouse JSON reports found.")
        return 0

    seen = set()
    for path in reports:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or "audits" not in data or "categories" not in data:
            continue
        url = data.get("finalDisplayedUrl") or data.get("finalUrl") or path.name
        key = (url, data.get("fetchTime"))
        if key in seen:
            continue
        seen.add(key)
        print(f"\n=== {url} ===")
        categories = data.get("categories", {})
        for name in ("performance", "accessibility", "best-practices", "seo"):
            cat = categories.get(name) or {}
            score = cat.get("score")
            if isinstance(score, (int, float)):
                print(f"{name}: {score:.2f}")

        audits = data.get("audits", {})
        for audit_id in (
            "largest-contentful-paint",
            "cumulative-layout-shift",
            "total-blocking-time",
            "speed-index",
            "first-contentful-paint",
        ):
            audit = audits.get(audit_id) or {}
            if audit.get("displayValue"):
                print(f"{audit.get('title', audit_id)}: {audit['displayValue']}")

        refs = {}
        for category_name in ("accessibility", "best-practices", "seo"):
            cat = categories.get(category_name) or {}
            for ref in cat.get("auditRefs", []):
                if ref.get("weight", 0) > 0:
                    refs.setdefault(ref["id"], set()).add(category_name)

        failures = []
        for audit_id, cats in refs.items():
            audit = audits.get(audit_id) or {}
            score = audit.get("score")
            mode = audit.get("scoreDisplayMode")
            if mode in {"notApplicable", "manual", "informative"}:
                continue
            if isinstance(score, (int, float)) and score < 1:
                failures.append((audit_id, ",".join(sorted(cats)), audit.get("title", audit_id), audit.get("displayValue", "")))
        if failures:
            print("Actionable category deductions:")
            for audit_id, cats, title, value in failures:
                suffix = f" — {value}" if value else ""
                print(f"  [{cats}] {audit_id}: {title}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
