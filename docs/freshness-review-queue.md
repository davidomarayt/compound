# Compound Review Queue

A private maintenance workflow for ten existing electricity and solar pages. It captures
SEAI/CRU evidence, saves resumable jobs, prepares exact before/after edits, and records
approve/dismiss feedback. It does not publish, modify content, execute model-provided code,
or send Telegram messages. The existing publishing pipeline remains separate.

## Run

From the repository with its normal dependencies installed:

```bash
python -m compound.freshness check
python -m compound.freshness serve
```

The first command captures sources with **no model spend**. The second prints the loopback
URL and a fresh password (username `owner`). Do not expose this plain HTTP server publicly.
For a remote server use `ssh -L 8765:127.0.0.1:8765 user@server` and browse localhost.

For drafting, set `ANTHROPIC_API_KEY` and `FRESHNESS_MODEL` in the existing private `.env`,
then run `python -m compound.freshness check --ai`. Model selection is explicit; no subscription
or existing publishing model is silently repurposed. Use an API account spending limit as the
monetary backstop. This pilot enforces **token reservations, not a euro/dollar cap**.

The first observation audits the current page against current evidence; it does not claim
that the source changed historically. Unchanged source/page combinations are deduplicated.
Each job retains its page text and source snapshot. Approval checks that page content has not
changed since drafting. Approval means accepted proposal, not publication. Use **Download proposed patch** to export the exact change without modifying source files. Apply accepted edits
through the normal repository review process, run calculator tests where appropriate, and publish
through the existing pipeline. A `no_change` result is source-specific, not a whole-page accuracy badge.

## Schedule on the existing Linux host

After merging/installing this branch and configuring the API, install the included units:

```bash
sudo install -m 644 deploy/compound-freshness.service deploy/compound-freshness.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now compound-freshness.timer
systemctl list-timers compound-freshness.timer
```

The timer runs daily around 06:00 Europe/Dublin. It is not activated by committing these files.
It needs the existing `/srv/compound` layout, a writable data directory, and network access.
The worker is capped at four model calls per run, three attempts per job, 200,000 reserved
input/output tokens per UTC day, and six minutes per service execution. UTF-8 input bytes plus
2,500 output tokens form a conservative reservation; failed calls keep their reservation.
An SDK request has no automatic retries, so hidden retries cannot bypass the allowance.
Worker retries occur on subsequent runs. Held or exhausted jobs require an explicit retry.

Snapshots, job state, feedback, budget and memory proposals live in `data/freshness.sqlite3`.
Back up this file with SQLite's backup API; do not copy a live WAL database file alone. Do not
commit the database or serve it under `public/`. An OS lock excludes overlapping workers;
after a crash, saved running jobs return to the queue within their attempt allowance.

## Memory and scope

Repeated identical human feedback (at least twice) becomes a proposed editorial rule.
Only approved rules enter future prompts. `python -m compound.freshness reflect` also runs
this consolidation. This is deliberately modest feedback memory, not Anthropic's managed
Dreams product and not model training. Review dates and changing facts against fresh sources.

Mappings are in `config/freshness.json`. Add official hosts to the code allowlist only after
review. All redirects are checked, response size/time are bounded, and browser challenge pages
are rejected. The pilot does not monitor individual supplier prices. Source failures are shown
in the dashboard and preserve earlier evidence; a failed fetch never counts as a fresh check.

Calculator source files are documented in the configuration for impact review. The AI never
edits their formulas. Run existing arithmetic checks with `node tests/tools_arithmetic.cjs`
and `pytest -q tests/test_solar_hub.py tests/test_budget_2027_energy.py` before publishing any
related manual calculator changes. Automatic calculator impact analysis, draft PR publication,
and semantic memory consolidation are later extensions, not enabled features of this pilot.

## Validation

`pytest -q tests/test_freshness.py` exercises deduplication, source failures, crash recovery,
evidence rejection, budget limits, stale approvals, access controls and feedback memory.
