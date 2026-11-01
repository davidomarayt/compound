# Finance discovery

Every `compound build` emits:

- `/finance/`: server-rendered, source-linked directory, linked in the site footer and main XML sitemap.
- `/finance/index.json`: version 1 custom catalogue with canonical URLs, descriptions, declared source links and available dates. It is navigation metadata, not a financial data API.
- `/llms.txt`: optional Markdown navigation with a bounded set of starting points and a link to the JSON catalogue.

Selection lives in `compound/site/finance_discovery.py`: curated investing guide slugs; the existing 20 priority stock profiles with filing data; 30 most recently updated published Wealth articles tagged stocks/company-research/stock-analysis/earnings; finance-category calculators and the car-finance/compound-interest calculators. The full stock register remains in `/stocks/` and the sitemap. Missing guide slugs are omitted for minimal/test builds. Drafts and superseded automated quarter articles are excluded. New qualifying company analysis enters automatically at build time.

Sources are taken from existing content metadata or the underlying company filing report. A source link is not an assertion that its claims have been freshly checked. Entries without declared source links retain an empty list; no citations or review dates are invented. Stock records distinguish fiscal label, period end and filing date. Article modification dates use the explicit review date or publication date, not build time. Calculator dates retain their authored `updated` value. No price feed, forecast or financial recommendation is created by this index.

## Structured data decisions

The HTML directory uses `CollectionPage` with an `ItemList` that exactly matches the visible links. Existing Article/NewsArticle citation metadata and calculator WebApplication/FinanceApplication metadata remain in place. Existing priority stock pages describe a WebPage about a Corporation with filing citations. Do not label editorial analysis as a FinancialProduct, invent reviews/ratings, or use Dataset simply to seek a search feature. JSON-LD is descriptive; it does not grant special AI placement.

## Access and canonical behaviour

The wildcard robots group allows public content for all crawlers, including OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, Googlebot and bingbot. It continues to disallow `/preview/`. No new bot-specific group overrides that protection, and training policies are unchanged. robots.txt is advisory, not authentication.

Only the HTML directory joins the sitemap; JSON and llms.txt are discoverable through links and the robots comment. Existing stock and editorial canonical routes are retained. The build rejects an indexed target if it is missing, absent from the sitemap, noindex, a redirect, or has a mismatched/multiple canonical. Rebuilding replaces the catalogue rather than retaining removed entries.

## Validation and measurement

Run `python -m pytest -q tests/test_finance_discovery.py` and the normal production image preparation + `compound build`. The site workflow runs the regression checks as a publication gate. Tests cover drafts/legacy content, provenance, dates, missing/redirect/noindex targets, sitemap integration and crawler preview exclusions.

After deployment, check HTTP 200, content types (HTML, JSON and plain text), canonical tags and absence of blocking X-Robots-Tag/CDN rules on `/finance/`, `/finance/index.json`, `/llms.txt` and representative target pages. A user-agent probe verifies delivery for that request, not access from an actual crawler's network. Track referrals and actual citations over time; neither a successful build nor llms.txt establishes indexing, recommendations or answer placement.

Reference guidance:
- https://developers.google.com/search/docs/appearance/ai-features
- https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
- https://schema.org/CollectionPage
- https://schema.org/ItemList

## Automated production verification

The publishing workflow now runs an independent `verify-finance-discovery` job after
successful deployment. `python scripts/verify_finance_discovery.py` checks the three
public discovery endpoints, the homepage discovery link, robots.txt, the XML sitemap,
all catalogue URLs' sitemap membership and Googlebot permissions, and two live HTML
targets from each of the four catalogue groups. It rejects unexpected redirects,
wrong content types, blocking response headers/meta directives, mismatched canonicals,
malformed/missing JSON-LD and disagreement between the directory's visible links,
ItemList and JSON catalogue. Network requests have bounded retries and timeouts.
It also probes the three endpoints with a Googlebot user agent; this is not evidence
of a request from Google's infrastructure. Run with `--all-targets` for a full live
catalogue audit. Counts are derived from the catalogue rather than fixed at 107.

These checks verify technical discovery and indexing prerequisites, not Google's
index. JSON and llms.txt intentionally are not sitemap entries or HTML pages with
canonical tags. The JSON's `url` identifies its HTML directory; it is not an HTTP
canonical instruction. Google does not need llms.txt or a custom JSON catalogue for
Search/AI placement. Use Search Console URL Inspection for indexed status and Google's
selected canonical; generic web search results do not independently establish Google
indexing. Neither valid JSON-LD nor sitemap inclusion guarantees indexing or ranking.
