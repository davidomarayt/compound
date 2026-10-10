# Compound Earnings — source-verified automated publishing

## What is automated

`.github/workflows/earnings.yml` checks a 15-stock watchlist at :17 and :47 every hour (UTC). When an SEC 10-Q or 10-K has arrived within the last five calendar days, `scripts/earnings.py` fetches SEC Company Facts. It publishes at most three new articles per execution, written to `content/wealth/`, with canonical URLs under `/wealth/earnings/`.

**Publication threshold**: revenue, net income, and diluted GAAP EPS for the same exact filing and standalone reported period, plus matching year-earlier comparable figures. The first version intentionally skips companies with incomplete or ambiguous data. Quarterly reports are 10-Q only; 10-K results are correctly described as annual.

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

To expand tickers, edit `content/earnings-watchlist.yml`. Avoid mass publishing without reviewing factual quality and web-search traffic.