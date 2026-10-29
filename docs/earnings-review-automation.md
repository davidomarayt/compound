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
2. **ChatGPT: Compound Company Review** runs each morning in Europe/Dublin. It reviews
   existing content and can publish one genuinely distinct company analysis per Dublin
   calendar day under the publication protocol below. Verified corrections and updates to
   existing company pages and articles may also publish automatically under the extension below. It checks existing PRs and published work before starting, and reports
   verified live articles, useful drafts and meaningful failures. Its active schedule is
   managed in ChatGPT, not by this repository file.

The original SEC ingestion workflow continues refreshing company results automatically.
On 28 October 2026 the publisher authorised automatic publication of new company analysis
when every publication gate passes. This extends the scheduled ChatGPT agent; the deterministic
GitHub audit still only writes review records. No new API-based publisher is introduced.

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


## New-article publication protocol (authorised 28 October 2026)

The scheduled agent may create and merge a narrowly scoped publication PR without another
publisher confirmation for a genuinely new company-analysis article passing ALL checks.
The 29 October extension below also authorises verified existing-content updates. A held
article stays a draft.

1. Select a material, source-confirmed change in business economics: margins, guidance,
   capital spending, cash conversion, segment performance or a comparable distinct story.
   Explain what the article teaches beyond the company's results announcement. No daily
   output quota, generic evergreen filler, price prediction or routine quarterly recap.
2. Read all editorial indexes, actual related articles, open publication PRs and recent
   Mag 7 publications. If the reader question is already answered, prepare an update to
   its canonical article instead. Avoid a competing article about the same company and
   event. Check the latest publishing branch again immediately before merging.
3. Use at least two directly inspected primary documents where available, including the
   relevant filing or official results release. Maintain a claim/evidence table with
   exact URLs, quoted passages, fiscal periods, units and arithmetic. Quotes must follow
   source copyright limits. Distinguish facts, management guidance and scenario assumptions.
   A second deliberate fact-checking pass must verify each material assertion against
   those sources; record unresolved contradictions and hold publication if any remain.
4. Use authentic, topic-specific licensed photography, with full source, credit, permission
   basis, accurate alt text and archive date when applicable. Follow AGENTS.md metadata.
   No generated cover, reused unrelated photo or unlicensed news-agency image.
5. Give the article a stable canonical URL, clear title/description and links to its
   company dashboard, earnings hub and relevant existing research. Preserve the original
   dates and URLs of all existing content.
6. Save an audit record in monitoring/company-publications/<story-fingerprint>.json with
   company, story thesis, source documents, duplicate checks, claim checks, image provenance,
   article path and gate results. Fingerprint company + event + thesis, not the run time.
   Record proposed/held/published states truthfully. Search PR bodies for that fingerprint
   so reruns resume the same work. Never treat a failed run as an invitation to republish.
7. Before merging, run appropriate offline tests, process/validate images, build the site,
   inspect the rendered article, cover and actual Open Graph/Twitter image, and confirm
   the checks apply to the exact PR head. Fix failures or leave a draft; do not bypass
   failing checks, protected-branch rules, permissions or unavailable verification.
8. Merge only the verified publication PR with an expected-head SHA. The existing site
   workflow is triggered by content changes to the publishing branch. Observe deployment
   completion and inspect the live canonical page and social image before reporting it
   as published. If a merge succeeded but deployment did not, report that precise state
   and recover the same publication rather than creating another article.
9. Limit this agent to one new article per Europe/Dublin calendar day, including manual
   reruns. Check publication records and already-merged PRs before writing or merging.
   Do not overlap an active publication attempt. Existing independent pipelines keep
   their own schedules, but their recent articles count for topical duplication checks.
10. Do not send email/social messages, modify unrelated publishing systems, add paid model
    dependencies or run live LLM tests. Report the live URL and a concise audit summary
    after success; report a specific blocker when publication is held.

The agent performs these checks as a workflow; configuring this protocol is not evidence
that any particular article has passed them. A requested immediate run is also not proof
that publication has completed.

## Existing-content automatic publication (authorised 29 October 2026)

The publisher explicitly requested automatic publication of these updates in future.
This supersedes earlier draft-only restrictions for bounded, source-verified corrections
and additions to existing company earnings pages and company analysis articles. No further
publisher review is required when the applicable checks pass.

- Apply the same primary-source verification, separate claim-by-claim fact-check, audit
  record, offline tests, image validation, full build, rendered-page/social-image inspection,
  exact-head CI and expected-head-SHA merge requirements as the new-article protocol.
- Preserve canonical URLs, original publication dates, historical context and valid photo
  provenance. Add dated updates where appropriate. Existing suitable licensed photographs
  may remain; a new photograph is not required merely because the text changes.
- Keep the five-company review budget. The one-new-article-per-Dublin-day limit remains
  unchanged and applies to new articles, not corrections on existing canonical pages.
- Resume relevant existing maintenance drafts, including Meta PR #62, after rechecking
  their current scope, sources and exact head. This does not authorise arbitrary unrelated PRs.
- Resolve recoverable build and asset-preparation problems within scope; do not repeatedly
  stop at the same fixable missing-cache issue. Do not bypass failures or substitute
  generated/unlicensed/unrelated images. Hold with a precise blocker when verification
  remains unavailable.
- Merge eligible maintenance PRs without asking for confirmation. Verify successful site
  deployment and live changed text and social image before reporting an update as live.
  Record the truthful publication state and notify the publisher with the live link.

No publication quota, paid API dependency, live LLM test, third-party message or social post
is authorised by this extension. Configuring this permission does not itself publish content.
