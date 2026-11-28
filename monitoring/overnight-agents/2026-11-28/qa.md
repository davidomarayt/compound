# Compound independent Editor-in-Chief QA — 28 November 2026 (Europe/Dublin)

Automated QA, not human editorial review. Scheduled 06:17 Dublin; the first attempt was cut off by an API error at 06:18 and resumed at 07:23 Dublin. Production branch confirmed as `claude/clever-babbage-uibieq` (site.yml push target), base 9fbe32794fa9990341ff458730feb2c5bf742b0f. Read AGENTS.md, docs/overnight-agents.md and all four dated reports, which the workers committed on their PR branches: [discovery](discovery.md) and [content](content.md) via #319, [research](research.md) and [engineering](engineering.md) via #320; all four are now on production through those merges. No settings, secrets, accounts, ad placement or consent controls changed.

## Role outcomes (from worker reports, cross-checked)

| Role | Outcome |
| --- | --- |
| Technical SEO (discovery) | Changed: #319, dead /stocks/mat/ link in the Mattel article replaced with plain text pointing at its listed sources; new test checks every /stocks/<x>/ content link against generated profiles. Merged, verified live. |
| Content Gap | Review-only; backlog updated, no new page. |
| Internal Linking | Changed: #319, retire-at-61 article links the savings goal calculator and State Pension guide (+ related_tools). Merged, verified live. |
| Content Freshness | Review-only: ECB SPACE 2026 Ireland figures match the 27 Nov article (fraud rows not verified). gov.ie / citizensinformation.ie / SEC 403 — State Pension rate not re-verified. |
| Original Research | Review-only: CSO Retail Sales Index Oct 2026 implied-price brief; nothing published. |
| Private Company Intelligence | NO_MATERIAL_PROFILE_CHANGE. Note: no 27 Nov private-company ledger on production (flagged by research, not investigated here). |
| Technical SEO (engineering) | Changed: #320, pages with a front-matter `meta_description` now render it (3 tool pages). Merged, verified live. |
| UX & Conversion | Same PR #320: AA contrast on small /stocks/ labels (CSS v=2) and keyboard-focusable guide table scroll boxes. Merged, verified live. No conversion figures claimed. |
| Revenue Optimisation | BLOCKED_DATA_ACCESS (no GA4/AdSense connector). Next 5 Dec. |
| Editor-in-Chief QA | 2 approved, 2 merged, deployed, verified live; 0 held. |

## Release evidence

- [PR #319](https://github.com/davidomarayt/compound/pull/319) — head e53de3f5739b2649118fc856833f6d03d694083d. Diff checked: one sentence replacing the dead link (no figures changed; release and 10-Q already in the article's sources), two contextual internal links, one `related_tools` entry, one test; publication date unchanged, no reviewed date added. Arithmetic beside the new link (€90,000/180 = €500; €150,000/180 ≈ €833) rechecked. PR CI `test` + `performance` successful on exact head (runs 46098297866, 46098314731). Was draft; marked ready, merged with expected head → c1a92114487b73cc31a59e8b69785e0a0cbce6ab.
- [PR #320](https://github.com/davidomarayt/compound/pull/320) — head fc3b9321963a5675099bb7f27d886e2f487c25ea. Diff checked: one `{% elif page.meta_description %}` branch before the default in `page.html` (earlier slug-specific branches untouched); five colour values darkened in `stocks-research.css` + cache key v=2 in two templates; `tabindex="0" role="region" aria-label` on the guide-table wrapper. No URL, title, canonical, robots, sitemap, ad, consent or tracking change. PR CI `test` + `performance` successful on exact head (runs 46100355359, 46100378090). No file overlap with #319; mergeable clean. Was draft; marked ready, merged with expected head → 30ca5410ca53d0a44f9ab980a6b6d47a9cc662b6.
- Combined check: both branches merged locally onto 9fbe3279 with no conflicts; full `pytest -q` 439 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed.
- Licences/duplication: no images, no new articles, no new external citations.
- Rollback: a normal revert PR of either merge commit; changes are independent. Never force.

## Deployment and live verification

- [site run 46121278651](https://github.com/davidomarayt/compound/actions/runs/46121278651) on 30ca5410: build, deploy (07:30:38 UTC), verify-live and verify-finance-discovery successful; mobile-audit still running when this was written. The #319 site run 46121268800 was cancelled by concurrency; the later run deploys both.
- Public canonical pages fetched after deploy (HTTP 200, self-canonical):
  - /wealth/mattel-tariff-refund-margin/ — no /stocks/mat/ link; new sources sentence present.
  - /news/retire-at-61-ireland-five-year-pension-gap/ — links /savings-goal-calculator/ and /wealth/state-pension-ireland/ (both 200); /savings-goal-calculator/ lists the article (reverse link).
  - /ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/ — each serves its own front-matter description, not the sitewide default.
  - /stocks/ and /stocks/aapl/ — load `stocks-research.css?v=2`; served CSS has the new colours.
  - /compound-interest-calculator/ — guide table wrappers carry `tabindex="0" role="region"`.
- Ads/consent: every page above still carries the standard ad loader and consent markup in the served HTML. No ad-fill or compliance claim.

**Totals:** approved 2; merged 2; deployed 2; verified live 2; held 0 of tonight's candidates; skipped 0. Older open PRs (incl. #310, the 27 Nov QA record) were not part of tonight's run and were left untouched. Open backlog: 7 static pages on the default meta description; MyFutureFund freshness blocked by source fetch.
