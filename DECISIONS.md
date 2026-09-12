# Decisions

Hard-to-reverse choices, with the reasoning, so they can be challenged before launch.

## 1. Site: Python static generator, content in git (recommended; please confirm)

The brief offered Ghost or Astro/Next + headless CMS and asked for the option with the least custom
code for draft → pending → published. Session one builds the simplest thing that gives that
workflow end to end:

- **Pending queue lives in the pipeline's SQLite, not in a CMS.** Drafts are rows. A preview is an
  unlisted, `noindex` page at `/preview/<random-token>/` rendered from the row. That is all a
  "pending" state needs.
- **Publish = write one markdown file to `content/<pillar>/<slug>.md` and rebuild `public/`.**
  Content is plain files in this repo, so the figures block and source list are diffable and
  auditable forever, and there is no CMS account, token or API to break.
- **One process, one language.** Bot, poller, LLM calls and site build are one Python service on
  one €5 VPS with Caddy serving `public/`. Previews appear instantly (same directory), no build
  pipeline or second host.

Why not Ghost: it would give a nice editor and a native newsletter, but the three-column pillar
homepage needs a custom Handlebars theme anyway, the pipeline would need Admin API JWT plumbing,
and previews/publishing would round-trip through another system. Ghost's main advantage (native
email list) is covered by Kit/MailerLite, which the brief already picked.

Why not Astro/Next: a second language and toolchain, and a deploy step between "approve" and
"live". Fine later if the theme outgrows Jinja templates; the content files would carry over
unchanged.

Switching later is cheap: `Pipeline.publish()` is the only function that touches the site. A
Ghost or Astro adapter is ~60 lines that replace the markdown write + build.

## 2. URL structure (fixed by the brief, implemented as given)

`/wealth/<slug>/`, `/health/<slug>/`, `/happiness/<slug>/`, `/tag/<topic>/`. Trailing slash,
directory-style output so any static host serves it.

## 3. Hosting: one small VPS + Caddy (proposed)

Cheapest boring option that also serves previews without a build step. `deploy/` has a systemd
unit and a Caddyfile. Alternative: keep the pipeline on the VPS and rsync `public/` to a static
host (set `DEPLOY_COMMAND`). Not yet chosen; no code depends on it.

## 4. Speech to text: any OpenAI-compatible transcription endpoint

Whisper-style endpoints (OpenAI, Groq) accept Telegram's OGG/Opus voice notes directly and cost
cents. Configurable base URL so the provider can be swapped without code. `STT_PROVIDER=none`
keeps the bot usable with typed answers until a key is set.

## 5. Model: Claude Opus 5 with structured outputs

Questions at medium effort, drafts at high effort, both returning validated JSON so the bot never
parses prose. The figures block is a schema field, not a convention.

## 6. Human approval is enforced in code, not just policy

`Pipeline.publish()` is the only writer to `content/`; it refuses without an `approved_by` string
and a draft in `pending` status. The bot passes the Telegram username; the CLI requires `--yes`.
Polling, question generation and drafting never call it.
