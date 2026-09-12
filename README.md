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

## Research-led writing

Scheduled pieces are not written from memory. For each one the pipeline:

1. **Plans a topic around search demand.** Google autocomplete completions for seed phrases
   (`topics/seeds/<pillar>.md`, or built-in defaults) go to Claude, which picks a target query, title, slug,
   meta description, the questions the piece must answer, and the research to fetch.
2. **Builds a research pack.** PubMed (free NCBI API; meta-analyses, systematic reviews and trials in humans
   since 2015) for health and happiness; exact pages on trusted bodies (Citizens Information, Revenue, gov.ie,
   CSO, Central Bank, HSE, WHO, NHS, ...) for anything. Untrusted domains are dropped.
3. **Drafts from the pack only.** Every figure must quote its source verbatim; each is verified against the
   text of the page or abstract it cites. Fewer than `MIN_SOURCES` fetched sources holds the piece.
4. **Editor pass.** A second call scores the draft 0-10 against a rubric (accuracy against sources, honesty
   about evidence, usefulness, writing, safety). Below `EDITOR_MIN_SCORE` it is redrafted once with the
   editor's notes and re-scored; still below, it is held for you.
5. **Publishes with search metadata**: meta description, canonical link, Open Graph tags and schema.org
   Article markup, plus the sitemap and RSS feed that already existed.

`/unpublish <id>` removes a published piece (file deleted, site rebuilt, deploy command run).

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

## Using your Claude subscription instead of API credits

If Claude Code is installed and logged in on the machine running the bot, set `LLM_BACKEND=claude-code`
in `.env`. Every Claude call (triage, topic, questions, draft) then runs `claude -p --output-format json
--json-schema ...` locally with the same prompts, and is covered by the subscription that `claude` is
logged in with. `ANTHROPIC_API_KEY` is not used. Subscription usage limits apply, and Claude Code must be
runnable from the same user account as the bot (check with `claude --version`). This is Anthropic's
documented headless mode; it does not extract or reuse login tokens. The bot strips `ANTHROPIC_API_KEY`
from Claude Code's environment, because Claude Code would otherwise prefer the key to the login and bill it.

## Keeping the API bill down

Every Claude call is logged with its token counts (`llm ok: ... in=... out=...`). The levers, cheapest first:
`SCHEDULE_HOURS` (fewer scheduled pieces), `DRAFT_EFFORT=medium` (roughly halves draft cost),
`ANTHROPIC_MODEL=claude-sonnet-5` (about 2.5x cheaper per token than Opus), `MIN_RELEVANCE` (fewer news
drafts). Never run two copies of the bot on one token: they both fire the schedule. Set a monthly spend
limit in the Anthropic console as a backstop.

## Publish for free on GitHub Pages (bot on your own machine)

If the bot runs on a laptop or PC that stays on, the site itself can be served by GitHub Pages at no
cost. The bot commits each published article to `content/` and pushes; the `site.yml` workflow builds
`public/` and deploys it.

1. In the GitHub repo: Settings -> Pages -> Source: **GitHub Actions**. Then Custom domain: `compound.ie`
   (GitHub shows the DNS records it wants; they are the four `A` records below plus a `CNAME` for `www`).
2. At your domain's DNS: `A` records for `compound.ie` -> `185.199.108.153`, `185.199.109.153`,
   `185.199.110.153`, `185.199.111.153`; `CNAME` for `www` -> `<your-github-username>.github.io`.
   Tick "Enforce HTTPS" in the Pages settings once DNS has propagated.
3. In `.env`: `SITE_BASE_URL=https://compound.ie`, `PREVIEW_BASE_URL=http://localhost:8080` (previews stay
   local), and `DEPLOY_COMMAND=git add content && git commit -q -m "publish" && git push`.
4. Run `git push` once by hand in the project folder so Git stores your GitHub login; after that the bot's
   pushes need no prompt.

Keep the machine awake: on Windows, Settings -> System -> Power -> Screen and sleep -> Never when plugged
in, and set "closing the lid" to "Do nothing". The bot only runs while its window is open; to start it
automatically at login, create a Task Scheduler task that runs `python -m compound.cli run` in the
project folder.

## Deploy (one VPS)

On a fresh Ubuntu 22.04/24.04 server, as root:

```bash
curl -fsSL https://raw.githubusercontent.com/<you>/compound/main/deploy/bootstrap.sh -o bootstrap.sh
bash bootstrap.sh https://github.com/<you>/compound.git main
```

That installs Python, Caddy and Claude Code, creates the `compound` user, clones into `/srv/compound`,
builds the venv, writes a starter `.env` (Claude Code backend, site URL https://compound.ie) and
installs the systemd unit and Caddyfile. It then prints the three remaining steps: log Claude Code in
as the `compound` user, fill in the Telegram token and owner id, start the service. Point the domain's
A records at the server and Caddy issues HTTPS certificates itself. Re-running the script is safe: it
pulls the repo and reinstalls without touching `.env`.

By hand, the same thing is:

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
