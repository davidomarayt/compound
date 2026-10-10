# Compound Earnings — S&P 500 coverage

## What the new system does

The publication uses a **validated snapshot** of the S&P 500 constituents from a [public daily constituent dataset](https://github.com/datasets/s-and-p-500-companies/blob/main/data/constituents.csv) derived from the [Wikipedia constituent table](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies), not an official/licensed S&P constituent data feed. Every weekly refresh verifies roughly 500 securities, >=480 distinct SEC CIKs, distinct ticker symbols and all 11 GICS sectors before it can replace the preceding snapshot. Existing companies that leave the index are retained as `active=false` so historical reports and profiles are not erased.

Compound uses **unique CIK identifiers** for tracking; dual-share classes count as one company. The monitor polls a quarter of active companies at a time: scheduled checks at minute 17 and 47 scan the entire index over a roughly two-hour rotation (schedules may be delayed by GitHub). SEC access is identified and throttled at >=350ms per request. On large blocks of SEC errors the publishing run fails instead of appearing successful. Any earnings summary is generated only when the company's 10-Q/10-K XBRL figures contain matching three-month/full-year revenue, GAAP net income and diluted EPS with comparable year-earlier periods. All other filing types, adjusted earnings, and companies with insufficient standardised metrics remain in the directory without a generated earnings report.

## Pages and SEO

- `/wealth/earnings/`: searchable public S&P directory, sectors, source/checked date, full index, latest verified reports.
- `/wealth/earnings/company/<symbol>/`: stable company profiles, SEC filing links, earnings archive. Empty company profiles have `noindex,follow` and are excluded from XML sitemap. Report-bearing profiles become indexable and enter the sitemap.
- `/wealth/earnings/<symbol>-earnings-fy<year>-q<quarter>/`: individual source-verified reports, preserved at their existing canonical URLs.

The S&P 500 index is approximately 500 companies and a few extra share classes; it is **not** the 500 largest companies globally or even the 500 largest US companies. S&P Global maintains the licensed official index and membership can change.

## Launch, monitoring and failures

The first production push to the monitored branch triggers the monitor and attempts to build `content/earnings-sp500.json`. Subsequent weekly membership refreshes and twice-hourly SEC scans commit only validated changes to the source repository, then dispatch the GitHub Pages site workflow. If the reference cannot be read/validated, that run fails without overwriting a good registry. If the registry has never been built, the new directory must say the register is being populated; the 15-company pilot is not presented as full coverage.

No shares prices, earnings guidance, analyst consensus or unsupported banks' revenue numbers are invented. Source freshness and data completeness vary by company; the directory lists monitored companies, **not 500 guaranteed published earnings articles**. Generated briefs are conspicuously labelled automated and not personally reviewed.
## Expanded stock directory and filing backfill

The additional 10 public companies are tracked from `content/company-watchlist.json` and retain their existing `/stocks/<slug>/` URLs. They are **not** S&P 500 members by virtue of being in the directory. Their official primary investor sources are checked daily, with 20-F/6-K filings staged for review rather than auto-parsed as US domestic earnings. SpaceX may qualify for SEC 10-Q/10-K articles only after validating its issuer identity.

Historical SEC earnings backfill is strictly limited to 2026-or-newer filing dates and financial periods, with at most two retrospective reports each day and thirty across the site, and never more than one per issuer in the first pass. The live thirty-minute monitor is unchanged apart from the SEC-verified extra issuer check. Each backfilled story retains its filing date and public filing URL; publishing occurs on the actual day Compound first posts it.

## 10 October 2026: consolidated SEC reports

The earnings monitor no longer emits individual FY-quarter Markdown articles.
Instead, source-verified Q1/Q2/Q3 data feeds a single canonical company
page at `/stocks/<ticker>/`, preserving actual fiscal periods and SEC
source dates. Q3 vs Q2 and year-to-date financial comparisons are omitted
if comparable standalone quarters cannot be validated. Old quarter URLs
canonical-redirect to their company page and are removed from the sitemap.
The historical article backfill scheduler was retired to avoid duplicate
or outdated quarter pages. Legacy document paragraphs above describe the
former launch architecture only.
