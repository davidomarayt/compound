# Compound overnight engineering — 28 November 2026 (Europe/Dublin)

Base 9fbe32794fa9990341ff458730feb2c5bf742b0f on `claude/clever-babbage-uibieq`. One substantive PR for this group, branch `claude/project-thread-hmnf6x` (link in the PR list; `Overnight-Agents: 2026-11-28`). No file overlap with tonight's discovery/content draft #319 (that PR touches two articles, one test file and discovery.md/content.md). Overlap with older open PRs was not checked hunk by hunk (shallow clone); GitHub's mergeability check on the PR is the gate.

## 7. Technical SEO — CHANGED/STAGED

Picks up tonight's discovery backlog item `default-meta-description` for the three tool pages. Cause: `content/pages/{ireland-rent-map,rent-commute-map,sun-path-explorer}.md` set `meta_description`, but `page.html` only used it for named slugs (solar, PIA, claims, caffeine), so these pages fell through to the sitewide default. Fix: one `{% elif page.meta_description %}` branch before the default. Rendered every `content/pages` page before and after: exactly those three pages change, each now carrying its own front-matter description; all other pages identical. The 7 static pages (/, /about/, /contact/, /cookies/, /disclaimer/, /editorial-policy/, /privacy/) have no `meta_description` and keep the default; left as backlog (low priority, needs new copy).

No title, URL, canonical, robots, sitemap, index, ads or consent change.

## 8. UX & Conversion — CHANGED/STAGED in the same PR

axe-core 4.10.2 (WCAG 2 A/AA) on live pages at 390 px width, 28 Nov ~02:50 Dublin: /ireland-rent-map/, /rent-commute-map/, /sun-path-explorer/, /tools/ clean; no horizontal overflow on any. Two real defects fixed:

- **/stocks/ and every /stocks/<ticker>/ page:** small labels failed AA contrast: section kickers `#a07659` (3.37–3.95:1), hub numbers `#a3775d` (3.73:1), "EXPLORE STOCKS" `#88756c` (4.04:1), ticker/sector line `#6d6d63` (4.43:1), metric period `#7c756d` (4.03:1). Darkened to `#7d5a43`, `#5f5f56` and `#6b5e57`, all ≥4.75:1 on every measured background. Same hue family, so the look is unchanged apart from slightly darker labels. CSS cache key bumped to `stocks-research.css?v=2`. (axe also flags the hub `<h1>` at 1.23:1; that is a false reading over the dark hero background, not changed.)
- **Calculator guides (e.g. /compound-interest-calculator/):** wide tables sit in a horizontally scrolling box that keyboard users could not reach (axe `scrollable-region-focusable`). The wrapper now has `tabindex="0" role="region" aria-label="Scrollable table"`.

No copy, tracking, layout, ad or consent changes; no conversion numbers claimed.

## 9. Revenue Optimisation — BLOCKED_DATA_ACCESS

Weekly check due tonight (last actual check 21 Nov: GA4 NOT_AUTHENTICATED, AdSense TRIAL_EXPIRED). Checked 28 Nov ~02:45 Dublin: this session has no GA4, AdSense or Supermetrics connector installed (connector listing shows only Google Calendar and Google Drive, both not connected). No metric query possible; none attempted. Next check due 5 Dec. Standard ads untouched.

## Validation and QA handoff

- Local on the PR head: full `pytest -q` 438 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. New `tests/test_page_meta_and_stock_contrast.py`: 4 failed on base, 4 passed on head. `tests/test_stock_research_layout.py` updated for the v=2 cache key.
- Static build left to CI (pre-existing local News image-cache requirement). No CI success or deployment claimed here.
- Risk low; rollback = revert the single commit. Not merged, not published. The 06:17 QA decides.
