from pathlib import Path
import re
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


def test_mortgage_calculator_has_flagship_guide():
    content_dir = Path(__file__).parents[1] / "content"
    mortgage = next(tool for tool in load_tools(content_dir) if tool["slug"] == "mortgage-calculator")
    guide = mortgage["guide"]

    assert len(guide.split()) >= 1200
    assert len(mortgage["sources"]) >= 4
    assert "€1,347" in guide
    assert "4 times gross income" in guide
    assert "3.5 times gross income" in guide
    assert "APRC" in guide
    assert "/mortgage-borrowing-calculator/" in guide
    assert "/mortgage-affordability-calculator/" in guide
    assert "/mortgage-overpayment-calculator/" in guide
    assert "/mortgage-switch-calculator/" in guide
    assert "/house-buying-costs-calculator/" in guide


def test_every_calculator_has_substantial_educational_depth():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)

    assert len(tools) >= 49
    for tool in tools:
        words = str(tool.get("guide") or "").split()
        assert len(words) >= 500, f"{tool['slug']} guide is too thin: {len(words)} words"
        assert tool.get("sources"), f"{tool['slug']} should expose at least one source"
        assert "Method" in str(tool.get("guide") or "") or "method" in str(tool.get("guide") or "").lower()

    compound = (content_dir / "compound-calculator-guide.md").read_text()
    bmi = (content_dir / "bmi-guide.md").read_text()
    assert len(compound.split()) >= 1800
    assert len(bmi.split()) >= 1800


def test_every_standard_calculator_has_a_dedicated_guide_file():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)
    guide_dir = content_dir / "tool-guides"

    expected = {f"{tool['slug']}.md" for tool in tools}
    actual = {path.name for path in guide_dir.glob("*.md")}
    assert actual == expected
    assert all((guide_dir / name).stat().st_size >= 2500 for name in expected)


def test_flagship_calculator_experience_is_catalogue_wide():
    from compound.site.build import TOOL_PRIMARY_RESULTS

    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)

    assert set(TOOL_PRIMARY_RESULTS) == {tool["slug"] for tool in tools}
    for tool in tools:
        result_ids = {result["id"] for result in tool["results"]}
        assert tool["primary_result"] in result_ids
        assert len(tool.get("guide_toc") or []) >= 5, f"{tool['slug']} needs navigable guide sections"
        assert len(tool.get("faq") or []) >= 3, f"{tool['slug']} needs useful FAQs"


def test_flagship_calculator_frontend_features_are_present():
    root = Path(__file__).parents[1] / "compound" / "site"
    template = (root / "templates" / "tool.html").read_text()
    tools_js = (root / "static" / "tools.js").read_text()
    tools_css = (root / "static" / "tools.css").read_text()
    debt_template = (root / "templates" / "debt_repayment.html").read_text()
    debt_js = (root / "static" / "debt-repayment.js").read_text()

    assert "data-tool-share" in template
    assert "data-tool-print" in template
    assert "data-tool-insights" in template
    assert "tool-guide-toc" in template
    assert "buildInsights" in tools_js
    assert "fallbackChart" in tools_js
    assert "TextEncoder" in tools_js and "#scenario=" in tools_js
    assert "tool-result-primary" in tools_css
    assert "tool-use-strip" in tools_css
    assert "data-debt-share" in debt_template
    assert "TextEncoder" in debt_js and "#scenario=" in debt_js


def test_every_formula_has_a_personalised_readout():
    root = Path(__file__).parents[1] / "compound" / "site" / "static"
    js = (root / "tools.js").read_text()

    calculator_block = js.split("const calculators = {", 1)[1].split("\n  };", 1)[0]
    formulas = set(re.findall(r"^\s{4}([a-zA-Z0-9_]+)\(v\)\{", calculator_block, re.MULTILINE))
    insight_block = js.split("const buildInsights", 1)[1].split("const renderInsights", 1)[0]
    insight_cases = set(re.findall(r"case '([^']+)'", insight_block))

    assert formulas
    assert formulas == insight_cases


def test_every_numeric_formula_has_visual_context_or_explicit_timeline():
    root = Path(__file__).parents[1] / "compound" / "site" / "static"
    js = (root / "tools.js").read_text()

    calculator_block = js.split("const calculators = {", 1)[1].split("\n  };", 1)[0]
    formulas = re.findall(r"^\s{4}([a-zA-Z0-9_]+)\(v\)\{", calculator_block, re.MULTILINE)
    fallback_block = js.split("const fallbackChart", 1)[1].split("const buildInsights", 1)[0]
    fallback_cases = set(re.findall(r"case '([^']+)'", fallback_block))

    embedded = set()
    for index, formula in enumerate(formulas):
        start = calculator_block.index(f"    {formula}(v){{")
        end = (
            calculator_block.index(f"    {formulas[index + 1]}(v){{", start)
            if index + 1 < len(formulas)
            else len(calculator_block)
        )
        if "__chart" in calculator_block[start:end]:
            embedded.add(formula)

    assert set(formulas) - embedded - fallback_cases == {"pregnancy_timeline"}


