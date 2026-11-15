"""Guard the dated, primary-source-backed legislative label on the existing PIA guide.

These checks assert source editorial constraints only. They do not verify whether
Finance (No. 2) Bill 2026 has completed its parliamentary stages.
Primary records checked on 15 November 2026:
- https://www.oireachtas.ie/en/bills/bill/2026/98/
- https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf
- https://data.oireachtas.ie/ie/oireachtas/bill/2026/98/dail/3/amendment/numberedList/eng/b9826d-dcnl.pdf
- https://www.revenue.ie/ga/corporate/press-office/press-releases/2026/pr-100726-irish-investment-account.aspx
"""

from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "content/wealth/personal-investment-account-ireland.md"


def test_pia_guide_retains_original_canonical_and_attribution():
    text = GUIDE.read_text(encoding="utf-8")
    assert "slug: personal-investment-account-ireland" in text
    assert "publication_status: published" in text
    assert "date: 2026-09-25" in text
    assert "reviewed: 2026-11-07" in text  # Do not imply new human review.
    assert "pexels_photo_id: 34016390" in text
    assert "/pia-calculator/" in text
    assert "/pia/vs-pension/" in text


def test_pia_guide_distinguishes_statutory_iia_and_common_pia():
    text = GUIDE.read_text(encoding="utf-8")
    assert "Individual Investment Account (IIA)" in text
    assert "**Personal Investment Account (PIA)**" in text
    assert "official draft name **Individual Investment Account**" in text
    assert "introduced on 19 October" in text
    assert "3 November committee amendments" in text
    assert "final law and commencement not confirmed" in text
    assert "1 July 2027" in text
    assert "subject to enactment and provider readiness" in text
    assert "Last checked: 6 October 2026." not in text


def test_pia_legislative_sources_are_explicit_and_no_approval_is_fabricated():
    text = GUIDE.read_text(encoding="utf-8")
    assert "https://www.oireachtas.ie/en/bills/bill/2026/98/" in text
    assert "https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf" in text
    assert "https://data.oireachtas.ie/ie/oireachtas/bill/2026/98/dail/3/amendment/numberedList/eng/b9826d-dcnl.pdf" in text
    assert "https://www.revenue.ie/ga/corporate/press-office/press-releases/2026/pr-100726-irish-investment-account.aspx" in text
    assert "this is not a whole-article editorial re-review" in text
