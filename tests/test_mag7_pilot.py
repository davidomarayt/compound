"""Mag 7 pilot safety: four weeks only, no publication without editorial approval."""
from datetime import date, timedelta
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mag7_pilot", ROOT / "scripts/mag7_pilot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_four_full_rotation_cycles_only():
    start = date(2026, 10, 16)
    assert module.DAYS == 28
    assert module.assignment(start) == ("TSLA", 1)
    assert module.assignment(start + timedelta(days=1)) == ("MSFT", 1)
    assert module.assignment(start + timedelta(days=6)) == ("META", 1)
    assert module.assignment(start + timedelta(days=7)) == ("TSLA", 2)
    assert module.assignment(start + timedelta(days=27)) == ("META", 4)
    assert module.assignment(start - timedelta(days=1)) is None
    assert module.assignment(start + timedelta(days=28)) is None
    all_slots = [module.assignment(start + timedelta(days=n)) for n in range(28)]
    assert all(sum(1 for ticker, _ in all_slots if ticker == t) == 4 for t in module.ROTATION)


def test_primary_filing_and_distinct_editorial_themes_for_every_company():
    for ticker in module.ROTATION:
        data = module.latest_sec(ticker)
        assert data["filing"].startswith("https://www.sec.gov/Archives/")
        assert data["period"].startswith("FY")
        assert len(data["metrics"]) == 3
        assert ticker in module.COMPANIES
        assert module.IR_PAGES[ticker].startswith("https://")


def test_packet_is_a_review_artefact_with_explicit_guardrails():
    date_key = date(2026, 10, 17)
    packet = module.brief(date_key, "MSFT", 1, module.latest_sec("MSFT"), [], [])
    assert "Review required, not published" in packet
    assert "No auto-publish" in packet
    assert "Revenue" in packet and "Diluted EPS" in packet
    assert "/stocks/msft/" in packet and "/wealth/earnings/" in packet
    assert "never reuse stock desks" in packet
    assert "If no distinct, well-supported angle exists" in packet


def test_tesla_first_article_is_original_source_backed_and_has_a_specific_hero():
    p = ROOT / "content/wealth/tesla-roadster-reveal-2026-investor-economics.md"
    body = p.read_text(encoding="utf-8")
    assert "date: 2026-10-16" in body
    assert "draft: false" in body and "publication_status: published" in body
    assert "/static/images/evergreen/tesla-roadster-reveal-2026-investor-economics.jpg" in body
    assert 'hero_image_url: "https://upload.wikimedia.org/' in body
    assert "Steve Jurvetson" in body and "CC BY 2.0" in body
    assert "April 2019" in body and "not a photograph from the 15 October 2026 event" in body
    assert "require_pinned_hero: true" in body
    assert "2028" in body and "not company guidance" in body.lower()
    assert "Reuters" in body and "www.sec.gov/Archives" in body
    assert "/stocks/tsla/" in body
    assert "0.21%" in body and "1.05%" in body and "2.11%" in body
    assert round(1000 * 200_000 / 94_827_000_000 * 100, 2) == 0.21
    assert round(5000 * 200_000 / 94_827_000_000 * 100, 2) == 1.05
    assert round(10000 * 200_000 / 94_827_000_000 * 100, 2) == 2.11
    image_renderer = (ROOT / "scripts/render_editorial_heroes.py").read_text()
    assert "make_roadster" not in image_renderer
    assert "tesla-roadster-reveal-investment-case-2026.jpg" not in image_renderer


def test_workflow_drafts_issues_not_live_site():
    wf = (ROOT / ".github/workflows/mag7-research.yml").read_text()
    assert "cron: '17 8 * * *'" in wf
    assert "gh issue create" in wf
    assert "--output mag7-review.md" in wf
    assert "permissions:" in wf and "issues: write" in wf
    assert "git push" not in wf
    assert "compound build" not in wf
