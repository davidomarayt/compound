"""Offline release guards for resumable SEC-to-profile historical hydration."""
import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import earnings_historical_profiles as historical
from test_earnings import FILING, facts


def company(ticker, cik):
    return {"symbol": ticker, "name": ticker + " Inc.", "cik": cik, "active": True,
            "sector": "Technology", "symbols": [ticker]}


class FakeSEC:
    def __init__(self, unavailable=(), old_tickers=()):
        self.unavailable = set(unavailable)
        self.old_tickers = set(old_tickers)
        self.requests = []

    def get_json(self, url):
        self.requests.append(url)
        cik = int(url.split("CIK")[1].split(".json")[0])
        if cik in self.unavailable:
            raise RuntimeError("SEC temporarily unavailable")
        if "submissions/" in url:
            filing = dict(FILING)
            if cik in self.old_tickers:
                filing["filingDate"] = "2025-11-07"
                filing["reportDate"] = "2025-09-30"
            return {"filings": {"recent": {
                key: [filing[key]]
                for key in ("accessionNumber", "form", "filingDate", "reportDate", "primaryDocument")
            }}}
        return facts()


def members(monkeypatch):
    rows = [company("AAA", 100), company("BBB", 200),
            company("CCC", 300), company("DDD", 400)]
    monkeypatch.setattr(historical, "universe", lambda _: rows)
    return rows


def test_populates_existing_stock_profiles_and_persists_a_resume_cursor(tmp_path, monkeypatch):
    members(monkeypatch)
    folder = tmp_path / "content"
    state_path = folder / "earnings-backfill-state.json"
    source = FakeSEC(old_tickers={300})
    first = historical.backfill(tmp_path / "registry", folder, state_path,
                                client=source, now=date(2026, 10, 15), batch_size=2)
    assert first["cursor"] == 2
    assert first["created"] == 2
    assert (folder / "earnings-profiles" / "aaa.json").is_file()
    assert (folder / "earnings-profiles" / "bbb.json").is_file()
    assert not (folder / "wealth").exists()
    assert (folder / "earnings-profiles" / "aaa.json").read_text().count('"accession"') >= 1
    assert json.loads(state_path.read_text())["scanned"] == 2
    second = historical.backfill(tmp_path / "registry", folder, state_path,
                                 client=source, now=date(2026, 10, 15), batch_size=2)
    assert second["cursor"] == 4
    assert second["no_eligible_filing"] == 1
    assert second["created"] == 3
    assert second["completed"] is True
    calls = len(source.requests)
    third = historical.backfill(tmp_path / "registry", folder, state_path,
                                client=source, now=date(2026, 10, 15), batch_size=2)
    assert third == second
    assert len(source.requests) == calls


def test_dry_run_never_creates_profiles_or_advances_state(tmp_path, monkeypatch):
    members(monkeypatch)
    folder = tmp_path / "content"
    state = folder / "progress.json"
    trial = historical.backfill(tmp_path / "registry", folder, state,
                                client=FakeSEC(), now=date(2026, 10, 15), batch_size=2,
                                dry_run=True)
    assert trial["created"] == 2 and trial["cursor"] == 2
    assert not folder.exists()


def test_rate_limit_failures_abort_without_partially_writing(tmp_path, monkeypatch):
    rows = [company(str(i), i+1) for i in range(10)]
    monkeypatch.setattr(historical, "universe", lambda _: rows)
    folder = tmp_path / "content"
    state = folder / "state.json"
    with pytest.raises(RuntimeError, match="do not advance progress"):
        historical.backfill(tmp_path / "registry", folder, state,
                            client=FakeSEC(unavailable={1, 2, 3, 4, 5, 6}),
                            now=date(2026, 10, 15), batch_size=10)
    assert not state.exists()
    assert not (folder / "earnings-profiles").exists()


def test_failed_companies_retry_once_without_inventing_results(tmp_path, monkeypatch):
    members(monkeypatch)
    folder = tmp_path / "content"
    state = folder / "state.json"
    client = FakeSEC(unavailable={200})
    first = historical.backfill(tmp_path / "registry", folder, state,
                                client=client, now=date(2026, 10, 15), batch_size=4)
    assert first["cursor"] == 4 and not first["completed"]
    assert first["pending_retry"] == ["BBB"]
    assert not (folder / "earnings-profiles" / "bbb.json").exists()
    client.unavailable.clear()
    last = historical.backfill(tmp_path / "registry", folder, state,
                               client=client, now=date(2026, 10, 15), batch_size=4)
    assert last["completed"] and not last["pending_retry"]
    assert (folder / "earnings-profiles" / "bbb.json").exists()


def test_identity_mismatch_refuses_to_reassign_company_history(tmp_path, monkeypatch):
    members(monkeypatch)
    folder = tmp_path / "content"
    (folder / "earnings-profiles").mkdir(parents=True)
    (folder / "earnings-profiles" / "aaa.json").write_text(
        json.dumps({"ticker": "AAA", "cik": 9999, "periods": []}))
    with pytest.raises(ValueError, match="identity mismatch"):
        historical.backfill(tmp_path / "registry", folder, folder / "state.json",
                            client=FakeSEC(), now=date(2026, 10, 15), batch_size=1)
    assert not (folder / "state.json").exists()


def test_backfill_stays_capped_and_can_only_use_sec_q_or_k():
    assert historical.EARLIEST == date(2026, 1, 1)
    with pytest.raises(ValueError):
        historical.backfill(Path("not-used"), Path("not-used"), Path("not-used"),
                            client=None, now=date(2026,10,15), batch_size=41)
