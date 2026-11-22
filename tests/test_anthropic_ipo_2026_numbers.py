"""Regression checks for the 16 November 2026 Anthropic IPO prospectus analysis."""
from pathlib import Path
import re

ARTICLE = Path(__file__).resolve().parents[1] / "content/wealth/anthropic-ipo-2026-prospectus-numbers-valuation.md"


def test_prospectus_offering_arithmetic_and_source_provenance():
    text = ARTICLE.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "date: '2026-11-16'" in text
    assert "publication_status: published" in text
    assert "editorial_review_status: pending" in text
    assert "https://www.sec.gov/Archives/edgar/data/2130357/000162828026072484/anthropicpbc-sx1ax2.htm" in text
    assert "https://www.anthropic.com/news/roadshow-launch" in text
    assert "require_pinned_hero: true" in text
    assert "PD-textlogo" in text and "File:Claude_AI_logo.svg" in text

    primary = 801_351_354
    secondary = 23_648_646
    price = 74
    assert primary + secondary == 825_000_000
    assert round(primary * price / 1e9, 2) == 59.30
    assert round(secondary * price / 1e9, 2) == 1.75
    assert round(825_000_000 * price / 1e9, 2) == 61.05
    assert round((primary + secondary) * price / 1e9 + 26, 2) == 87.05


def test_company_numbers_have_the_right_periods_and_ipo_is_not_treated_as_trading():
    text = ARTICLE.read_text(encoding="utf-8")
    for value in ["$16.956bn", "$33.242bn", "$104.039bn", "$94.324bn",
                  "$900.9bn", "$131.845bn", "$84.6bn", "50.1%", "$8.21"]:
        assert value in text
    assert "not a final ipo or market price" in text.lower()
    assert "not a personalised recommendation" in text
    assert "/stocks/ant/" in text
    assert "/wealth/anthropic-loss-ipo-valuation/" in text
    assert "18 November" in text
    assert re.search(r"Run-Rate Revenue.*not.*GAAP", text, flags=re.IGNORECASE | re.DOTALL)
