from pathlib import Path
import yaml

from compound.site.build import load_articles, load_tools, linked_articles, tool_catalogue


def test_tool_catalogue_has_unique_routes():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)
    assert len(tools) >= 49
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
        "solar_optimizer", "retrofit_planner", "myfuturefund", "childcare_return",
        "mortgage_switch", "lifetime_cost", "car_finance",
        "nutrition_needs", "pregnancy_timeline", "alcohol_ireland", "net_worth", "debt_repayment",
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
        "solar-ev-battery-optimiser", "whole-house-retrofit-planner", "myfuturefund-calculator",
        "childcare-return-to-work-calculator", "mortgage-switch-calculator", "lifetime-cost-calculator",
        "car-finance-calculator",
        "nutrition-needs-calculator", "pregnancy-due-date-calculator",
        "alcohol-units-calories-cost-calculator", "net-worth-calculator", "debt-repayment-calculator",
    }
    assert expected <= slugs


def test_solar_payback_has_energy_system_controls():
    content_dir = Path(__file__).parents[1] / "content"
    solar = next(tool for tool in load_tools(content_dir) if tool["slug"] == "solar-payback-calculator")
    fields = {field["id"]: field for field in solar["fields"]}
    assert fields["grant_eligible"]["type"] == "checkbox"
    assert fields["has_ev"]["type"] == "checkbox"
    assert fields["has_battery"]["type"] == "checkbox"
    assert fields["night_charge"]["type"] == "checkbox"
    assert fields["annual_home_kwh"]["default"] == 4200
    assert fields["annual_ev_km"]["show_if"] == "has_ev"
    assert fields["battery_cost"]["show_if"] == "has_battery"
    assert fields["night_rate"]["show_if"] == "night_charge"
    result_ids = {result["id"] for result in solar["results"]}
    assert {"grant", "total_demand", "solar_used", "exported", "battery_arbitrage", "payback"} <= result_ids
    guide = solar["guide"]
    assert "4,200 kWh" in guide
    assert "built and occupied before 2021" in guide
    assert "EV" in guide and "battery" in guide.lower() and "night" in guide.lower()


def test_next_flagship_tools_have_expected_controls():
    content_dir = Path(__file__).parents[1] / "content"
    tools = {tool["slug"]: tool for tool in load_tools(content_dir)}

    mff_fields = {field["id"]: field for field in tools["myfuturefund-calculator"]["fields"]}
    assert mff_fields["workplace_pension"]["type"] == "checkbox"

    childcare = tools["childcare-return-to-work-calculator"]
    childcare_fields = {field["id"]: field for field in childcare["fields"]}
    assert childcare_fields["ncs_rate"]["default"] == 2.14

    retrofit_fields = {field["id"]: field for field in tools["whole-house-retrofit-planner"]["fields"]}
    assert retrofit_fields["oss_eligible"]["type"] == "checkbox"
    assert retrofit_fields["solar_kwp"]["show_if"] == "solar"

    solar_fields = {field["id"]: field for field in tools["solar-ev-battery-optimiser"]["fields"]}
    assert solar_fields["grant_eligible"]["type"] == "checkbox"
    assert solar_fields["has_ev"]["type"] == "checkbox"
    assert solar_fields["ev_loss_pct"]["show_if"] == "has_ev"

    lifetime = tools["lifetime-cost-calculator"]
    assert any(result["id"] == "lifetime_nominal" for result in lifetime["results"])


def test_car_finance_has_basic_and_advanced_fields():
    content_dir = Path(__file__).parents[1] / "content"
    car = next(tool for tool in load_tools(content_dir) if tool["slug"] == "car-finance-calculator")
    fields = {field["id"]: field for field in car["fields"]}
    assert fields["car_price"].get("advanced") is not True
    assert fields["pcp_balloon"].get("advanced") is not True
    assert fields["loan_term_years"]["advanced"] is True
    assert fields["estimated_value"]["advanced"] is True
    assert fields["annual_mileage_limit"]["advanced"] is True
    assert fields["condition_charge"]["advanced"] is True
    result_ids = {result["id"] for result in car["results"]}
    assert {"loan_monthly", "hp_monthly", "pcp_monthly", "pcp_keep_total", "pcp_return_total", "pcp_equity"} <= result_ids
    assert "Personal car loan" in car["guide"]
    assert "Hire Purchase" in car["guide"]
    assert "Personal Contract Plan" in car["guide"]


def test_health_expansion_is_substantial_and_sourced():
    content_dir = Path(__file__).parents[1] / "content"
    tools = {tool["slug"]: tool for tool in load_tools(content_dir)}

    nutrition = tools["nutrition-needs-calculator"]
    nutrition_results = {result["id"] for result in nutrition["results"]}
    assert {"resting", "maintenance", "target", "protein", "fat", "carbs", "fibre"} <= nutrition_results
    assert len(nutrition["sources"]) >= 6
    assert "Mifflin" in nutrition["guide"] and "0.83 g" in nutrition["guide"] and "1.6 g/kg" in nutrition["guide"]

    pregnancy = tools["pregnancy-due-date-calculator"]
    pregnancy_fields = {field["id"]: field for field in pregnancy["fields"]}
    assert pregnancy_fields["lmp"]["type"] == "date"
    assert pregnancy_fields["assigned_due_date"]["optional"] is True
    assert len(pregnancy["sources"]) >= 3
    assert "first-trimester ultrasound" in pregnancy["guide"]

    alcohol = tools["alcohol-units-calories-cost-calculator"]
    alcohol_results = {result["id"] for result in alcohol["results"]}
    assert {"standard_drinks", "grams", "weekly_kcal", "annual_spend", "annual_saving"} <= alcohol_results
    assert len(alcohol["sources"]) >= 5
    assert "10 grams" in alcohol["guide"] and "0.789" in alcohol["guide"]

