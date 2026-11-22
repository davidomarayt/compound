# Compound.ie — Independent Editor-in-Chief QA, 22 November 2026 (Europe/Dublin)

**Agent 10:** automated independent QA, **not human editorial review or a publisher-policy clearance**. Checked at the 06:30 morning gate, following `docs/overnight-agents.md` and `AGENTS.md`. **Publishing branch:** `claude/clever-babbage-uibieq` (confirmed GitHub default and `.github/workflows/site.yml` push trigger); production branch before merges `dc536842bc2dd3dd834d6faa432f5e1a8ea4c3ba`.

**Outcome at reporting checkpoint:** **two narrow PRs approved and squash-merged with exact expected PR-head SHAs**, after independently checking official Revenue sources, the full six/eight-file scoped changes, exact-head test/static-build jobs, mergeability and rollback. **No newly changed public page marked VERIFIED_LIVE**, because the last merged production Pages deployment is still in progress. Two PRs merged is not two pages verified live.

## Independent review of four worker records and ten distinct roles

Read [discovery.md](discovery.md), [content.md](content.md), [research.md](research.md), [engineering.md](engineering.md), current PR bodies/patches, current GitHub source, existing editorial index/inventory, 22 Nov public canonical pages and primary Revenue evidence. These four daily files are present; this records actual work, not merely schedule assumptions.

| Agent / role | Verified actual output | QA status |
|---|---|---|
| 1. Search Console Growth | 21 Nov GSC `NOT_AUTHENTICATED` per dated discovery ledger; no fresh authenticated query/page metrics; no speculative CTR/ranking edits | `BLOCKED_DATA_ACCESS`; acknowledged |
| 2. Content Gap | Existing child-savings canonical identified and deduplicated against topic index, published CGT guide, calculator and other PRs; helped scope #243, no new URL | `STAGED` then `MERGED` via #243 |
| 3. Internal Linking | One contextual existing CGT guide link from child-savings worked example; live destination observed, no sitewide link farm | `STAGED` then `MERGED` via #243; new rendered link not yet verified live |
| 4. Content Freshness | Dated direct-share CGT article correction with preserved 33% historic example, CAT, DIRT, article publication/review data, original image | `STAGED` then `MERGED` via #243 |
| 5. Original Research | Source-checked independent Revenue rate change; no genuinely distinct new dataset/article, 12–21 Nov research deduplicated | `SKIPPED: NO_DISTINCT_RESEARCH` (valid no-action) |
| 6. Private Company Intelligence | Checked OpenAI/Canva/Blue Origin/Stripe official releases, existing 21 Nov publishing ledger; Anthropic/SpaceX public-stock classification observed | `SKIPPED: NO_MATERIAL_PROFILE_CHANGE` |
| 7. Technical SEO | Existing compound-interest calculator's JS engine, dateModified/asset caching, canonical metadata and date-sensitive CGT fixed in #244 | `STAGED` then `MERGED` via #244 |
| 8. UX & Conversion | Corrected calculator tax scenario explanatory text, 31% projections, versioned JS and date notes; no measured conversion claims | `STAGED` then `MERGED` via #244 |
| 9. Revenue Optimisation | Latest dated GA4/GSC `NOT_AUTHENTICATED` and AdSense data query `TRIAL_EXPIRED`; no valid analytics or ad yield results, no ad settings changed | `BLOCKED_DATA_ACCESS`; no invented metrics |
| 10. Editor-in-Chief QA | This review: independent exact-head PR checks, scoped approvals/merges, production verification checkpoint and dated QA record | `QA_MERGED`; `DEPLOYMENT_PENDING` |

## Primary-source verification and reader value

