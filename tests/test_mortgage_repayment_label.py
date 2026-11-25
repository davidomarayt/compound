"""Mortgage normalised payment must display the same unit the formula uses."""
from pathlib import Path

from compound.site.build import load_tools


def test_mortgage_repayment_comparison_label_keeps_full_unit():
    tools = {t["slug"]: t for t in load_tools(Path(__file__).parents[1] / "content")}
    mortgage = tools["mortgage-calculator"]
    result = next(r for r in mortgage["results"] if r["id"] == "payment_per_100k")
    assert result["label"] == "Monthly repayment per €100,000 borrowed"
    assert mortgage["formula"] == "mortgage"
    fields = {f["id"]: f for f in mortgage["fields"]}
    assert fields["amount"]["default"] == 300000
    assert fields["rate"]["default"] == 3.5
    assert fields["years"]["default"] == 30
