"""Premium earnings data charts: finance accuracy, accessibility and presentation."""
from datetime import date
from pathlib import Path
import importlib.util

import pytest
import yaml

from compound.site.earnings_visuals import (
    render_earnings_dashboard, from_existing_markdown,
)
from compound.site.build import build_site


MOD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "earnings.py"
spec = importlib.util.spec_from_file_location("earnings_visual_test", MOD_PATH)
earnings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(earnings)


def snapshot(history=None):
    return {
        "form": "10-Q", "period_label": "FY 2026 Q3",
        "metrics": {
            "revenue": {
                "current": 8050000000, "prior": 8810000000, "reported_change": "-8.7%",
                "history": history or [],
            },
            "net_income": {"current": 283880000, "prior": 590970000,
                           "reported_change": "-52.0%"},
            "diluted_eps": {"current": 1.19, "prior": 2.29,
                            "reported_change": "-48.0%"},
        },
    }


def test_financial_dashboard_is_compact_accessible_and_trustworthy():
    html = render_earnings_dashboard(snapshot())
    assert "The headline:" in html
    assert "−8.7%" in html
    assert "$8.05bn" in html and "$283.88m" in html and "$1.19" in html
    assert html.count('class="earnings-kpi ') == 3
    assert html.count("<svg ") == 3
    assert html.count('role="img"') == 3
    assert 'scope="col"' in html and 'scope="row"' in html
    assert "Only periods confirmed in SEC data" in html
    assert "Older reports may show only two" in html
    assert "<img " not in html and "Unsplash" not in html
    assert "<script" not in html


def test_no_8_quarter_claim_from_two_comparable_periods():
    html = render_earnings_dashboard(snapshot())
    assert "2 reported periods" in html
    assert "8 reported periods" not in html
    assert "Not comparable" not in html


def test_eight_sourced_quarters_render_in_order_without_js():
    points = [
        {"end": f"202{year}-{month:02d}-30", "value": 1000000000 + i * 1e8}
        for i, (year, month) in enumerate(
            [(4, 3), (4, 6), (4, 9), (4, 12),
             (5, 3), (5, 6), (5, 9), (5, 12)]
        )
    ]
    # Real SEC quarter endings can vary: source periods, not inferred spacing.
    html = render_earnings_dashboard(snapshot(points))
    assert "8 reported periods" in html
    assert "Mar &#x27;24" in html
    assert "Dec &#x27;25" in html
    assert 'viewBox="0 0 720 238"' in html


def test_invalid_or_unverified_financial_data_fails_closed():
    data = snapshot()
    data["metrics"]["revenue"]["current"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        render_earnings_dashboard(data)
    data = snapshot()
    data["metrics"]["revenue"]["prior"] = 0
    with pytest.raises(ValueError, match="Revenue"):
        render_earnings_dashboard(data)


def test_legacy_yoy_is_preserved_without_recomputing_rounded_values():
    markdown = """## Earnings at a glance
| Reported metric | Current period | Corresponding prior-year period | Change |
|:---|---:|---:|---:|
| Revenue (US GAAP) | $8.05bn | $8.81bn | -8.7% |
| Net income (US GAAP) | $283.88m | $590.97m | -52.0% |
| Diluted earnings per share (GAAP) | $1.19 | $2.29 | -48.0% |
"""
    data = from_existing_markdown(markdown, {
        "tags": ["automated-earnings"], "title": "Lennar FY 2026 Q3 earnings",
    })
    html = render_earnings_dashboard(data)
    assert "−8.7%" in html
    assert "−8.6%" not in html


def test_generator_embeds_validated_snapshot_and_does_not_repeat_dashboard():
    filing = {"form": "10-Q", "filingDate": "2026-10-09", "reportDate": "2026-09-30",
              "accessionNumber": "0000000001-26-000123", "primaryDocument": "q3.htm"}
    tags = {
        "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "USD", 120e9, 100e9),
        "net_income": ("NetIncomeLoss", "USD", 20e9, 10e9),
        "diluted_eps": ("EarningsPerShareDiluted", "USD/shares", 2.0, 1.5),
    }
    facts = {"facts": {"us-gaap": {}}}
    for name,(tag,unit,now,old) in tags.items():
        facts["facts"]["us-gaap"][tag] = {"units": {unit: [
            {"start": "2026-07-01", "end": "2026-09-30", "filed": "2026-10-09",
             "accn": filing["accessionNumber"], "form": "10-Q", "val": now, "fy": 2026,
             "fp": "Q3", "frame": "CY2026Q3"},
            {"start": "2025-07-01", "end": "2025-09-30", "filed": "2026-10-09",
             "accn": filing["accessionNumber"], "form": "10-Q", "val": old, "fy": 2026,
             "fp": "Q3", "frame": "CY2025Q3"},
            {"start": "2026-01-01", "end": "2026-09-30", "filed": "2026-10-09",
             "accn": filing["accessionNumber"], "form": "10-Q", "val": now * 3,
             "fy": 2026, "fp": "Q3", "frame": "CY2026Q3YTD"},
        ]}}
    metrics = earnings.extract_metrics(facts, filing)
    slug, markdown = earnings.build_article("AAPL", "Apple Inc.", 320193,
                                             filing, metrics, date(2026, 10, 10), facts=facts)
    assert slug.endswith("fy2026-q3")
    meta = yaml.safe_load(markdown.split("---", 2)[1])
    snap = meta["earnings_snapshot"]
    assert snap["metrics"]["revenue"]["current"] == 120e9
    assert len(snap["metrics"]["revenue"]["history"]) == 2
    assert snap["metrics"]["revenue"]["history"][-1]["value"] == 120e9
    assert "## Earnings at a glance" not in markdown
    assert "## What stands out" in markdown
    assert "not an investment recommendation" in markdown
    assert render_earnings_dashboard(snap).count("<svg ") == 3


def test_earnings_template_has_cards_trends_and_optional_ads(settings):
    folder = settings.content_dir / "wealth"
    folder.mkdir(parents=True, exist_ok=True)
    (settings.content_dir / "site.yml").write_text(
        """adsense:
  client: "ca-pub-6115783809711785"
  slots:
    article_top: "1111111111"
    article_bottom: "2222222222"
    earnings_mid: "3333333333"
""", encoding="utf-8")
    metadata = {
        "title": "TestCo earnings", "slug": "testco-earnings",
        "pillar": "wealth", "canonical_path": "/wealth/earnings/testco-earnings/",
        "date": "2026-10-10",
        "summary": "Official US GAAP data", "tags": ["automated-earnings", "earnings"],
        "earnings_snapshot": snapshot(),
    }
    file = folder / "testco-earnings.md"
    file.write_text("---\n" + yaml.safe_dump(metadata,sort_keys=False) +
                    "---\n\n## SEC filing and limitations\n\nVerified results.", encoding="utf-8")
    build_site(settings)
    html = (settings.public_dir / "wealth" / "earnings" / "testco-earnings" /
            "index.html").read_text(encoding="utf-8")
    assert html.count('class="earnings-kpi ') == 3
    assert html.count('class="earnings-trend"') == 3
    assert html.index('class="earnings-dashboard"') < html.index("Verified results.")
    assert 'data-ad-slot="3333333333"' in html
    assert 'data-ad-slot="2222222222"' in html
    assert 'data-ad-slot="1111111111"' not in html
    assert '<img ' not in html
    assert '<link rel="canonical" href="https://example.test/wealth/earnings/testco-earnings/">' in html
