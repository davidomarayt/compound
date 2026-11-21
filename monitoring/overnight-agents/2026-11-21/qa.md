# Compound.ie — independent overnight Editor-in-Chief QA — 2026-11-21 (Europe/Dublin)

**Status at initial QA write (21 November, approximately 06:28 UTC):** two independent worker PRs passed their exact-head test and performance/build jobs and were safely merged using the exact expected PR head SHA. Both are **MERGED**, but **DEPLOYMENT and PUBLIC CANONICAL VERIFICATION are still pending** at this checkpoint. This is **automated editorial QA, not human review**. The publishing branch `claude/clever-babbage-uibieq` was independently confirmed as repo default and the GitHub Pages publishing branch in `.github/workflows/site.yml`.

## Required daily worker records checked
- [Discovery](discovery.md): Search Console Growth and Content Gap, recorded after the 00:15 worker; source-backed correction in PR #224 and metrics blocked.
- [Content](content.md): Internal Linking and Content Freshness, shared PR #224; no worker merge.
- [Research](research.md): Original Research (fresh CSO transport/EV survey brief, review only) and Private Company Intelligence (no material eligible private profile change); no user-facing publication.
- [Engineering](engineering.md): Technical SEO and UX & Conversion, shared PR #225; Revenue Optimisation metrics blocked. No worker merge.
- Record history: workers reviewed all available records since 12 November (directory begins then), with previous 30-day Original Research source overlap check and related recent publishing ledgers; QA compared 20 November QA report and existing PR #176 on a **different** earnings hub URL.

## Independent per-role assessment (do not count suggestions as site outputs)

| Role | Worker evidence inspected | Independent disposition |
| --- | --- | --- |
| 1. Search Console Growth | 21 November authenticated status discovery for GSC `GW` returned `NOT_AUTHENTICATED`; GA4 not rechecked at that stage | `BLOCKED_DATA_ACCESS`; no query impressions, clicks, CTR, ranking or growth claim |
| 2. Content Gap | Inventory + existing RSU canonical identifies outdated unconditional 33% wording; next candidate saving-for-child guide kept in backlog | `STAGED→MERGED #224` for existing URL; no duplicate article |
| 3. Internal Linking | One direct contextual link from RSU rate assertion to existing CGT guide, preserving existing calculator links | `STAGED→MERGED #224`, rendered link verification pending |
| 4. Content Freshness | Revenue's 6 October eBrief and current CGT manual confirm 31% standard rate for ordinary disposals from 7 October 2026, historical 33% earlier, and continuing 33% development-land rate; worked €2,730 × 31% = €846.30 checked | `STAGED→MERGED #224`, no false whole-guide re-review |
| 5. Original Research | CSO Sustainable Mobility and Transport 2024 report released 20 November 2026; published 2024 survey data correctly distinguished from 2026 observations; methodology and derived differences recorded | `REVIEW_ONLY`; zero new article/URL |
| 6. Private Company Intelligence | Confirmed Anthropic and SpaceX now classified listed; 07:00 publisher overlap; official OpenAI and Databricks changes lacked documented new profile-level business metrics | `NO_MATERIAL_PROFILE_CHANGE`; zero private profile updates |
| 7. Technical SEO | Source distinction on /stocks/ misleadingly described every report as SEC-backed; narrow provenance wording correction and regression test | `STAGED→MERGED #225`; no index/route change |
| 8. UX & Conversion | Same existing Stocks directory cards now say primary-source earnings instead of universal SEC backing; accessibility, search and canonical assertions retained | `STAGED→MERGED #225`; no conversion KPI claim |
| 9. Revenue Optimisation | 21 November GA4 GAWA status `NOT_AUTHENTICATED`; AdSense ADM data query returned `TRIAL_EXPIRED` (account presence does not mean metrics enabled) | `BLOCKED_DATA_ACCESS`, next regular recheck no earlier than 28 Nov absent reconnect; no estimated revenues/RPM |
| 10. Editor-in-Chief QA | This report: checked all four current worker ledgers, patches, official source, exact-head jobs, no conflicting source paths, merge/deployment status | `COMPLETE` for source/CI/merge, `PENDING` for production verification |

## PR #224 — RSU standard CGT correction — APPROVED / MERGED / DEPLOY PENDING

