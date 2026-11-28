# Compound overnight discovery — 2026-11-28 (Europe/Dublin)

Production branch confirmed: `claude/clever-babbage-uibieq` (GitHub Pages workflow `site`), base 9fbe32794fa9990341ff458730feb2c5bf742b0f (merge of #318). Read the runbook incl. 14 Nov efficiency gates, 14–27 Nov records and all 17 open PRs. Roster per routine: Technical SEO, Content Gap, Internal Linking, Content Freshness. Search Console Growth removed; no GSC/GA4 calls.

Note: the run started at 00:15 but was cut off by an API error at 00:16; this record is from the automatic restart, with checks made ~02:25–02:45 Dublin.

## 1. Technical SEO — measurable change staged (one PR, shared with Internal Linking)

Crawled every URL in https://compound.ie/sitemap.xml (1,694 `<loc>`, fetched 28 Nov ~02:30 Dublin; 12 more than 27 Nov) from raw served HTML, then status-checked all 60 root-relative internal link targets that are not in the sitemap (excluding /tag/ and /search/).

Clean:
- 1,694/1,694 HTTP 200; 0 redirects; 0 canonical mismatches; 0 `noindex` in sitemap; 0 missing or duplicate titles; 0 missing descriptions; every page has JSON-LD and every JSON-LD block parses.
- Every page now has exactly one `<h1>` (27 Nov: 7 pages had 2+; fixed by #305, confirmed live).
- The 3 broken links fixed by #304 are no longer found. robots.txt unchanged (allows all but /preview/, lists both sitemaps).
- /companies/epic-games/ now serves `noindex` (27 Nov backlog item handled elsewhere). /companies/neuralink/ is indexable but no longer a thin stub (Neuralink article published 27 Nov).

Defect found and staged:
- **/stocks/mat/ (404)**, linked from /wealth/mattel-tariff-refund-margin/ (`content/wealth/mattel-tariff-refund-margin.md:41`), carried from 27 Nov. Mattel is not on `content/earnings-sp500.json` or the listed watchlist, so the build never makes that profile. Replaced the dead link with a sentence pointing at the results release and 10-Q already in the article's sources. No figures changed.
- New test `test_stock_profile_links_point_at_generated_profiles` checks every `/stocks/<x>/` link in content against the profiles the build generates (S&P list + listed watchlist). The existing link test skipped all /stocks/ links, which is why this one survived. Fails on base (1 failed: the Mattel link), passes on head. All 13 /stocks/ant/ links resolve (watchlist slug).

Review-only, carried: 10 pages still share the sitewide default meta description (/, /about/, /contact/, /cookies/, /disclaimer/, /editorial-policy/, /privacy/, /ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/). Not staged (one-PR limit).

## 2. Content Gap — review-only, backlog updated

Deduplicated against 14–27 Nov records and open PRs. No new page proposed; no thin gap-filler. Backlog (fingerprint | source | checked | owner | priority | disposition):

- `/wealth/mattel-tariff-refund-margin/|missing-stock-profile` | sitemap crawl | 28 Nov | Technical SEO | MEDIUM | STAGED (tonight's PR). A real Mattel profile remains a stocks-workflow decision.
- `7 pages|duplicate-h1` | crawl | 28 Nov | — | DONE (#305, verified in served HTML).
- `/life/, /insurance/, /life/commute-time…/|broken-html-links` | crawl | 28 Nov | — | DONE (#304, verified in served HTML).
- `/companies/epic-games/|thin-indexable-stub` | crawl | 28 Nov | — | DONE (now noindex). `/companies/neuralink/` closed: has an article.
- `/retire-at-61-ireland-five-year-pension-gap/|savings-tool-links` | article (26 Nov) | 28 Nov | Internal Linking | MEDIUM | STAGED (tonight's PR).
- `/ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/|default-meta-description` | crawl | 28 Nov | Technical SEO | LOW | open.
- `/myfuturefund-calculator/|2026-rules-freshness` | myfuturefund.ie | 27 Nov | Content Freshness | MEDIUM | BLOCKED_SOURCE_FETCH (not retried; gov.ie and citizensinformation.ie also 403 tonight). Carried.
- Carried, unchanged: #254 shares CGT, #168 rent credit, #175 MyFutureFund matching, #270 PIA, #274 fuel. No query volumes, rankings or traffic claimed.

See [content.md](content.md).
