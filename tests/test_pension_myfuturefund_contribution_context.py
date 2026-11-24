"""Guard the source-backed 2026 MyFutureFund context in the pension-contributions chapter.

Primary official material rechecked 2026-11-19:
https://myfuturefund.ie/participant/contributions
https://myfuturefund.ie/employer-faq
"""
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[1] / "content/wealth/how-much-pension-contribute-ireland.md"


def _text() -> str:
    return CHAPTER.read_text(encoding="utf-8")


def test_pension_contributions_distinguishes_workplace_match_from_myfuturefund():
    text = _text()
    assert "## If your employer offers no pension: check MyFutureFund" in text
    assert "**1 January 2026**" in text
    assert "**2026–2028**" in text
    assert "employer adds **1.5%**" in text
    assert "State adds **0.5%**" in text
    assert "€600 employee + €600 employer + €200 State = **€1,400**" in text
    assert "from **net pay**" in text
    assert "not** amounts to add together automatically for the same job" in text


def test_primary_sources_and_canonical_destinations_are_preserved():
    text = _text()
    assert "https://myfuturefund.ie/participant/contributions" in text
    assert "https://myfuturefund.ie/employer-faq" in text
    assert "[MyFutureFund Calculator](/myfuturefund-calculator/)" in text
    assert "[MyFutureFund vs private pension guide](/wealth/myfuturefund-vs-private-pension-ireland/)" in text
    assert "not every" in text.lower() or "Not every" in text
    assert "date: 2026-09-23" in text
    assert "reviewed: 2026-09-23" in text
    assert "slug: how-much-pension-contribute-ireland" in text
