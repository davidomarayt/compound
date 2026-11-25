"""Protect comma-containing tax calculator labels from YAML flow-map truncation."""
from pathlib import Path

from compound.site.build import load_tools


def test_tax_calculators_preserve_complete_labels():
    tools = {t["slug"]: t for t in load_tools(Path(__file__).parents[1] / "content")}

    cgt = tools["capital-gains-tax-calculator"]
    fields = {f["id"]: f for f in cgt["fields"]}
    assert fields["costs"]["label"] == "Allowable acquisition, disposal and enhancement costs"
    assert fields["exemption_used"]["label"] == "Annual €1,270 exemption already used this tax year"
    assert fields["exemption_used"]["max"] == 1270
    assert fields["exemption_used"]["default"] == 0
    assert cgt["formula"] == "cgt"

    cat = tools["inheritance-tax-calculator"]
    gift = next(f for f in cat["fields"] if f["id"] == "small_gift_used")
    assert gift["label"] == "€3,000 Small Gift Exemption already used from this giver this year"
    assert gift["max"] == 3000
    assert gift["default"] == 0
    assert cat["formula"] == "cat"

    salary = tools["take-home-pay-calculator"]
    result = next(r for r in salary["results"] if r["id"] == "next_1000_net")
    assert result["label"] == "Change in take-home from next €1,000 gross"
    assert salary["formula"] == "take_home_2026"
