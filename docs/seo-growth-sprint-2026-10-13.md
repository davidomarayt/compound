# Compound.ie — October 2026 SEO growth sprint

**Date:** 13 October 2026  
**Source:** Google Search Console user-exported CSVs through 10 October 2026. These are retrospective data, not live measurements.

## Baseline and immediate priorities

- **21,244 Google impressions, 167 clicks, 0.79% aggregate CTR.** In the latest seven days: 9,990 impressions, 69 clicks (previous seven: 7,521 impressions, 82 clicks).
- Existing high-impression calculator and guide pages are the priority for title/snippet testing, search-intent improvements and stronger related-page linking, not mass new article production.
- Do not treat an aggregate CTR as a performance target for all positions. Segment by page, query, position and device; higher impressions from lower rankings can reduce aggregate CTR even as coverage expands.
- Changes made in this sprint: Salary-to-Hourly and Fuel Cost calculator copy and titles; Standard Drinks and PIA snippets; confirmed Budget 2027 Living Wage/Minimum Wage update; active SEAI Battery Grant guide; cross-links to /solar/ and /insurance/ from closely related pages.

## Tracking model and interpretation

The consent-gated sitewide `solar-funnel.js` already records the event `solar_journey_click` once per qualifying **internal link click** (not once per page view), with no form input or query-string data. Relevant parameters:

| Dimension | Example / interpretation |
| --- | --- |
| `source_path` | Article or tool that contains the clicked link |
| `destination_path` | Canonical internal page destination |
| `destination_step` | `hub`, `payback_calculator`, `quote_comparison`, `quote_brief`, `installer_directory` |
| `journey_origin` | First source path retained within a consented 30-minute tab session |
| `source_type` | `news`, `evergreen`, `tool`, `solar_hub`, etc. |
| `link_area` | Article body, related content, navigation, or page content |
| `audience` | `homeowner_research` or `installer_business` |

Additional interaction events already exist: `solar_quote_comparison_used` (first comparator input), `solar_quote_brief_copied` (successful copy of self-generated quote request); check the remaining `solar-hub.js` events for more details. A quote brief **copied** is an intent proxy, NOT a completed homeowner quote enquiry. The current `/solar/get-quotes/` generates a copyable request; it does not currently transmit homeowners' requests to an installer.

The new event `solar_installer_enquiry_submitted` represents the FormSubmit provider's successful return to `/solar/for-installers/?submitted=1` (and only when analytics consent was granted). It represents **an installer business enquiry**, not a consumer lead or proof of payment. Count separately and inspect for duplicate navigations and provider completion semantics.

**Key GA4 configuration after access is restored:**
1. Register event-scoped custom dimensions named `source_path`, `destination_path`, `destination_step`, `journey_origin`, `source_type`, `link_area`, and `audience` in Admin > Custom definitions (event parameters already sent by site).
2. Verify actual `solar_journey_click`, `solar_quote_comparison_used`, `solar_quote_brief_copied` and `solar_installer_enquiry_submitted` events in DebugView and Events on a consented session.
3. Build an Exploration with path funnel **organic article → Solar Hub → tool → quote preparation**. Use event totals and distinct users for separate questions; do not sum raw clicks as unique visitors.
4. Track installer directory/outbound contact separately once there is an explicit verified consumer-lead pathway; do not advertise a fabricated qualification/conversion rate.
5. Segment by `audience` to keep B2B subscription acquisition separate from household solar-interest metrics.

The connected GSC Wizard integration returned a **trial/subscription expired** error on 13 Oct 2026, and Supermetrics GA4 indicated **not authenticated**. This prevents independent confirmation of GA4 receipt, custom dimension registration, and Search Console indexing via those integrations. Source-level and GitHub build checks are not a substitute for those live account verifications.

## Indexing checklist (Google account access needed)

The site builder generates `/sitemap.xml` for published articles, guides, tools and static pages; `robots.txt` links the sitemap. The pages below have canonical-path entries in their content front matter. This verifies the site's **intended** discoverability, not Google's indexed/canonical verdict.

After Search Console access is restored, use *URL Inspection* to check **live** crawl eligibility and indexing for:

- https://compound.ie/solar/
- https://compound.ie/solar/grants/
- https://compound.ie/solar/batteries/
- https://compound.ie/solar/compare-quotes/
- https://compound.ie/solar/get-quotes/
- https://compound.ie/insurance/
- https://compound.ie/news/solar-battery-grant-ireland-budget-2027/
- https://compound.ie/salary-hourly-rate-calculator/

Record for each: last crawl, page indexed yes/no, Google-selected canonical, user canonical, mobile usability if available, last modified. Re-submit `https://compound.ie/sitemap.xml` only if absent/outdated; request indexing only for material new/corrected pages. Search Console will not guarantee an indexing date.

## Next evergreen content queue — research, not auto-publish

This is an **editorial research queue**. Before drafting, re-run `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, and `data/content-inventory.json` duplicate-intent checks; the 13 Oct index lacked exact east- or west-facing solar roof titles. Prioritise improvements of existing canonicals where search intent overlaps.

1. **Solar panels on east- or west-facing roofs in Ireland: how much does orientation matter?** Distinct technical search intent. Support with evidence-based SEAI/PVGIS location-specific modelling for matched roof pitch and shading; give clearly labelled assumptions and cross-link to existing `/wealth/how-many-solar-panels-do-i-need-ireland/`, `/solar/`, `/solar-payback-calculator/`, `/solar/compare-quotes/`. Relevant roof-specific hero needed, not generic kitchen/calculator.
2. **Do solar panels pay off in an Irish winter?** Seasonal yield, household demand and savings; distinguish Irish solar yield vs imported tariff units and export payments. If `/wealth/solar-panels-ireland/` already serves this search, add a detailed section rather than duplicate a new article.
3. **How to compare two solar installer quotes in Ireland**, only if different enough from `/solar/compare-quotes/` and `/solar/get-quotes/`; otherwise deepen existing pages with examples and checklists.
4. **Home insurance rebuild cost vs market value in Ireland**, only if distinct from the existing `/home-insurance-rebuild-cost-calculator/`; likely improve the existing guide/tool rather than create another URL.

Ensure original fact checking, date-stamped government/SEAI references, worked calculations, mobile-first useful diagrams/charts, pinned relevant hero/social photography, strong unique intent, and tasteful AdSense placements before publication.

## Post-deployment measurement (14 and 28 days)

- Verify a successful GitHub Pages `site` workflow deployment and HTTP 200/canonical/meta tags for all updated URLs. A successful build alone is insufficient.
- At day 14, compare each updated page's query-by-query impressions, CTR, position and clicks versus pre-change 14-day period. Exclude or explain new-query ranking shifts.
- Solar hub: organic entrances, article-to-hub clicks, unique tool users, quote-brief copies, and any *verified* homeowner lead submissions (none implemented as of this sprint).
- Insurance hub: organic entrances, links from insurance guides, tool interactions and session engagement.
- At day 28, retain/revise SEO snippets using page/query/device evidence. Do not assume CTR increases automatically or promise sponsor-ready enquiry rates.

## Execution limits

This document and GitHub source commits implement code/content changes. They are **not** proof that Google has indexed those URLs, GA4 reports events, prospective customers have converted, or the latest site build is deployed. Verify independently before reporting those outcomes to advertisers.
