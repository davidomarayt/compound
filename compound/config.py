"""Settings loaded from environment / .env. One place, no magic."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    return int(raw) if raw else default


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_owner_id: int  # 0 = not yet configured; bot will tell you your id on /start
    anthropic_model: str
    fake_llm: bool
    stt_provider: str
    stt_api_key: str
    stt_base_url: str
    stt_model: str
    db_path: Path
    content_dir: Path
    public_dir: Path
    style_dir: Path
    site_base_url: str
    preview_base_url: str
    email_form_action: str
    deploy_command: str
    poll_interval_minutes: int
    first_run_backfill: int
    # Source URLs (kept here so they can be pointed at a fixture server in tests)
    revenue_ebrief_index_url: str
    revenue_ebrief_rss_url: str


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=_env("TELEGRAM_BOT_TOKEN"),
        telegram_owner_id=_env_int("TELEGRAM_OWNER_ID", 0),
        anthropic_model=_env("ANTHROPIC_MODEL", "claude-opus-5"),
        fake_llm=_env("COMPOUND_FAKE_LLM", "0") in {"1", "true", "yes"},
        stt_provider=_env("STT_PROVIDER", "none").lower(),
        stt_api_key=_env("STT_API_KEY"),
        stt_base_url=_env("STT_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        stt_model=_env("STT_MODEL", "whisper-1"),
        db_path=Path(_env("COMPOUND_DB", str(ROOT / "data" / "compound.sqlite3"))),
        content_dir=Path(_env("COMPOUND_CONTENT_DIR", str(ROOT / "content"))),
        public_dir=Path(_env("COMPOUND_PUBLIC_DIR", str(ROOT / "public"))),
        style_dir=ROOT / "style",
        site_base_url=_env("SITE_BASE_URL", "http://localhost:8080").rstrip("/"),
        preview_base_url=_env("PREVIEW_BASE_URL", _env("SITE_BASE_URL", "http://localhost:8080")).rstrip("/"),
        email_form_action=_env("EMAIL_FORM_ACTION"),
        deploy_command=_env("DEPLOY_COMMAND"),
        poll_interval_minutes=_env_int("POLL_INTERVAL_MINUTES", 30),
        first_run_backfill=_env_int("FIRST_RUN_BACKFILL", 1),
        revenue_ebrief_index_url=_env(
            "REVENUE_EBRIEF_INDEX_URL", "https://www.revenue.ie/en/tax-professionals/ebrief/index.aspx"
        ),
        revenue_ebrief_rss_url=_env("REVENUE_EBRIEF_RSS_URL"),
    )
