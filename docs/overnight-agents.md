# Compound.ie overnight improvement agents

Status: approved by publisher 11 November 2026. Use the repository's current default/production publishing branch, verified at runtime; it was `claude/clever-babbage-uibieq` at setup. This runbook is for the nightly ChatGPT-scheduled improvement agents, not a replacement for existing earnings/news/company/evergreen publication workflows.

## Objective and schedule

Ten distinct agents collaborate overnight in four scheduled runs (two multi-agent specialist runs, one independent QA run and one report), using `Europe/Dublin` local civil time (including daylight-saving changes). Scheduling is external to GitHub and lives in ChatGPT Automations. Four runs are used to stay within the account's 15-active-automation limit without pausing unrelated existing tasks.

| Dublin time | Scheduled group | Agent ownership |
| --- | --- | --- |
| 00:15 | Discovery + existing-content upgrades | Search Console Growth; Content Gap; Internal Linking; Content Freshness |
| 03:00 | Research + engineering | Original Research; Private Company Intelligence; Technical SEO; UX & Conversion; Revenue Optimisation |
| 06:30 | Final editorial gate | Editor-in-Chief QA |
| 08:00 | Morning report | Aggregate verified overnight outcomes only |

Scheduling does not imply completion by a clock time. Every group independently checks unfinished work, existing PRs and newer changes before acting. Never claim a later task was completed merely because its schedule fired.

## Global contract for every run

