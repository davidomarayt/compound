# Compound Earnings — One continuously updated fiscal report per company

**Current publishing model (10 October 2026): one canonical `/stocks/<ticker>/` report per company.**
The scheduled SEC monitor examines roughly one-quarter of the S&P 500 every
30 minutes (plus SEC-identity-verified SpaceX). An eligible 10-Q/10-K updates
`content/earnings-profiles/<ticker>.json`; it NEVER creates a quarter-specific
Markdown article. The GitHub Pages builder re-renders the existing stock
page. This prevents repeated earnings URLs in the sitemap and RSS.

When a valid Q3 10-Q arrives, the parser finds the same issuer's official
fiscal-year Q1 and Q2 10-Q filings in SEC EDGAR, extracts comparable
standalone three-month revenue, net income and diluted EPS from exact SEC
XBRL accession numbers, and keeps only 2026-or-newer reporting periods.
The page displays actual period-end dates, SEC links and a quarterly table,
Q3 vs Q2 percent changes, quarterly charts, and YTD revenue/net income
with matching prior-year growth where all intervening quarters are verified.
Incomplete figures are labelled as such; fiscal FY2027 Q1 ending in 2026
is valid and is NEVER renamed FY2026 Q3.

The first nine quarter-article URLs are redirected to their canonical
company pages, with noindex and canonical metadata, rather than disappearing
or becoming broken links. Their existing SEC XBRL snapshots can seed initial
presentation while the main monitor builds fully hydrated reports.

The separate `earnings-backfill.yml` scheduled job has been retired. The
historical generator is no longer called by automation; Q1 and Q2 are only
collected as context for newly detected filings, not published as standalone
articles. No pre-2026 individual earnings article backfills. No implied Q4
derived from a 10-K. No image or price chart treated as proof of GAAP income.

**International companies:** The 10 additional public firms remain in the
same stock directory; the global watch checks their primary investor
pages and SEC 20-F/6-K as appropriate. Non-domestic accounting formats
are recorded for review, NOT automatically converted to US domestic Q3
results. Their reports are only shown when metrics pass issuer-specific
verification. No ticker/company identity is inferred from names alone.

**Transparency:** Figures are source-linked, SEC-filing based, automated,
not individually reviewed before publication, and not personal investing
advice. TradingView market prices are a separate data source. Corrections:
david@compound.ie.
