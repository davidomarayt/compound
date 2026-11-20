# Compound.ie independent overnight Editorial QA — Friday 20 November 2026 (Europe/Dublin)

**Decision at this QA checkpoint:** **1 narrowly scoped pull request approved and merged** ([#192](https://github.com/davidomarayt/compound/pull/192)); **1 held, unmerged** ([#198](https://github.com/davidomarayt/compound/pull/198)); **0 overnight changes independently verified live**. The merge commit is `b7ce1af7f0db2b183ef63cc0a59c81d92191735e`. Its Pages `site` deployment was **in progress** at the last independent read; therefore **MERGED != DEPLOYED != VERIFIED_LIVE**. Review is automated and **not human review**. No other automations, secrets, ad-account configuration, consent/CMP settings, pricing or author/review fields were modified.

## Production branch, evidence, coordination

- Independent GitHub repository metadata and `.github/workflows/site.yml` both confirm **`claude/clever-babbage-uibieq`** is the default and GitHub Pages publishing branch. Pre-merge branch tip: `c69aca31d20d2cc0df0976cc79c52e05b8d229f4`; after #192 merge: `b7ce1af7f0db2b183ef63cc0a59c81d92191735e` (re-read from Git refs). Do not confuse this GitHub Pages branch with the unrelated Vercel check currently failing due to a build-rate-limit upgrade notice.
- Read [runbook](../../../docs/overnight-agents.md), [AGENTS.md](../../../AGENTS.md), `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, existing canonical page/source and both PR diffs; independently verified all **four actual dated worker records**: [discovery.md](discovery.md), [content.md](content.md), [research.md](research.md), [engineering.md](engineering.md). The records exist and contain separate findings for agents 1–9; their existence is not proof of successful worker deployments or a change from every role.
- The workers report deduplication checks against all **available** 12–19 November specialist records and current publication ledgers/inventory; the daily overnight record series did not have earlier 14-day records. The original-research worker also inspected the relevant available 30-day period. Content inventory is a repository snapshot (391 editorial pages, 69 tools, 511 public and 13 private profiles in the initial 20 Nov inventory), **not proven live coverage or search analytics**; later 20 November health publishing may have changed source counts.
- Independent primary-source review: [Law Society practice note, dated 7 Oct 2011](https://www.lawsociety.ie/Solicitors/knowledge-base/Practice-Notes/Payment-of-funeral-expenses) confirms many/most banks' direct funeral-director invoice settlement practice before grant from sufficient estate account funds; not a bank-specific guarantee. [Nasdaq 19 Nov 2026 exchange announcement](https://www.nasdaq.com/newsroom/anthropic-marks-ipo-at-nasdaq) confirms ANT **began trading** on 19 Nov and opened at **$111.50** (historical open, not a current quote). The CSO Q2 2026 productivity primary link provided in the separate research brief could not be independently fetched at this QA checkpoint; no research article was released from those unverified figures.
- Canonical-intent check: #192 enhances the **existing** `/wealth/probate-ireland/`, contextual link targets the already-public `/wealth/probate-costs-fees-ireland/`, and does not create competing probate content. #198 proposes a reclassification with a backwards-compatible legacy profile redirect, not a new duplicative IPO article. Open #188 medication hub and rapid Conditions A–Z publication PRs are distinct work owned by other workflows and were not modified.
- The existing probate guide retains its source-attested Pexels image credit, old published/reviewed dates and canonical URL. #192 introduces **no new hero/social image**, quotes, scripts, slots, review claims, tracking or personal information. On source inspection, `compound/site/templates/base.html` still conditionally loads the configured standard AdSense `pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=` for published non-preview pages, and preserves analytics consent + privacy-settings controls. Neither proposed PR touches these files. A source-level loader is not proof of a real ad impression, Google fill or actual policy status.

## 1. Search Console Growth — BLOCKED_DATA_ACCESS / review-only

The **last recorded** actual GSC/GA4 access check was 14 Nov, both `NOT_AUTHENTICATED`; no unauthorised fresh metrics query on 20 Nov within seven-day retry backoff. No clicks, CTR, rankings, impressions or SEO performance lift claimed. Reviewed existing probate metadata; no speculative SEO copy change or independent performance PR.

## 2. Content Gap — STAGED -> MERGED with #192

Documented fingerprint `/wealth/probate-ireland/|funeral-invoice-bank-before-grant-law-society` and verified missing before-grant process guidance on the original canonical. Did not publish a duplicate page. A funeral calculator route appearing in source could not independently be confirmed live, so no new link was created to it.

## 3. Internal Linking — STAGED -> MERGED with #192

One contextually relevant link to the already published `/wealth/probate-costs-fees-ireland/`. No templated, sitewide or speculative cross-linking; exact rendered new link still requires post-deployment verification.

## 4. Content Freshness — STAGED -> MERGED with #192

One dated, carefully qualified estate procedure explanation, a Law Society primary-source entry and a regression test. Makes **no claim that a 2026 law changed**, no guaranteed early bank payout, and no fabricated legal entitlement. Original date and reviewed metadata unchanged. Detailed PR review follows.

## 5. Original Research — REVIEW_ONLY, no article

The specialist report contains a separately fingerprinted CSO *Q2 2026 productivity* brief and calculations, distinguishing labour productivity/GVA per hour from wages and growth rates. This QA could not independently fetch the CSO primary page; no research article or new statistics have been approved or published from this brief. Originality dedup was documented; no invented publishing quota.

## 6. Private Company Intelligence — STAGED / HELD with #198

The Nasdaq source independently supports Anthropic becoming publicly listed as of **19 Nov 2026**, but the implementation is coupled to a **separate scheduled 07:00 private-company publisher still targeting Anthropic**. No automation was modified here; reclassification and redirect must not go live before publisher reconciliation and correct backlink treatment.

## 7. Technical SEO — STAGED / HELD with #198

Potentially useful `/companies/anthropic/` legacy noindex/canonical/refresh redirect to `/stocks/ant/` and directory declassification. Six-file exact PR diff checked; no bulk SEO change. Cannot release while exact-head performance CI fails and downstream navigation is unverified.

## 8. UX & Conversion — STAGED / HELD with #198

Maintains pre-IPO `company-anthropic` tags and reader bookmarks in proposed stock-profile generator, but CI explicitly found a missing published-article profile backlink. No conversion uplift claim, CTA experiment, prices or form changes.

## 9. Revenue Optimisation — BLOCKED_DATA_ACCESS

Last **actually checked** 14 Nov: Supermetrics AdSense report failed `TRIAL_EXPIRED`; GA4/GSC `NOT_AUTHENTICATED`. Seven-day backoff retained until 21 Nov absent a new authenticated response. No speculative RPM, fill, sales, traffic or ad-placement change. Standard from-publication ad and existing privacy/consent configuration preserved. Automated QA is not human review.

## 10. Editor-in-Chief independent PR decisions

### [#192 — probate funeral expenses before Grant of Representation](https://github.com/davidomarayt/compound/pull/192): APPROVED, MERGED; deployment pending live check

- Inspected exact two-file patch: `content/wealth/probate-ireland.md` and new `tests/test_probate_funeral_funds_context.py`. Source confirms direct payment is **bank-dependent and not guaranteed**, with available-funds and document caveats, and links to existing probate-costs canonical. No new copyright media, misleading author/review date, financial calculation or ad/CMP modification.
- Exact final pre-merge PR head **`3ac730c9b81efc9ee771e25bf89bb10c466c9b17`**. [GitHub Actions PR CI #44644894543](https://github.com/davidomarayt/compound/actions/runs/44644894543) **completed SUCCESS** on that SHA: both `test` and `performance` jobs passed, including static site build and Lighthouse runs. Threshold enforcement step was skipped by configuration, not a failure. Separately reported Vercel check failure is the unrelated account build-rate-limit status, not GitHub Pages test failure. GitHub PR reported `mergeable=true`, no current same-file conflict; changed-file comparison contained only the intended two files.
- Before merging, publishing branch had advanced **54 commits** since the source PR branch fork. This concurrency risk was assessed: latest base copy retained the original insertion anchor, same probate metadata and no competing edit of that file, and the change is prose/source/test only. The PR was marked ready, re-read, and merged through GitHub with **`expected_head_sha=3ac730...`**, never force merged. [Merge commit](https://github.com/davidomarayt/compound/commit/b7ce1af7f0db2b183ef63cc0a59c81d92191735e).
- A **new merged-tree CI** and [GitHub Pages deployment #44688706728](https://github.com/davidomarayt/compound/actions/runs/44688706728) were **in progress** at the last read; [push CI #44688706564](https://github.com/davidomarayt/compound/actions/runs/44688706564) likewise not complete. Do **not** mark production deployment or updated public paragraph `VERIFIED_LIVE` until the deploy finishes and a *fresh* public canonical HTML response contains the Law Society passage, canonical URL, contextual probate link, standard configured ad script and preserved privacy/CMP controls. An available web index of the page still showed the older paragraph and was not a post-merge live verification. This is a **release-verification gap**, not evidence of a completed rollback.
- Rollback if merged-tree CI or live behaviour regresses: revert **only** merge `b7ce1af...` / the added probate paragraph, source entry and test; run CI and verify Pages deployment again. Do not revert concurrent Conditions A–Z or other publishers' source.

### [#198 — migrate Anthropic private profile to listed ANT](https://github.com/davidomarayt/compound/pull/198): HELD / DRAFT / NOT MERGED / NOT DEPLOYED

- Current head **`4605fa9a60abc15197fa9a0be40f97c89f3aac3d`**; six file diff covers one issuer's registry, build routing, private-directory metadata and three regression test files. Source date and listing status confirmed against Nasdaq, but no live `/stocks/ant/` page or live old-profile redirect has been verified.
- **Exact-head [CI #44666575006](https://github.com/davidomarayt/compound/actions/runs/44666575006) = COMPLETED / FAILURE.** Test job passed **379 pytest + two subtests**, but `performance` job failed in `Validate 12 November private-company static content in audit mode`: `AssertionError: Missing profile backlink: https://compound.ie/news/anthropic-ipo-pricing-nasdaq/`. Remaining performance checks were skipped; full build/deployment gate has NOT passed. Earlier heads also failed worker test assumptions. Independently compared to latest publishing branch: **9 ahead / 32 behind**, although GitHub reported mergeable; concurrent publishing makes integrated verification important.
- Independent QA left it **draft/open/unmerged** and documented the exact failure plus required fix, tests and 07:00 scheduled-publisher coordination in [PR QA comment](https://github.com/davidomarayt/compound/pull/198#issuecomment-7032399182). Do not disable other automations or allow a now-listed issuer to be misclassified in future scheduled private-company output. Source supports the factual change, but neither clean tests nor a release plan currently supports merging.
- Rollback if later approved: revert the six-file reclassification/redirect patch only; retain original article and photo URLs. Verify links, sitemap, noindex/canonical, stock ticker, AdSense loader and unchanged consent after a future deployment.

## Outcome ledger and next owner actions

| Candidate | Approved | Merged | Deployed | Verified live | Held / skipped |
| --- | --- | --- | --- | --- | --- |
| #192 Probate | YES (automated QA) | YES, `b7ce1af` | **PENDING** (Pages run #44688706728) | **NO** | No; requires post-merge deploy + fresh URL check |
| #198 Anthropic | NO | NO | NO | NO | **HELD** — performance CI failure, stale publisher instruction, 32 commits behind |
| Original Research article | NO | NO | NO | NO | **REVIEW_ONLY** — new unlaunched brief |
| GSC/GA4/AdSense metric operations | NO | NO | NO | NO | **BLOCKED_DATA_ACCESS** — last actual check 14 Nov |

**Priorities:** (1) Finish #192 merged-tree CI/Pages and verify the updated public probate canonical plus ad/consent rendering; (2) correct #198 missing profile backlink and reconcile the 07:00 private-company publisher *before* a reclassification merge; (3) revisit authenticated analytics only on or after 21 Nov, subject to actual connection availability. No other existing automation was edited, disabled or replaced. **No human editorial approval, AdSense policy clearance, ad fill or traffic change is asserted.**
