# Compound overnight engineering — 26 November 2026 (Europe/Dublin)

Base caf84557f698837f1021e8a345a274a85ba6ebd3 on `claude/clever-babbage-uibieq`. One substantive PR for this group (link in the PR list for `Overnight-Agents: 2026-11-26`, branch `claude/project-thread-bs3385`). Distinct from today's #289 (tools.yml labels only): this PR touches content Markdown links and one new test, and none of its 21 content files appear in any open PR's file list (checked all 19 open PRs).

## 7. Technical SEO — CHANGED/STAGED

Parsed every root-relative Markdown link under content/ against the routes the builder actually emits (article/page/tool URLs plus data-built hubs and /stocks/, /companies/, /health/, /pia/ prefixes). Found three defects:

1. **54 links in 20 files** (19 Life articles, 1 Health) pointed at legacy `/happiness/<slug>/` paths. build.py emits those only as noindex client-redirect stubs for old external links, so internal links were sending readers and crawlers through an extra redirect hop to a noindex page. Each now points at the article's own canonical URL (mostly `/life/<slug>/`, some `/news/<slug>/`), taken from load_articles — no guessed targets; every legacy slug mapped.
2. `/tools/glp-1-cost/` in the Eli Lilly Foundayo Europe approval article: route never built (404). Now `/glp1-cost-calculator-ireland/`, the real tool URL.
3. `/wealth/investing-in-ireland/` in the young-savers survey article: route never built (404). Now `/wealth/how-to-start-investing-in-ireland/`, which 37 other links already use.

Link targets only; no anchor text, dates, reviewed fields, metadata, canonical, robots or sitemap changes. New `tests/test_content_internal_links.py`: sitewide guard (no legacy /happiness/ links; every root-relative content link resolves to a built route or generated prefix) plus exact assertions for the two 404 fixes. Fingerprint `content/*|internal-links-to-redirect-stubs-and-404s`, priority high, owner Technical SEO.

## 8. UX & Conversion — CHANGED/STAGED in the same PR

Readers clicking the GLP-1 calculator and beginner-investing links got a 404; they now land on the intended tool and guide. Life links now open directly instead of flashing a redirect page. No copy, layout, tracking or ad changes; no conversion numbers claimed.

## 9. Revenue Optimisation — BLOCKED_DATA_ACCESS

Last actual check 21 Nov (GA4 NOT_AUTHENTICATED, AdSense TRIAL_EXPIRED); seven-day backoff runs to 28 Nov, so no query tonight. No ad, consent, account or placement changes; standard ads untouched.

## Validation and QA handoff

- Local on the PR head: full `pytest -q` 425 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. New test fails on base (4 failed) and passes on head.
- Local `compound build` stops on the pre-existing News image-cache requirement (ireland-tax-statistics-2025-usc-fell), same as #289's record, so the static build is left to CI. No CI success claimed here.
- Risk low; rollback = revert the single commit. Not merged, not published. The 06:17 QA decides.
