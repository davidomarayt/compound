"""A blocked assignment must be observable without bypassing editorial gates."""
from datetime import date, datetime, timezone
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import mag7_autopublish as publisher


@pytest.mark.parametrize("key", [None, "   "])
def test_missing_key_fails_before_research(monkeypatch, tmp_path, key):
    if key is None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    else:
        monkeypatch.setenv("ANTHROPIC_API_KEY", key)
    def forbidden(*args):
        pytest.fail("Research must not start without a credential")
    monkeypatch.setattr(publisher.pilot, "latest_sec", forbidden)
    report = tmp_path / "audit.md"
    assert publisher.run(date(2026, 10, 17), report) == 1
    assert "secret missing" in report.read_text()


def test_editor_rejection_never_reaches_article(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-placeholder-not-a-credential")
    monkeypatch.setattr(publisher.pilot, "latest_sec", lambda *args: {})
    monkeypatch.setattr(publisher, "photo_for", lambda *args: {})
    monkeypatch.setattr(publisher, "research", lambda *args: {})
    monkeypatch.setattr(publisher, "validate", lambda *args: None)
    def reject(*args):
        raise ValueError("Independent review failed")
    monkeypatch.setattr(publisher, "independent_review", reject)
    monkeypatch.setattr(publisher, "article", lambda *args: pytest.fail("Rejected article published"))
    report = tmp_path / "audit.md"
    assert publisher.run(date(2026, 10, 18), report) == 1
    assert "Independent review failed" in report.read_text()


def test_recovery_keeps_assignment_but_does_not_backdate(monkeypatch, tmp_path):
    monkeypatch.setattr(publisher, "ROOT", tmp_path)
    (tmp_path / "content/wealth").mkdir(parents=True)
    monkeypatch.setattr(publisher, "fetch_real_photo", lambda *args: None)
    data = dict(title="Recovery test", summary="Summary", meta_description="Description",
                body_markdown="Body", sources=[])
    photo = dict(alt="Microsoft building", credit="Photographer / Unsplash", year="2022",
                 source="https://unsplash.com/photos/example")
    path, _, slug = publisher.article(date(2026, 10, 17), "MSFT", 1, data, photo)
    metadata = publisher.yaml.safe_load(path.read_text().split("---", 2)[1])
    assert metadata["assignment_date"] == "2026-10-17"
    assert metadata["date"] == datetime.now(timezone.utc).date().isoformat()
    assert slug.endswith("2026-10-17")
