"""Claude calls: interview questions and article drafts.

Both calls use structured outputs (Pydantic) so the bot never has to parse prose.
Set COMPOUND_FAKE_LLM=1 to get canned output without an API key (for testing the loop).
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from compound.config import Settings

log = logging.getLogger(__name__)
PROMPTS = Path(__file__).parent / "prompts"
MAX_SOURCE_CHARS = 60_000


# --- output schemas ---------------------------------------------------------
class QuestionSet(BaseModel):
    summary: str = Field(description="One plain-English line on what the source announces")
    questions: list[str] = Field(description="3-4 short, specific interview questions")
    tags: list[str] = Field(description="3-6 lowercase hyphenated tags")


class Triage(BaseModel):
    score: int = Field(description="0-10 relevance to an everyday reader in Ireland")
    reason: str = Field(description="One plain sentence on why")
    angle: str = Field(description="If relevant: the everyday reader it affects and what they should know or do; else empty")
    summary: str = Field(description="One plain-English line on what the item announces")


class TopicIdea(BaseModel):
    title: str = Field(description="Working title, plain and specific, under 80 chars")
    brief: str = Field(description="2-3 sentences: angle, who it is for, the one takeaway")


class Figure(BaseModel):
    value: str
    label: str
    source_url: str
    quote: str


class SourceRef(BaseModel):
    title: str
    url: str


class ArticleDraft(BaseModel):
    headline: str
    slug: str
    summary: str
    body_markdown: str
    figures: list[Figure]
    sources: list[SourceRef]
    tags: list[str]
    email_cta: str


# --- interface --------------------------------------------------------------
class LLM(Protocol):
    def generate_triage(self, *, kind: str, pillar: str, title: str, url: str, source_text: str) -> Triage: ...

    def generate_topic(self, *, pillar: str, recent_titles: list[str]) -> TopicIdea: ...

    def generate_questions(self, *, kind: str, pillar: str, title: str, url: str, source_text: str, n_questions: int = 3) -> QuestionSet: ...

    def generate_draft(
        self,
        *,
        kind: str,
        pillar: str,
        title: str,
        url: str,
        summary: str,
        source_text: str,
        interview: list[tuple[str, str]],
        angle: str = "",
        previous_draft: str | None = None,
        redraft_notes: str | None = None,
    ) -> ArticleDraft: ...


def build_llm(settings: Settings) -> LLM:
    if settings.fake_llm:
        return FakeLLM()
    if settings.llm_backend == "claude-code":
        return ClaudeCodeLLM(
            bin=settings.claude_code_bin, model=settings.claude_code_model, style_dir=settings.style_dir,
            draft_effort=settings.draft_effort,
        )
    return ClaudeLLM(model=settings.anthropic_model, style_dir=settings.style_dir, draft_effort=settings.draft_effort)


# --- prompt assembly --------------------------------------------------------
def load_style_samples(style_dir: Path) -> list[str]:
    path = style_dir / "voice-samples.md"
    if not path.exists():
        return []
    lines = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            lines.append(s.lstrip("-* ").strip())
    return lines


def style_block(samples: list[str]) -> str:
    if not samples:
        return "## Voice\nNo voice samples supplied yet. Write plainly and directly; avoid corporate tone."
    joined = "\n".join(f"- {s}" for s in samples)
    return "## Voice\nThese are sentences David has written. Match this register, rhythm and directness:\n" + joined


def interview_block(interview: list[tuple[str, str]]) -> str:
    if not interview:
        return (
            "(No interview for this piece. Write it from the source alone: report the facts neutrally, say plainly "
            "what they mean for the reader, and give practical next steps. Do not invent opinions or first-person claims.)"
        )
    parts = []
    for i, (q, a) in enumerate(interview, start=1):
        a = a.strip() or "(no answer)"
        parts.append(f"Q{i}: {q}\nDavid: {a}")
    return "\n\n".join(parts)


def _fill(template: str, **values: str) -> str:
    # Plain replacement so braces inside source text never break str.format.
    out = template
    for k, v in values.items():
        out = out.replace("{" + k + "}", v)
    return out


TRIAGE_SOURCE_CHARS = 20_000  # triage is a cheap pass; the opening of the page is enough to score it


def triage_prompt(*, kind: str, pillar: str, title: str, url: str, source_text: str) -> str:
    return _fill(
        (PROMPTS / "triage.md").read_text(encoding="utf-8"),
        kind=kind, pillar=pillar, title=title, url=url or "(none)",
        source_text=source_text[:TRIAGE_SOURCE_CHARS] or "(no source text)",
    )


def topic_prompt(*, pillar: str, recent_titles: list[str]) -> str:
    from datetime import date

    recent = "\n".join(f"- {t}" for t in recent_titles) or "(none yet)"
    return _fill((PROMPTS / "topic.md").read_text(encoding="utf-8"), pillar=pillar, recent=recent, today=date.today().isoformat())


def questions_prompt(*, kind: str, pillar: str, title: str, url: str, source_text: str, n_questions: int) -> str:
    return _fill(
        (PROMPTS / "questions.md").read_text(encoding="utf-8"),
        n_questions=str(n_questions), kind=kind, pillar=pillar, title=title, url=url or "(none)",
        source_text=source_text[:MAX_SOURCE_CHARS] or "(no source text; this is a manual topic)",
    )


def draft_prompt(
    *, kind: str, pillar: str, title: str, url: str, summary: str, source_text: str,
    interview: list[tuple[str, str]], samples: list[str], previous_draft: str | None, redraft_notes: str | None,
    angle: str = "",
) -> str:
    angle_block = f"## Reader angle\n{angle.strip()}\n" if angle.strip() else ""
    redraft = ""
    if previous_draft or redraft_notes:
        redraft = "## Redraft\nDavid reviewed the previous draft and asked for changes. Apply them.\n"
        if redraft_notes:
            redraft += f"David's notes: {redraft_notes}\n"
        if previous_draft:
            redraft += f"\nPrevious draft:\n<previous>\n{previous_draft}\n</previous>"
    return _fill(
        (PROMPTS / "draft.md").read_text(encoding="utf-8"),
        style_block=style_block(samples), kind=kind, pillar=pillar, title=title, url=url or "(none)",
        summary=summary or "(none)", source_text=source_text[:MAX_SOURCE_CHARS] or "(no source text)",
        interview=interview_block(interview), redraft_block=redraft, angle_block=angle_block,
    )


# --- Claude ---------------------------------------------------------------------
class ClaudeLLM:
    def __init__(self, model: str, style_dir: Path, draft_effort: str = "high"):
        import anthropic

        # An empty key (e.g. ANTHROPIC_API_KEY= in .env) makes the SDK raise a bare TypeError at
        # request time; hold the client back and turn that into a clear LLMError instead.
        self.client = anthropic.Anthropic() if os.environ.get("ANTHROPIC_API_KEY", "").strip() else None
        self.model = model
        self.style_dir = style_dir
        self.draft_effort = draft_effort

    def _parse(self, prompt: str, schema, *, effort: str, max_tokens: int):
        import anthropic

        if self.client is None:
            raise LLMError("ANTHROPIC_API_KEY is not set. Add it to .env and restart, or run with COMPOUND_FAKE_LLM=1.")
        try:
            response = self.client.messages.parse(
                model=self.model,
                max_tokens=max_tokens,
                output_config={"effort": effort},
                messages=[{"role": "user", "content": prompt}],
                output_format=schema,
            )
        except anthropic.RateLimitError as e:
            raise LLMError("Anthropic rate limit hit; try again in a minute.") from e
        except anthropic.APIStatusError as e:
            raise LLMError(f"Anthropic API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise LLMError("Could not reach the Anthropic API.") from e
        except anthropic.AnthropicError as e:
            raise LLMError(f"Anthropic client error: {e}") from e
        if response.stop_reason == "refusal":
            raise LLMError("The model declined this request (stop_reason=refusal).")
        if response.stop_reason == "max_tokens":
            raise LLMError("The model ran out of output tokens before finishing.")
        if response.parsed_output is None:
            raise LLMError("The model returned no structured output.")
        log.info("llm ok: model=%s in=%s out=%s", response.model, response.usage.input_tokens, response.usage.output_tokens)
        return response.parsed_output

    def generate_triage(self, *, kind, pillar, title, url, source_text) -> Triage:
        prompt = triage_prompt(kind=kind, pillar=pillar, title=title, url=url, source_text=source_text)
        t: Triage = self._parse(prompt, Triage, effort="low", max_tokens=1500)
        t.score = max(0, min(10, int(t.score)))
        return t

    def generate_topic(self, *, pillar, recent_titles) -> TopicIdea:
        t: TopicIdea = self._parse(topic_prompt(pillar=pillar, recent_titles=recent_titles), TopicIdea, effort="medium", max_tokens=2000)
        t.title = t.title.strip()[:80]
        return t

    def generate_questions(self, *, kind, pillar, title, url, source_text, n_questions=3) -> QuestionSet:
        prompt = questions_prompt(kind=kind, pillar=pillar, title=title, url=url, source_text=source_text, n_questions=n_questions)
        qs: QuestionSet = self._parse(prompt, QuestionSet, effort="medium", max_tokens=4000)
        qs.questions = [q.strip() for q in qs.questions if q.strip()][: max(n_questions, 4)]
        qs.tags = normalise_tags(qs.tags)
        return qs

    def generate_draft(self, *, kind, pillar, title, url, summary, source_text, interview, angle="", previous_draft=None, redraft_notes=None) -> ArticleDraft:
        prompt = draft_prompt(
            kind=kind, pillar=pillar, title=title, url=url, summary=summary, source_text=source_text,
            interview=interview, samples=load_style_samples(self.style_dir),
            previous_draft=previous_draft, redraft_notes=redraft_notes, angle=angle,
        )
        draft: ArticleDraft = self._parse(prompt, ArticleDraft, effort=self.draft_effort, max_tokens=16000)
        draft.slug = slugify(draft.slug or draft.headline)
        draft.tags = normalise_tags(draft.tags)
        return draft


class LLMError(RuntimeError):
    pass


# --- Claude Code (headless, subscription-billed) --------------------------------
class ClaudeCodeLLM(ClaudeLLM):
    """Same prompts and schemas as ClaudeLLM, but each call runs the local Claude Code CLI in
    non-interactive mode (`claude -p --output-format json --json-schema ...`). Authenticated by
    whatever `claude` is logged in as, so a Pro/Max subscription covers it instead of API credits.
    The CLI must be installed and logged in on this machine; run `claude` once by hand to check."""

    TIMEOUT = 900  # seconds; a long draft at high effort can take a few minutes

    def __init__(self, bin: str, model: str, style_dir: Path, draft_effort: str = "high"):
        self.bin = bin
        self.model = model
        self.style_dir = style_dir
        self.draft_effort = draft_effort

    def _resolve_bin(self) -> str:
        path = shutil.which(self.bin) or shutil.which(self.bin + ".cmd") or shutil.which(self.bin + ".exe")
        if not path:
            raise LLMError(
                f"Claude Code CLI '{self.bin}' not found. Install it (https://code.claude.com), log in with `claude`, "
                "or set CLAUDE_CODE_BIN to its full path."
            )
        return path

    def _parse(self, prompt: str, schema, *, effort: str, max_tokens: int):
        cmd = [
            self._resolve_bin(), "-p",
            "--output-format", "json",
            "--json-schema", json.dumps(schema.model_json_schema()),
            "--tools", "",  # answer from the prompt alone: no file reads, shell or browsing
            "--permission-mode", "dontAsk",
            "--bare",  # skip hooks, plugins and MCP servers: faster and nothing else runs
            "--effort", effort if effort in {"low", "medium", "high"} else "high",
        ]
        if self.model:
            cmd += ["--model", self.model]
        full_prompt = prompt + "\n\nAnswer directly from the text above."
        # Claude Code prefers an API key over the subscription login when it finds one in the
        # environment. The bot loads .env into its own environment, so strip the API credentials
        # here or every "subscription" call would quietly bill the key.
        env = {k: v for k, v in os.environ.items() if k not in {"ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"}}
        try:
            r = subprocess.run(
                cmd, input=full_prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=self.TIMEOUT, env=env,
            )
        except subprocess.TimeoutExpired as e:
            raise LLMError(f"Claude Code did not answer within {self.TIMEOUT}s.") from e
        except OSError as e:
            raise LLMError(f"Could not run Claude Code: {e}") from e
        out = (r.stdout or "").strip()
        if r.returncode != 0 or not out:
            err = (r.stderr or out or "").strip()
            raise LLMError(f"Claude Code failed (exit {r.returncode}): {err[:400] or 'no output'}")
        try:
            data = json.loads(out)
        except json.JSONDecodeError as e:
            raise LLMError(f"Claude Code returned non-JSON output: {out[:200]}") from e
        if data.get("is_error"):
            raise LLMError(f"Claude Code error: {str(data.get('result') or data.get('subtype') or data)[:400]}")
        structured = data.get("structured_output")
        if structured is None:
            # Some versions put the schema-conforming JSON in `result` as a string.
            raw = data.get("result")
            try:
                structured = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, json.JSONDecodeError):
                structured = None
        if not isinstance(structured, dict):
            raise LLMError("Claude Code returned no structured output (is --json-schema supported by this version?).")
        log.info(
            "claude-code ok: turns=%s duration_ms=%s (subscription; nominal cost %s)",
            data.get("num_turns"), data.get("duration_ms"), data.get("total_cost_usd"),
        )
        try:
            return schema.model_validate(structured)
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Claude Code output did not match the expected shape: {e}") from e


# --- fake backend for tests / dry runs -----------------------------------------
class FakeLLM:
    triage_score = 8  # tests set this low to exercise the skip path

    def generate_triage(self, *, kind, pillar, title, url, source_text) -> Triage:
        return Triage(
            score=self.triage_score, reason="(fake) scored by the fake backend",
            angle="(fake) renters: claim it this week" if self.triage_score >= 5 else "",
            summary=f"(fake) {title[:80]}",
        )

    def generate_topic(self, *, pillar, recent_titles) -> TopicIdea:
        n = len(recent_titles) + 1
        return TopicIdea(title=f"(fake) {pillar} topic {n}", brief=f"(fake) a {pillar} piece for the everyday reader")

    def generate_questions(self, *, kind, pillar, title, url, source_text, n_questions=3) -> QuestionSet:
        return QuestionSet(
            summary=f"(fake) {title[:80]}",
            questions=[
                "What does this change mean for a PAYE worker on shift allowance?",
                "Who is most likely to miss out, and why?",
                "What is the one thing a reader should do this week?",
            ][:n_questions],
            tags=["revenue", "paye"],
        )

    def generate_draft(self, *, kind, pillar, title, url, summary, source_text, interview, angle="", previous_draft=None, redraft_notes=None) -> ArticleDraft:
        answers = "\n\n".join(f"{a}" for _, a in interview if a.strip()) or "No answers were given."
        m = re.search(r"€\s?[\d,]+", source_text)
        value = m.group(0).replace(" ", "") if m else "€0"
        quote = ""
        if m:
            start = source_text.rfind("\n", 0, m.start()) + 1
            end = source_text.find("\n", m.end())
            quote = source_text[start : end if end != -1 else None].strip()
        body = (
            f"Revenue has published an update: {title}. The headline figure is {value} ([source]({url})).\n\n"
            f"## What David says\n\n{answers}\n\n"
            f"{'Redrafted with notes: ' + redraft_notes if redraft_notes else ''}"
        ).strip()
        return ArticleDraft(
            headline=f"{title}: what it means for you",
            slug=slugify(title),
            summary=f"{title}. Here is what it means in practice.",
            body_markdown=body,
            figures=[Figure(value=value, label="headline figure", source_url=url or "owner", quote=quote or "(not in source)")],
            sources=[SourceRef(title=title, url=url or "")],
            tags=["revenue", "paye"],
            email_cta="Want deadline reminders and an application checklist? Join the Compound list.",
        )


# --- helpers --------------------------------------------------------------------
def slugify(text: str, max_len: int = 60) -> str:
    s = text.lower()
    s = s.replace("€", "eur").replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0] if "-" in s[:max_len] else s[:max_len]
    return s or "article"


def normalise_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    for t in tags:
        if not t or not t.strip():
            continue
        s = slugify(t, 40)
        if s and s not in out:
            out.append(s)
    return out[:6]
