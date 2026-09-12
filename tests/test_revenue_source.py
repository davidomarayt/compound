from compound.sources.base import html_to_text
from compound.sources.revenue import parse_index
from tests.conftest import FIXTURES


def test_parse_index_extracts_ebriefs_in_order_without_duplicates():
    html = (FIXTURES / "revenue_index.html").read_text()
    items = parse_index(html, base_url="https://www.revenue.ie/en/tax-professionals/ebrief/index.aspx")
    ids = [i.external_id for i in items]
    assert ids == ["2026/no-0472026", "2026/no-0462026", "2026/no-0452026", "2024/no-0012024"]
    assert items[0].url == "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-0472026.aspx"
    assert items[0].title.startswith("Revenue eBrief No. 047/26")
    assert items[2].published_at == "2026-09-09"
    assert items[1].published_at is None


def test_html_to_text_keeps_main_and_drops_chrome():
    text = html_to_text((FIXTURES / "revenue_ebrief.html").read_text())
    assert "Rent Tax Credit" in text
    assert "€1,000 for a single person" in text
    assert "var x" not in text
    assert "Home" not in text
    assert "© Revenue" not in text
