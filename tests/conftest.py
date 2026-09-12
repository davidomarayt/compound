import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def settings(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPOUND_DB", str(tmp_path / "db.sqlite3"))
    monkeypatch.setenv("COMPOUND_CONTENT_DIR", str(tmp_path / "content"))
    monkeypatch.setenv("COMPOUND_PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setenv("COMPOUND_FAKE_LLM", "1")
    monkeypatch.setenv("SITE_BASE_URL", "https://example.test")
    monkeypatch.setenv("PREVIEW_BASE_URL", "https://example.test")
    monkeypatch.setenv("FIRST_RUN_BACKFILL", "1")
    monkeypatch.setenv("DEPLOY_COMMAND", "")
    monkeypatch.setenv("STT_PROVIDER", "none")
    from compound.config import load_settings

    s = load_settings()
    (s.content_dir / "pages").mkdir(parents=True)
    (s.content_dir / "pages" / "about.md").write_text("---\ntitle: About\n---\nHello.\n")
    return s
