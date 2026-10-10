# Compound Earnings — visual, editorial and technical quality standard

Status: implemented in the static-site generator and SEC filing monitor.

## Editorial goal

A reader should understand **what changed in under ten seconds** and reach the original SEC filing in one tap. Articles are concise, sourced, indexable and genuinely useful without requiring JavaScript. No stock photos or unrelated editorial hero images.

## Page hierarchy

1. Company, ticker, fiscal period and published date; accurate automated byline.
2. One-sentence data-led takeaway.
3. Three responsive KPI cards: revenue, net income, diluted US GAAP EPS, with the corresponding year-earlier figure and YoY percentage.
4. Source-verified four-column comparison table, with correct headings and tabular numerals.
5. Three responsive accessible SEC-period charts with dates, units and underlying values in expandable HTML tables.
6. Short interpretation and limitations, with a direct primary-filing URL.
7. One compact related-company-history / PIA Centre / PIA Calculator navigation area near the bottom.
8. Any separately configured display ads only outside the core financial data.

Generated content is terse and factual; missing values must be withheld, not fabricated. The journal does not infer why a stock price moved from financial-statement data alone.

## Data validation

- Primary sources: SEC EDGAR 10-Q or 10-K and XBRL Company Facts.
- The headline's metrics must match the exact accession and reporting duration. Current and prior-year comparisons share the same US GAAP accounting concept.
- For quarterly charts, show up to eight **actually reported stand-alone** quarters from the same concept, with submission dates no later than the report being summarised. A fiscal Q4 is *not* inferred from full-year minus year-to-date amounts.
- For annual charts, show up to four complete annual reporting periods. Do not mix annual and quarterly axes.
- Use separate metrics where reporting calendars or tagged concepts differ. Missing quarters and discontinued tags are omitted, not connected with invented points.
- Newly automated articles include their source-bound `earnings_snapshot` YAML metadata. Older 2026-10-10 articles contain a two-period snapshot based on previously published rounded SEC figures; their original, verified YoY percentage is preserved rather than recomputed from rounded values.
- On conflict, missing current metric, or invalid non-finite numbers, the renderer raises an error rather than displaying unsourced figures.

## Graph standards

Charts use inline semantic SVG with real dates and legible labels, no remote scripts or image downloads. Maintain neutral axes, note negative EPS/profit correctly, and provide the source values in HTML tables underneath each graph. Data labels are not based on price movements. Graphs are responsive and honour reduced-motion preferences.

## SEO

- Preserve permanent `/wealth/earnings/<ticker>-earnings-<period>/` URLs, original SEC source links, canonical tags, Article JSON-LD and breadcrumbs.
- Use a unique year/fiscal-period title with ticker, revenue, net income and GAAP EPS terminology.
- Company profiles at `/wealth/earnings/company/<ticker>/` are indexable only when they have genuine content; unpopulated profiles remain noindex.
- Company history and archive links provide sensible navigational context. PIA pages are secondary, and no company is portrayed as eligible for a PIA without evidence.
- Keep pages fast, text-first and accessible; do not add images solely for Discover eligibility.

## AdSense

The site's existing AdSense publisher script remains active. An optional `adsense.slots.earnings_mid` identifier may enable a single in-article display unit **after the earnings content**, while the standard bottom article slot can remain active. The existing top-of-article fixed slot is suppressed for these short earnings pieces to keep financial metrics immediately visible. Blank slot IDs are not rendered; no fake IDs have been supplied. Auto Ads behaviour is controlled in the AdSense console and may still insert ads.

Do not place fixed ads inside KPI cards, rows of financial statements, source tables or trend charts. Confirm the actual creative placement, mobile CLS and policy compliance in the live AdSense account before increasing ad density.

## Acceptance criteria

- Rendered report shows 3 KPI cards, 3 labelled data charts and a readable comparison table, with no raster hero, stock-image credit or client-side chart API.
- The reported YoY percentages agree with the original financial facts, including legacy rounded reports.
- Incomplete SEC data cannot create new unverified lines or false 8-quarter history.
- Internal links point to correct company profile, PIA Centre and calculator.
- Ads render only when genuine configured unit IDs exist, in designated areas away from the core data.
- A complete CI run and a GitHub Pages live verification must pass before launch.
