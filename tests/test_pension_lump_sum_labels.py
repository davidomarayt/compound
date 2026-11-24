"""Regression for comma-containing pension lump-sum labels in YAML flow maps."""
from pathlib import Path

from compound.site.build import load_tools


def test_pension_lump_sum_displays_full_paye_threshold():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(t for t in load_tools(content_dir)
                if t["slug"] == "pension-lump-sum-calculator-ireland")
    fields = {f["id"]: f for f in tool["fields"]}
    results = {r["id"]: r for r in tool["results"]}

    assert fields["marginal_rate"]["label"] == (
        "Assumed PAYE rate on cumulative lump sums above €500,000"
    )
    assert results["above_500"]["label"] == (
        "Current portion above cumulative €500,000 threshold"
    )
    assert results["marginal_tax"]["label"] == (
        "Estimated PAYE on amount above €500,000"
    )
    assert fields["marginal_rate"]["default"] == 40
    assert tool["formula"] == "pension_lump_sum_ireland"
