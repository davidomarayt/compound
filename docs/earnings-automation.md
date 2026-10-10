# Compound Earnings — source-verified automated publishing

## What is automated

`.github/workflows/earnings.yml` now checks a validated, versioned S&P 500 constituent register. It monitors approximately one quarter of unique companies per run at :17 and :47 UTC (full sweep in roughly two hours). The register is refreshed weekly and at initial deployment. SEC 10-Q or 10-K filings within a 10-day lookback are checked using structured company facts. At most eight verified new articles publish per run under `/wealth/earnings/`; ambiguous financial data are skipped. See [S&P 500 automation](sp500-automation.md) for the registration and company-profile details.

**Text-only policy:** automatically published earnings articles contain financial text and tables only. They do not receive cover photographs, stock-photo fallbacks, charts or image-based social previews.

**Publication threshold**: revenue, net income, and diluted GAAP EPS for the same exact filing and standalone reported period, plus matching year-earlier comparable figures. The reporting system intentionally skips companies with incomplete or ambiguous data, including firms whose financial statements require sector-specific metrics. Quarterly reports are 10-Q only; 10-K results are correctly described as annual.

**What is not covered yet**: immediate earnings press releases, unofficial social posts, non-US listings, consensus estimates, adjusted EPS, guidance, transcript summaries, stock price reactions, or automatic interpretation. Results may follow the original earnings press release by days or weeks.

## Operating guardrails

- Respect SEC fair access: identifying contact in `User-Agent`, request throttling, no keys needed.
- Original SEC filing, Company Facts links and accession number included in each report.
- Match reporting dates and durations; do not confuse year-to-date amounts with quarter-only results.
- Unique ticker + fiscal period filenames prevent duplicate publication.
- Excludes today's implied gains, price targets or investment recommendations.
- Editing, replacing or correcting already-published articles is manual to avoid silent data changes.
- No generated article is labelled as manually reviewed. Corrections point to the site's public contact email.
- Scheduled GitHub runs can start late or be dropped. The lookback window helps recover missed runs.
- Changes land as committed Markdown and flow through the existing GitHub Pages build.

## Manual test

Use Actions → Compound Earnings Monitor → Run workflow, with **dry_run=true** (default). Check the job output for candidates before enabling publication. The scheduled workflow publishes automatically after merge to the repository's default branch. To disable, disable the workflow in Actions; or remove the `schedule` triggers.

To test offline: `python -m pytest tests/test_earnings.py -q`. No SEC traffic is used in the unit tests.

The old `content/earnings-watchlist.yml` is a fallback for offline/manual legacy tests only. Production index coverage is controlled by the validated `content/earnings-sp500.json` snapshot, refreshed by `scripts/sp500_registry.py`. Do not manually add tickers to imply index membership. Avoid mass publishing without reviewing factual quality and web-search traffic.
## Historical SEC earnings rollout (from 10 October 2026)

`.github/workflows/earnings-backfill.yml` publishes up to **eight** verified
filing reports in one daily batch, with an initial batch on release. The first
pass is capped at **one recent, qualifying historic 10-Q or 10-K per issuer**.
It looks back up to 550 days for matching SEC XBRL revenue, GAAP net income
and diluted EPS with year-earlier comparables. Every article includes the
real filing date and accession, and carries a publication date of the day
it was published; history is never falsely presented as breaking news.
Existing issuer reports are not duplicated or silently overwritten.
Eligible reports retain SEO indexability; monitor indexing, quality and
crawl load before increasing batch size. Dry-run dispatches do not publish.

## Ten additional global public companies

`content/company-watchlist.json` is the exact ten-company source of truth:
SpaceX (SPCX), TSMC, ASML, Samsung Electronics, Toyota, Tencent, BYD,
Nintendo, Novo Nordisk and LVMH. The unified 510-company stock directory
continues to present these alongside S&P stocks without a visually separate
section.

The 30-minute SEC monitor includes SpaceX **only if the SEC ticker registry
verifies a matching SpaceX/Space Exploration Technologies issuer** and a
qualifying 10-Q/10-K is available. SEC identity is checked every run rather
than invented or inferred from a ticker symbol.

Many other international firms use 20-F, 6-K, IFRS and local-exchange
disclosures rather than standard US domestic 10-Q/10-K reports.
`scripts/global_earnings_watch.py` checks each of the ten official
investor-relations URLs daily and retrieves 20-F/6-K filings for
SEC-identifiable overseas companies. New official links and SEC filings go
to `monitoring/global-earnings-review.json` as **unpublished review
candidates**. This is intentionally not automated earnings publication:
individual accounting schemas, periods, currencies and disclosure dates
must be validated before converting them into reports.

Some IR pages block automated requests, are client-rendered, or are not
dedicated financial-results feeds. The JSON logs the limitation; a 200
response must not be represented as proof of complete financial coverage.
No source status or unverified financial number appears as a published
earnings article. Regulated share-price charts remain separate from
filing-backed financial statements.

A scheduled monitor run failing due to official-source restrictions should
be investigated rather than worked around with unrelated or unlicensed
sources. Manual backfill should never be used to mass publish repetitive
thin pages.
