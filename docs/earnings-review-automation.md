# Automated company earnings and article maintenance

This adds an editorial review layer to the existing SEC earnings monitor. It does not
replace the monitor, change its publication gates, or create quarterly article duplicates.

## Two cooperating jobs

1. **GitHub Actions: Company Earnings Review Queue** runs daily at 06:41 UTC and whenever
   its implementation changes on the publishing branch. It audits all saved profiles,
   maps published company articles using explicit ticker tags (falling back to company
   links), and commits a durable queue/report under `monitoring/`. It makes no model calls
   and needs no new API secret or server. The workflow uses the existing earnings writer
   concurrency group and always checks out the latest publishing branch.
2. **ChatGPT: Compound Company Review** runs each morning in Europe/Dublin. It reads the
   queue and current primary sources, handles a bounded batch, and prepares draft PRs
   for warranted corrections to existing pages/articles. It checks existing open PRs
   before creating work. It reports new drafts, meaningful failures or decisions needed;
   unchanged checks do not need notifications. Its active schedule is managed in ChatGPT,
   not by this repository file.

The original SEC ingestion workflow continues refreshing company results automatically.
The new layer automates auditing, research and preparation. Editorial changes remain draft
PRs for review; this does not add autonomous publication of financial commentary.

## Durable review state

`monitoring/earnings-review-queue.json` contains evidence fingerprints, input paths,
severity, saved filing details, review status and decision notes. `monitoring/earnings-review.md`
is the readable queue. These are public repository artifacts: store only public company
information and editorial decisions, never credentials or private notes.

A rerun preserves decisions for unchanged evidence. Changes to source data or article text
create a new review item and retire the previous fingerprint. Changing only the profile's
`updated` timestamp does not reopen an article. A disappeared alert is described as retired,
not as an independently verified fix. State is written atomically under an exclusive lock;
invalid checkpoints fail visibly instead of silently resetting the review history.

```bash
python scripts/earnings_review.py
python scripts/earnings_review.py --resolve JOB_ID --decision reviewed --note 'Evidence checked; no change required because ...'
python scripts/earnings_review.py --resolve JOB_ID --decision drafted --note 'Prepared exact correction with source and period' --pr-url https://github.com/davidomarayt/compound/pull/NUMBER
```

A drafted decision must point to an actual PR. Keep it in that PR alongside the edit.
Until the PR is merged, future runs search for the fingerprint in open PR bodies and avoid
creating duplicates. If a PR is closed without merging, explicitly re-evaluate the proposal;
never treat closure as acceptance. `reviewed` means a human/agent recorded a supported
assessment, not that the structural auditor independently verified every figure.

## Review rules

- Read AGENTS.md and the topic indexes before proposing editorial work. Improve existing
  canonical company pages and articles; do not generate quarter-by-quarter article spam.
- Verify issuer CIK, accession, fiscal year, fiscal quarter, currency, units and period end.
  Do not infer a fiscal quarter from the calendar month. Distinguish full-year totals from
  standalone quarters; do not fabricate Q4 by subtracting annual and YTD figures.
- Treat 8-K/6-K earnings exhibits as potentially valid primary releases. Do not pretend a
  release is a 10-Q. Missing prior-year comparisons can remain missing; never invent them.
- Keep GAAP and adjusted measures separate. Distinguish consolidated profit from profit
  attributable to shareholders and identify whether figures are millions or billions.
- Use official filings and company investor-relations releases. Article source metadata is
  a lead to verify, not proof. Search snippets and the saved dataset alone are not enough
  to establish that an edit is correct.
- A newer filing than an article's review date is a reason to inspect it, not evidence that
  a historical statement is wrong. Preserve historical context and original publication
  dates. Update review dates only after a substantive source check.
- If a page cannot be fetched or evidence conflicts, keep the item pending with a clear
  explanation. Never replace valid data with an empty response, estimates or model memory.
- Existing photographs and credits stay intact. The worker has no need to generate images.
- Run targeted offline financial-data tests and build/render checks appropriate to the
  actual change. Do not run live LLM tests. Confirm the publishing branch is current before
  preparing a patch, and never overwrite unrelated concurrent updates.

## Batch and cost control

The deterministic audit covers the whole saved universe without paid LLM calls. The editorial
automation handles at most five company reviews per run, prioritising up to two data/coverage
issues and three changed-article reviews. It can use remaining slots for baseline article
reviews. It should preserve progress in review decisions and draft PRs, not run unbounded
retry loops. Source failures get at most two fetch attempts in a run and are revisited later.
No claim is made of a hard euro spending cap for the ChatGPT task; account limits apply.

## Validation and coverage limits

Run `python -m pytest -q tests/test_earnings_review.py`. The audit catches structural
inconsistencies, identity mismatches, unsupported periods, malformed metrics, missing
coverage and articles needing assessment. It does not prove freshness relative to every
worldwide earnings release, validate sentiment, or automatically fix figures. International
and private companies without a supported mapping remain explicit review items.
