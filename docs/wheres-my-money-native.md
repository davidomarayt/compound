# Where’s My Money — native public spending library

Scope: 44 new canonical pages: a national overview, eight sectors, 34 programme
pages with multi-line detail, and methodology. All 57 source programme groups
and 228 component lines remain reachable. Singleton programmes stay on sector
pages; education opens all 16 components without a duplicate intermediary page.

## Data

`content/public-spending-detail-2026.json` is the versioned snapshot.
`content/public-spending-sources/2026/` retains primary-source chart captures and
provenance. SHA-256 hashes bind the normalized data to those captures. Figures
are integer euros; no government charting library, styling or runtime request
is used. The 2026 national sum is EUR 132,996,715,000. No 2027 projection is mixed
into 2026 figures. Four Social Protection component lists are incomplete; their
unitemised balances remain visible. A EUR 1,000 non-voted rounding difference is
retained. Housing history starts in 2020, not an invented 2016 zero series.

After a reviewed data update, run `python scripts/sync_wmm_views.py`. It generates
the data template, page routes, CSV and native receipt links. `--check` verifies
all derived files. The standard `load_pages` pipeline renders canonicals and
includes them in the sitemap and search. There is no second application server.

## Interface and SEO

Original server-rendered HTML/CSS bar charts and inline SVG history charts have
exact-value tables. Links, charts and tables work without JavaScript. Each page
has a unique title, description, canonical and breadcrumb. Programme pages link
to their parent sector, siblings and related Compound tools. Source links remain
as references, not the main detail action. Dataset markup states the reporting
period and the limitations; it does not claim the figures are actual spending.

Optional browser controls switch published amounts, parent shares and personal
spending illustrations. Every personal illustration uses the national total as
its denominator. Missing detail is not redistributed. Inputs are not persisted,
sent to analytics or placed in URLs. This is not a net-contributor score.

## Advertising and quality

The existing AdSense account and consent settings are inherited. Substantial
native data pages have two labelled between-section placements; methodology has
no manual slots. Main receipt placements remain three desktop / two mobile.

Run `python scripts/sync_wmm_views.py --check`, then
`python -m pytest -q tests/test_wmm_explorer.py tests/test_wheres_my_money.py`
and `node tests/wheres_my_money.cjs`.

For browser QA, run `python scripts/render_wmm_preview.py` followed by
`python scripts/verify_wmm_explorer.py` (requires Playwright Chromium).
Third-party requests are blocked during tests. The read-only WMM native explorer
quality workflow checks desktop, mobile, no-JS data, invalid inputs, native links
and the existing EUR 103,000 receipt regression. Screenshots are retained.
The source capture workflow is manual-only and cannot publish changes.