def test_advanced_modes_explain_hidden_assumptions():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)

    for tool in tools:
        if any(field.get("advanced") for field in tool["fields"]):
            assert tool.get("basic_note"), f"{tool['slug']} needs a Basic-mode assumptions note"
            assert tool.get("advanced_note"), f"{tool['slug']} needs an Advanced-mode explanation"


def test_every_calculator_has_contextual_input_help():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)

    for tool in tools:
        assert any(field.get("help") for field in tool["fields"]), f"{tool['slug']} needs at least one contextual input hint"


def test_calculators_support_side_by_side_scenario_comparison():
    root = Path(__file__).parents[1] / "compound" / "site"
    template = (root / "templates" / "tool.html").read_text()
    js = (root / "static" / "tools.js").read_text()
    css = (root / "static" / "tools.css").read_text()

    assert "data-tool-save-scenario" in template
    assert "data-tool-compare-panel" in template
    assert "data-tool-clear-scenario" in template
    assert "snapshotResults" in js
    assert "renderSavedComparison" in js
    assert "tool-compare-row" in css


def test_calculator_sitemap_tracks_review_dates():
    build_py = (Path(__file__).parents[1] / "compound" / "site" / "build.py").read_text()
    assert "<lastmod>" in build_py
    assert 'str(tool.get("updated") or "")' in build_py
    assert '(a.reviewed or a.date).isoformat()' in build_py


def test_2026_statutory_calculator_parameters_are_regression_locked():
    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()

    # Revenue 2026 USC: €13,000 exemption; 0.5%, 2%, 3%, 8% bands.
    assert "if(x<=13000) return 0" in js
    assert "[[12012,.005],[16688,.02],[41344,.03],[Infinity,.08]]" in js

    # Class A employee PRSI changes from 4.20% to 4.35% on 1 October 2026.
    assert "weeklyClassA(weekly,.042)" in js
    assert "weeklyClassA(weekly,.0435)" in js
    assert "before*39+after*13" in js

    # Self-employed USC surcharge and 2026 Class S blended PRSI.
    assert "Math.max(0,x-100000)*.03" in js
    assert "Math.max(650,x*.042375)" in js

    # CAT thresholds / rate and small-gift exemption.
    assert "A:400000,B:40000,C:20000" in js
    assert "Math.min(3000,v.benefit)" in js
    assert "afterTax=Math.max(0,v.prior+current-threshold)*.33" in js

    # Help to Buy enhanced 2026 limits and qualifying-finance treatment.
    assert "valueOk=v.property_value<=500000" in js
    assert "financeOk=ltv>=70" in js
    assert "Math.min(30000,valueCap,v.tax_paid)" in js
    assert "v.__advanced?Math.max(0,v.la_affordable_contribution||0):0" in js
    assert "qualifyingFinance=Math.max(0,v.mortgage)+affordable" in js

    # First Home Scheme funding limits, local price ceilings and service charges.
    assert "v.htb==='yes'?.20:.30" in js
    assert "Math.max(v.property_value*.025,10000)" in js
    assert "fhsPriceCeiling(v.authority,v.property_type)" in js
    assert "serviceBase*.0175" in js

    # Solar PV grant: €700/kWp first 2 kWp, €200/kWp next 2 kWp, €1,800 max.
    assert "Math.min(1800" in js
    assert "*700" in js and "*200" in js

    # Standard residential Stamp Duty bands.
    assert "Math.min(p,1000000)*.01" in js
    assert "1500000)-1000000)*.02" in js
    assert "Math.max(0,p-1500000)*.06" in js

    # DIRT and standard CGT rate / annual exemption.
    assert "dirt(v){ const tax=v.interest*.33" in js
    assert "afterLoss-1270" in js and "tax=taxable*.33" in js

    # Central Bank standard LTI/LTV modelling assumptions.
    assert "v.buyer_type==='ftb'?4:3.5" in js
    assert "v.buyer_type==='btl'?.30:.10" in js




