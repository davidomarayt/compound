# Compound Overnight Editor-in-Chief QA — 2026-11-12 (Europe/Dublin)

**Independent QA decision:** two narrow PRs approved, exact-head checks passed, both merged via expected-head-SHA guarded squash merges. **Deployment and verified-live status remain unconfirmed** at QA checkpoint; the next reporting task must not represent a merge as a confirmed live page. No new article URLs, author approvals, editorial dates, ad settings or consent controls were changed.

## Production branch and upstream evidence

- Verified GitHub repository `davidomarayt/compound` default and website publishing branch: `claude/clever-babbage-uibieq`. `.github/workflows/site.yml` triggers GitHub Pages builds on pushes to that branch affecting `content/**` and `compound/site/**`; both merges qualify to trigger the workflow.
- Reviewed `docs/overnight-agents.md`, `AGENTS.md`, `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, `data/content-inventory.json`, `.github/workflows/ci.yml`, `.github/workflows/site.yml`, and all four worker ledgers: [discovery.md](./discovery.md), [content.md](./content.md), [research.md](./research.md), [engineering.md](./engineering.md). The inventory snapshot is dated 2026-11-12; the two PRs add no new canonical content.
- Checked current GitHub PR metadata, full diffs, filenames, review submissions (none), exact-commit CI run results and individual jobs. Reviewed existing/pending work noted by worker agents (#57, #107); neither new PR touched their reported files. No ads or site-policy editing took place.
- Independent primary evidence: [Central Bank mortgage measures](https://www.centralbank.ie/consumer-hub/explainers/what-are-the-mortgage-measures) confirms standard 10% owner-occupier and 30% buy-to-let deposits; [Revenue residential stamp duty rates](https://www.revenue.ie/en/property/stamp-duty/property/stamp-duty-property/rates.aspx) confirm 1% / 2% / 6% ordinary bands. [CSO CPI October 2026, released 11 Nov](https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/) confirms the worker's 4.3% annual CPI and division figures. [Anthropic IPO roadshow statement, 10 Nov](https://www.anthropic.com/news/roadshow-launch) confirms offered shares, the stated $70–$78 indicative range and that registration was not yet effective at announcement. The research briefs were not site edits and no current IPO stage/market price beyond that source date was assumed.
- No content photo assets, social media images, or related attribution were changed. Existing original source URL, publication date and displayed byline preserved for the amended mortgage article.

## PR #115 — Contextual house-deposit calculator link

- [PR #115](https://github.com/davidomarayt/compound/pull/115), original head `11599f3a960f59fa7d9fec14563271cef0a09e2b` and sole changed file `content/wealth/buying-home-budget-deposit-ireland.md`.
- Review: a single added paragraph within the existing canonical buying-home guide links to `/house-deposit-calculator/`; explanatory boundaries correctly distinguish standard LTV from affordability/approval and separate fees/reserves. The target existed and had been fetched publicly. This is a bounded, nonduplicate internal navigation addition; no altered claims, images, route or review metadata.
- **Exact-head CI:** [run 43125849624](https://github.com/davidomarayt/compound/actions/runs/43125849624) = `completed/success`. `test` and `performance` jobs succeeded, including `pytest -q`, JS checks and static `compound build`; Lighthouse job succeeded. The conditional "Enforce Lighthouse thresholds" step was skipped because its triggering failure condition was not met, not manually bypassed.
- Latest pre-merge GitHub mergeability rechecked as `true`. Converted draft to ready after independent QA.
- **Approved and MERGED** with `expected_head_sha=11599f3a960f59fa7d9fec14563271cef0a09e2b` (squash SHA `521a0ef375af0868b618d0f6163ab4712ae44ca1`). GitHub subsequently confirmed PR closed/merged and current publishing-branch source includes the link.
- **DEPLOYED: not verified. VERIFIED LIVE: not verified.** Public route was accessible to a crawler, but the subsequent text extraction did not show the added paragraph at the QA checkpoint; crawler caching, a pending Pages run or deployment lag were not distinguishable. Do not claim it was live yet. Rollback: revert `521a0ef...` if warranted.

## PR #116 — Private-company directory OG + accessible breadcrumb

- [PR #116](https://github.com/davidomarayt/compound/pull/116), original head `1df914a0dd7aa54ae334f0a6396fc02e2376a200`, changing only `compound/site/templates/companies_hub.html` and `tests/test_company_watchlist.py`.
- Review: adds `og:type=website`, `og:title`, `og:description`, `og:url` to an existing canonical `/companies/` hub and `aria-label="Breadcrumb"` to its navigation. Added `build_site` HTML test assertions. No changed company data, pages, index flags, images, ads, permissions, consent, privacy or checkout. Existing `/stocks/` hub conventions were used.
- **Exact-head CI:** [run 43146229545](https://github.com/davidomarayt/compound/actions/runs/43146229545) = `completed/success`; both `test` and `performance` jobs passed, including new HTML assertions and static build.
- After PR #115 merge, re-evaluated PR #116 mergeability; GitHub returned `true` after updating draft status to ready. The changed files do not overlap with #115 or noted other open PRs.
- **Approved and MERGED** with `expected_head_sha=1df914a0dd7aa54ae334f0a6396fc02e2376a200` (squash SHA `e968abbdb72d17d17f9652be58c17c0f97bad967`). GitHub subsequently confirmed closed/merged and the publishing-branch template includes the new tags and accessible nav.
- **DEPLOYED: not verified. VERIFIED LIVE: not verified.** The public directory was reachable but the available web text extractor omits raw meta/head attributes, and no confirmed GitHub Pages run status or raw served HTML was accessible at QA time. Rollback: revert `e968abb...` if warranted.

## Advertising, privacy and editorial safety

- Neither PR touches `content/site.yml`, `base.html`, ad eligibility, ad placement, `adsbygoogle` loader, or consent code. Source check confirms configured public AdSense publisher client and stock mid/lower slot IDs; fixed article top/bottom slots are blank. The base template loads the standard Google loader when configured and its existing eligibility condition permits, and retains consent/privacy controls. **Rendered ad loader and per-page slots after these merges cannot be independently verified until real deployed HTML is available; ad-fill and Google account compliance are not asserted.**
- The publisher's latest advertising-from-publication instruction is reflected in repository `AGENTS.md` and `docs/overnight-agents.md`. No ads were disabled or withheld by this QA run, and no human approval was invented. This QA sign-off is automated code/content QA, not human editorial curation.
- No new medically/financially substantive article or private-company IPO article was merged. Source-led research remains a held proposal, not a live publication.
- No evidence of Search Console 7/28-day query-page metrics, GA4 engagement, or actual AdSense revenue: worker records mark connections unauthenticated or expired. Do not infer uplift.

## Final dispositions and follow-up

| Item | Independent QA | Merge | Deployment | Verified live |
| --- | --- | --- | --- | --- |
| #115 (internal link) | passed exact-head CI & primary-source check | **YES**: `521a0ef...` | **NOT VERIFIED** | **NOT VERIFIED** |
| #116 (OG tags + breadcrumb) | passed exact-head CI & tests | **YES**: `e968abb...` | **NOT VERIFIED** | **NOT VERIFIED** |
| Research notes / topic gaps | researched, no website edits | not applicable | not applicable | not applicable |
| Search/analytics revenue figures | unavailable (not authenticated / trial expired) | not applicable | not applicable | not applicable |

**Outstanding:** Verify GitHub Pages `site.yml` run on the newest publishing-branch tip, confirm successful build/deploy, then fetch **raw current production HTML** for `/wealth/buying-home-budget-deposit-ireland/` and `/companies/` to check new link, `og:*`, `aria-label`, canonical, loader/slots/consent and correct public URLs. If any deployment failed, record the run URL and diagnose; do not retroactively label source merges as live. The 08:00 report should carry these specific verification gaps if unresolved.

**Production changes this QA run:** 2 PRs merged; **verified live pages: 0**, because evidence was insufficient. **Other publishing automations:** unchanged.
