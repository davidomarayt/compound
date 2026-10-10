# Expanded company research: listed and private watchlists

**Checked:** 10 October 2026. The existing 500-company S&P 500 feed is unchanged.

## New destinations
- `/stocks/`: the existing S&P 500 search/table plus curated non-S&P public-company cards.
- `/stocks/{slug}/`: 10 major public companies outside the monitored S&P 500. The slug uses the US ticker where possible (e.g., SPCX, TSM, ASML) or an exchange-qualified URL slug (e.g., `005930-ks`, `0700-hk`, `7974-t`, `mc-pa`). Charts use explicitly registered TradingView symbols, and the profile names the actual listing venue, including ADR status.
- `/companies/`: directory of 13 private companies.
- `/companies/{slug}/`: private-company research landing page; no stock price chart or tradeable ticker.

## Content modelling and linking
The curated watchlist is `content/company-watchlist.json`. This is **not** an S&P index update or an input to the automated SEC earnings scanner. Do not combine its company_count with S&P membership.

To link a stock report or news article explicitly to a watchlist public company, tag it `stock-spcx`, `stock-005930-ks` etc. Unique unambiguous ticker tags (e.g. `spcx`) are also recognised. For private companies tag `company-openai`, `company-revolut`, etc. Do **not** match on substrings of article headlines. The source article will link back to the corresponding hub; hub lists new content chronologically. Keep canonical article URLs under `/wealth/` or `/news/`.

No unreported P&L, revenue, market cap, IPO forecast or private funding estimate is generated for placeholders. Before writing detailed research verify latest ownership, listing status, regulatory filings and dates. Companies transitioning from private to public require a deliberate URL/canonical migration and database update.

## Indexing and revenue
All company URLs are browseable. Empty and unresearched profiles are **noindex,follow**, not placed into search.json or sitemap.xml, and have no ads; article-backed profiles become eligible for discovery and ads, subject to editorial quality checks. The directories themselves are indexable. TradingView pricing may be delayed; never equate quoted prices with SEC financial statements or ADRs with local ordinary shares. No claim is made about eligibility for Ireland's Personal Investment Account.

Run tests under `tests/test_company_watchlist.py`, then live-check the directories and a private and listed stock profile, chart symbol, canonical, noindex and links.
