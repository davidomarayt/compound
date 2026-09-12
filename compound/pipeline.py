"""The workflow, independent of Telegram so it can be driven from the CLI and tests.

  item (new) --questions--> questions_sent --answers--> drafting --draft--> pending
  pending --approve--> published        pending --redraft--> pending (new version)
  any --drop--> dropped

There is exactly one function that writes to the content directory: publish(). It requires an
approved_by string and a pending draft. Nothing calls it except a human action.
"""
from __future__ import annotations

import logging
import secrets
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from compound.config import Settings
from compound.db import Database, loads_list
from compound.llm import Triage, LLM, ArticleDraft, LLMError
from compound.poller import load_source_text
from compound.site.build import Article, build_site, remove_preview, render_markdown, render_preview
from compound.sources import Source
from compound.verify import unlisted_numbers, verify_figures

log = logging.getLogger(__name__)
N_QUESTIONS = 3


@dataclass
class Pipeline:
    settings: Settings
    db: Database
    llm: LLM
    sources: list[Source]

    def source_for(self, key: str) -> Source | None:
        return next((s for s in self.sources if s.key == key), None)

    # -- questions ---------------------------------------------------------
    def triage(self, item_id: int) -> Triage:
        """Score the item for the everyday reader and store the result. Cheap; runs before any draft."""
        item = self.db.get_item(item_id)
        if item is None:
            raise ValueError(f"no item {item_id}")
        source_text = self.ensure_source_text(item_id)
        try:
            t = self.llm.generate_triage(
                kind=item["kind"], pillar=item["pillar"], title=item["title"], url=item["url"] or "", source_text=source_text,
            )
        except LLMError:
            self.db.set_item_status(item_id, "failed")
            raise
        self.db.set_triage(item_id, t.score, t.reason, t.angle)
        if t.summary and not item["summary"]:
            self.db.conn.execute("UPDATE items SET summary = ? WHERE id = ?", (t.summary, item_id))
            self.db.conn.commit()
        return t

    def needs_triage(self, item_id: int) -> bool:
        item = self.db.get_item(item_id)
        return bool(item) and self.settings.min_relevance > 0 and item["kind"] == "news" and item["relevance"] is None

    def skip(self, item_id: int) -> None:
        self.db.set_item_status(item_id, "skipped")

    def prepare_questions(self, item_id: int) -> list[int]:
        """Fetch the source page, generate questions, store them. Returns question ids."""
        item = self.db.get_item(item_id)
        if item is None:
            raise ValueError(f"no item {item_id}")
        source_text = self.ensure_source_text(item_id)
        try:
            qs = self.llm.generate_questions(
                kind=item["kind"], pillar=item["pillar"], title=item["title"], url=item["url"] or "",
                source_text=source_text, n_questions=N_QUESTIONS,
            )
        except LLMError:
            self.db.set_item_status(item_id, "failed")
            raise
        if qs.summary and not item["summary"]:
            self.db.conn.execute("UPDATE items SET summary = ? WHERE id = ?", (qs.summary, item_id))
            self.db.conn.commit()
        ids = self.db.add_questions(item_id, qs.questions)
        self.db.set_item_status(item_id, "questions_sent")
        return ids

    def ensure_source_text(self, item_id: int) -> str:
        """The item's cached page text, fetching it first if a news item has none yet."""
        item = self.db.get_item(item_id)
        source_text = item["source_text"] or ""
        if not source_text and item["kind"] == "news":
            src = self.source_for(item["source_key"])
            if src is not None:
                source_text = load_source_text(self.db, src, item_id)
        return source_text

    def create_manual_item(self, topic: str, pillar: str) -> int:
        ext = f"manual-{secrets.token_hex(4)}"
        return self.db.insert_item(
            source_key="manual", external_id=ext, pillar=pillar, title=topic, url=None, summary=None,
            published_at=None, kind="manual", status="new",
        )

    # -- answers -----------------------------------------------------------
    def record_answer(self, item_id: int, text: str, kind: str, question_id: int | None = None) -> tuple[int | None, int, int]:
        """Store an answer. Binds to question_id, else the next unanswered question, else an extra note.
        Returns (bound question ordinal or None, answered_count, total_questions)."""
        qs = self.db.questions_for(item_id)
        target = None
        if question_id is not None:
            target = next((q for q in qs if q["id"] == question_id), None)
        if target is None:
            target = self.db.next_unanswered_question(item_id)
        self.db.add_answer(item_id, target["id"] if target else None, kind, text)
        answered = len(self.db.answered_question_ids(item_id))
        return (target["ordinal"] if target else None), answered, len(qs)

    def all_answered(self, item_id: int) -> bool:
        return self.db.next_unanswered_question(item_id) is None and bool(self.db.questions_for(item_id))

    def interview(self, item_id: int) -> list[tuple[str, str]]:
        answers = self.db.answers_for(item_id)
        by_q: dict[int, list[str]] = {}
        extras: list[str] = []
        for a in answers:
            if a["question_id"] is None:
                extras.append(a["text"])
            else:
                by_q.setdefault(int(a["question_id"]), []).append(a["text"])
        out = [(q["text"], " ".join(by_q.get(int(q["id"]), []))) for q in self.db.questions_for(item_id)]
        if extras:
            out.append(("Anything else David added:", " ".join(extras)))
        return out

    # -- drafting ----------------------------------------------------------
    def make_draft(self, item_id: int, redraft_notes: str | None = None) -> int:
        item = self.db.get_item(item_id)
        if item is None:
            raise ValueError(f"no item {item_id}")
        self.db.set_item_status(item_id, "drafting")
        previous = self.db.latest_draft_for_item(item_id)
        prev_md = None
        if previous is not None and redraft_notes:
            prev_md = f"# {previous['headline']}\n\n{previous['summary']}\n\n{previous['body_md']}"
        source_text = self.ensure_source_text(item_id)
        try:
            draft = self.llm.generate_draft(
                kind=item["kind"], pillar=item["pillar"], title=item["title"], url=item["url"] or "",
                summary=item["summary"] or "", source_text=source_text, interview=self.interview(item_id),
                angle=item["angle"] or "", previous_draft=prev_md, redraft_notes=redraft_notes,
            )
        except LLMError:
            self.db.set_item_status(item_id, "failed")
            raise
        verification = verify_figures(draft, source_text)
        token = secrets.token_urlsafe(12)
        draft_id = self.db.add_draft(
            item_id=item_id, headline=draft.headline, slug=draft.slug, summary=draft.summary,
            body_md=draft.body_markdown, figures=[f.model_dump() for f in draft.figures],
            sources=[s.model_dump() for s in draft.sources], tags=draft.tags, email_cta=draft.email_cta,
            verification=verification, preview_token=token, redraft_notes=redraft_notes,
        )
        if previous is not None:
            remove_preview(self.settings, previous["preview_token"])
        render_preview(self.settings, token, self._article_from_draft(self.db.get_draft(draft_id), item))
        self.db.set_item_status(item_id, "pending")
        return draft_id

    def preview_url(self, draft_row) -> str:
        return f"{self.settings.preview_base_url}/preview/{draft_row['preview_token']}/"

    def _article_from_draft(self, d, item, slug: str | None = None) -> Article:
        return Article(
            title=d["headline"], slug=slug or d["slug"], pillar=item["pillar"], date=date.today(),
            summary=d["summary"], body_html=render_markdown(d["body_md"]), tags=loads_list(d["tags_json"]),
            sources=loads_list(d["sources_json"]), figures=loads_list(d["figures_json"]), email_cta=d["email_cta"],
        )

    def draft_warnings(self, d) -> list[str]:
        """Human-readable warnings for the review message."""
        warnings: list[str] = []
        for v in loads_list(d["verification_json"]):
            if v.get("owner_supplied"):
                continue
            if v.get("in_source") is False:
                warnings.append(f"{v['value']} ({v['label']}): quote not found in source")
            elif v.get("in_source") is None:
                warnings.append(f"{v['value']} ({v['label']}): quote not verbatim, check it")
            if not v.get("in_body"):
                warnings.append(f"{v['value']} listed but not used in body")
        try:
            fake = ArticleDraft(
                headline=d["headline"], slug=d["slug"], summary=d["summary"], body_markdown=d["body_md"],
                figures=loads_list(d["figures_json"]), sources=loads_list(d["sources_json"]),
                tags=loads_list(d["tags_json"]), email_cta=d["email_cta"],
            )
            extra = unlisted_numbers(fake)
            if extra:
                warnings.append("numbers in body with no figure entry: " + ", ".join(extra))
        except Exception:  # verification must never block review
            log.exception("unlisted_numbers failed")
        return warnings

    # -- decisions ---------------------------------------------------------
    def drop(self, item_id: int) -> None:
        d = self.db.pending_draft_for_item(item_id)
        if d is not None:
            self.db.set_draft_status(d["id"], "rejected")
            remove_preview(self.settings, d["preview_token"])
        self.db.set_item_status(item_id, "dropped")

    def publish(self, draft_id: int, *, approved_by: str) -> str:
        """The only path to the content directory. Requires a pending draft and a named approver."""
        if not approved_by:
            raise PermissionError("publish requires approved_by")
        d = self.db.get_draft(draft_id)
        if d is None or d["status"] != "pending":
            raise ValueError("draft is not pending")
        item = self.db.get_item(d["item_id"])
        slug = d["slug"]
        pillar_dir = self.settings.content_dir / item["pillar"]
        pillar_dir.mkdir(parents=True, exist_ok=True)
        n = 2
        while (pillar_dir / f"{slug}.md").exists():
            slug = f"{d['slug']}-{n}"
            n += 1
        meta = {
            "title": d["headline"], "slug": slug, "pillar": item["pillar"], "date": date.today().isoformat(),
            "summary": d["summary"], "tags": loads_list(d["tags_json"]), "sources": loads_list(d["sources_json"]),
            "figures": loads_list(d["figures_json"]), "email_cta": d["email_cta"],
            "item_id": item["id"], "draft_id": d["id"], "approved_by": approved_by,
        }
        front = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
        path = pillar_dir / f"{slug}.md"
        path.write_text(f"---\n{front}---\n\n{d['body_md'].strip()}\n", encoding="utf-8")

        url = f"{self.settings.site_base_url}/{item['pillar']}/{slug}/"
        self.db.set_draft_status(draft_id, "approved")
        self.db.record_published(draft_id, item["id"], str(path), url, approved_by)
        self.db.set_item_status(item["id"], "published")
        remove_preview(self.settings, d["preview_token"])
        build_site(self.settings)
        self._deploy()
        return url

    def _deploy(self) -> None:
        cmd = self.settings.deploy_command
        if not cmd:
            return
        try:
            subprocess.run(cmd, shell=True, check=True, timeout=300)
        except Exception:
            log.exception("deploy command failed")
            raise
