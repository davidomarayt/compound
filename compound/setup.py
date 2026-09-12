"""`compound setup`: write .env without editing files by hand.

Asks for the Telegram token (checks it with getMe), the Anthropic key, optionally a speech-to-text
key, writes .env, then waits for the owner to send /start and records their user id.
"""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

import httpx

from compound.config import ROOT

TG = "https://api.telegram.org/bot{token}/{method}"


def read_env(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.exists():
        return vals
    for ln in path.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        vals[k.strip()] = v.strip()
    return vals


def write_env(path: Path, updates: dict[str, str], template: Path) -> None:
    """Rewrite .env from the template layout, keeping existing values and applying updates."""
    current = read_env(path)
    current.update({k: v for k, v in updates.items() if v is not None})
    out: list[str] = []
    seen: set[str] = set()
    src = template if template.exists() else path
    for ln in src.read_text(encoding="utf-8").splitlines() if src.exists() else []:
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.partition("=")[0].strip()
            seen.add(k)
            out.append(f"{k}={current.get(k, s.partition('=')[2].strip())}")
        else:
            out.append(ln)
    for k, v in current.items():
        if k not in seen:
            out.append(f"{k}={v}")
    path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")


def tg(token: str, method: str, **params):
    r = httpx.get(TG.format(token=token, method=method), params=params, timeout=40.0)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description") or f"HTTP {r.status_code}")
    return data["result"]


def _ask(prompt: str, secret: bool = False, default: str = "") -> str:
    hint = " [keep current]" if default else ""
    val = (getpass.getpass(prompt + hint + ": ") if secret else input(prompt + hint + ": ")).strip()
    return val or default


def run_setup(env_path: Path | None = None, skip_verify: bool = False) -> int:
    env_path = env_path or ROOT / ".env"
    template = ROOT / ".env.example"
    current = read_env(env_path)
    print("Compound setup. Press Enter to keep a current value or skip an optional one.\n")

    token = _ask("Telegram bot token (from @BotFather)", secret=True, default=current.get("TELEGRAM_BOT_TOKEN", ""))
    if not token:
        print("A bot token is required.", file=sys.stderr)
        return 2
    bot_username = ""
    if not skip_verify:
        try:
            me = tg(token, "getMe")
            bot_username = me.get("username", "")
            print(f"  ok: bot is @{bot_username}")
        except Exception as e:  # noqa: BLE001
            print(f"  Telegram rejected that token: {e}", file=sys.stderr)
            return 2

    anthropic_key = _ask("Anthropic API key (optional for now)", secret=True, default=current.get("ANTHROPIC_API_KEY", ""))
    stt_key = _ask("Speech-to-text API key (optional; OpenAI or Groq)", secret=True, default=current.get("STT_API_KEY", ""))
    updates = {"TELEGRAM_BOT_TOKEN": token, "ANTHROPIC_API_KEY": anthropic_key, "STT_API_KEY": stt_key}
    if stt_key:
        updates["STT_PROVIDER"] = "openai"
        if stt_key.startswith("gsk_"):
            updates["STT_BASE_URL"] = "https://api.groq.com/openai/v1"
            updates["STT_MODEL"] = "whisper-large-v3-turbo"
    write_env(env_path, updates, template)
    print(f"  wrote {env_path}")

    if skip_verify:
        return 0

    owner = current.get("TELEGRAM_OWNER_ID", "")
    if owner:
        print(f"  owner id already set: {owner}")
    else:
        print(f"\nNow open Telegram, find @{bot_username or 'your bot'} and send it /start. Waiting…")
        offset = 0
        try:
            for u in tg(token, "getUpdates", timeout=0):
                offset = u["update_id"] + 1
            while True:
                for u in tg(token, "getUpdates", offset=offset, timeout=30):
                    offset = u["update_id"] + 1
                    msg = u.get("message") or {}
                    frm = msg.get("from") or {}
                    if frm.get("id"):
                        owner = str(frm["id"])
                        break
                if owner:
                    break
        except KeyboardInterrupt:
            print("\nStopped. Run `compound setup` again to finish linking.")
            return 1
        write_env(env_path, {"TELEGRAM_OWNER_ID": owner}, template)
        name = (frm.get("first_name") or "") + (" @" + frm["username"] if frm.get("username") else "")
        print(f"  linked to {name.strip()} (id {owner})")
        try:
            tg(token, "sendMessage", chat_id=owner, text="Linked. This bot now answers only you. Start it with: compound run")
        except Exception:  # noqa: BLE001
            pass

    print("\nDone. Start the pipeline with:\n  compound run\nThen send /poll in Telegram.")
    return 0
