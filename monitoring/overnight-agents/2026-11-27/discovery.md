# Compound overnight discovery — 2026-11-27 (Europe/Dublin)

Production branch confirmed: `claude/clever-babbage-uibieq` (site.yml push target), base 1f4c70048a8dc2c83451e8b381e3b402c944d346 (merge of #303). Read AGENTS.md, the runbook incl. 14 Nov efficiency gates, 13–26 Nov records and all open PRs. Roster per routine: Technical SEO, Content Gap, Internal Linking, Content Freshness. Search Console Growth removed; no GSC/GA4 calls.

Access note: tonight the container could fetch compound.ie directly (HTTP 200), unlike earlier runs, so checks below use raw served HTML.

## 1. Technical SEO — measurable change staged (one PR, shared with Internal Linking)

Crawled every URL in https://compound.ie/sitemap.xml (1,682 `<loc>`, fetched 27 Nov ~00:30 Dublin) and recorded status, final URL, canonical, robots meta, title, description, H1 count and JSON-LD count. Then status-checked every root-relative internal link target found on those pages that is not itself in the sitemap (excluding /tag/ and /search/).

Clean (no change needed):
- 1,682/1,682 HTTP 200; 0 redirects; 0 canonical mismatches (every page self-canonical); 0 `noindex` in sitemap; 0 missing titles; 0 duplicate titles; 0 missing descriptions; every page has JSON-LD.
- robots.txt allows all crawlers except /preview/ and lists both sitemaps.

Defects found:
- **3 internal links to 404s, all raw HTML `href` in Markdown** (missed by the 26 Nov link test, which only read `](…)` links):
  - /life/ hub → `/life/workplace-stress-ireland-job-design-wellbeing-2026/` (404; canonical is `/news/…`, 200). Source `content/pages/life.md:51`.
  - /insurance/ hub → `/wealth/health-insurance-price-rises-benefit-cuts-ireland/` (404; canonical is `/news/…`, 200). Source `content/pages/insurance.md:193`.
  - /stocks/mat/ (404) linked from /wealth/mattel-tariff-refund-margin/ — no Mattel stock profile exists. **Not changed**: needs either a profile from the stocks workflow or an editorial wording change. Flagged to backlog.
- **1 legacy link**: /life/commute-time-ireland-hidden-cost/ → `/happiness/remote-working-ireland-rights-request/` (noindex redirect stub; canonical `/life/…`, 200). Source `content/happiness/commute-time-ireland-hidden-cost.md:104`.
- Review-only: 7 pages render 2+ `<h1>` because the Markdown body repeats the title as `# …`: six pension chapters (when-can-i-access-pension, pension-options, pension-funds-fees, how-pensions-work, how-much-pension-contribute, changing-jobs-transfer-pension) and /news/manchester-city-114-financial-rule-breaches-explained/ (13 H1s, 12 `# ` body headings). Not staged (one-PR limit; heading changes touch 7 article bodies). Backlog.
- Review-only: 10 pages share the sitewide default meta description (/, /about/, /contact/, /cookies/, /disclaimer/, /editorial-policy/, /privacy/, /ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/). The three tool/map pages would benefit from their own. Backlog.
- Review-only: /companies/epic-games/ and /companies/neuralink/ are live and indexable but intentionally excluded from the sitemap (build.py adds private profiles only when they have stories). Thin stub profiles; consider `noindex` until they have coverage. Needs a decision, not changed.

Staged in [PR #304](https://github.com/davidomarayt/compound/pull/304): the 3 link fixes + `tests/test_content_internal_links.py` now also scans `href="/…"` links (fails on base with exactly those 3 links, passes on head). `/wealth/` added to the generated-hub allowlist (live 200).

## 2. Content Gap — review-only, backlog updated

Deduplicated against 13–26 Nov records and open PRs. No new page proposed. Backlog (fingerprint | source | checked | owner | priority | disposition):

- `/life/, /insurance/, /life/commute-time…/|broken-html-links` | sitemap crawl | 27 Nov | Technical SEO | HIGH | STAGED #304.
- `/news/bank-of-ireland-5-percent-savings-account/|savings-tool-links` | article + BoI product page | 27 Nov | Internal Linking | MEDIUM | STAGED #304 (closes 26 Nov recommendation).
- `/wealth/mattel-tariff-refund-margin/|missing-stock-profile` | sitemap crawl (/stocks/mat/ 404) | 27 Nov | stocks workflow / editorial | MEDIUM | NEW, open.
- `7 pages|duplicate-h1` | sitemap crawl | 27 Nov | Technical SEO | LOW–MEDIUM | NEW, open.
- `/ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/|default-meta-description` | sitemap crawl | 27 Nov | Technical SEO | LOW | NEW, open.
- `/companies/epic-games/, /companies/neuralink/|thin-indexable-stub` | crawl + build.py | 27 Nov | owner decision | LOW | NEW, open.
- `/myfuturefund-calculator/|2026-rules-freshness` | myfuturefund.ie | 27 Nov | Content Freshness | MEDIUM | BLOCKED_SOURCE_FETCH again (CloudFront 403). Carried.
- Carried, unchanged: #254 shares CGT, #168 rent credit, #175 MyFutureFund matching, #270 PIA, #274 fuel. No query volumes, rankings or traffic claimed.

See [content.md](content.md).
