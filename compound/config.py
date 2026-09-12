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
    draft_effort: str  # low | medium | high: thinking effort for drafts (questions/triage/topic run lower)
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
    interview: bool  # False = skip the questions and draft straight from the source
    min_relevance: int  # 0 = draft everything; otherwise items scoring below this (0-10) are skipped
    schedule_hours: int  # 0 = off; otherwise write one evergreen piece every N hours, rotating pillars
    schedule_pillars: tuple[str, ...]
    auto_publish: str  # off | verified | always
    topics_dir: Path
    # Source URLs (kept here so they can be pointed at a fixture server in tests)
    revenue_ebrief_index_url: str
    revenue_ebrief_rss_url: str


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=_env("TELEGRAM_BOT_TOKEN"),
        telegram_owner_id=_env_int("TELEGRAM_OWNER_ID", 0),
        anthropic_model=_env("ANTHROPIC_MODEL", "claude-opus-5"),
        draft_effort=(_env("DRAFT_EFFORT", "high").lower() if _env("DRAFT_EFFORT", "high").lower() in {"low", "medium", "high"} else "high"),
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
        interview=_env("INTERVIEW", "1") not in {"0", "false", "no"},
        min_relevance=max(0, min(10, _env_int("MIN_RELEVANCE", 6))),
        schedule_hours=max(0, _env_int("SCHEDULE_HOURS", 0)),
        schedule_pillars=tuple(
            x.strip().lower() for x in _env("SCHEDULE_PILLARS", "health,wealth,happiness").split(",") if x.strip()
        ),
        auto_publish=_env("AUTO_PUBLISH", "off").lower() or "off",
        topics_dir=ROOT / "topics",
        revenue_ebrief_index_url=_env(
            "REVENUE_EBRIEF_INDEX_URL", "https://www.revenue.ie/en/tax-professionals/ebrief/index.aspx"
        ),
        revenue_ebrief_rss_url=_env("REVENUE_EBRIEF_RSS_URL"),
    )
