"""The workflow, independent of Telegram so it can be driven from the CLI and tests.

  item (new) --questions--> questions_sent --answers--> drafting --draft--> pending
  pending --approve--> published        pending --redraft--> pending (new version)
  any --drop--> dropped

There is exactly one function that writes to the content directory: publish(). It requires an
approved_by string and a pending draft. Nothing calls it except a human action.
"""
from __future__ import annotations

import json

import logging
import re
import secrets
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from compound.config import Settings
from compound.db import utcnow, Database, loads_list
from compound.llm import Triage, LLM, ArticleDraft, LLMError, TopicPlan
from compound.research import ResearchPack, build_pack, suggestions
from compound.poller import load_source_text
from compound.site.build import Article, build_site, remove_preview, render_markdown, render_preview
from compound.sources import Source
from compound.verify import unlisted_numbers, verify_charts, verify_figures

log = logging.getLogger(__name__)
N_QUESTIONS = 3


@dataclass
class Pipeline:
    settings: Settings
    db: Database
    llm: LLM
    sources: list[Source]

    def fetch_page_text(self, url: str) -> str:
        """Fetch a cited page as readable text. Replaced in tests."""
        from compound.sources.base import html_to_text, http_get

        return html_to_text(http_get(url))

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
            out.append(("Anything else the owner added:", " ".join(extras)))
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
        plan = self.item_plan(item_id)
        try:
            draft = self.llm.generate_draft(
                kind=item["kind"], pillar=item["pillar"], title=item["title"], url=item["url"] or "",
                summary=item["summary"] or "", source_text=source_text, interview=self.interview(item_id),
                angle=item["angle"] or "", seo=self.seo_block(plan, (item["research_notes"] if "research_notes" in item.keys() else "") or ""),
                previous_draft=prev_md, redraft_notes=redraft_notes,
            )
        except LLMError:
            self.db.set_item_status(item_id, "failed")
            raise
        pack = ResearchPack.from_json(item["research_json"])
        page_texts = pack.page_texts()
        page_texts.update(self.fetch_cited_pages(draft, item["url"] or "", skip=set(page_texts)))
        verification = verify_figures(draft, source_text, page_texts)
        charts, chart_warnings = verify_charts(draft, verification)
        for w in chart_warnings:
            log.warning("draft chart dropped: %s", w)
        token = secrets.token_urlsafe(12)
        draft_id = self.db.add_draft(
            item_id=item_id, headline=draft.headline, slug=draft.slug, summary=draft.summary,
            body_md=draft.body_markdown, figures=[f.model_dump() for f in draft.figures],
            sources=[s.model_dump() for s in draft.sources], tags=draft.tags, email_cta=draft.email_cta,
            verification=verification, preview_token=token, redraft_notes=redraft_notes,
        )
        if charts:
            self.db.set_draft_field(draft_id, "charts_json", json.dumps(charts, ensure_ascii=False))
        if draft.meta_description or (plan and plan.meta_description):
            self.db.set_draft_field(draft_id, "meta_description", (draft.meta_description or plan.meta_description).strip()[:160])
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
            meta_description=(d["meta_description"] if "meta_description" in d.keys() else "") or "",
            charts=loads_list(d["charts_json"]) if "charts_json" in d.keys() and d["charts_json"] else [],
        )

    MAX_CITED_PAGES = 6

    def fetch_cited_pages(self, draft, item_url: str, skip: set[str] | None = None) -> dict[str, str]:
        """Text of every distinct page the draft's figures cite (other than the item's own page and
        'owner'), so each quote can be checked against the page it claims. Failed fetches map to ''."""
        urls: list[str] = []
        for f in draft.figures:
            u = (f.source_url or "").strip()
            if u and u.lower() != "owner" and u != item_url and u.startswith("http") and u not in urls and u not in (skip or set()):
                urls.append(u)
        out: dict[str, str] = {}
        for u in urls[: self.MAX_CITED_PAGES]:
            try:
                out[u] = self.fetch_page_text(u)
            except Exception as e:  # noqa: BLE001 - an unreachable citation is a finding, not a crash
                log.warning("could not fetch cited page %s: %s: %s", u, type(e).__name__, str(e)[:200])
                out[u] = ""
        return out

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

    # -- scheduled evergreen writing --------------------------------------
    SCHEDULE_PILLAR_KEY = "schedule_pillar_index"
    SCHEDULE_LAST_KEY = "schedule_last_run"

    def next_pillar(self) -> str:
        """Rotate through settings.schedule_pillars, remembering position across restarts."""
        pillars = self.settings.schedule_pillars or ("health", "wealth", "happiness")
        idx = int(self.db.get_state(self.SCHEDULE_PILLAR_KEY, "0") or 0) % len(pillars)
        self.db.set_state(self.SCHEDULE_PILLAR_KEY, str(idx + 1))
        return pillars[idx]

    def recent_titles(self, pillar: str, limit: int = 40) -> list[str]:
        rows = self.db._all(
            "SELECT title FROM items WHERE pillar = ? AND status NOT IN ('dropped', 'skipped', 'seen') ORDER BY id DESC LIMIT ?",
            (pillar, limit),
        )
        return [r["title"] for r in rows]

    def bank_topic(self, pillar: str) -> str:
        """First unused line of topics/<pillar>.md, else ''."""
        used = {t.strip().lower() for t in self.recent_titles(pillar, limit=1000)}
        bank = self.settings.topics_dir / f"{pillar}.md"
        if bank.exists():
            for ln in bank.read_text(encoding="utf-8").splitlines():
                t = ln.strip()
                if t and not t.startswith("#") and t.lower() not in used:
                    return t
        return ""

    DEFAULT_SEEDS = {
        "wealth": ["tax credit ireland", "how to claim ireland", "grant ireland 2026", "pension ireland", "renting ireland"],
        "health": ["is it bad to", "how much sleep", "vitamin d ireland", "how to lower", "is it normal to"],
        "happiness": ["how to stop worrying", "loneliness ireland", "how to be happier", "burnout", "how to make friends as an adult"],
    }

    def seeds(self, pillar: str) -> list[str]:
        f = self.settings.topics_dir / "seeds" / f"{pillar}.md"
        if f.exists():
            lines = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines()]
            lines = [ln for ln in lines if ln and not ln.startswith("#")]
            if lines:
                return lines
        return self.DEFAULT_SEEDS.get(pillar, [])

    def search_suggestions(self, pillar: str) -> list[str]:
        """Real autocomplete completions for this pillar's seed phrases (best effort, deduped)."""
        out: list[str] = []
        for seed in self.seeds(pillar)[:6]:
            for q in self.fetch_suggestions(seed):
                if q not in out:
                    out.append(q)
        return out[:40]

    def fetch_suggestions(self, seed: str) -> list[str]:
        """Replaced in tests."""
        return suggestions(seed)

    def plan_topic(self, pillar: str, fixed_title: str | None = None) -> TopicPlan:
        return self.llm.generate_plan(
            pillar=pillar, recent_titles=self.recent_titles(pillar), suggestions=self.search_suggestions(pillar),
            fixed_title=fixed_title if fixed_title is not None else self.bank_topic(pillar),
        )

    def item_plan(self, item_id: int) -> TopicPlan | None:
        item = self.db.get_item(item_id)
        raw = item["plan_json"] if item is not None and "plan_json" in item.keys() else None
        return TopicPlan.model_validate_json(raw) if raw else None

    @staticmethod
    def seo_block(plan: TopicPlan | None, notes: str = "") -> str:
        if plan is None:
            return ""
        qs = "\n".join(f"- {q}" for q in plan.questions)
        block = (
            f"Target search query: {plan.target_query}\nAnswer it directly in the first two paragraphs.\n"
            f"Use these questions as the subheadings, in this order:\n{qs}\n"
            f"Suggested meta description: {plan.meta_description}"
        )
        if notes.strip():
            block += (
                "\n\n## Research notes\nThe researcher read the sources below and reported this. Use it to decide what "
                "to say and how strongly; every figure must still be quoted from the source text itself.\n" + notes.strip()
            )
        return block

    def research(self, pillar: str, plan: TopicPlan) -> tuple[ResearchPack, str]:
        """Deep research (Claude with web search, when the backend has it) plus the planner's
        queries and URLs, fetched into a pack. Returns (pack, research notes for the writer)."""
        notes = ""
        pubmed_ids: list[str] = []
        urls = list(plan.source_urls)
        if self.settings.deep_research:
            try:
                report = self.llm.research_topic(pillar=pillar, plan=plan)
            except LLMError as e:
                log.warning("deep research failed, continuing with the planner's sources: %s", e)
                report = None
            if report is not None and (report.findings or report.sources or report.pubmed_ids):
                notes = report.notes()
                pubmed_ids = list(report.pubmed_ids)
                for src in report.sources:
                    if src.url not in urls:
                        urls.append(src.url)
                for f in report.findings:
                    if f.source_url not in urls:
                        urls.append(f.source_url)
                if report.suggested_structure:
                    plan.questions = report.suggested_structure[:7]
        # PubMed pages are fetched as abstracts by ID, not as HTML
        for u in list(urls):
            m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", u)
            if m:
                urls.remove(u)
                if m.group(1) not in pubmed_ids:
                    pubmed_ids.append(m.group(1))
        pack = build_pack(
            pubmed_queries=plan.pubmed_queries, urls=urls, fetch_page=self.fetch_page_text,
            pubmed_max=self.settings.pubmed_max, max_sources=16, pubmed_ids=pubmed_ids,
        )
        return pack, notes

    def create_planned_item(self, pillar: str, plan: TopicPlan, pack: ResearchPack, notes: str = "") -> int:
        item_id = self.create_manual_item(plan.title, pillar)
        self.db.set_item_field(item_id, "summary", plan.brief)
        self.db.set_item_field(item_id, "angle", plan.brief)
        self.db.set_item_field(item_id, "plan_json", plan.model_dump_json())
        self.db.set_item_field(item_id, "research_json", pack.to_json())
        self.db.set_item_field(item_id, "research_notes", notes)
        if pack.sources:
            self.db.set_item_source_text(item_id, pack.source_text())
        return item_id

    def editor_pass(self, item_id: int, draft_id: int) -> dict | None:
        """Review the draft; if it must be revised, redraft once with the editor's notes. Returns the
        final review dict (score, verdict, must_fix, notes) or None when the editor is off."""
        if self.settings.editor_min_score <= 0:
            return None
        item = self.db.get_item(item_id)
        plan = self.item_plan(item_id)
        d = self.db.get_draft(draft_id)
        review = self._review(item, plan, d)
        if review["verdict"] == "publish" and review["score"] >= self.settings.editor_min_score:
            return review
        notes = "Editor review (score {}/10). Fix all of these:\n- {}".format(
            review["score"], "\n- ".join(review["must_fix"] + review["notes"])
        )
        new_id = self.make_draft(item_id, redraft_notes=notes)
        review2 = self._review(item, plan, self.db.get_draft(new_id))
        review2["revised_from"] = draft_id
        return review2

    def _review(self, item, plan, d) -> dict:
        draft = ArticleDraft(
            headline=d["headline"], slug=d["slug"], summary=d["summary"], body_markdown=d["body_md"],
            figures=loads_list(d["figures_json"]), sources=loads_list(d["sources_json"]),
            tags=loads_list(d["tags_json"]), email_cta=d["email_cta"],
        )
        r = self.llm.review_draft(
            pillar=item["pillar"], target_query=plan.target_query if plan else "", questions=plan.questions if plan else [],
            draft=draft, source_text=item["source_text"] or "",
        )
        out = r.model_dump()
        self.db.set_draft_field(d["id"], "editor_json", json.dumps(out, ensure_ascii=False))
        return out

    def auto_publishable(self, d) -> bool:
        mode = self.settings.auto_publish
        if mode == "always":
            return True
        if mode == "verified":
            return not self.draft_warnings(d)
        return False

    def run_scheduled(self, pillar: str | None = None, fixed_title: str | None = None) -> dict:
        """One research-led cycle: plan a search-led topic (or the given one), gather its research pack,
        draft from it, run the editor pass, publish if allowed. Returns a dict for the owner's notification."""
        pillar = pillar or self.next_pillar()
        plan = self.plan_topic(pillar, fixed_title)
        pack, notes = self.research(pillar, plan)
        item_id = self.create_planned_item(pillar, plan, pack, notes)
        draft_id = self.make_draft(item_id)
        review = self.editor_pass(item_id, draft_id)
        d = self.db.latest_draft_for_item(item_id)
        draft_id = d["id"]
        warnings = self.draft_warnings(d)
        holds: list[str] = []
        if len(pack.sources) < self.settings.min_sources:
            holds.append(f"only {len(pack.sources)} source(s) could be fetched (need {self.settings.min_sources})")
        holds += warnings
        if review and (review["verdict"] != "publish" or review["score"] < self.settings.editor_min_score):
            holds.append(f"editor score {review['score']}/10 after revision: " + "; ".join(review["must_fix"] or review["notes"][:2]))
        url = None
        if not holds and self.auto_publishable(d):
            url = self.publish(draft_id, approved_by=f"auto:{self.settings.auto_publish}")
        elif self.settings.auto_publish == "always" and not url:
            url = self.publish(draft_id, approved_by="auto:always")
        if fixed_title is None:
            self.db.set_state(self.SCHEDULE_LAST_KEY, utcnow())  # an owner-requested piece does not reset the clock
        return {
            "item_id": item_id, "draft_id": draft_id, "pillar": pillar, "title": d["headline"],
            "target_query": plan.target_query, "sources": len(pack.sources), "published": url,
            "warnings": holds, "editor": review,
        }

    def unpublish(self, item_id: int) -> str | None:
        """Take a published piece off the site: delete its content file, rebuild, deploy. Returns the old URL."""
        pub = self.db.published_for_item(item_id)
        if pub is None:
            return None
        path = Path(pub["path"])
        if path.exists():
            path.unlink()
        self.db.delete_published(pub["id"])
        self.db.set_draft_status(pub["draft_id"], "rejected")
        self.db.set_item_status(item_id, "dropped")
        build_site(self.settings)
        self._deploy()
        return pub["url"]

    def schedule_due(self) -> bool:
        hours = self.settings.schedule_hours
        if hours <= 0:
            return False
        last = self.db.get_state(self.SCHEDULE_LAST_KEY)
        if not last:
            return True
        from datetime import datetime, timedelta, timezone

        return datetime.now(timezone.utc) - datetime.fromisoformat(last) >= timedelta(hours=hours)

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
            "meta_description": (d["meta_description"] if "meta_description" in d.keys() else "") or "",
            "charts": loads_list(d["charts_json"]) if "charts_json" in d.keys() and d["charts_json"] else [],
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
