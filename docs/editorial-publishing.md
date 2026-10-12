# Compound.ie editorial publishing pipeline (12 October 2026)

## Goal
Publish accurate, search-ready articles quickly without tying their availability
to unrelated Lighthouse/mobile QA. A green deployment alone is not a fact check.

## Editorial release — per article
1. **Editorial checks before committing:** verify current official Irish facts, dates,
   amounts, eligibility and quotes against primary sources; check for duplicate or
   outdated Compound pages; label hypothetical figures clearly. The automated
   validator does **not** prove any factual statement to be true.
2. **SEO and trust:** unique intent and slug, concise answer first, meaningful
   summary/metadata, appropriately structured headings, dated sources, readable
   accessible charts with caption/units, topic-specific licensed cover with
   descriptive alt and proper credit; evergreen links and one clear next step.
3. **Conversion:** link only relevant calculators, independent topic hubs and
   optional quote tools. Do not misrepresent a click as a lead or send personal
   information via GA4. The existing global solar attribution listener records
   consented internal journeys.
4. **Fast PR checks:** one CI run on the PR, with a changed-file article preflight,
   unit/calculator tests, and script syntax checks. No duplicate branch-push CI,
   image fetching, site generation or Lighthouse in the PR gate.
5. **Publish:** merge into `claude/clever-babbage-uibieq`. GitHub Pages builds
   and uploads once, requiring relevant photos and internally verifying generated
   route and canonical metadata. After deploy, only recently changed articles
   are checked for live HTTP 200/canonical/heading/social image plus the homepage.
   Dynamic route tests replace manual edits to the workflow for each new story.
6. **Independent QA:** full historical live smoke checks and live Lighthouse run
   overnight (or on manual dispatch). The Solar mobile browser audit runs after
   a successful solar-related site deployment, or overnight. Failures remain
   actionable but cannot retroactively withhold a successfully deployed article.

## Troubleshooting
- **New article 404:** inspect site `build`, `deploy` and `verify-live` jobs,
  and confirm the URL was generated. Never claim a successful publication from a
  merged PR alone.
- **Missing image:** the site build intentionally fails rather than silently
  publishing News without a cover. Pin topic-appropriate assets rather than
  repeatedly picking inconsistent photos or using unrelated fallback covers.
- **Audit red, article live:** inspect `quality-audit`; it is separate from
  publication and should be resolved as independent website maintenance.
- **CI red on article:** check specific preflight error before weakening a
  validity rule; legacy content differences can warrant a warning.
- **Analytics:** source attribution is consent based. New GA4 reporting dimensions
  still need registration and verification. Report quote requests separately from
  merely clicking into tools.

## What is not automated
Checking truth of externally sourced facts, financial/medical suitability,
photo licensing clearance, chart method assumptions, editorial originality, and
GA4 account configuration all require review. Do not claim automation has
verified these.
