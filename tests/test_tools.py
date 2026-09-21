from pathlib import Path
import yaml

from compound.site.build import load_tools


def test_tool_catalogue_has_unique_routes():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)
    assert len(tools) >= 18
    assert len({tool["slug"] for tool in tools}) == len(tools)
    assert all(tool["url"].startswith("/") and tool["url"].endswith("/") for tool in tools)
    assert all(tool["fields"] and tool["results"] for tool in tools)


def test_tool_formulas_are_supported():
    data = yaml.safe_load((Path(__file__).parents[1] / "content" / "tools.yml").read_text())
    supported = {
        "mortgage", "mortgage_overpayment", "mortgage_borrowing", "house_deposit",
        "stamp_duty", "lpt", "loan", "savings_goal", "regular_savings",
        "pension_relief", "cgt", "vat", "inflation", "emergency",
        "salary_hourly", "fuel", "ev", "electricity",
    }
    assert {tool["formula"] for tool in data["tools"]} <= supported
