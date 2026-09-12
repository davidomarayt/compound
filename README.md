# Compound

Content pipeline and site for [compound.ie](https://compound.ie): Health, Wealth, Happiness.

```
source poller ──► questions (Claude) ──► Telegram ──► your voice/text answers
      ──► draft + figures block (Claude) ──► preview page ──► ✅ Approve on Telegram ──► published
```

Nothing publishes without a tap. See `DECISIONS.md` for the choices behind the stack.

## Layout

```
compound/            Python package
  config.py          settings from .env
  db.py              SQLite schema + queries
  sources/           pollable sources (revenue.py first; add more here)
  poller.py          poll sources, queue new items
  llm.py             Claude calls (questions, drafts), structured outputs, fake backend
  prompts/           questions.md, draft.md
  verify.py          checks every figure's quote against the source text
  transcribe.py      voice note → text
  pipeline.py        the workflow; publish() is the only writer to content/
  bot.py             Telegram bot (review surface) + scheduled polling
  site/              static site generator, templates, CSS
  cli.py             `compound …` commands
style/voice-samples.md   paste your own sentences here; injected into the drafting prompt
content/<pillar>/    published articles (markdown + front matter, committed to git)
content/pages/       About, Contact, Privacy, Cookies, Disclaimer
public/              built site (gitignored) – serve this
data/                SQLite database (gitignored)
deploy/              systemd unit + Caddyfile
```

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
compound setup
```

`compound setup` asks for the Telegram bot token (from @BotFather), checks it, asks for the
Anthropic key and an optional speech-to-text key, writes `.env`, then waits for you to send
`/start` to the bot and records your Telegram user id. After that the bot ignores everyone else.
Run it again any time to change a key. `.env` is gitignored; never commit it.

Speech to text: any OpenAI-compatible endpoint. A Groq key (`gsk_…`) is detected and configured
automatically; an OpenAI key uses `whisper-1` at api.openai.com. Until a key is set, answer by text.

Then paste 20-30 of your own sentences into `style/voice-samples.md`, and set `SITE_BASE_URL` /
`PREVIEW_BASE_URL` in `.env` to wherever `public/` is served (defaults to http://localhost:8080).

## Prove the loop

Without spending anything (fake LLM, no Telegram):

```bash
COMPOUND_FAKE_LLM=1 compound simulate-item      # queues a fake Revenue item as 'new'
COMPOUND_FAKE_LLM=1 compound draft 1            # questions + draft, prints preview URL and checks
compound serve                                  # http://localhost:8080/preview/<token>/
COMPOUND_FAKE_LLM=1 compound publish 1 --yes    # writes content/wealth/<slug>.md, rebuilds
```

With Telegram and real keys:

```bash
compound run
```

Then either wait for the poller (every `POLL_INTERVAL_MINUTES`) or send `/poll`. On the first poll
of a source only the newest `FIRST_RUN_BACKFILL` item is queued; the rest are marked seen.

Every polled item is first triaged: a cheap Claude call scores it 0-10 for an everyday reader in Ireland and
writes a one-line reason. Anything under `MIN_RELEVANCE` (default 6) is skipped with that reason in Telegram;
`/open <id>` drafts it anyway. Set `MIN_RELEVANCE=0` to draft everything.

Don't want to be interviewed? Set `INTERVIEW=0` in `.env` and every new item goes straight to a draft
and the review message. `/draft <id>` also works on any item at any time.

Bot commands: `/queue`, `/open <id>`, `/draft [id]`, `/skip`, `/newpiece [pillar] <topic>`,
`/drop [id]`, `/poll`. Answer a question by replying to its message, or just send answers in order.
When every question is answered the draft is generated automatically and you get: headline,
summary, figures used (✅ quote verified in source, ❔ figure present but quote not verbatim,
⚠️ not found, 🗣 attributed to you), warnings, preview link, and Approve / Redraft / Drop buttons.

## Scheduled writing

Set `SCHEDULE_HOURS=6` (or any interval) and the running bot writes one evergreen piece per interval,
rotating through `SCHEDULE_PILLARS` (default health, wealth, happiness). Topics come from
`topics/<pillar>.md` (one per line, first unused line wins) or, if there is none, Claude proposes one
that does not overlap recent titles. `/auto [pillar]` in Telegram or `compound auto-once` runs a cycle now.

What happens to the draft depends on `AUTO_PUBLISH`: `off` (default) sends it for your ✅ like any other
draft; `verified` publishes it only when every figure verifies against its source and nothing is flagged,
holding anything doubtful for your tap; `always` publishes everything. Evergreen pieces are told to give
practical guidance rather than statistics, so a clean piece usually has no figures at all. The schedule
survives restarts (the last run time is stored in the database) and only runs while `compound run` is up.

## Keeping the API bill down

Every Claude call is logged with its token counts (`llm ok: ... in=... out=...`). The levers, cheapest first:
`SCHEDULE_HOURS` (fewer scheduled pieces), `DRAFT_EFFORT=medium` (roughly halves draft cost),
`ANTHROPIC_MODEL=claude-sonnet-5` (about 2.5x cheaper per token than Opus), `MIN_RELEVANCE` (fewer news
drafts). Never run two copies of the bot on one token: they both fire the schedule. Set a monthly spend
limit in the Anthropic console as a backstop.

## Deploy (one VPS)

```bash
sudo useradd -r -m -d /srv/compound compound
sudo -u compound git clone <repo> /srv/compound && cd /srv/compound
sudo -u compound python3 -m venv .venv && sudo -u compound .venv/bin/pip install -e .
# .env as above, then:
sudo cp deploy/compound.service /etc/systemd/system/ && sudo systemctl enable --now compound
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile && sudo systemctl reload caddy
```

`compound build` regenerates `public/` from `content/` at any time (e.g. after editing a page).

## Tests

```bash
pytest -q
```

## Adding a source

Subclass `compound.sources.base.Source`, implement `fetch()` returning `SourceItem`s newest first
(and `fetch_text()` if the default HTML-to-text is not good enough), register it in
`compound/sources/__init__.py`. Run `compound poll --dry-run` to see what it returns before it
goes live.
