# Compound overnight engineering — 27 November 2026 (Europe/Dublin)

Base 1f4c70048a8dc2c83451e8b381e3b402c944d346 on `claude/clever-babbage-uibieq`. One substantive PR for this group: [draft PR #305](https://github.com/davidomarayt/compound/pull/305), branch `claude/project-thread-6cyji5`. It picks up the duplicate-H1 backlog item that tonight's discovery run found in its sitemap crawl and did not stage (discovery.md on #304). Overlap check: none of the 7 content files is in #304. Draft #175 touches `how-much-pension-contribute-ireland.md`, but in other hunks (sources list and a new section near line 65); this PR only removes line 32 of that file, so the two should merge cleanly. Confirmed by comparing that file's blob on every open PR head.

## 7. Technical SEO — CHANGED/STAGED

The article template already renders the title as the page's one `<h1>`. Seven article bodies added more `<h1>` elements through Markdown `# ` headings:

- Five pension course chapters repeated the title as `# …` straight after the chapter nav: pension-options, how-much-pension-contribute, when-can-i-access-pension, pension-funds-fees, how-pensions-work. Removed the repeated heading line. No body text changed.
- changing-jobs-transfer-pension: its `# What happens to your pension when you change jobs?` is a question worded differently from the title, so it is kept and demoted to `##`.
- /wealth/manchester-city-114-financial-rule-breaches-explained/: 12 section headings used `# `, so the page had 13 `<h1>`s, and its `###` subsections sat under the wrong parents. All 12 demoted to `##`, matching the article's other sections.

No title, URL, date, reviewed field, metadata, canonical, robots, sitemap, template, ads or consent changes. New `tests/test_article_single_h1.py`: a sitewide guard (no article `body_html` contains `<h1`) plus exact checks for the two demotions. Fingerprint `7 pages|duplicate-h1`, priority low–medium, owner Technical SEO.

## 8. UX & Conversion — CHANGED/STAGED in the same PR

Screen-reader users who move through a page by heading now get one page title and a correct section outline. On the Man City explainer this was 13 top-level headings; it is now one, with the sections and subsections nested correctly. The visible text is the same. Heading sizes change for the demoted lines (h1 to h2 styling). No layout, copy, tracking or ad changes; no conversion numbers claimed.

## 9. Revenue Optimisation — BLOCKED_DATA_ACCESS

Last actual check 21 Nov (GA4 NOT_AUTHENTICATED, AdSense TRIAL_EXPIRED). The seven-day backoff runs to 28 Nov, so no query tonight. The next check is due on tomorrow's run. No ad, consent, account or placement changes; standard ads untouched.

## Validation and QA handoff

- Local on the PR head: full `pytest -q` 430 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. The new test fails on base (3 failed) and passes on head (3 passed).
- Static build left to CI (the local build has the pre-existing News image-cache requirement noted on 26 Nov). No CI success claimed here.
- Risk low; rollback = revert the single commit. Not merged, not published. The 06:17 QA decides.
