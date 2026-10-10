"""Offline regression checks for controlled historical SEC and global disclosure watch."""
from datetime import date
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
backfill = importlib.import_module("earnings_backfill")
watch = importlib.import_module("global_earnings_watch")

from test_earnings import FILING, facts


class FakeSEC:
    def get_json(self, url):
        if url.endswith("company_tickers.json"):
            return {"0": {"ticker": "SPCX", "title": "Space Exploration Technologies Corp.",
                          "cik_str": 123456}}
        if "submissions/" in url:
            return {"filings": {"recent": {
                k: [FILING[k]] for k in
                ("accessionNumber", "form", "filingDate", "reportDate", "primaryDocument")
            }}}
        return facts()


def test_one_per_issuer_and_idempotent_with_real_filing_date(tmp_path, monkeypatch):
    monkeypatch.setattr(backfill, "eligible_universe", lambda *args:
                        [{"symbol": "AAPL", "name": "Apple Inc.", "cik": 320193}])
    registry = tmp_path / "registry.json"
    root = tmp_path / "content"
    preview = backfill.backfill(registry, root, client=FakeSEC(), today=date(2026, 10, 10),
                                days=365, max_new=8, dry_run=True)
    assert len(preview) == 1
    assert not list((root / "wealth").glob("*.md"))
    output = backfill.backfill(registry, root, client=FakeSEC(), today=date(2026, 10, 10),
                               days=365, max_new=8)
    assert len(output) == 1
    text = Path(output[0]).read_text()
    assert "historical_backfill: true" in text
    assert "filing_date: '2026-10-09'" in text or "filing_date: 2026-10-09" in text
    assert "2026-10-10" in text
    assert "https://www.sec.gov/Archives/" in text
    assert backfill.backfill(registry, root, client=FakeSEC(), today=date(2026, 10, 10),
                             days=365, max_new=8) == []


def test_backfill_cap_and_skip_prior_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(backfill, "eligible_universe", lambda *args: [
        {"symbol": "AAPL", "name": "Apple Inc.", "cik": 320193},
        {"symbol": "MSFT", "name": "Microsoft", "cik": 789019},
    ])
    root = tmp_path / "content"
    directory = root / "wealth"
    directory.mkdir(parents=True)
    (directory / "aapl-earnings-fy2026-q3.md").write_text("already published")
    out = backfill.backfill(tmp_path / "registry", root, client=FakeSEC(),
                             today=date(2026, 10, 10), days=365, max_new=1)
    assert len(out) == 1
    assert "msft-earnings" in out[0]
    assert (directory / "aapl-earnings-fy2026-q3.md").read_text() == "already published"


def test_extra_sec_identity_guard(tmp_path):
    path = tmp_path / "companies.json"
    path.write_text(json.dumps({"listed": [
        {"slug": "spcx", "ticker": "SPCX", "name": "SpaceX", "exchange": "Nasdaq"}
    ]}))
    matched = backfill.extra_sec_companies(FakeSEC(), path)
    assert matched == [{"symbol": "SPCX", "name": "SpaceX", "cik": 123456}]
    class WrongSEC(FakeSEC):
        def get_json(self, url):
            if url.endswith("company_tickers.json"):
                return {"0": {"ticker": "SPCX", "title": "Generic Space ETF", "cik_str": 44}}
            return super().get_json(url)
    assert backfill.extra_sec_companies(WrongSEC(), path) == []


def test_ir_monitor_baselines_then_detects_new_primary_results(tmp_path):
    companies = [{"slug": str(i), "name": f"Company {i}", "ticker": f"EX{i}",
                  "source": f"https://investor{i}.example.test/results"} for i in range(10)]
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(json.dumps({"listed": companies}))
    snapshot = tmp_path / "monitoring" / "snapshot.json"
    html1 = '<a href="/investors/quarterly-results">Quarterly results</a>'
    html2 = html1 + '<a href="/investors/2026-earnings">2026 annual earnings report</a>' + (
        '<a href="https://untrusted.example/earnings">Annual earnings on third party</a>')
    first = watch.run(watchlist, snapshot, today=date(2026, 10, 10), fetch=lambda url: html1)
    assert first["companies_checked"] == 10
    assert len(first["pending_review"]) == 0
    second = watch.run(watchlist, snapshot, today=date(2026, 10, 11), fetch=lambda url: html2)
    assert len(second["pending_review"]) == 10
    assert second["new_review_candidates"] == 10
    assert all("untrusted.example" not in x["url"] for x in second["pending_review"])
    third = watch.run(watchlist, snapshot, today=date(2026, 10, 12), fetch=lambda url: html2)
    assert third["new_review_candidates"] == 0
    assert len(third["pending_review"]) == 10


