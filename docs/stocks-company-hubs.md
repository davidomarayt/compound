# Company research hubs: /stocks/{ticker}/

The canonical company URL is `https://compound.ie/stocks/<primary-ticker>/`; the browseable directory is `/stocks/`. These pages are rendered from the already-monitored `content/earnings-sp500.json` register, which counts unique companies by SEC CIK. An S&P 500 constituent snapshot is not a licensed official live index feed.

## Page types and source separation

- `/stocks/`: filterable company directory, with an indexable overview of methodology.
- `/stocks/aapl/`, `/stocks/nvda/`, etc.: one permanent company research landing page per CIK. TradingView provides market charts; SEC EDGAR provides filing links; generated earnings reports remain separate and linked.
- `/wealth/earnings/<ticker>-earnings-<period>/`: existing reports retain their canonical URLs and SEC financial charts, and link back to their company hub.
- `/wealth/earnings/company/<ticker>/`: legacy paths emit noindex, canonical and immediate client/meta redirect to the new stock page. **GitHub Pages cannot send a server-side HTTP 301.** Use real 301 redirects at the CDN or edge if routing is moved to an HTTP-capable host.
- Alternate share classes redirect to the primary CIK stock profile: e.g. `/stocks/goog/` to `/stocks/googl/`, rather than duplicate company profiles.

## Connect editorial content

Add the **lower-case primary or alternate ticker** as a dedicated `tags` entry on a company-specific article; e.g. `tags: [stocks, aapl, company-research]` or `tags: [news, nvda]`. Ticker tags make matching explicit. No text-only headline detection or keyword guesses are used.

The generator automatically groups exact matches into earnings reports, latest company news, and research/guides. The matching research/news articles receive a contextual link back to the company page. Check that the ticker truly identifies the company before applying it. Avoid generic ticker tags to prevent misleading associations.

## Quality, search and advertising

All canonical public stock profiles are eligible for search indexing and included in `sitemap.xml`, including profiles awaiting earnings or editorial coverage. Do not apply `noindex` based on coverage availability. Profiles without dated coverage omit sitemap `lastmod`. Internal `search.json` continues to highlight profiles with coverage; unfinished research is not presented as complete and existing advertising eligibility rules remain unchanged. Legacy and alternate-ticker redirect URLs retain `noindex` and stay out of the sitemap. Indexability does not guarantee Google indexing or ranking; continue improving source citations and company-specific research.

Market prices are TradingView-provided and may be delayed; SEC accounting statements are not equivalent to share prices. No claims are made that a given security is eligible for a Personal Investment Account.

## QA

Run `pytest -q`, build the site, and verify `/stocks/`, one covered profile, one profile awaiting coverage, alternate-ticker alias, and old earnings-company redirect. Check canonical, HTML title, search and sitemap targets, mobile TradingView sizing, and links from a matching article.
