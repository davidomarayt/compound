"""Guard every calculator against YAML flow-map truncation of comma-bearing text.

An unquoted value such as ``{label: Legal, valuation costs}`` parses as
label="Legal" plus a stray null key "valuation costs". Labels then render cut
off at the first comma. This scans all tools so new cases fail CI.
"""
from pathlib import Path

from compound.site.build import load_tools

CONTENT = Path(__file__).parents[1] / "content"


def _stray_keys(obj, path="tools"):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if value is None and (not isinstance(key, str) or not key.isidentifier()):
                found.append(f"{path}: {key!r} (label={obj.get('label')!r})")
            found.extend(_stray_keys(value, f"{path}/{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(_stray_keys(item, f"{path}[{i}]"))
    return found


def test_no_tool_has_comma_truncated_flow_map_values():
    assert _stray_keys(load_tools(CONTENT)) == []


def test_previously_truncated_labels_are_complete():
    tools = {t["slug"]: t for t in load_tools(CONTENT)}

    def item(slug, group, item_id):
        return next(x for x in tools[slug][group] if x["id"] == item_id)

    expected = [
        ("first-home-scheme-calculator", "results", "charges_to_year10", "Illustrative service charges, years 6–10"),
        ("rent-vs-buy-calculator", "fields", "buying_costs", "Legal, valuation & other buying costs (excluding stamp duty)"),
        ("rent-vs-buy-calculator", "fields", "owner_fixed_annual", "Annual LPT, insurance & other fixed ownership costs"),
        ("house-buying-costs-calculator", "results", "other_costs", "Professional, moving & setup costs"),
        ("house-buying-costs-calculator", "results", "moving_setup_costs", "Moving, setup & immediate works"),
        ("myfuturefund-calculator", "fields", "assume_opt_in", "If not auto-enrolled but eligible, assume I opt in"),
        ("college-cost-calculator", "fields", "student_living", "Monthly food, bills and personal costs"),
        ("college-cost-calculator", "fields", "setup_cost", "Books, equipment and other setup costs"),
        ("mortgage-switch-calculator", "fields", "switching_costs", "Legal, valuation and other switching costs"),
        ("lifetime-cost-calculator", "fields", "leisure_monthly", "Leisure, eating out and subscriptions per month"),
    ]
    for slug, group, item_id, label in expected:
        assert item(slug, group, item_id)["label"] == label, (slug, item_id)

    # Numeric settings on edited lines are unchanged.
    assert item("rent-vs-buy-calculator", "fields", "buying_costs")["default"] == 3500
    assert item("rent-vs-buy-calculator", "fields", "owner_fixed_annual")["default"] == 1200
    assert item("college-cost-calculator", "fields", "student_living")["max"] == 15000
    assert item("mortgage-switch-calculator", "fields", "switching_costs")["default"] == 1500
    assert item("myfuturefund-calculator", "fields", "assume_opt_in")["default"] is False