def test_ir_monitors_failure_without_false_positive(tmp_path):
    rows = [{"slug": str(i), "name": "Company", "ticker": "ZZ",
             "source": "https://example.test/investors"} for i in range(10)]
    list_path = tmp_path / "watchlist.json"
    list_path.write_text(json.dumps({"listed": rows}))
    def offline(url):
        raise OSError("Not accessible")
    state = watch.run(list_path, tmp_path / "status.json",
                      today=date(2026, 10, 10), fetch=offline)
    assert not state["pending_review"]
    assert all("Unavailable" in item["official_source_status"]
               for item in state["companies"].values())


def test_20f_and_6k_queued_not_published(tmp_path):
    records = [{"slug": "nvo", "name": "Novo Nordisk", "ticker": "NVO",
                "source": "https://novonordisk.example.test/financial-results"}] + [
                    {"slug": str(i), "name": f"Other {i}", "ticker": str(i),
                     "source": f"https://other{i}.example.test/investors"} for i in range(9)]
    path = tmp_path / "list.json"
    path.write_text(json.dumps({"listed": records}))
    class ForeignSEC:
        def get_json(self, url):
            if url.endswith("company_tickers.json"):
                return {"0": {"ticker": "NVO", "title": "Novo Nordisk A/S", "cik_str": 353278}}
            if "submissions/" in url:
                return {"filings": {"recent": {
                    "accessionNumber": ["0000353278-26-000123"],
                    "form": ["6-K"], "filingDate": ["2026-10-08"],
                    "reportDate": ["2026-10-07"], "primaryDocument": ["form6k.htm"]
                }}}
            return {}
    state = watch.run(path, tmp_path / "monitor.json", today=date(2026,10,10),
                      client=ForeignSEC(), fetch=lambda url: "")
    assert state["new_review_candidates"] == 1
    assert state["pending_review"][0]["form"] == "6-K"
    assert "requires review" in state["pending_review"][0]["source"]


def test_pre_2026_filings_and_reporting_periods_are_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(backfill, "eligible_universe", lambda *args:
                        [{"symbol": "AAPL", "name": "Apple Inc.", "cik": 320193}])

    class HistoricalSEC(FakeSEC):
        def __init__(self, filed, reported):
            self.filed = filed
            self.reported = reported

        def get_json(self, url):
            if "/submissions/" in url:
                prior = {**FILING, "filingDate": self.filed, "reportDate": self.reported}
                return {"filings": {"recent": {
                    k: [prior[k]] for k in ("accessionNumber", "form", "filingDate",
                                           "reportDate", "primaryDocument")
                }}}
            if "companyfacts/" in url:
                raise AssertionError("Disallowed dates must be rejected before requesting SEC XBRL")
            return super().get_json(url)

    for filing, period in [
        ("2025-12-31", "2025-09-30"),   # Old filing and old financial period
        ("2026-02-10", "2025-12-31"),   # New filing but 2025 results
    ]:
        root = tmp_path / (filing + "_" + period)
        result = backfill.backfill(root / "registry", root, client=HistoricalSEC(filing, period),
                                   today=date(2026, 10, 10), days=365, max_new=2)
        assert result == []
        assert not list((root / "wealth").glob("*.md"))

    assert backfill.in_allowed_period({"filingDate": "2026-01-01",
                                       "reportDate": "2026-01-01"})
    assert not backfill.in_allowed_period({"filingDate": "2026-01-01",
                                           "reportDate": "2025-12-31"})


def test_two_per_day_and_total_thirty_historical_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(backfill, "eligible_universe", lambda *args: [
        {"symbol": "AAPL", "name": "Apple Inc.", "cik": 320193},
        {"symbol": "MSFT", "name": "Microsoft", "cik": 789019},
        {"symbol": "NVDA", "name": "Nvidia", "cik": 1045810},
    ])
    root = tmp_path / "content"
    first = backfill.backfill(tmp_path / "registry", root, client=FakeSEC(),
                              today=date(2026, 10, 10), days=365, max_new=8)
    assert len(first) == 2   # Hard limit, even if the caller requests eight
    folder = root / "wealth"
    assert backfill.existing_backfill_count(folder) == 2

    # Once 29 existing reports are marked as backfilled, only one slot remains.
    for i in range(27):
        (folder / f"stub{i}-earnings-fy2026.md").write_text(
            "---\\nhistorical_backfill: true\\n---\\nSample article\\n".replace("\\\\n", "\\n")
        )
    assert backfill.existing_backfill_count(folder) == 29
    final = backfill.backfill(tmp_path / "registry", root, client=FakeSEC(),
                              today=date(2026, 10, 11), days=365, max_new=8)
    assert len(final) == 1
    assert backfill.existing_backfill_count(folder) == 30
    assert backfill.backfill(tmp_path / "registry", root, client=FakeSEC(),
                             today=date(2026, 10, 12), days=365, max_new=8) == []
