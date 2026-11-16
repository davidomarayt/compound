# Compound overnight technical SEO, UX and revenue — 2026-11-16 (Europe/Dublin)

**Worker:** roles **7. Technical SEO**, **8. UX & Conversion** and **9. Revenue Optimisation**, independent of the four 00:15 roles. Current GitHub default and Pages push branch verified as `claude/clever-babbage-uibieq` from live GitHub metadata and `.github/workflows/site.yml` **before source changes**. Read `AGENTS.md`, efficiency runbook, index/inventory, 12–15 Nov agent records, 16 Nov discovery/content records, current open PRs and company publishing ledgers, source templates, JS and tests. Worker created exactly **one substantive DRAFT PR**, [#150](https://github.com/davidomarayt/compound/pull/150), unmerged and unpublished; the research role's separate report is [research.md](research.md).

## 7. Technical SEO — source-accuracy bug fixed in draft (NOT LIVE)

### Independently observable source and published-page discrepancy

- Existing canonical [`https://compound.ie/wealth/earnings/`](https://compound.ie/wealth/earnings/) was fetched **16 Nov 2026**. In the "Latest company earnings" section, the live page both includes an actual `COMPANY RESULTS · PUBLISHED` entry (VYLR, pro forma Q3) **and** calls the same ten mixed items `10 most recently filed reports` and `Showing 10 latest filings`. It additionally refers to all search-index items as verified *reports* even though the publisher includes issuer announcements.
- Root cause verified in existing `compound/site/build.py`: `archive_result()` sets `from_release=True` when a latest issuer company-results announcement is used; the server-rendered cards already label that source differently. However, `compound/site/earnings_archive.py` constructs `report_search_index` without preserving `from_release`. The client `compound/site/static/earnings-report-search.js` consequently labels **every filtered result** `SEC-VERIFIED FINANCIAL REPORT · FILED`, even source-checked company-release entries. The false filing label is meaningful in source credibility and search-result interpretation; no SEO ranking benefit is claimed.
- `AGENTS.md`, 15 Nov source inventory and editorial index reviewed. Fix applies to an existing canonical URL, creates no article, content duplication or invented financial value. Open draft [#149](https://github.com/davidomarayt/compound/pull/149) owns PIA/CGT; open #127, #120, #119, #57, #43 do not overlap earnings search provenance. Recent #143 stock breadcrumbs are a different template/issue; this worker deliberately prioritised financial-source honesty over another breadcrumb tweak.

### Exactly one [DRAFT PR #150](https://github.com/davidomarayt/compound/pull/150)

- Branch: `agents/research-engineering-2026-11-16-earnings-provenance` off verified publishing branch; initial and **current proposed head** `9693444241915f3be665482c1fb8d1530b58d721`. The branch is one operational-report commit behind the updated default branch, with no overlapping tracked source files in compare, so QA must recheck base/head and conflicts.
- `compound/site/earnings_archive.py`: add explicit boolean `from_release` in search-index JSON, retaining provenance already known to build, without any change in ordering, finance figures, report counts, or URLs.
- `compound/site/static/earnings-report-search.js`: continue using safe `textContent`/URL guard, but display `COMPANY RESULTS · PUBLISHED` for flagged issuer releases and `SEC-VERIFIED FINANCIAL REPORT · FILED` for SEC filings. Use source-neutral count when resetting the search.
- `compound/site/templates/earnings_hub.html`: correct descriptions and initial results count to say **reports and releases**, dynamically using `report_cards|length` rather than an incorrect constant 10.
- `tests/test_earnings_release_provenance.py`: assert type flag survives index generation (including explicit false for SEC filing), source-appropriate labels in both template/JS, and no stale `10 latest filings` text. The new test does not invent company results; its example companies are clearly fixtures.

**Diff inspected:** compare current publishing ref to feature head shows **exactly these four files**, 4 commits, no staging of article/asset/publication/consent or account changes. [PR patch](https://github.com/davidomarayt/compound/pull/150/files) and [source file](../../../../compound/site/earnings_archive.py) can be independently reviewed.

### Exact-head verification and remaining gate

- [GitHub Actions PR CI run **43795799929**](https://github.com/davidomarayt/compound/actions/runs/43795799929) was explicitly tied to candidate head `9693444241915f3be665482c1fb8d1530b58d721`. The **test job completed SUCCESS**, including `pytest -q`: **340 passed, 2 subtests passed** (03:04:41 UTC), six additional spending votes tests, existing Node/financial arithmetic checks, Python compilation. Our new tests are included in this pytest total. The changed JS `earnings-report-search.js` was additionally fetched at exact candidate blob `11d422a91ba3bf217581498417324e9c197f126c` and **syntax-parsed without execution** in the current V8 tool runtime; this is a parser-only check, not a browser interaction or Node-specific CI claim.
- **At last CI checkpoint the `performance` job remained IN_PROGRESS at `compound build`**. Successful full static build, later performance/Lighthouse steps, generated output and public deployment were **NOT YET VERIFIED**. The GitHub combined status also contains an unrelated `compound-solar-api` Vercel success; that is not evidence of this site's Pages CI or publication. Independent 06:30 QA must recheck current exact head, all required CI jobs, built JS/result labels, count, canonical/index flags, ad loader/consent, PR state and mergeability.
- The local execution container cannot resolve `github.com` for a full repository clone; no local full build claim was made. All tests referred to above are attached to the exact GitHub PR head.

**Risk:** low, source classification and HTML/JS labels only, no issuer numbers; the code is careful not to infer SEC verification of an issuer announcement. **Rollback:** revert only the four PR files. The staging PR is **OPEN / DRAFT / UNMERGED**, so **0 newly merged, deployed or verified-live URLs** from this worker. Do not publish/merge before independent QA.

**Outcome:** TECHNICAL SEO / CONTENT INTEGRITY — 1 source-inaccuracy remediation **staged with tests**, awaiting build and QA.

## 8. UX & Conversion — truthful archive labels, source-level only

- Each company search result now identifies whether its date is an issuer result-release date or an SEC-filing date; the reset status and initial count no longer announce SEC filings exclusively for a mixed source list. This improves the **reader's context when comparing the financial reporting basis** and makes accessible `role=status` announcements truthful. Dynamic count handles fewer than ten entries without falsely announcing ten reports.
- Search filtering, keyboard input, focus, labels, company URLs, cards, DOM-safe text rendering, styles and page layout remain unchanged. No browser screen-reader trial, mobile screenshot, conversion instrumentation or measured uplift performed. The independent CI/build/QA and eventual live comparison are prerequisites to calling it a user-facing improvement.

**Outcome:** UX — same draft PR, one precise source-transparency improvement, **0 measured conversions**.

## 9. Revenue Optimisation — BLOCKED_DATA_ACCESS, backoff respected

- Latest actual permitted source check was **14 November 2026**, recorded in [14 Nov engineering.md](../2026-11-14/engineering.md): Supermetrics AdSense `ADM` account authentication succeeded for account discovery, but actual earnings/reporting returned **`TRIAL_EXPIRED`** (trial date 19 Oct 2026). GSC `GW` and GA4 `GAWA` returned **`NOT_AUTHENTICATED`**. These statuses were **not rechecked on 16 Nov** because the 7-day failed-query backoff applies absent reconnection evidence (ordinary retry no earlier than **21 Nov**).
- Consequently there are **no newly verified page RPM, ad requests, ad revenue, CTR, visitor conversions or attributable earnings** to base changes on. The worker did not invent a trend or recommend a speculative placement change. No app was connected and no paid integration/subscription triggered.
- `compound/site/templates/base.html` (as documented in prior worker checks) and the 16 Nov PR diff leave the standard site AdSense loader and consent/privacy controls untouched. Publishing ads independent of human-review status remains the approved standard; **actual ad fill and compliance were not independently verified today**.

**Outcome:** REVENUE — `BLOCKED_DATA_ACCESS`, no metrics or ad account changes.

## Independent gate and counts

**Research:** 1 distinct primary-source CSO 2025 agricultural-land brief only (see [research.md](research.md)), 0 articles/URLs. **Private Company:** `NO_MATERIAL_PROFILE_CHANGE` after issuer/ledger dedup, 0 edits. **Technical SEO:** 1 draft low-risk provenance fix (#150), tests passed, performance build/QA pending. **UX:** same draft improves user-facing source clarity, no separate PR. **Revenue:** blocked, no data or speculative account changes. Group **one substantive PR total**, **zero production merges/deployments**. Independent 06:30 Editor-in-Chief QA owns any decision after exact-head full CI.