- [PR #224](https://github.com/davidomarayt/compound/pull/224), exact reviewed head `794b724e66591383345fb3849e0a050477027d9b`; GitHub squash-merged with `expected_head_sha` to publishing branch as `529a26e3906d9f0347a8ac5af6aca5c6b9af6280`. Only `content/wealth/rsu-share-options-tax-ireland.md` plus `tests/test_rsu_cgt_rate_2026.py` changed. No other worker source ownership collisions. Existing page URL, old publication/review metadata, attribution, hero, article author, tax distinctions, other links, pricing and tracking untouched.
- Original authority independently opened: [Revenue eBrief 142/26, 6 Oct 2026](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx), and [Revenue current CGT rate/calculation](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx). Ordinary shares use standard 31% for disposals since 7 Oct; historical 33%, development land 33%; €1,270 annual personal exemption confirmed. Decimal check: €4,000 − €1,270 = €2,730; current €846.30; historical €900.90. Capital tax is later sale, not vesting tax.
- [Exact-head CI run 44842657519](https://github.com/davidomarayt/compound/actions/runs/44842657519) **completed SUCCESS**, including all test steps and performance/static build/Lighthouse CI; Lighthouse threshold enforcement was separately marked skipped by workflow configuration, not represented as passed threshold enforcement. Actual live article was fetched **before merge**, confirming the outdated public 33% text and the original canonical existed.
- Base moved with operational records and an unrelated PTC earnings profile; GitHub confirmed PR mergeable and accepted expected-head merge. Rollback: revert this squash commit, preserving site history. No synthetic/licence or ad asset changed.

## PR #225 — Stocks directory source provenance — APPROVED / MERGED / DEPLOY PENDING

- [PR #225](https://github.com/davidomarayt/compound/pull/225), exact reviewed head `b754b814ebaf73bc6109e5f693fddda162edbb30`; GitHub squash-merged with `expected_head_sha` as `9d250f203c3e58b31601a4a32e7793954f839f7d` (latest confirmed publishing head). Scope: only `compound/site/templates/stocks_hub.html` and `tests/test_stocks_directory_provenance_2026.py`. Replaces four blanket filing/SEC source phrases with truthful, primary-source-neutral phrasing; preserves existing earnings, directory, breadcrumb, search JS, canonical, JSON-LD, asset versions and data sources. Existing [PR #176](https://github.com/davidomarayt/compound/pull/176) concerns different `/wealth/earnings/` template and remains separate.
- [Exact-head push CI 44858995365](https://github.com/davidomarayt/compound/actions/runs/44858995365) and [exact-head PR CI 44859020845](https://github.com/davidomarayt/compound/actions/runs/44859020845) **completed SUCCESS**, with test and performance/build jobs successful. Templates rendered with eight featured stocks in regression tests; production-mode `compound build` succeeded; Lighthouse threshold-enforcement step is skipped by CI policy, and no actual conversion/SEO gain claimed. Public `/stocks/` was fetched **before merge**, with existing SEC-backed labels visible.
- Base moved due to specialist ledgers, unrelated PTC earnings data and #224 merge. Independent comparison confirmed no changes to #225's two files in the intervening base commits; GitHub subsequently showed mergeable=true, mergeable_state=clean and accepted the expected-head squash merge. Rollback: revert the standalone squash commit.

## Advertising, consent, licences, risk

- Reviewed live-build source template `compound/site/templates/base.html`. Standard `pagead2.googlesyndication.com/pagead/js/adsbygoogle.js` is included for configured ad-enabled non-preview public pages, subject to existing condition `ads_allowed`; that condition, CMP/privacy settings, analytics-consent logic, and ad placement are **unchanged in both PRs**. Neither PR introduces a review-status advertising gate or suppresses ads. Source guard is NOT proof that the updated deployed pages render the loader, configured slots, consent UI or that Google filled any impressions; those require live HTML inspection. Do not assert AdSense compliance, real impressions or human review.
- RSU hero image, licence/credit and OG policy unchanged; Stocks directory changes no editorial imagery. Both are tightly scoped source-correctness changes and include deterministic regression tests; no settings, secrets, ads accounts, payments or other automations modified.
- **Post-merge publishing checks initially pending:** [final-commit site run 44875615319](https://github.com/davidomarayt/compound/actions/runs/44875615319) and [final-commit CI run 44875615368](https://github.com/davidomarayt/compound/actions/runs/44875615368) were pending at first check; the previous #224 merge triggered [site run 44875592098](https://github.com/davidomarayt/compound/actions/runs/44875592098) which may be superseded by GitHub Pages concurrency. Only the latest successful production deploy and an independent changed-text/SEO/canonical/ad-loader/consent fetch at both URLs count as `VERIFIED_LIVE`.

## State ledger at initial checkpoint

| Item | Approved | Merged | Production deployed | Public URL verified changed | Held/skipped |
| --- | --- | --- | --- | --- | --- |
| PR #224 RSU guide | Yes, automated QA only | Yes, `529a26e` | Pending | No | No |
| PR #225 stocks provenance | Yes, automated QA only | Yes, `9d250f2` | Pending | No | No |
| Original Research brief | Review only | No | No | No | Publication skipped |
| Private Company Intelligence | No material correction | No | No | No | Skipped |
| GSC/GA4/AdSense analysis | Metrics unavailable | No | No | No | Blocked data access |

**Follow-up:** re-read the latest GitHub Pages run and independently fetch `https://compound.ie/wealth/rsu-share-options-tax-ireland/` and `https://compound.ie/stocks/` after successful deployment. Do not treat CI completion alone as a verified-live assertion.
