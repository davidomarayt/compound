# Compound overnight content — 2026-11-28 (Europe/Dublin)

One substantive PR for the group (link below in the PR body / QA record). It carries the Technical SEO link fix (see [discovery.md](discovery.md)) and the Internal Linking item below.

## 3. Internal Linking — measurable change staged

[Retire at 61 article](https://compound.ie/wealth/retire-at-61-ireland-five-year-pension-gap/) (published 26 Nov, 2 internal links). Chosen from the 25–27 Nov articles with the fewest internal links; no record in the last 14 days or open PR touches it.
- Added the [savings goal calculator](https://compound.ie/savings-goal-calculator/) in "Saving for the bridge", right after the €90,000 / €150,000 monthly-saving examples.
- Added [Compound's State Pension guide](https://compound.ie/wealth/state-pension-ireland/) where the article says the contributory amount depends on the social insurance record.
- `related_tools` gains `savings-goal-calculator`, so the article also lists on that calculator page.
- Both targets fetched 28 Nov ~02:35: HTTP 200, self-canonical, correct titles.
- Arithmetic around the new link rechecked: €90,000 / 180 months = €500; €150,000 / 180 = €833; €30,000 rising 2% a year over 5 years = €156,121. All match.
- Original `date` unchanged; no `reviewed` date added.

## 4. Content Freshness — review-only (verified, no correction needed)

- [ECB SPACE 2026 country data (Excel)](https://www.ecb.europa.eu/stats/ecb_surveys/space/shared/pdf/ecb.space2026_countryspecificdata.en.xlsx), published 25 Nov 2026, fetched 28 Nov, Ireland sheet, checked against [/news/ecb-space-2026-ireland-cash-cards-fraud/](https://compound.ie/news/ecb-space-2026-ireland-cash-cards-fraud/) (published 27 Nov). Share of till payments by number: Ireland cash 42.5%, card 42.5%, mobile 14.0%; euro area cash 43.8%, card 45.4%, mobile 8.6%. Prefer card or cashless: Ireland 52.4%, euro area 54.0%; prefer cash: Ireland 24.9%. Cash option very or fairly important: Ireland 65.3%, euro area 62.3%. Cash fairly or very hard to get: Ireland 16.4%, euro area 14.3%. All agree with the article's rounded figures. The fraud rows were not located in the sheet by this check, so those two figures are not verified here.
- Blocked: gov.ie State Pension (Contributory) page and citizensinformation.ie both returned 403 to the container, and SEC EDGAR returned 403. The State Pension rate (€299.30) was therefore not re-verified tonight.

## Validation and handoff

- Tests on the PR head: full `pytest -q` 435 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. The new stock-link test fails on base (1 failed) and passes on head. Static build left to CI.
- Risk low: one dead link replaced with plain text, two contextual links, one `related_tools` entry, one test. No rates, formulas, templates, metadata, canonical, robots, ads or consent touched. Rollback = revert the PR's commit.
- No merges, deployments, settings, secrets or outbound messages. Standard ads untouched and independent of review. Nothing claimed live; final QA is the 06:17 task.

Totals: 1 PR, 1 broken link fixed, 2 contextual links added, 1 regression test, 0 new pages, 0 merges, 0 verified-live.