def test_bmi_guide_cites_waist_to_height_meta_analysis():
    content_dir = Path(__file__).parents[1] / "content"
    guide = (content_dir / "bmi-guide.md").read_text()
    assert "300,000 adults" in guide
    assert "22106927" in guide


def test_article_tool_link_network_is_explicit_and_bidirectional():
    content_dir = Path(__file__).parents[1] / "content"
    articles = load_articles(content_dir)
    tools = load_tools(content_dir)
    catalogue = tool_catalogue(content_dir, tools)

    linked = [article for article in articles if article.related_tools]
    assert len(linked) >= 15
    assert all(len(article.related_tools) <= 4 for article in linked)
    assert all(slug in catalogue for article in linked for slug in article.related_tools)

    by_slug = {article.slug: article for article in articles}
    assert by_slug["mortgage-overpayments-100-euro-ireland"].related_tools == [
        "mortgage-overpayment-calculator", "mortgage-switch-calculator"
    ]
    assert "nutrition-needs-calculator" in by_slug["macronutrients-micronutrients-guide-ireland"].related_tools
    assert by_slug["rent-tax-credit-ireland-who-can-claim"].related_tools == ["rent-tax-credit-calculator"]

    reverse = linked_articles("mortgage-overpayment-calculator", articles)
    assert any(article.slug == "mortgage-overpayments-100-euro-ireland" for article in reverse)

def test_happiness_articles_are_not_forced_into_tool_links():
    content_dir = Path(__file__).parents[1] / "content"
    happiness = [a for a in load_articles(content_dir) if a.pillar == "happiness"]
    assert happiness
    assert all(not a.related_tools for a in happiness)


def test_net_worth_calculator_is_substantial_and_sourced():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "net-worth-calculator")
    fields = {field["id"]: field for field in tool["fields"]}
    results = {result["id"] for result in tool["results"]}

    assert tool["formula"] == "net_worth"
    assert fields["cash"]["section_start"] == "Assets"
    assert fields["mortgage"]["section_start"] == "Debts"
    assert fields["other_property"]["advanced"] is True
    assert fields["business_value"]["advanced"] is True
    assert fields["other_property_mortgage"]["advanced"] is True
    assert {"net_worth", "total_assets", "total_liabilities", "property_equity",
            "financial_assets", "net_ex_pension", "debt_asset_ratio"} <= results
    assert len(tool["sources"]) >= 3
    assert "€256,900" in tool["guide"]
    assert "net worth is a balance-sheet number" in tool["guide"].lower()
    assert "do not count the same value twice" in tool["guide"].lower()


def test_debt_repayment_calculator_is_flagship_quality():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "debt-repayment-calculator")

    assert tool["formula"] == "debt_repayment"
    assert len(tool["sample_debts"]) >= 3
    assert tool["extra_default"] > 0
    assert len(tool["sources"]) >= 5
    guide = tool["guide"].lower()
    assert "debt avalanche" in guide
    assert "debt snowball" in guide
    assert "priority debts" in guide
    assert "mabs" in guide
    assert "credit card" in guide or "credit-card" in guide


def test_debt_repayment_custom_assets_exist():
    root = Path(__file__).parents[1]
    assert (root / "compound" / "site" / "templates" / "debt_repayment.html").is_file()
    assert (root / "compound" / "site" / "static" / "debt-repayment.css").is_file()
    assert (root / "compound" / "site" / "static" / "debt-repayment.js").is_file()


def test_calculator_responsive_overflow_guardrails():
    root = Path(__file__).parents[1] / "compound" / "site" / "static"
    tools_css = (root / "tools.css").read_text()
    debt_css = (root / "debt-repayment.css").read_text()
    compound_css = (root / "compound-calculator.css").read_text()
    bmi_css = (root / "bmi-calculator.css").read_text()

    assert 'container-type:inline-size' in tools_css
    assert '.tool-page[data-tool-name="net-worth-calculator"] .tool-result-grid' in tools_css
    assert 'grid-template-columns:1fr!important' in tools_css
    assert 'overflow-wrap:anywhere' in tools_css
    assert 'container-type:inline-size' in debt_css
    assert 'overflow-wrap:anywhere' in debt_css
    assert '#compound-concept .result{container-type:inline-size}' in compound_css
    assert '.bmi-workspace>*' in bmi_css


def test_sponsorship_categories_cover_tool_catalogue():
    from compound.site.build import TOOL_SPONSORSHIP_CATEGORY_ORDER

    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)
    expected_order = [
        "Mortgages & Home Buying",
        "Pensions & Investing",
        "Home Energy",
        "Tax & Take-Home Pay",
        "Loans & Debt",
        "EV & Motoring",
        "Health",
        "Family & Life Planning",
    ]
    assert TOOL_SPONSORSHIP_CATEGORY_ORDER == expected_order
    assert {tool["category"] for tool in tools} <= set(expected_order)
    assert all(any(tool["category"] == category for tool in tools) for category in expected_order)

    by_slug = {tool["slug"]: tool["category"] for tool in tools}
    assert by_slug["mortgage-calculator"] == "Mortgages & Home Buying"
    assert by_slug["net-worth-calculator"] == "Pensions & Investing"
    assert by_slug["solar-payback-calculator"] == "Home Energy"
    assert by_slug["take-home-pay-calculator"] == "Tax & Take-Home Pay"
    assert by_slug["debt-repayment-calculator"] == "Loans & Debt"
    assert by_slug["car-finance-calculator"] == "EV & Motoring"
    assert by_slug["nutrition-needs-calculator"] == "Health"
    assert by_slug["pregnancy-due-date-calculator"] == "Family & Life Planning"
