"""Telegram bot: the review surface. One owner, one chat.

Flow
----
new item -> header message + one message per question
voice/text reply -> answer bound to the replied-to question, else the next unanswered one
all answered (or /draft) -> draft generated -> review message: headline, summary, figures, preview link,
                            inline buttons Approve / Redraft / Drop
Approve -> publish. Redraft -> asks what to change, next message is the notes. Drop -> item dead.

Polling of sources runs inside the same process via the job queue.
"""
from __future__ import annotations

import asyncio
import logging
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from compound.config import Settings
from compound.db import loads_list
from compound.llm import LLMError
from compound.pipeline import Pipeline
from compound.poller import poll_all
from compound.transcribe import TranscriptionError, TranscriptionUnavailable, transcribe

log = logging.getLogger(__name__)
ACTIVE_ITEM = "active_item"
AWAITING_REDRAFT = "awaiting_redraft_draft_id"
PILLARS = {"wealth", "health", "happiness"}
TG_LIMIT = 4000


def _h(s: str) -> str:
    return escape(str(s or ""))


class Bot:
    def __init__(self, settings: Settings, pipeline: Pipeline):
        self.settings = settings
        self.p = pipeline
        self.db = pipeline.db

    # -- wiring --------------------------------------------------------------
    def build(self) -> Application:
        app = Application.builder().token(self.settings.telegram_bot_token).build()
        owner = filters.User(user_id=self.settings.telegram_owner_id) if self.settings.telegram_owner_id else filters.ALL
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_start, filters=owner))
        app.add_handler(CommandHandler("queue", self.cmd_queue, filters=owner))
        app.add_handler(CommandHandler("open", self.cmd_open, filters=owner))
        app.add_handler(CommandHandler("draft", self.cmd_draft, filters=owner))
        app.add_handler(CommandHandler("skip", self.cmd_skip, filters=owner))
        app.add_handler(CommandHandler("newpiece", self.cmd_newpiece, filters=owner))
        app.add_handler(CommandHandler("poll", self.cmd_poll, filters=owner))
        app.add_handler(CommandHandler("auto", self.cmd_auto, filters=owner))
        app.add_handler(CommandHandler("unpublish", self.cmd_unpublish, filters=owner))
        app.add_handler(CommandHandler("drop", self.cmd_drop, filters=owner))
        app.add_handler(CallbackQueryHandler(self.on_callback))
        app.add_handler(MessageHandler(owner & filters.VOICE, self.on_voice))
        app.add_handler(MessageHandler(owner & filters.AUDIO, self.on_voice))
        app.add_handler(MessageHandler(owner & filters.TEXT & ~filters.COMMAND, self.on_text))
        app.add_error_handler(self.on_error)
        if self.settings.telegram_owner_id:
            minutes = max(1, self.settings.poll_interval_minutes)
            app.job_queue.run_repeating(self.job_poll, interval=minutes * 60, first=10, name="poll")
        if self.settings.schedule_hours > 0:
            # Checked every 10 minutes against the persisted last-run time, so restarts neither
            # fire an extra piece nor lose the schedule.
            app.job_queue.run_repeating(self.job_schedule, interval=600, first=30, name="schedule")
        return app

    def _is_owner(self, update: Update) -> bool:
        uid = update.effective_user.id if update.effective_user else 0
        return bool(self.settings.telegram_owner_id) and uid == self.settings.telegram_owner_id

    @property
    def chat_id(self) -> int:
        return self.settings.telegram_owner_id

    # -- commands ------------------------------------------------------------
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id if update.effective_user else 0
        if not self.settings.telegram_owner_id:
            await update.message.reply_text(
                f"Your Telegram user id is {uid}. Put it in .env as TELEGRAM_OWNER_ID and restart the bot."
            )
            return
        if not self._is_owner(update):
            return
        await update.message.reply_text(
            "Compound pipeline.\n\n"
            "/queue – what's open\n/open <id> – switch to an item and resend its questions\n"
            "/draft [id] – draft now with the answers so far\n/skip – skip the current question\n"
            "/newpiece [pillar] <topic> – research and write a piece on your topic\n/auto [pillar] – write a scheduled piece now\n/unpublish <id> – take a published piece off the site\n/drop [id] – kill an item\n/poll – poll sources now\n\n"
            "Answer questions by voice note or text. Reply to a specific question message to bind the answer to it."
        )

    async def cmd_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        items = self.db.open_items()
        if not items:
            await update.message.reply_text("Queue empty.")
            return
        active = self.db.get_state(ACTIVE_ITEM)
        lines = []
        for it in items:
            qs = self.db.questions_for(it["id"])
            answered = len(self.db.answered_question_ids(it["id"]))
            mark = "▶ " if str(it["id"]) == active else "  "
            extra = f" {answered}/{len(qs)} answered" if qs and it["status"] == "questions_sent" else ""
            lines.append(f"{mark}#{it['id']} [{it['status']}]{extra} {it['pillar']}: {it['title'][:70]}")
        await update.message.reply_text("\n".join(lines)[:TG_LIMIT])

    async def cmd_open(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        item_id = _int_arg(context.args)
        item = self.db.get_item(item_id) if item_id else None
        if item is None:
            await update.message.reply_text("Usage: /open <item id>")
            return
        self.db.set_state(ACTIVE_ITEM, str(item["id"]))
        if item["status"] in {"new", "skipped"} or (item["status"] == "failed" and not self.db.questions_for(item["id"])):
            await self._start_interview(item["id"])
        elif item["status"] == "pending":
            d = self.db.pending_draft_for_item(item["id"])
            if d:
                await self.send_review(d["id"])
        else:
            await self.send_questions(item["id"], resend=True)

    async def cmd_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        item_id = self._active_item_id()
        q = self.db.next_unanswered_question(item_id) if item_id else None
        if q is None:
            await update.message.reply_text("No open question to skip.")
            return
        self.db.skip_question(q["id"])
        await update.message.reply_text(f"Skipped Q{q['ordinal']}.")
        await self._maybe_autodraft(item_id)

    async def cmd_draft(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        item_id = _int_arg(context.args) or self._active_item_id()
        if not item_id or self.db.get_item(item_id) is None:
            await update.message.reply_text("No active item. /queue then /open <id>.")
            return
        await update.message.reply_text(f"Drafting #{item_id}… this takes a minute or two.")
        await self.run_draft(item_id)

    async def cmd_drop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        item_id = _int_arg(context.args) or self._active_item_id()
        if not item_id or self.db.get_item(item_id) is None:
            await update.message.reply_text("Usage: /drop <item id>")
            return
        self.p.drop(item_id)
        if self.db.get_state(ACTIVE_ITEM) == str(item_id):
            self.db.set_state(ACTIVE_ITEM, None)
        await update.message.reply_text(f"Dropped #{item_id}.")

    async def cmd_newpiece(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        args = list(context.args or [])
        pillar = "happiness"
        if args and args[0].lower().rstrip(":") in PILLARS:
            pillar = args.pop(0).lower().rstrip(":")
        topic = " ".join(args).strip()
        if not topic:
            await update.message.reply_text("Usage: /newpiece [health|wealth|happiness] <topic>")
            return
        if not self.settings.interview:
            await update.message.reply_text(f"New {pillar} piece: {topic}\nResearching, drafting and editing… three to five minutes.")
            await self.run_scheduled(pillar, fixed_title=topic)
            return
        item_id = self.p.create_manual_item(topic, pillar)
        self.db.set_state(ACTIVE_ITEM, str(item_id))
        await update.message.reply_text(f"New {pillar} piece #{item_id}: {topic}\nThinking of questions…")
        await self._start_interview(item_id)

    async def cmd_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Polling…")
        n = await self._poll_and_dispatch()
        await update.message.reply_text(f"Done. {n} new item(s).")

    async def cmd_auto(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        args = list(context.args or [])
        pillar = args[0].lower() if args and args[0].lower() in PILLARS else None
        await update.message.reply_text(f"Writing a {pillar or 'scheduled'} piece now… this takes a minute or two.")
        await self.run_scheduled(pillar)

    async def cmd_unpublish(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        item_id = _int_arg(context.args)
        if not item_id or self.db.get_item(item_id) is None:
            await update.message.reply_text("Usage: /unpublish <item id>  (the #number from the published message)")
            return
        try:
            url = await asyncio.to_thread(self.p.unpublish, item_id)
        except Exception as e:  # noqa: BLE001
            log.exception("unpublish failed")
            await update.message.reply_text(f"⚠️ Could not unpublish #{item_id}: {type(e).__name__}: {e}")
            return
        if url is None:
            await update.message.reply_text(f"#{item_id} is not published.")
            return
        await update.message.reply_text(f"🗑 Removed #{item_id} from the site: {url}")

    async def run_scheduled(self, pillar: str | None = None, fixed_title: str | None = None) -> None:
        try:
            r = await asyncio.to_thread(self.p.run_scheduled, pillar, fixed_title)
        except LLMError as e:
            await self._send(f"⚠️ Scheduled piece failed: {e}")
            return
        except Exception as e:  # noqa: BLE001 - surface anything to the owner
            log.exception("scheduled piece failed")
            await self._send(f"⚠️ Scheduled piece failed: {type(e).__name__}: {e}")
            return
        ed = r.get("editor")
        detail = f"query: {r.get('target_query') or '-'} · sources: {r.get('sources', 0)}"
        if ed:
            detail += f" · editor {ed['score']}/10"
        if r["published"]:
            await self._send(f"🚀 Published ({r['pillar']}) #{r['item_id']}: {r['title']}\n{r['published']}\n{detail}\n/unpublish {r['item_id']} to take it down.")
        else:
            ws = r["warnings"]
            if self.settings.auto_publish == "off":
                why = "auto-publish is off"
            elif len(ws) > 6:
                why = f"held ({len(ws)} checks failed): " + "; ".join(ws[:5]) + f"; … and {len(ws) - 5} more"
            else:
                why = "held: " + "; ".join(ws)
            await self._send(f"📝 Draft ready ({r['pillar']}), {why}\n{detail}")
            await self.send_review(r["draft_id"])

    async def job_schedule(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            if self.p.schedule_due():
                await self.run_scheduled()
        except Exception:
            log.exception("schedule job failed")

    # -- polling job -----------------------------------------------------------
    async def job_poll(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            await self._poll_and_dispatch()
        except Exception:
            log.exception("poll job failed")

    async def _poll_and_dispatch(self) -> int:
        new_ids = await asyncio.to_thread(poll_all, self.db, self.p.sources, self.settings)
        # Also pick up anything left in 'new' from a previous crash or from `compound simulate-item`.
        pending_new = [it["id"] for it in self.db.items_with_status("new")]
        for item_id in dict.fromkeys(new_ids + pending_new):
            await self._start_interview(item_id)
        return len(new_ids)

    # -- interview -------------------------------------------------------------
    async def _start_interview(self, item_id: int) -> None:
        if self.p.needs_triage(item_id):
            try:
                t = await asyncio.to_thread(self.p.triage, item_id)
            except LLMError as e:
                await self._send(f"⚠️ Could not triage #{item_id}: {e}\nSend /open {item_id} to retry.")
                return
            if t.score < self.settings.min_relevance:
                self.p.skip(item_id)
                item = self.db.get_item(item_id)
                await self._send(
                    f"⏭ #{item_id} skipped · {t.score}/10 · {_h(item['title'])}\n{_h(t.reason)}\n/open {item_id} to draft it anyway."
                )
                return
        if not self.settings.interview:
            self.db.set_state(ACTIVE_ITEM, str(item_id))
            item = self.db.get_item(item_id)
            await self._send(f"#{item_id} · {_h(item['title'])}\nDrafting…")
            await self.run_draft(item_id)
            return
        try:
            await asyncio.to_thread(self.p.prepare_questions, item_id)
        except LLMError as e:
            await self._send(f"⚠️ Could not generate questions for #{item_id}: {e}\nSend /open {item_id} to retry.")
            return
        self.db.set_state(ACTIVE_ITEM, str(item_id))
        await self.send_questions(item_id)

    async def send_questions(self, item_id: int, resend: bool = False) -> None:
        item = self.db.get_item(item_id)
        qs = self.db.questions_for(item_id)
        answered = self.db.answered_question_ids(item_id)
        head = (
            f"<b>#{item['id']} · {_h(item['pillar'].title())}{' · resend' if resend else ''}</b>\n"
            f"<b>{_h(item['title'])}</b>\n"
        )
        if item["summary"]:
            head += f"{_h(item['summary'])}\n"
        if item["url"]:
            head += f"{_h(item['url'])}\n"
        head += f"\n{len(qs)} question(s). Reply by voice note or text, one answer per question."
        await self._send(head, html=True)
        for q in qs:
            state = " ✅" if q["id"] in answered else (" (skipped)" if q["skipped"] else "")
            msg = await self._send(f"Q{q['ordinal']}{state}: {q['text']}")
            if msg is not None:
                self.db.set_question_message_id(q["id"], msg.message_id)

    def _active_item_id(self) -> int | None:
        raw = self.db.get_state(ACTIVE_ITEM)
        return int(raw) if raw else None

    def _resolve_target(self, update: Update) -> tuple[int | None, int | None]:
        """(item_id, question_id) for an incoming answer."""
        replied = update.message.reply_to_message
        if replied is not None:
            q = self.db.question_by_message_id(replied.message_id)
            if q is not None:
                return int(q["item_id"]), int(q["id"])
        return self._active_item_id(), None

    async def on_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        media = update.message.voice or update.message.audio
        try:
            tg_file = await media.get_file()
            data = bytes(await tg_file.download_as_bytearray())
            text = await asyncio.to_thread(transcribe, self.settings, data, "voice.ogg", media.mime_type or "audio/ogg")
        except TranscriptionUnavailable:
            await update.message.reply_text("Voice transcription isn't configured (STT_PROVIDER). Type the answer instead.")
            return
        except TranscriptionError as e:
            await update.message.reply_text(f"Transcription failed: {e}. Try again or type it.")
            return
        await self._handle_answer(update, text, "voice")

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self._handle_answer(update, update.message.text.strip(), "text")

    async def _handle_answer(self, update: Update, text: str, kind: str) -> None:
        if not text:
            return
        awaiting = self.db.get_state(AWAITING_REDRAFT)
        if awaiting:
            self.db.set_state(AWAITING_REDRAFT, None)
            d = self.db.get_draft(int(awaiting))
            if d is not None:
                await update.message.reply_text("Got it. Redrafting…")
                await self.run_draft(int(d["item_id"]), redraft_notes=text)
                return
        item_id, question_id = self._resolve_target(update)
        item = self.db.get_item(item_id) if item_id else None
        if item is None:
            await update.message.reply_text("No active item. /queue then /open <id>, or /newpiece <topic>.")
            return
        if item["status"] not in {"questions_sent", "failed", "pending", "drafting"}:
            await update.message.reply_text(f"#{item_id} is {item['status']}; nothing to answer.")
            return
        ordinal, answered, total = self.p.record_answer(item_id, text, kind, question_id)
        label = f"Q{ordinal}" if ordinal else "note"
        snippet = text if len(text) <= 160 else text[:157] + "…"
        prefix = "🎙" if kind == "voice" else "✍️"
        await update.message.reply_text(f"{prefix} #{item_id} {label} recorded ({answered}/{total}): “{snippet}”")
        await self._maybe_autodraft(item_id)

    async def _maybe_autodraft(self, item_id: int) -> None:
        item = self.db.get_item(item_id)
        if item and item["status"] == "questions_sent" and self.p.all_answered(item_id):
            await self._send(f"All questions for #{item_id} answered. Drafting…")
            await self.run_draft(item_id)

    # -- drafting and review -------------------------------------------------------
    async def run_draft(self, item_id: int, redraft_notes: str | None = None) -> None:
        try:
            draft_id = await asyncio.to_thread(self.p.make_draft, item_id, redraft_notes)
        except LLMError as e:
            await self._send(f"⚠️ Draft failed for #{item_id}: {e}\nSend /draft {item_id} to retry.")
            return
        except Exception as e:  # noqa: BLE001 - surface anything to the owner
            log.exception("draft failed")
            await self._send(f"⚠️ Draft failed for #{item_id}: {type(e).__name__}: {e}")
            return
        await self.send_review(draft_id)

    def review_text(self, d) -> str:
        item = self.db.get_item(d["item_id"])
        figures = loads_list(d["figures_json"])
        ver = {(v["value"], v["label"]): v for v in loads_list(d["verification_json"])}
        lines = [
            f"<b>📝 Draft v{d['version']} · #{item['id']} · {_h(item['pillar'].title())}</b>",
            f"<b>{_h(d['headline'])}</b>",
            _h(d["summary"]),
            "",
            f"<b>Figures used ({len(figures)})</b>",
        ]
        for f in figures:
            v = ver.get((f.get("value"), f.get("label")), {})
            if v.get("owner_supplied"):
                icon = "🗣"
            elif v.get("ok"):
                icon = "✅"
            elif v.get("in_source") is None:
                icon = "❔"
            else:
                icon = "⚠️"
            src = f.get("source_url") or ""
            lines.append(f"{icon} <b>{_h(f.get('value'))}</b> — {_h(f.get('label'))}")
            lines.append(f"   ↳ {_h(src)}")
            if f.get("quote"):
                lines.append(f"   “{_h(f['quote'][:200])}”")
        if not figures:
            lines.append("(none listed)")
        warnings = self.p.draft_warnings(d)
        if warnings:
            lines.append("")
            lines.append("<b>Check</b>")
            lines.extend(f"• {_h(w)}" for w in warnings)
        lines.append("")
        lines.append(f"Preview: {self.p.preview_url(d)}")
        text = "\n".join(lines)
        if len(text) > TG_LIMIT:
            text = text[: TG_LIMIT - 60] + "\n…(truncated; full figures table on the preview page)"
        return text

    async def send_review(self, draft_id: int) -> None:
        d = self.db.get_draft(draft_id)
        if d is None:
            return
        kb = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft_id}"),
                InlineKeyboardButton("✏️ Redraft", callback_data=f"redraft:{draft_id}"),
                InlineKeyboardButton("❌ Drop", callback_data=f"drop:{draft_id}"),
            ]]
        )
        await self._send(self.review_text(d), html=True, reply_markup=kb)

    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not self._is_owner(update):
            await query.answer()
            return
        action, _, raw = (query.data or "").partition(":")
        draft_id = int(raw) if raw.isdigit() else 0
        d = self.db.get_draft(draft_id)
        if d is None:
            await query.answer("Unknown draft")
            return
        if d["status"] != "pending":
            await query.answer(f"Draft is already {d['status']}")
            return
        await query.answer()
        if action == "approve":
            await query.edit_message_reply_markup(reply_markup=None)
            await self._send(f"Publishing draft v{d['version']} for #{d['item_id']}…")
            try:
                approver = update.effective_user.username or str(update.effective_user.id)
                url = await asyncio.to_thread(self.p.publish, draft_id, approved_by=f"telegram:{approver}")
            except Exception as e:  # noqa: BLE001
                log.exception("publish failed")
                await self._send(f"⚠️ Publish failed: {type(e).__name__}: {e}\nThe draft is still pending; /open {d['item_id']} to retry.")
                return
            await self._send(f"✅ Published: {url}")
            if self.db.get_state(ACTIVE_ITEM) == str(d["item_id"]):
                self.db.set_state(ACTIVE_ITEM, None)
        elif action == "redraft":
            self.db.set_state(AWAITING_REDRAFT, str(draft_id))
            self.db.set_state(ACTIVE_ITEM, str(d["item_id"]))
            await self._send("What should change? Send it as text or a voice note.")
        elif action == "drop":
            await query.edit_message_reply_markup(reply_markup=None)
            self.p.drop(int(d["item_id"]))
            if self.db.get_state(ACTIVE_ITEM) == str(d["item_id"]):
                self.db.set_state(ACTIVE_ITEM, None)
            await self._send(f"❌ Dropped #{d['item_id']}.")

    # -- plumbing ----------------------------------------------------------------
    async def _send(self, text: str, html: bool = False, reply_markup=None):
        if not self.chat_id:
            log.warning("no owner configured; not sending: %s", text[:80])
            return None
        return await self.app.bot.send_message(
            chat_id=self.chat_id, text=text, parse_mode=ParseMode.HTML if html else None,
            reply_markup=reply_markup, disable_web_page_preview=True,
        )

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        log.error("update %s caused error", update, exc_info=context.error)

    def run(self) -> None:
        self.app = self.build()
        which = (
            f"claude-code model={self.settings.claude_code_model or 'Claude Code default'}"
            if self.settings.llm_backend == "claude-code" else f"api model={self.settings.anthropic_model}"
        )
        if self.settings.fake_llm:
            which = "FAKE (canned output)"
        log.info(
            "bot starting (owner=%s, poll every %s min, writer: %s, interview=%s, auto_publish=%s, schedule=%sh)",
            self.settings.telegram_owner_id, self.settings.poll_interval_minutes, which, self.settings.interview,
            self.settings.auto_publish, self.settings.schedule_hours,
        )
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def _int_arg(args) -> int | None:
    if args and str(args[0]).lstrip("#").isdigit():
        return int(str(args[0]).lstrip("#"))
    return None
