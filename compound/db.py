"""SQLite storage. Plain sqlite3, one connection per process, explicit SQL.

Tables
------
sources    one row per polled source (last poll time, first-run flag)
items      a thing worth an article: a detected announcement or a manual /newpiece
questions  interview questions generated for an item
answers    the owner's answers (text or transcribed voice), bound to a question
drafts     generated articles, versioned per item; only one is "pending" at a time
published  the record of what went live and where
state      small key/value store for bot conversation state (active item, awaiting redraft notes)
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    key            TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    pillar         TEXT NOT NULL,
    last_polled_at TEXT,
    initialised    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_key    TEXT NOT NULL,
    external_id   TEXT NOT NULL,
    kind          TEXT NOT NULL DEFAULT 'news',      -- news | manual
    pillar        TEXT NOT NULL,                     -- wealth | health | happiness
    title         TEXT NOT NULL,
    url           TEXT,
    summary       TEXT,
    source_text   TEXT,                              -- fetched page text the LLM reads
    published_at  TEXT,
    discovered_at TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'new',       -- new | seen | skipped | questions_sent | drafting | pending | published | dropped | failed
    relevance     INTEGER,                          -- triage score 0-10, NULL until triaged
    triage_note   TEXT,                             -- one-line reason from triage
    angle         TEXT,                             -- everyday-reader angle carried into the draft
    UNIQUE (source_key, external_id)
);

CREATE TABLE IF NOT EXISTS questions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id   INTEGER NOT NULL REFERENCES items(id),
    ordinal   INTEGER NOT NULL,
    text      TEXT NOT NULL,
    skipped   INTEGER NOT NULL DEFAULT 0,
    telegram_message_id INTEGER
);

CREATE TABLE IF NOT EXISTS answers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id     INTEGER NOT NULL REFERENCES items(id),
    question_id INTEGER REFERENCES questions(id),   -- NULL = extra note not tied to a question
    kind        TEXT NOT NULL,                       -- text | voice
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drafts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id       INTEGER NOT NULL REFERENCES items(id),
    version       INTEGER NOT NULL,
    headline      TEXT NOT NULL,
    slug          TEXT NOT NULL,
    summary       TEXT NOT NULL,
    body_md       TEXT NOT NULL,
    figures_json  TEXT NOT NULL,
    sources_json  TEXT NOT NULL,
    tags_json     TEXT NOT NULL,
    email_cta     TEXT NOT NULL DEFAULT '',
    verification_json TEXT NOT NULL DEFAULT '[]',
    preview_token TEXT NOT NULL,
    redraft_notes TEXT,
    status        TEXT NOT NULL DEFAULT 'pending',   -- pending | approved | rejected | superseded
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS published (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id     INTEGER NOT NULL REFERENCES drafts(id),
    item_id      INTEGER NOT NULL REFERENCES items(id),
    path         TEXT NOT NULL,                      -- content file path
    url          TEXT NOT NULL,
    approved_by  TEXT NOT NULL,
    published_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self._migrate()

    def _migrate(self) -> None:
        """Columns added after the first release; CREATE TABLE IF NOT EXISTS does not add them to old files."""
        have = {r["name"] for r in self.conn.execute("PRAGMA table_info(items)")}
        for col, typ in (("relevance", "INTEGER"), ("triage_note", "TEXT"), ("angle", "TEXT")):
            if col not in have:
                self.conn.execute(f"ALTER TABLE items ADD COLUMN {col} {typ}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # -- generic helpers ---------------------------------------------------
    def _one(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, tuple(params)).fetchone()

    def _all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchall()

    # -- sources -----------------------------------------------------------
    def ensure_source(self, key: str, name: str, pillar: str) -> sqlite3.Row:
        self.conn.execute(
            "INSERT OR IGNORE INTO sources (key, name, pillar) VALUES (?, ?, ?)", (key, name, pillar)
        )
        self.conn.commit()
        return self._one("SELECT * FROM sources WHERE key = ?", (key,))

    def mark_source_polled(self, key: str, initialised: bool = True) -> None:
        self.conn.execute(
            "UPDATE sources SET last_polled_at = ?, initialised = ? WHERE key = ?",
            (utcnow(), 1 if initialised else 0, key),
        )
        self.conn.commit()

    # -- items -------------------------------------------------------------
    def item_exists(self, source_key: str, external_id: str) -> bool:
        return self._one("SELECT 1 FROM items WHERE source_key = ? AND external_id = ?", (source_key, external_id)) is not None

    def insert_item(
        self,
        *,
        source_key: str,
        external_id: str,
        pillar: str,
        title: str,
        url: str | None,
        summary: str | None,
        published_at: str | None,
        kind: str = "news",
        status: str = "new",
        source_text: str | None = None,
    ) -> int:
        cur = self.conn.execute(
            """INSERT INTO items (source_key, external_id, kind, pillar, title, url, summary, source_text,
                                  published_at, discovered_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (source_key, external_id, kind, pillar, title, url, summary, source_text, published_at, utcnow(), status),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_item(self, item_id: int) -> sqlite3.Row | None:
        return self._one("SELECT * FROM items WHERE id = ?", (item_id,))

    def set_item_status(self, item_id: int, status: str) -> None:
        self.conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
        self.conn.commit()

    def set_triage(self, item_id: int, score: int, note: str, angle: str) -> None:
        self.conn.execute(
            "UPDATE items SET relevance = ?, triage_note = ?, angle = ? WHERE id = ?", (score, note, angle, item_id)
        )
        self.conn.commit()

    def set_item_source_text(self, item_id: int, text: str) -> None:
        self.conn.execute("UPDATE items SET source_text = ? WHERE id = ?", (text, item_id))
        self.conn.commit()

    def items_with_status(self, *statuses: str) -> list[sqlite3.Row]:
        marks = ",".join("?" for _ in statuses)
        return self._all(f"SELECT * FROM items WHERE status IN ({marks}) ORDER BY id", statuses)

    def open_items(self) -> list[sqlite3.Row]:
        """Everything the owner may still need to act on."""
        return self.items_with_status("new", "questions_sent", "drafting", "pending", "failed")

    # -- questions / answers ---------------------------------------------
    def add_questions(self, item_id: int, texts: list[str]) -> list[int]:
        ids = []
        for i, t in enumerate(texts, start=1):
            cur = self.conn.execute(
                "INSERT INTO questions (item_id, ordinal, text) VALUES (?, ?, ?)", (item_id, i, t)
            )
            ids.append(int(cur.lastrowid))
        self.conn.commit()
        return ids

    def set_question_message_id(self, question_id: int, message_id: int) -> None:
        self.conn.execute("UPDATE questions SET telegram_message_id = ? WHERE id = ?", (message_id, question_id))
        self.conn.commit()

    def questions_for(self, item_id: int) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM questions WHERE item_id = ? ORDER BY ordinal", (item_id,))

    def question_by_message_id(self, message_id: int) -> sqlite3.Row | None:
        return self._one("SELECT * FROM questions WHERE telegram_message_id = ?", (message_id,))

    def answers_for(self, item_id: int) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM answers WHERE item_id = ? ORDER BY id", (item_id,))

    def answered_question_ids(self, item_id: int) -> set[int]:
        rows = self._all(
            "SELECT DISTINCT question_id FROM answers WHERE item_id = ? AND question_id IS NOT NULL", (item_id,)
        )
        return {int(r["question_id"]) for r in rows}

    def next_unanswered_question(self, item_id: int) -> sqlite3.Row | None:
        answered = self.answered_question_ids(item_id)
        for q in self.questions_for(item_id):
            if q["id"] not in answered and not q["skipped"]:
                return q
        return None

    def skip_question(self, question_id: int) -> None:
        self.conn.execute("UPDATE questions SET skipped = 1 WHERE id = ?", (question_id,))
        self.conn.commit()

    def add_answer(self, item_id: int, question_id: int | None, kind: str, text: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO answers (item_id, question_id, kind, text, created_at) VALUES (?, ?, ?, ?, ?)",
            (item_id, question_id, kind, text, utcnow()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    # -- drafts ------------------------------------------------------------
    def add_draft(
        self,
        *,
        item_id: int,
        headline: str,
        slug: str,
        summary: str,
        body_md: str,
        figures: list[dict],
        sources: list[dict],
        tags: list[str],
        email_cta: str,
        verification: list[dict],
        preview_token: str,
        redraft_notes: str | None = None,
    ) -> int:
        # Any earlier pending draft for this item is superseded by the new one.
        self.conn.execute(
            "UPDATE drafts SET status = 'superseded' WHERE item_id = ? AND status = 'pending'", (item_id,)
        )
        row = self._one("SELECT COALESCE(MAX(version), 0) AS v FROM drafts WHERE item_id = ?", (item_id,))
        version = int(row["v"]) + 1
        cur = self.conn.execute(
            """INSERT INTO drafts (item_id, version, headline, slug, summary, body_md, figures_json, sources_json,
                                   tags_json, email_cta, verification_json, preview_token, redraft_notes, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (
                item_id, version, headline, slug, summary, body_md,
                json.dumps(figures, ensure_ascii=False), json.dumps(sources, ensure_ascii=False),
                json.dumps(tags, ensure_ascii=False), email_cta, json.dumps(verification, ensure_ascii=False),
                preview_token, redraft_notes, utcnow(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_draft(self, draft_id: int) -> sqlite3.Row | None:
        return self._one("SELECT * FROM drafts WHERE id = ?", (draft_id,))

    def pending_draft_for_item(self, item_id: int) -> sqlite3.Row | None:
        return self._one(
            "SELECT * FROM drafts WHERE item_id = ? AND status = 'pending' ORDER BY version DESC LIMIT 1", (item_id,)
        )

    def latest_draft_for_item(self, item_id: int) -> sqlite3.Row | None:
        return self._one("SELECT * FROM drafts WHERE item_id = ? ORDER BY version DESC LIMIT 1", (item_id,))

    def pending_drafts(self) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM drafts WHERE status = 'pending' ORDER BY id")

    def set_draft_status(self, draft_id: int, status: str) -> None:
        self.conn.execute("UPDATE drafts SET status = ? WHERE id = ?", (status, draft_id))
        self.conn.commit()

    def draft_by_preview_token(self, token: str) -> sqlite3.Row | None:
        return self._one("SELECT * FROM drafts WHERE preview_token = ?", (token,))

    def slug_taken(self, slug: str) -> bool:
        return self._one("SELECT 1 FROM published p JOIN drafts d ON d.id = p.draft_id WHERE d.slug = ?", (slug,)) is not None

    # -- published ---------------------------------------------------------
    def record_published(self, draft_id: int, item_id: int, path: str, url: str, approved_by: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO published (draft_id, item_id, path, url, approved_by, published_at) VALUES (?, ?, ?, ?, ?, ?)",
            (draft_id, item_id, path, url, approved_by, utcnow()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def published_for_item(self, item_id: int) -> sqlite3.Row | None:
        return self._one("SELECT * FROM published WHERE item_id = ? ORDER BY id DESC LIMIT 1", (item_id,))

    # -- state -------------------------------------------------------------
    def get_state(self, key: str, default: str | None = None) -> str | None:
        row = self._one("SELECT value FROM state WHERE key = ?", (key,))
        return row["value"] if row else default

    def set_state(self, key: str, value: str | None) -> None:
        if value is None:
            self.conn.execute("DELETE FROM state WHERE key = ?", (key,))
        else:
            self.conn.execute(
                "INSERT INTO state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
        self.conn.commit()


def loads_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return val if isinstance(val, list) else []
