"""Claude calls: interview questions and article drafts.

Both calls use structured outputs (Pydantic) so the bot never has to parse prose.
Set COMPOUND_FAKE_LLM=1 to get canned output without an API key (for testing the loop).
"""
from __future__ import annotations

import logging
import re
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
        previous_draft: str | None = None,
        redraft_notes: str | None = None,
    ) -> ArticleDraft: ...


def build_llm(settings: Settings) -> LLM:
    if settings.fake_llm:
        return FakeLLM()
    return ClaudeLLM(model=settings.anthropic_model, style_dir=settings.style_dir)


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
        return "(David gave no answers; write a short, factual piece and flag in the summary that it has no owner take.)"
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


def questions_prompt(*, kind: str, pillar: str, title: str, url: str, source_text: str, n_questions: int) -> str:
    return _fill(
        (PROMPTS / "questions.md").read_text(encoding="utf-8"),
        n_questions=str(n_questions), kind=kind, pillar=pillar, title=title, url=url or "(none)",
        source_text=source_text[:MAX_SOURCE_CHARS] or "(no source text; this is a manual topic)",
    )


def draft_prompt(
    *, kind: str, pillar: str, title: str, url: str, summary: str, source_text: str,
    interview: list[tuple[str, str]], samples: list[str], previous_draft: str | None, redraft_notes: str | None,
) -> str:
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
        interview=interview_block(interview), redraft_block=redraft,
    )


# --- Claude ---------------------------------------------------------------------
class ClaudeLLM:
    def __init__(self, model: str, style_dir: Path):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model
        self.style_dir = style_dir

    def _parse(self, prompt: str, schema, *, effort: str, max_tokens: int):
        import anthropic

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
        if response.stop_reason == "refusal":
            raise LLMError("The model declined this request (stop_reason=refusal).")
        if response.stop_reason == "max_tokens":
            raise LLMError("The model ran out of output tokens before finishing.")
        if response.parsed_output is None:
            raise LLMError("The model returned no structured output.")
        log.info("llm ok: model=%s in=%s out=%s", response.model, response.usage.input_tokens, response.usage.output_tokens)
        return response.parsed_output

    def generate_questions(self, *, kind, pillar, title, url, source_text, n_questions=3) -> QuestionSet:
        prompt = questions_prompt(kind=kind, pillar=pillar, title=title, url=url, source_text=source_text, n_questions=n_questions)
        qs: QuestionSet = self._parse(prompt, QuestionSet, effort="medium", max_tokens=4000)
        qs.questions = [q.strip() for q in qs.questions if q.strip()][: max(n_questions, 4)]
        qs.tags = normalise_tags(qs.tags)
        return qs

    def generate_draft(self, *, kind, pillar, title, url, summary, source_text, interview, previous_draft=None, redraft_notes=None) -> ArticleDraft:
        prompt = draft_prompt(
            kind=kind, pillar=pillar, title=title, url=url, summary=summary, source_text=source_text,
            interview=interview, samples=load_style_samples(self.style_dir),
            previous_draft=previous_draft, redraft_notes=redraft_notes,
        )
        draft: ArticleDraft = self._parse(prompt, ArticleDraft, effort="high", max_tokens=16000)
        draft.slug = slugify(draft.slug or draft.headline)
        draft.tags = normalise_tags(draft.tags)
        return draft


class LLMError(RuntimeError):
    pass


# --- fake backend for tests / dry runs -----------------------------------------
class FakeLLM:
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

    def generate_draft(self, *, kind, pillar, title, url, summary, source_text, interview, previous_draft=None, redraft_notes=None) -> ArticleDraft:
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
