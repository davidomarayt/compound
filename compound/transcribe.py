"""Speech to text for Telegram voice notes (OGG/Opus).

Any OpenAI-compatible /audio/transcriptions endpoint works (OpenAI, Groq...). Provider "none"
raises TranscriptionUnavailable so the bot can ask for a typed answer instead.
"""
from __future__ import annotations

import httpx

from compound.config import Settings


class TranscriptionUnavailable(RuntimeError):
    pass


class TranscriptionError(RuntimeError):
    pass


def transcribe(settings: Settings, audio: bytes, filename: str = "voice.ogg", mime: str = "audio/ogg") -> str:
    if settings.stt_provider in {"", "none"}:
        raise TranscriptionUnavailable("STT_PROVIDER is 'none'")
    if settings.stt_provider != "openai":
        raise TranscriptionUnavailable(f"unknown STT_PROVIDER {settings.stt_provider!r}")
    if not settings.stt_api_key:
        raise TranscriptionUnavailable("STT_API_KEY is empty")
    url = f"{settings.stt_base_url}/audio/transcriptions"
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(
                url,
                headers={"Authorization": f"Bearer {settings.stt_api_key}"},
                data={"model": settings.stt_model, "language": "en", "response_format": "json"},
                files={"file": (filename, audio, mime)},
            )
    except httpx.HTTPError as e:
        raise TranscriptionError(f"transcription request failed: {e}") from e
    if r.status_code >= 400:
        raise TranscriptionError(f"transcription failed ({r.status_code}): {r.text[:300]}")
    text = (r.json().get("text") or "").strip()
    if not text:
        raise TranscriptionError("transcription came back empty")
    return text
