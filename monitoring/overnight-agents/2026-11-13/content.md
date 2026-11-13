# Compound overnight existing-content work — 2026-11-13 (Europe/Dublin)

**Production branch:** `claude/clever-babbage-uibieq` (GitHub default verified at run start). **Worker state:** one evidence-backed CGT rate correction prepared as **DRAFT, OPEN PR #121**; no worker merge, build/deploy or human review claimed. Ads remain on standard publisher settings independent of human review status.

## 3. Internal Linking Agent — verified existing canonical paths; no speculative link insertion

- Reviewed [Broker guide](https://compound.ie/wealth/choose-investment-broker-ireland/), [Before You Invest](https://compound.ie/wealth/before-you-invest-ireland/), [CGT guide](https://compound.ie/wealth/capital-gains-tax-ireland/), [CGT calculator](https://compound.ie/capital-gains-tax-calculator/) and [Investment Tax guide](https://compound.ie/wealth/investment-tax-ireland/) as distinct existing canonical destinations; these public routes resolved in site fetches, and source routes appear in the 2026-11-12 inventory.
- Existing CGT guide already links contextually to its **CGT calculator** and the wider **Investment Tax** article. These links were preserved while rate references were corrected; adding a duplicate CTA or sitewide link provides no clear reader benefit.
- Potential follow-up: a single highly contextual link from the broker compensation section (once correctly expanded) to the existing cash-reserve and time-horizon advice at `/wealth/before-you-invest-ireland/`. This work was deferred to keep #121 narrow; **new internal links committed in the final PR: 0**.
- No link to unpublished content, invented target, noindex preview, redirect, or new route. Full rendered link verification on candidate #121 is **pending CI/QA**.

## 4. Content Freshness Agent — material CGT accuracy correction staged

### Primary sources independently checked, 13 Nov 2026

| Existing claim/URL | Dated source | Finding and action |
| --- | --- | --- |
| `/wealth/capital-gains-tax-ireland/` currently claims standard **33%** and uses 33% worked examples | [Revenue eBrief 142/26, **6 Oct 2026**](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx); [Revenue CGT calculation guide (published 7 Oct 2026)](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx) | **Incorrect for most disposals from 7 Oct 2026.** Rate 31%; earlier standard rate 33% up to 6 Oct; development land 33%. Corrected source, metadata, method/example/FAQ in PR #121 only. |
| `/wealth/investment-tax-ireland/` still says 33% CGT and 33% example, while DIRT and fund taxes are distinct | Same CGT sources; [Revenue eBrief 016/26, **22 Jan 2026**](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-0162026.aspx); [Revenue DIRT guidance](https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx) | CGT figure and €4,730 worked example corrected to 31% and €1,466.30. **33% DIRT** and relevant **38%** fund tax preserved. |
| `/capital-gains-tax-calculator/` calculation/rate choice and text | Revenue sources above | Basic default and rate selector already had correct 31% post-change and 33% historical/development land. Corrected only two stale explanation sentences in `content/tools.yml` and the embedded guide. Calculator JS/formula **untouched**. |
| `/wealth/pension-vs-investing-ireland/` age-related relief thresholds, €115k cap | [Revenue pension relief limits](https://www.revenue.ie/en/jobs-and-pensions/pension/relief/tax-relief-limits.aspx) (published 15 Oct 2026) | Source spot check: 15/20/25/30/35/40% limits and €115,000 earnings cap consistent; no change. |
| `/wealth/personal-investment-account-ireland/` 2027 PIA legal status and review banner | [Oireachtas Bill 98/2026](https://www.oireachtas.ie/en/bills/bill/2026/98/); source links in page | Date/status mismatch logged for follow-up; no assertion of enactment or unverified latest parliamentary stage, no speculative edit. |

### Draft PR, tests and exact state

- **PR [#121 — Correct Irish CGT guides to 31% from 7 October 2026](https://github.com/davidomarayt/compound/pull/121)**: `OPEN`, `DRAFT`, **NOT MERGED**, head `c3957bc490ebb3beb890ca303babd40facfdc2dd` at creation; base `claude/clever-babbage-uibieq`. This is the **only substantive PR** for this worker group.
- Net PR diff from production: exactly five files: `content/wealth/capital-gains-tax-ireland.md`, `content/wealth/investment-tax-ireland.md`, `content/tool-guides/capital-gains-tax-calculator.md`, `content/tools.yml` and `tests/test_cgt_2026_rate_editorial.py`. No broker change remains.
- Static source checks on exact branch: current 31% guidance, pre-change 33% and development-land exceptions, original 30 Sept CGT article publication/review/attribution intact, dated source added, correct 31% examples, 33% DIRT and 38% fund rate unaffected. Arithmetic verified: €6,430×.31=€1,993.30; €6,730×.31=€2,086.30; €77,730×.31=€24,096.30; €10,730×.31=€3,326.30; €1,270×.31=€393.70; €4,730×.31=€1,466.30. Regression test added.
- [Exact-head CI run 43336020880](https://github.com/davidomarayt/compound/actions/runs/43336020880): **`test` job completed successfully; `performance` job in progress at the latest worker checkpoint**. Vercel commit status separately reports success, not a substitute for full GitHub CI. Full `pytest` completed; the performance build, PR-level review and final QA remain pending on this exact head.
- **No merge, no production deploy, no verified newly published page.** Public live CGT guide still displayed the old 33% when fetched during this worker run; the corrected 31% content is staged only.
- **Risk:** moderate editorial tax accuracy; late-2026 rate change is date-sensitive. **Rollback:** revert five CGT-specific files in this PR. All previous original content dates, photo attribution/licensing, site URLs, publishing workflows, ad, consent and privacy configuration unchanged. Automated checks must never be labelled human approval.

### Blockers / handoff to Editor-in-Chief QA

CI and rendered exact-commit build must finish; independently review the wording that earlier standard disposals (through 6 Oct 2026) and development land remain 33%, then check generated canonical outputs/links and ordinary ad loader (without gating ads on human review). Check PR head/base and whether another writer has changed relevant files before merging. If tests fail, leave PR open with failure evidence. Defer broker comparison and broader PIA review to their own verified updates, not this PR.
