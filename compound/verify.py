"""Cheap, deterministic checks on a draft's figures. Not a substitute for the owner's review;
its job is to point the owner at the figures that need a closer look."""
from __future__ import annotations

import re
import unicodedata

from compound.llm import ArticleDraft


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _digits(s: str) -> str:
    return re.sub(r"[^\d.]", "", s)


def verify_figures(draft: ArticleDraft, source_text: str, page_texts: dict[str, str] | None = None) -> list[dict]:
    """Return one dict per figure: {value, label, source_url, quote, in_source, in_body, value_in_quote, ok}.

    Each figure is checked against the text of the page it cites when `page_texts` has it
    (url -> fetched text; empty string = fetch failed), and otherwise against the item's own
    source text. Evergreen pieces have no item source, so their citations live or die by the
    fetched pages."""
    item_src = _norm(source_text)
    pages = {k.strip(): _norm(v) for k, v in (page_texts or {}).items()}
    body = _norm(draft.body_markdown + "\n" + draft.headline + "\n" + draft.summary)
    results: list[dict] = []
    for f in draft.figures:
        quote = _norm(f.quote)
        value = _norm(f.value)
        owner = f.source_url.strip().lower() == "owner"
        cited = f.source_url.strip()
        src = pages[cited] if cited in pages else item_src
        if cited in pages and not src and item_src:
            src = item_src  # cited page could not be fetched; the item page is the next best evidence
        in_source = bool(quote) and quote in src if not owner else None
        # Fall back to the value's digits when the quote was lightly paraphrased.
        if in_source is False and _digits(value) and _digits(value) in _digits(src):
            in_source = None  # unclear: digits present, quote not verbatim
        value_in_quote = bool(value) and (value in quote or (_digits(value) and _digits(value) in _digits(quote)))
        in_body = bool(value) and (value in body or (_digits(value) and _digits(value) in _digits(body)))
        ok = (in_source is True or owner) and in_body and value_in_quote
        results.append(
            {
                "value": f.value,
                "label": f.label,
                "source_url": f.source_url,
                "quote": f.quote,
                "in_source": in_source,
                "in_body": in_body,
                "value_in_quote": value_in_quote,
                "owner_supplied": owner,
                "ok": bool(ok),
            }
        )
    return results


def unlisted_numbers(draft: ArticleDraft) -> list[str]:
    """Numbers that appear in the body but in no figure value. Surfaced as a warning only."""
    listed = {_digits(f.value) for f in draft.figures if _digits(f.value)}
    # Ignore URLs (markdown link targets, bare links) so eBrief numbers in paths are not "figures".
    body = re.sub(r"\]\([^)]*\)", "]", draft.body_markdown)
    body = re.sub(r"https?://\S+", " ", body)
    found: list[str] = []
    for m in re.finditer(r"(?:€\s?)?\d[\d,]*(?:\.\d+)?\s?%?", body):
        tok = m.group(0).strip()
        d = _digits(tok)
        if not d or d in listed or any(d in l for l in listed):
            continue
        if re.fullmatch(r"\d{1,2}", d) and "€" not in tok and "%" not in tok:  # "3 things" is not a figure
            continue
        if re.fullmatch(r"(19|20)\d{2}", d) and "€" not in tok and "%" not in tok:  # bare years are context, not figures
            continue
        if tok not in found:
            found.append(tok)
    return found[:10]
