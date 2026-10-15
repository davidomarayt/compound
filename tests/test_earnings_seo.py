"""Guard the 20-company, one-URL SEO rollout against fiscal-date and data regressions."""
from pathlib import Path

from compound.site.earnings_seo import ORDER, PRIORITY, build_earnings_seo, fiscal_period_display
from compound.site.earnings_view import load_company_report

ROOT = Path(__file__).resolve().parents[1]
MAG7 = {"AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA"}


def test_exactly_seven_plus_thirteen_source_backed_profiles():
    assert len(PRIORITY) == len(ORDER) == 20
    assert len(set(ORDER)) == 20
    assert MAG7.issubset(PRIORITY)
    for ticker in ORDER:
        report = load_company_report(ROOT / "content", ticker)
        assert report is not None, ticker
        assert report["latest_source"].startswith("https://www.sec.gov/Archives/"), ticker
        assert report["latest_figures"]["revenue"].startswith("$"), ticker
        output = build_earnings_seo({"symbol": ticker}, report)
        assert output is not None
        assert output["latest_end"] == report["latest_end"]
        label = report["latest_label"]
        fy, fp = label.split()
        expected = f"{fp} {fy}" if fp != "FY" else f"{fy} Full-Year"
        assert expected in output["headline"]
        assert output["period_subtitle"].startswith(("Quarter ended ", "Fiscal year ended "))
        assert output["readable_end"].endswith(report["latest_end"][:4])
        if int(fy[2:]) != int(report["latest_end"][:4]):
            assert f"({output['calendar_period']})" in output["title"], ticker
            assert f"({output['calendar_period']})" in output["hub_period"], ticker
        else:
            assert f"({output['calendar_period']})" not in output["title"], ticker
        assert output["source"] == report["latest_source"]
        assert all(url["ticker"] in PRIORITY for url in output["related"])


def test_non_priority_profiles_and_missing_filings_never_gain_optimised_copy():
    assert build_earnings_seo({"symbol": "CTAS"}, {"latest_source": "https://www.sec.gov/Archives/"}) is None
    assert build_earnings_seo({"symbol": "AAPL"}, None) is None


def test_fiscal_2027_second_quarter_is_not_claimed_to_be_calendar_2027():
    report = {
        "latest_label": "FY2027 Q2", "latest_end": "2026-07-26", "latest_filed": "2026-08-20",
        "latest_source": "https://www.sec.gov/Archives/test",
        "latest_figures": {"revenue": "$40.00bn", "net_income": "$20.00bn", "diluted_eps": "$1.20"},
        "yoy": {"revenue": 12.5, "net_income": -2.5, "diluted_eps": 0},
        "latest_qoq": {"revenue": 4.5}, "latest_prev_label": "FY2027 Q1"
    }
    out = build_earnings_seo({"symbol": "NVDA"}, report)
    assert "Q2 FY2027 Earnings (July 2026)" in out["title"]
    assert out["headline"] == "Nvidia Q2 FY2027 Earnings Results"
    assert "Quarter ended 26 July 2026" in out["period_subtitle"]
    assert "SEC 10-Q filed 20 August 2026" in out["period_subtitle"]
    assert "July 2026" in out["description"]
    assert "Revenue rose 12.5%" in out["movements"][0]
    assert any("fell 2.5%" in item for item in out["movements"])
    assert all("2027-07" not in val for val in (out["title"], out["description"]))


def test_amazon_nonoperating_gain_is_not_applied_to_later_fiscal_quarters():
    report = {
        "latest_label": "FY2026 Q2", "latest_end": "2026-06-30",
        "latest_source": "https://www.sec.gov/Archives/test",
        "latest_figures": {"revenue": "$200.61bn", "net_income": "$62.65bn", "diluted_eps": "$5.75"},
        "yoy": {}, "latest_qoq": {},
    }
    old = build_earnings_seo({"symbol": "AMZN"}, report)
    assert "Anthropic" in old["caveat"]
    newer = build_earnings_seo(
        {"symbol": "AMZN"}, {**report, "latest_label": "FY2026 Q3", "latest_end": "2026-09-30"}
    )
    assert "Anthropic" not in newer["caveat"]


def test_full_year_report_not_turned_into_a_fake_q4():
    report = {
        "latest_label": "FY2026 FY", "latest_end": "2026-06-30",
        "latest_source": "https://www.sec.gov/Archives/test",
        "latest_figures": {"revenue": "$200.00bn", "net_income": "$50.00bn", "diluted_eps": "$12.50"},
        "yoy": {}, "latest_qoq": {},
    }
    output = build_earnings_seo({"symbol": "MSFT"}, report)
    assert "FY2026 Full-Year" in output["title"]
    assert "Fiscal year ended 30 June 2026" in output["period_subtitle"]
    assert "Q4" not in output["title"]


def test_oracle_profile_uses_sec_verified_fy2027_label():
    report = load_company_report(ROOT / "content", "ORCL")
    assert report["latest_label"] == "FY2027 Q1"
    label = fiscal_period_display(report)
    assert label["display"] == "Q1 FY2027"
    assert label["title_calendar"] == " (August 2026)"
    output = build_earnings_seo({"symbol": "ORCL"}, report)
    assert "Oracle Q1 FY2027 Earnings (August 2026)" in output["title"]
    assert "Quarter ended 31 August 2026" in output["period_subtitle"]


def test_same_calendar_and_fiscal_year_does_not_repeat_year_in_title():
    report = load_company_report(ROOT / "content", "AMZN")
    output = build_earnings_seo({"symbol": "AMZN"}, report)
    assert "Q2 FY2026 Earnings" in output["title"]
    assert "(June 2026)" not in output["title"]
    assert "Quarter ended 30 June 2026" in output["period_subtitle"]