1. Inspect `AGENTS.md`, `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, `data/content-inventory.json`, this runbook, relevant site code and recent open/merged PRs; inspect existing company/news/evergreen publication ledgers. Resolve the active publishing branch before writing. Respect related workflows including 23:30 earnings, 07:00 private companies and 08:00 daily company analysis.
2. Use trustworthy fresh data. GSC/GA4/AdSense numbers require authorised access to those services (a third-party report is not proof of real-time access). When absent, write `not connected/not verified`, rely on permitted site/repo evidence, and do not invent clicks, impressions, CTR, earnings, revenue, positions or attribution.
3. Prefer improving the original canonical URL over duplicating search intent. Do not generate content merely for volume or perceived search rank. Use source-specific reasoning, genuinely new analysis and documented derivations for quantitative claims. Keep original URLs, publication dates, photo assets and credits intact. Never artificially update a reviewed/modified date without a substantive verified review.
4. Stage bounded work in a narrow PR based on the latest verified publishing branch; for each group prepare at most one substantive PR per night, except a small emergency correctness/security fix. Use a unique branch. Do not merge during the worker runs. A claim that a PR was opened is not a claim of publication. Never force-push or overwrite another agent's edits.
5. Attach to every PR the run date, owning agents, files/URLs affected, pre-change evidence, verification sources, test/build results, risk level, proposed rollback and explicit statement of any missing checks. Include `Overnight-Agents: YYYY-MM-DD` in the PR body for discoverability. No change required is a valid outcome. Proposed work that cannot be verified stays an unmerged draft/recommendation.
6. Save each worker's plain-text evidence and outcomes to a separate daily status record at `monitoring/overnight-agents/YYYY-MM-DD/<group>.md`. Files must be public-safe and avoid keys, personal analytics, tokens or sensitive user data. These status files can be committed directly to the publishing branch because they are operational reports, not user-facing site content. If a report path already exists, update only that path using its latest blob SHA. Avoid concurrently updating shared files.
7. Do not change pricing, ad-account settings, payment flows, auth, privacy/consent, production secrets, schema, or major site structure without separate approval. Changes likely to change AdSense ad loading, viewability, policy compliance or tracking require dedicated validation and should remain in a PR until explicitly safe.
8. Never introduce new automatically generated pages with Google-served ads absent genuine human editorial review/curation or a deployed-and-tested no-ads pending-review mechanism. Automated agent QA is not human review. If policy controls are uncertain, hold the page unmerged/unpublished. Existing factual corrections can proceed only after verified sourcing and normal checks. No generated synthetic/AI hero images; honour the documented licences/attribution/OG image policy.
9. Every test must run on the exact proposed commit, using existing project commands rather than guessing. Validate links, canonical and index flags, content inventory, code tests, static build, metadata and rendered changes as applicable. Fail closed when CI status, deployment verification or data provenance is missing.
10. Do not connect apps, pay for services, create advertising campaigns, send email, publish to social media, or perform real transactions as part of this programme. Do not claim a deployment succeeded until the public canonical page is fetched and validated.

## Distinct agent instructions

**Search Console Growth:** Where GSC is authorised, compare 7/28-day query-page impressions, clicks, CTR and rankings, accounting for lag; shortlist high-impression low-CTR pages and ranks around 5–20. Make selective, user-helpful title, introduction, FAQ or structured-data proposals without keyword stuffing. If no connected GSC, work only from identifiable on-site deficiencies and mark metric-based growth claims unverified.

**Content Gap:** Compare query intent and coverage across finance, PIA, pensions, stock and private-company pages. Use competitor or public-source research responsibly. Prioritise a small backlog by reader usefulness, source availability, overlap risk and existing URL to improve. Do not claim search volumes without actual query evidence. Do not auto-publish gap-filler pages.

**Internal Linking:** Suggest or implement a small set of truly relevant bidirectional contextual links, using existing canonical routes and meaningful anchor text. Avoid sitewide or templated spam and links to unpublished content. Validate every target and the rendered link.

**Content Freshness:** Check existing Irish tax, pensions, PIA, calculator and financial reference pages against original, dated official sources. Correct only verified material changes and properly attribute effective dates and scope; preserve historical context. High-stakes or ambiguous legal/tax/health claims become flagged review tasks, not speculative changes.

**Original Research:** Create a dated, source-linked research brief, table or reproducible calculation based on CSO, Revenue, Central Bank, SEC or issuer data. Show units, formulas, cutoffs, definitions, uncertainties and non-equivalence. If a strong genuinely original on-site enhancement exists, stage it for review; do not publish an unreviewed ad-supported article.

**Private Company Intelligence:** Maintain existing canonical OpenAI/Anthropic/SpaceX and other private-company profiles. Verify funding announcements/valuation/capex/revenue disclosures against primary material where possible, label estimates and rumours, and avoid asserting unconfirmed financials. Do not duplicate the existing 07:00 private-company story automation. Prefer researched annotations or proposals to update the existing page.

**Technical SEO:** Inspect technical indexing, title/meta/canonical/robots/sitemap/broken-link/structured-data defects. Prepare minimal code fixes and deterministic regression tests. Never mass-change index directives, redirects or canonical routing without explicit coverage, risk assessment and QA.

**UX & Conversion:** Review mobile usability, accessibility, navigation, stock-directory discoverability, calculator flows, source transparency and path to another relevant page. Stage low-risk, accessible improvements with screenshots or build-level evidence; do not add manipulative copy or unvalidated tracking.

**Revenue Optimisation:** If authorised AdSense and GA4 data is available, analyse aggregate page-level revenue and engagement while respecting privacy and consent; otherwise describe observable on-site monetisation issues as hypotheses, not measured improvements. Recommend compliant layout/site-speed fixes, with no ad-click encouragement or account-settings modifications. Never claim AdSense policy-centre clearance without access.

**Editor-in-Chief QA:** Read all four group ledgers and candidate PRs from the local Dublin date. Independently cross-check sources, article duplication, attribution/licensing, tests, exact PR head, build and deployment gate, user benefit, AdSense/manual-curation requirement, concurrency and rollback. Merge only the clearly safe, wholly verified changes using expected head SHA and after applicable CI on that exact head. For high-risk, unverified, policy-sensitive or in-progress changes, leave PR open and record why. Fetch public canonical URLs after deployment before marking live. Record merged, deployed, held, failed and skipped separately in `monitoring/overnight-agents/YYYY-MM-DD/qa.md`. No auto-merging without explicit review of evidence; automated QA is not a substitute for required human editorial curation.

**08:00 report:** Read all the daily ledgers, GitHub PR state, confirmed deployments and public URLs. Report agent-by-agent completed tasks, real source changes, merged/verified live URLs, open PRs, blockers, data integrations that were not connected, and 1–3 priorities. Classify `proposed`, `PR opened`, `merged`, `deployed`, `verified live` accurately. Never invent missing-stage outcomes. Include links to the dated GitHub files/PRs. Do not merge at reporting time.

## Conflict handling

- Group stage records are distinct files: `discovery.md`, `content.md`, `research.md`, `engineering.md`; QA writes `qa.md`. Report reads only.
- Each stage checks for an existing PR for the same canonical URL and run date; if another worker owns it, annotate or defer instead of writing over it. The 00:15 combined run must write both discovery.md and content.md; the 03:00 combined run must write research.md and engineering.md. Neither specialist run may merge.
- Do not modify the existing news/company publishing schedules and don't reuse their quota.
- If any stage is late or does not finish, QA and the report explicitly list it as pending.
- Target throughput is zero-to-two quality specialist PRs per night, not mandatory publishing. No-results nights are valid.
