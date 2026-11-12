# Compound overnight engineering and revenue review — 12 November 2026

**Worker:** completed 3 separate agent inspections and staged one low-risk draft PR. **Verified publishing branch:** `claude/clever-babbage-uibieq` (repository default; `.github/workflows/site.yml` responds to pushes to that exact branch for GitHub Pages). **Overnight engineering changes merged:** 0. **Live deployment from this run:** 0.

## 3. Technical SEO Agent — narrow Open Graph improvement

- Existing canonical directory: [https://compound.ie/companies/](https://compound.ie/companies/) lists 13 private companies. The original source `compound/site/templates/companies_hub.html` had a canonical link and normal meta description, but **no Open Graph title, description or URL** for link-sharing. In contrast, `compound/site/templates/stocks_hub.html` already defines OG metadata for `/stocks/`.
- Added standard `og:type=website`, truthful fixed `og:title`, helpful `og:description` and canonical `og:url` to `companies_hub.html`. No index, canonical-route or robots changes; no potentially inconsistent company valuation claims.
- Created **draft PR [#116](https://github.com/davidomarayt/compound/pull/116)**; proposed exact head `1df914a0dd7aa54ae334f0a6396fc02e2376a200`, base publishing ref initially `a3da0f88f0856fd96af645b5eba245a40d7ab119`. Changed only `companies_hub.html` and `tests/test_company_watchlist.py`.
- Test fixture uses `build_site(settings)` output and asserts the private hub's canonical, OG tags and labelled breadcrumb. Existing CI `ci.yml` runs `pytest -q`, Node validation and a static build plus Lighthouse performance.
- No wholesale sitemap, redirects, structured data, index flags or robots changes were warranted on the inspected routes. This was a **focused** SEO check, not a full URL crawl.

## 4. UX & Conversion Agent — accessible breadcrumb

- The original private-company hub used an unlabelled `<nav class="earnings-crumb">` while stock hub already used `aria-label="Breadcrumb"`.
- PR #116 labels the existing breadcrumb navigation for assistive technology. The visual layout, destinations, text, private-company lists and associated conversion paths are unchanged; this is a targeted navigability/accessibility improvement, not a proven engagement uplift.
- Original live `/companies/` and `/stocks/` directory descriptions were publicly retrievable; no end-to-end mobile interaction or Lighthouse score has yet been inferred.

## 5. Revenue Optimisation Agent — actual connection and configuration state

**Supermetrics connection audit (12 November 2026):**
- Google AdSense source `ADM` was reported **AUTHENTICATED**, with the configured public publisher client `ca-pub-6115783809711785`.
- An attempt to request **domain-level estimated earnings (EUR), page views, requests, impressions and ad-request coverage** for the **seven complete calendar days 5–11 November 2026** returned a **`TRIAL_EXPIRED` error**. The trial expired **19 October 2026**, so **no AdSense figures were obtained**. Authentication alone is not working report access. Account/site revenue, fill, RPM, CTR, revenue changes and conversion performance are therefore **NOT VERIFIED**.
- Search Console source `GW` and GA4 source `GAWA` returned **NOT_AUTHENTICATED**; no search/engagement metrics obtained. No data sources were reconnected and no subscription/payment action taken.
- Repository `content/site.yml` sets an AdSense client and **stock_mid** and **stock_lower** slot IDs. It leaves the explicit **article_top**, **article_bottom**, **earnings_mid** and **feed** slot fields blank. `base.html` includes the standard AdSense loader when its existing configured/ad eligibility conditions pass; `_stock_inline_ad.html` renders explicitly labelled stock ads when its existing conditions and slots allow. Blank fixed slots alone do not tell us whether Google Auto ads serve on the live page; those account settings, render state and actual fill were not checked.
- Qualitative opportunity: after reporting access is restored, measure page-level/ad-format performance before changing any layout. Hypotheses only: ensure fixed units do not obstruct reading, monitor Core Web Vitals and mobile layout, and protect consent. **No ad slots, account settings, consent/privacy settings or publication gates were altered.** Human editorial review fields/attribution untouched; no claim of AdSense policy-centre clearance or live fill.

## PR/CI and publication gate

- [PR #116](https://github.com/davidomarayt/compound/pull/116) is **OPEN, DRAFT, UNMERGED**. Its change is limited to two files; full [diff](https://github.com/davidomarayt/compound/pull/116/files).
- The exact-head [GitHub Actions CI run 43146229545](https://github.com/davidomarayt/compound/actions/runs/43146229545) was **in progress** at the last checked checkpoint. Its **test** job had **completed successfully**, including the existing full `pytest -q` pipeline and JS checks. **performance** job was still in progress and must be rechecked by 06:30 independent QA before any merge.
- GitHub combined status returned a **Vercel success** for **compound-solar-api**, a different Git-connected deployment; this is **not** evidence that Compound's GitHub Pages site deployed. GitHub Pages is triggered by the publishing branch `site.yml`, which this worker did **not** push site changes into.
- Risk: **low**, only private directory static OG metadata and breadcrumb label; rollback by reverting the two-file PR. The worker did not merge, publish, edit live ad settings or claim production success.
- Conflict check: open #107 edits the `private_company.html` profile template, not the `companies_hub.html` directory template; #115 edits home-deposit article; #57 solar freshness. No overlapping changed files. Editor-in-Chief QA to confirm up-to-date PR/base and checks.

**Overall:** Technical SEO: 1 draft PR. UX & Conversion: jointly owned improvement in same PR. Revenue Optimisation: connector/config audit and evidence-based limitations; 0 account changes. **No new live content or confirmed revenue uplift.**
