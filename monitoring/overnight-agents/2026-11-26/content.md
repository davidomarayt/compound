# Compound overnight content — 2026-11-26 (Europe/Dublin)

One substantive draft PR for the group: [#289](https://github.com/davidomarayt/compound/pull/289), head 4d8caaf9b0941517b4ced2a269e901c2ba057e58, base caf84557f698837f1021e8a345a274a85ba6ebd3.

## 3. Internal Linking — review-only (recommendation)

[KickstartSaver article](https://compound.ie/news/bank-of-ireland-5-percent-savings-account/) (published 25 Nov 22:09 by a separate workflow) links only to /compound-interest-calculator/ (related_tools). Its "How does DIRT affect the 5% rate?" section and its emergency-fund paragraph are natural homes for /dirt-calculator/, /regular-savings-calculator/ and /emergency-fund-calculator/ (all three slugs exist in content/tools.yml). Not staged tonight: the one-PR limit is used by #289, and the article is under 3 hours old and owned by another publisher, so editing it overnight risks colliding with that workflow. Rendered links not checked. Suggested for a later run or the article's owner.

## 4. Content Freshness — review-only; one check blocked

- [Revenue DIRT rate](https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx) (published 24 Apr 2026, fetched 26 Nov): "deducted at a rate of 33%"; no announced change. KickstartSaver article's 33% DIRT and 5% → 3.35% arithmetic agree. No change.
- [HEA course fees](https://hea.ie/funding-governance-performance/funding/student-finance/course-fees/) (no page date, fetched 26 Nov): student contribution "€2,350 per year (2026/27 academic year)". College-cost calculator default €2,350 and source title agree. No change.
- MyFutureFund (23 to under 60, over €20,000, 1.5/1.5/0.5% rising to 6/6/2, €80,000 cap): BLOCKED. myfuturefund.ie (2 pages), citizensinformation.ie and gov.ie all returned client errors to the fetcher. Not verified; no change; do not record it as checked.
- Label fixes in #289 change display text only; no rates, thresholds or formulas.

## Validation and handoff

- Tests on exact head: pytest 423 passed + 2 subtests; tools arithmetic passed; new guard fails on base. Static build not run locally (pre-existing image-cache requirement). PR CI was pending at write time; no CI success claimed.
- PR state at creation: OPEN, DRAFT, unmerged. Review request to the author was refused by GitHub (author cannot review own PR).
- Branch note: work is on `claude/project-thread-3mlg9l` (session-assigned branch). A duplicate push to `agents/discovery-content-2026-11-26-comma-labels` (same commit) could not be deleted (proxy hung up); it has no PR and can be deleted.
- These two reports are committed on the PR branch, not pushed to production directly, so QA should read them from #289.
- Risk low; rollback = revert the label/test commit. No merges, deployments, settings, secrets, ads or consent changes. Standard ads untouched and independent of review. Nothing claimed live; final QA is the 06:17 task.

Totals: 1 draft PR, 10 labels in 7 calculators staged, 0 new pages, 0 merges, 0 verified-live.