def test_mortgage_switch_supports_fixed_period_comparison():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "mortgage-switch-calculator")
    fields = {field["id"]: field for field in tool["fields"]}
    results = {result["id"] for result in tool["results"]}

    assert fields["comparison_years"]["advanced"] is True
    assert fields["comparison_years"]["default"] == 5
    assert {"horizon_interest_current", "horizon_interest_new", "horizon_saving",
            "horizon_balance_difference", "lifetime_difference"} <= results
    assert "comparison horizon" in tool["guide"].lower()
    assert "cashback" in tool["guide"].lower()
    assert "remaining balance" in tool["guide"].lower()


def test_mortgage_overpayment_supports_timing_and_lump_sums():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "mortgage-overpayment-calculator")
    fields = {field["id"]: field for field in tool["fields"]}
    results = {result["id"] for result in tool["results"]}

    assert fields["overpayment_start_month"]["advanced"] is True
    assert fields["lump_sum"]["advanced"] is True
    assert fields["lump_sum_month"]["advanced"] is True
    assert fields["lump_sum_month"]["show_if"] == "lump_sum"
    assert {"new_term", "standard_interest", "overpayment_interest", "interest_saved"} <= results
    assert "one-off lump sum" in tool["guide"].lower()
    assert "month by month" in tool["guide"].lower()


def test_home_support_calculators_model_current_scheme_constraints():
    content_dir = Path(__file__).parents[1] / "content"
    tools = {tool["slug"]: tool for tool in load_tools(content_dir)}

    htb = tools["help-to-buy-calculator"]
    htb_fields = {field["id"]: field for field in htb["fields"]}
    htb_results = {result["id"] for result in htb["results"]}
    assert htb_fields["la_affordable_contribution"]["advanced"] is True
    assert {"ltv", "qualifying_finance", "minimum_finance", "claim", "eligibility"} <= htb_results
    assert "First Home Scheme equity does not count" in htb["guide"]
    assert "11 October 2023" in htb["guide"]

    fhs = tools["first-home-scheme-calculator"]
    fhs_fields = {field["id"]: field for field in fhs["fields"]}
    fhs_results = {result["id"] for result in fhs["results"]}
    assert fhs_fields["authority"]["type"] == "select"
    assert len(fhs_fields["authority"]["options"]) == 31
    assert fhs_fields["property_type"]["type"] == "select"
    assert {"price_ceiling", "gap", "share", "max_fhs", "year6_charge", "charges_to_year10", "check"} <= fhs_results
    assert "€475,000" in fhs["guide"]
    assert "1.75%" in fhs["guide"]
    assert "2.15%" in fhs["guide"]
    assert "2.85%" in fhs["guide"]


def test_every_calculator_guide_has_a_worked_example():
    content_dir = Path(__file__).parents[1] / "content"
    tools = load_tools(content_dir)

    for tool in tools:
        guide = str(tool.get("guide") or "")
        assert "## Worked example" in guide, f"{tool['slug']} needs a worked example"
        assert "## Method and limitations" in guide, f"{tool['slug']} needs an explicit methodology section"


def test_bespoke_flagships_match_quality_system():
    root = Path(__file__).parents[1] / "compound" / "site"
    compound_template = (root / "templates" / "calculator.html").read_text()
    compound_partial = (root / "templates" / "_compound_calculator.html").read_text()
    bmi_template = (root / "templates" / "bmi.html").read_text()
    bmi_js = (root / "static" / "bmi-calculator.js").read_text()

    assert "dateModified" in compound_template
    assert "cc-trust" in compound_partial
    assert "cc-share" in compound_partial and "cc-export" in compound_partial and "cc-report" in compound_partial
    assert "Rules checked 22 September 2026" in compound_partial

    assert "dateModified" in bmi_template
    assert "bmi-trust" in bmi_template
    assert "bmi-copy-result" in bmi_template and "bmi-print-result" in bmi_template
    assert "navigator.clipboard" in bmi_js
    assert "<noscript>" in bmi_template


def test_rent_vs_buy_models_transaction_and_ownership_costs():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "rent-vs-buy-calculator")
    fields = {field["id"]: field for field in tool["fields"]}
    results = {result["id"] for result in tool["results"]}

    assert fields["buying_costs"]["advanced"] is True
    assert fields["owner_fixed_annual"]["advanced"] is True
    assert fields["selling_cost_pct"]["advanced"] is True
    assert "upfront_buying_costs" in results

    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()
    assert "rent_vs_buy(v)" in js\n    assert "stampDutyResidential(price)" in js
    assert "v.deposit+upfrontCosts" in js
    assert "house*(1-sellPct)" in js
    assert "v.owner_fixed_annual" in js


