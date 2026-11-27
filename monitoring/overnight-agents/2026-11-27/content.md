# Compound overnight content — 2026-11-27 (Europe/Dublin)

One substantive PR for the group: [PR #304](https://github.com/davidomarayt/compound/pull/304), base 1f4c70048a8dc2c83451e8b381e3b402c944d346. It carries the Technical SEO link fixes (see [discovery.md](discovery.md)) and the two items below.

## 3. Internal Linking — measurable change staged (#304)

[KickstartSaver article](https://compound.ie/news/bank-of-ireland-5-percent-savings-account/) (published 25 Nov; served HTML on 27 Nov linked only /compound-interest-calculator/). Deferred from 26 Nov because the article was then hours old; no other open PR or commit touches it since publication.
- Added in context: [DIRT calculator](https://compound.ie/dirt-calculator/) in the DIRT section; [emergency fund calculator](https://compound.ie/emergency-fund-calculator/) where the article mentions an emergency fund; [regular savings calculator](https://compound.ie/regular-savings-calculator/) beside the existing compound-interest link.
- `related_tools` extended with the same three slugs, so the article also lists on those calculator pages (the reverse link; build.py matches `related_tools`).
- All four targets fetched 27 Nov: HTTP 200, self-canonical, correct titles. Rendered output not built locally (pre-existing CI image-cache requirement); left to CI `performance` job.
- Original `date: 2026-11-25` unchanged; no `reviewed` date added.

## 4. Content Freshness — one factual-context addition staged; one check blocked

- [Bank of Ireland KickstartSaver product page](https://personalbanking.bankofireland.com/save-and-invest/savings/regular-savings-accounts/kickstartsaver/) (fetched 27 Nov, no page date): 5% AER variable up to €5,000, 2% AER variable above; €5 minimum; €58 weekly / €115 fortnightly / €250 monthly maximum; no lump sums; from age 16; DIRT 33%. All agree with the article. The bank's own daily-interest example gives €76.85 gross / €51.49 after DIRT for €250 a month over 12 months, versus the article's start-of-month approximation of €81 / €54. The table was already labelled an approximation; staged one sentence citing the bank's figure so readers see both (no figures in the table changed). Change type: added sourced context, not a correction of an error.
- [Revenue CGT page](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx) (published 7 Oct 2026, fetched 27 Nov): 31% for most gains from 7 Oct 2026, 33% 6 Dec 2021–6 Oct 2026, 33% development land, €1,270 exemption. CGT calculator copy in `content/tools.yml` agrees. Open #254 (shares-vs-ETFs CGT wording) remains consistent with Revenue. No change.
- MyFutureFund rules: BLOCKED again. myfuturefund.ie is JS-rendered; plain fetch returns an empty shell and a headless browser gets CloudFront 403. citizensinformation.ie also 403. Not verified; no change. Suggest a check from a normal browser.

## Validation and handoff

- Tests on the PR head: full `pytest -q` 428 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. Extended link test fails on base with exactly the 3 broken links and passes on head. Static build not run locally (pre-existing image-cache requirement). PR CI was pending at write time; no CI success claimed.
- PR state at creation: OPEN, DRAFT, unmerged. Reports are committed on the PR branch, not pushed to production, so QA should read them from #304.
- Risk low: link targets and one sourced sentence; no rates, formulas, templates, metadata, canonical, robots, ads or consent touched. Rollback = revert the PR's commit.
- No merges, deployments, settings, secrets or outbound messages. Standard ads untouched and independent of review. Nothing claimed live; final QA is the 06:17 task.

Totals: 1 draft PR, 3 broken/legacy links fixed, 3 contextual calculator links added, 1 sourced sentence, 0 new pages, 0 merges, 0 verified-live.