- [Revenue eBrief 142/26, issued 6 October 2026](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx): standard CGT for *most* disposals falls from 33% to **31% beginning 7 October 2026**, development land remains at 33%. Checked directly 22 Nov.
- [Revenue calculation guidance](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx): annual **€1,270** individual CGT exemption, historical 33% through 6 Oct, aggregation/allowable losses and exceptions. Checked directly 22 Nov.
- Independent calculations: `(€20,000 − €1,270) × 31% = €5,806.30`; historic 33% `= €6,180.90`; sale proceeds `€50,000 − €5,806.30 = €44,193.70`. Calculator's real JavaScript `project(v)` tested by a new Node-backed pytest scenario for 31% and 33% DIRT preserved.
- No newly generated news/article cover or licensing changes; existing child-savings photo/credit/author and date unchanged. Neither PR creates a new canonical or duplicates another article. Explicit targeted rate-check notes do **not** purport to re-review all guidance.

## PR disposition, CI, concurrency, rollback

### [#243 — child-savings share comparison](https://github.com/davidomarayt/compound/pull/243)

- Changed exactly `content/wealth/saving-for-your-child-ireland.md` and new `tests/test_child_savings_cgt_rate_2026.py`. PR exact head **`a5f49c7e030272fb0ce09cca2f2f2ec816ca174a`**. Before merge: 2 ahead / 6 behind new production head; GitHub reported mergeable, no overlapping PR #244 files.
- [Exact-commit CI #44965707310](https://github.com/davidomarayt/compound/actions/runs/44965707310) `completed/success`, GitHub API verified `head_sha=a5f49c7...`. Jobs: test **success** (407 pytest passed, 2 subtests; JS/arithmetic checks); performance **success** (static site build, image processing, representative Lighthouse runs). Existing Lighthouse enforcement step was **skipped** by workflow configuration; do not call thresholds enforced.
- Independent decision: **approved**, changed from draft to ready for merge, squash-merged using **`expected_head_sha=a5f49c7...`**, resulting production commit **`49fccc15a00dc5e210a6fad9f7484ecb9e5307d4`**. **No separate production page verified live**. The site deploy initially triggered at [#44994252575](https://github.com/davidomarayt/compound/actions/runs/44994252575), then was **cancelled by the newer #244 merge** (expected deployment concurrency, not a verified release).
- Rollback: revert merge commit #243 with clean review/CI; only one article and one regression test touched.

### [#244 — compound interest calculator CGT](https://github.com/davidomarayt/compound/pull/244)

- Exact final head **`3262d5e144b78d322bc399486aafab2df07216ef`**; distinct six paths: calculator JS engine, calculator template, control partial, calculator explanatory guide, one added test and one targeted old-quality-test assertion correction. No ad/consent template or account configuration changed. Before merge: 2 ahead / 5 behind after #243; GitHub reported mergeable. The original first-head CI **FAILED** due to an obsolete date-string assertion; worker fixed only that assertion on new exact head, retaining the substantive quality guard.
- [Revised exact-commit CI #44979298039](https://github.com/davidomarayt/compound/actions/runs/44979298039) `completed/success`, API confirms the **new** head SHA. Test job **success** (407 pytest passed, 2 subtests, new real Node-backed projection regression); performance job **success** (static build and representative Lighthouse). Existing `Enforce Lighthouse thresholds` step skipped; no specific interactive-browser/mobile calculator screenshot test asserted.
- Independent decision: **approved**, changed from draft to ready for merge, squash-merged using **`expected_head_sha=3262d5e...`**. Production merge commit **`f131f84aea5e14bce1fe01a78f1ece8ec2050060`**. Both PRs now closed/merged.
- [Final combined production Pages deployment #44994273486](https://github.com/davidomarayt/compound/actions/runs/44994273486): **IN PROGRESS at QA checkpoint**, exact production source commit `f131f84...`. [Post-merge CI #44994273490](https://github.com/davidomarayt/compound/actions/runs/44994273490): **IN PROGRESS**. Do not conflate PR-head success with completed post-merge deployment/verification.
- Rollback: revert merge commit #244 (and scoped 31% source changes) if actual runtime misbehaves; rerun CI/site deploy. The separate #243 content correction is not coupled to this calculator code change.

## Advertising, consent, canonical and public release gate

- Source-level review of `compound/site/templates/base.html` verified existing standard AdSense script `pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=...` conditionally inserted on configured non-preview public pages and preserved existing analytics-consent defaults, CMP/privacy links and conditional logic. Neither PR changed this template, slots, ad policy, attribution or ad account. **Keep standard ads on published articles/profiles irrespective of human-review status**; automated QA does not assert human review or actual AdSense fill/compliance.
- Checked original live public canonical pages on 22 Nov **before new deployment**: [child-savings guide](https://compound.ie/wealth/saving-for-your-child-ireland/) and [compound-interest calculator](https://compound.ie/compound-interest-calculator/). They still exhibited older 33% standard CGT rate content in their fetched snapshots. Therefore neither changed canonical, contextual link, actual JS `?v=20261122-cgt`, rendered ad loader nor calculated UI output has been independently confirmed live after merge. No change to sitemap/canonical route/consent authored by these PRs.
- Next verification must wait for a successful production `site` deployment for **`f131f84...`** (or descendant containing both merges), then fetch **both** public canonical HTML pages, the actual versioned `/static/compound-calculator.js` and a representative article/company profile to check the loaded ad script/CMP. Assert new 31% / historic 33% text, `€5,806.30` example, new internal CGT link, exact `?v=20261122-cgt` JS, `dateModified`, privacy settings and proper attribution. Check browser/mobility if supported. **Only then set VERIFIED_LIVE.** A passed Pages job without changed live HTML is insufficient.

## Overnight release tallies at this checkpoint

| State | Count / condition |
|---|---|
| Worker PRs opened | 2 |
| Independently approved | 2 |
| Squash merged | 2 (PRs #243, #244) |
| Final combined deployment | In progress; 0 confirmed completed at checkpoint |
| Changed pages independently verified live | **0** |
| Held candidate PRs from today's two workers | 0 |
| Research/private-company skips | 2 |
| Analytics-blocked specialist roles | 2 |

No production secrets, paid integrations, pricing, consent, payment flows, ad settings, automated schedules or other workflow ownership changed. Morning report should re-fetch deployment and changed public pages; it must not infer publication from merge status.


## Post-merge production checkpoint (after QA report creation)

- [GitHub Pages #44994273486](https://github.com/davidomarayt/compound/actions/runs/44994273486) for **`f131f84aea5e14bce1fe01a78f1ece8ec2050060`** now has **build SUCCESS**, **deploy SUCCESS**, **verify-live SUCCESS** and **verify-finance-discovery SUCCESS**. The independent `mobile-audit` job was still **IN PROGRESS** at this checkpoint, so the *whole workflow* is not yet labelled successful.
- The generic live-verification job performed a direct curl fetch of `https://compound.ie/compound-interest-calculator/` and asserted the standard AdSense loader exists there. It did **not** assert this PR's new CGT example, actual new JS version, new child-savings text or the child-savings contextual link.
- Independent public webpage retrieval after the deploy job still showed the earlier **33% CGT** explanatory content for the calculator and child-savings page. Because this retrieval may reflect crawler/cache snapshots rather than a fresh origin response, it cannot establish either a production regression or a successful updated deployment. **Keep both individual canonical pages `NOT_VERIFIED_LIVE` despite successful Pages deploy** until new text and versioned executable code are independently fetched from the public origin.
- Source-of-truth production-branch files *do* contain `€5,806.30` and the new CGT article link; `compound-calculator.js` contains `standardCgtRate=0.31` with deposit DIRT remaining 0.33; page template refers to `?v=20261122-cgt`. These are **source verification**, not a live browser check.
- Updated state totals: **2 approved, 2 merged, production Pages deploy job 1 successful, changed canonicals 0 independently verified live, 1 mobile-audit stage pending**. The 08:00 report should reassess the whole workflow and actual changed public HTML/JavaScript separately; source merge is not evidence of public propagation.
