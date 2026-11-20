"""Regression checks for date-qualified probate funeral-funds explanation.

The 7 October 2011 Law Society practice note describes a common bank process,
not a guaranteed right to early release of funds. This source-level test does
not replace independent editorial review or rendered-site checks.
"""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "content" / "wealth" / "probate-ireland.md"
PRIMARY = "https://www.lawsociety.ie/Solicitors/knowledge-base/Practice-Notes/Payment-of-funeral-expenses"


def _source():
    content = PATH.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    return frontmatter, content


def test_bank_funeral_payment_context_is_qualified_and_primary_sourced():
    meta, content = _source()
    assert "If funeral costs are due before probate" in content
    assert "before a Grant of Representation is issued" in content
    assert "many banks will consider paying" in content
    assert "This is not guaranteed" in content
    assert "available account funds" in content
    assert PRIMARY in content
    assert any(source["url"] == PRIMARY for source in meta["sources"])
    assert "[Probate Costs & Fees in Ireland](/wealth/probate-costs-fees-ireland/)" in content


def test_probate_original_metadata_and_existing_routes_preserved():
    meta, content = _source()
    assert meta["slug"] == "probate-ireland"
    assert str(meta["date"]) == "2026-10-05"
    assert str(meta["reviewed"]) == "2026-10-05"
    assert meta["draft"] is False
    assert "/wealth/how-to-make-a-will-ireland/" in content
    assert "/wealth/what-happens-if-you-die-without-a-will-ireland/" in content
    assert "/wealth/inheritance-tax-ireland/" in content
