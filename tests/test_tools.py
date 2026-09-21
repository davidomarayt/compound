from pathlib import Path
import yaml

from compound.site.build import load_tools


def test_tool_catalogue_has_unique_routes():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)
    assert len(tools) >= 37
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
        "take_home_2026", "income_tax_2026", "usc_2026", "prsi_2026", "cat",
        "rent_credit", "help_to_buy", "first_home_scheme", "dirt",
        "contractor_vs_salary", "investment_fees", "fire_number", "retirement_income",
        "pension_projection", "rent_vs_buy", "mortgage_affordability",
        "house_buying_costs", "solar_payback", "ber_energy",
    }
    assert {tool["formula"] for tool in data["tools"]} <= supported


def test_high_intent_tool_routes_present():
    content_dir = Path(__file__).parents[1] / "content"
    slugs = {tool["slug"] for tool in load_tools(content_dir)}
    expected = {
        "take-home-pay-calculator", "income-tax-calculator", "usc-calculator", "prsi-calculator",
        "inheritance-tax-calculator", "rent-tax-credit-calculator", "help-to-buy-calculator",
        "first-home-scheme-calculator", "dirt-calculator", "contractor-vs-salary-calculator",
        "investment-fee-calculator", "fire-number-calculator", "retirement-income-calculator",
        "pension-projection-calculator", "rent-vs-buy-calculator", "mortgage-affordability-calculator",
        "house-buying-costs-calculator", "solar-payback-calculator", "ber-energy-cost-calculator",
    }
    assert expected <= slugs