def test_mortgage_affordability_applies_deposit_constraint():
    content_dir = Path(__file__).parents[1] / "content"
    tool = next(tool for tool in load_tools(content_dir) if tool["slug"] == "mortgage-affordability-calculator")
    result_ids = {result["id"] for result in tool["results"]}
    assert "deposit_based_mortgage" in result_ids

    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()
    assert "mortgage_affordability(v)" in js\n    assert "const depositBased=deposit*9" in js
    assert "Math.min(lti,paymentBased,depositBased)" in js


def test_retirement_tools_distinguish_nominal_real_and_sustainability():
    content_dir = Path(__file__).parents[1] / "content"
    tools = {tool["slug"]: tool for tool in load_tools(content_dir)}

    fire_fields = {field["id"]: field for field in tools["fire-number-calculator"]["fields"]}
    fire_results = {result["id"] for result in tools["fire-number-calculator"]["results"]}
    assert all(fire_fields[field]["advanced"] is True for field in (
        "ongoing_income", "extra_reserve", "contribution_growth", "annual_fee", "inflation_rate"
    ))
    assert {"portfolio_spending", "target", "gap", "progress", "real_return", "years",
            "target_3", "target_35", "target_4"} <= fire_results

    pension_fields = {field["id"]: field for field in tools["pension-projection-calculator"]["fields"]}
    pension_results = {result["id"] for result in tools["pension-projection-calculator"]["results"]}
    assert all(pension_fields[field]["advanced"] is True for field in (
        "contribution_growth", "annual_avc", "stress_return_rate", "annual_fee", "inflation_rate"
    ))
    assert {"projected_real", "employee_contributions", "employer_contributions",
            "fee_drag", "stress_projected"} <= pension_results

    retirement_fields = {field["id"]: field for field in tools["retirement-income-calculator"]["fields"]}
    retirement_results = {result["id"] for result in tools["retirement-income-calculator"]["results"]}
    assert all(retirement_fields[field]["advanced"] is True for field in (
        "target_income", "retirement_years", "return_rate", "stress_return_rate",
        "annual_fee", "inflation_rate"
    ))
    assert {"ending_pot", "depletion", "required_withdrawal_rate", "fees_paid",
            "stress_ending_pot", "stress_depletion"} <= retirement_results

    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()
    assert "const otherIncome=advanced?Math.max(0,v.ongoing_income):0" in js
    assert "const fee=advanced?Math.max(0,v.annual_fee/100):0" in js
    assert "stressReturn=advanced?v.stress_return_rate:2" in js
    assert "annualAvc=advanced?Math.max(0,v.annual_avc):0" in js


def test_myfuturefund_and_investment_fee_engines_match_advanced_outputs():
    content_dir = Path(__file__).parents[1] / "content"
    tools = {tool["slug"]: tool for tool in load_tools(content_dir)}

    mff = tools["myfuturefund-calculator"]
    mff_fields = {field["id"]: field for field in mff["fields"]}
    mff_results = {result["id"] for result in mff["results"]}
    assert mff_fields["employment_status"]["type"] == "select"
    assert mff_fields["assume_opt_in"]["advanced"] is True
    assert {"external_2026", "employer_total", "state_total", "projected_real",
            "investment_growth"} <= mff_results

    fees = tools["investment-fee-calculator"]
    fee_fields = {field["id"]: field for field in fees["fields"]}
    fee_results = {result["id"] for result in fees["results"]}
    assert all(fee_fields[field]["advanced"] is True for field in (
        "fixed_low", "fixed_high", "contribution_charge_low",
        "contribution_charge_high", "inflation_rate"
    ))
    assert {"low_fees_paid", "high_fees_paid", "real_fee_gap"} <= fee_results

    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()
    assert "const participating=autoEligible||(advanced&&optInEligible&&Boolean(v.assume_opt_in));" in js
    assert "external_2026:money(er2026+sr2026)" in js
    assert "contributionCharge=advanced?Math.max(0,contributionChargePct)/100:0" in js
    assert "real_fee_gap:" in js


def test_savings_returns_use_effective_annual_compounding():
    js = (Path(__file__).parents[1] / "compound" / "site" / "static" / "tools.js").read_text()
    assert "Math.pow(Math.max(.000001,1+annualRate/100),1/12)-1" in js
    assert "Math.pow(Math.max(.000001,1+v.rate/100),1/12)-1" in js
    assert "feeMonthFactor=Math.pow(Math.max(.000001,1-pctFee),1/12)" in js
    assert "((1+gross)*(1-Math.max(0,v.fee_low)/100)-1)*100" in js
    assert "((1+gross)*(1-Math.max(0,v.fee_high)/100)-1)*100" in js
