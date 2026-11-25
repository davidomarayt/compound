# Compound overnight discovery — 2026-11-25 (Europe/Dublin)

Confirmed production branch before work: repository default and GitHub Pages push target in .github/workflows/site.yml are `claude/clever-babbage-uibieq`; base SHA ec1f083c2ed1a941724194efea07ce6616be9961. Prior site workflow [45506339755](https://github.com/davidomarayt/compound/actions/runs/45506339755) completed successfully at ff682f15b7b57744204f00ce559d4968ba065da7; this does not prove the new work live. Read AGENTS.md, runbook including efficiency gates, topic index, Markdown/JSON inventory, CI and site workflow, open and recent closed PRs. No Search Console/GA4 calls.

## 1. Technical SEO — measurable change staged; wider review-only

Checked public text of [homepage](https://compound.ie/), [CGT calculator](https://compound.ie/capital-gains-tax-calculator/), [CAT calculator](https://compound.ie/inheritance-tax-calculator/), [take-home calculator](https://compound.ie/take-home-pay-calculator/), [investment-tax](https://compound.ie/wealth/investment-tax-ireland/), [PIA centre](https://compound.ie/pia/) and [pension comparison](https://compound.ie/wealth/pension-vs-investing-ireland/): distinct descriptive titles/H1 and summaries, relevant links. Source inspection of article/base/private-company templates shows per-article canonical, robots preview rules, description and Article/Breadcrumb schema hooks; not a claim that raw rendered HTML was inspected. Direct web-reader robots.txt and sitemap.xml inaccessible, no complete raw canonical/noindex/schema/redirect/ad-markup crawl. No broad metadata or indexing changes.

Found four truncated labels in three public calculator snapshots (CGT: Allowable acquisition, Annual €1; CAT: €3; take-home: Change in take-home from next €1). Current production source content/tools.yml contains matching unquoted comma-bearing flow-map values; same root cause as prior #267 but distinct fields/routes. Draft [PR #279](https://github.com/davidomarayt/compound/pull/279) quotes only these four labels and adds a load_tools regression. No numerical or formula changes. Further comma-bearing labels in source (e.g. mortgage, student costs) are candidates for a later bounded public verification, not claims of measured live defects.

Rechecked prior #267 and #268: both merged 24 Nov; source has corrected pension labels and truthful editorial-review wording. Public text snapshots for pension calculator, About and policy still show old wording, whereas investment-tax article snapshot displays updated author note. Cache/deployment timing cannot be resolved through text reader; no duplicate PR or claim of fresh raw verification. Later site workflow success is historical evidence only.

## 2. Content Gap — review-only, deduplicated priority backlog

24 Nov inventory: 439 published articles/guides, 69 tools, 512 public and 12 private-company profiles (source snapshot; not live counts/traffic). Reviewed all 13 available preceding daily discovery/content pairs 12–24 Nov (11 Nov absent), latest available 23 Nov private-company/Irish-money/PIA/Mag8 ledgers, 24 Nov private-company recovery listing, open/merged PRs. Existing CGT, inheritance, gift tax, take-home and related guides/tools answer these intents. No competing new page.

- HIGH / STAGED fingerprint `/capital-gains-tax-calculator/|annual-exemption-and-allowable-cost-labels`, owner Technical SEO/Content Freshness, PR #279. [Revenue CGT calculation](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx), 7 Oct 2026, checked 25 Nov. Distinct from earlier rate correction #121 and share comparison #254.
- HIGH / STAGED `/inheritance-tax-calculator/|small-gift-used-label`, same owner/PR, [Revenue small gift exemption](https://www.revenue.ie/en/gains-gifts-and-inheritance/cat-exemptions/small-gift-exemption/index.aspx), 12 Jun 2025, checked 25 Nov.
- HIGH / STAGED `/take-home-pay-calculator/|marginal-next-1000-display`, same owner/PR, existing formula source uses salary + 1000; no rule changes.
- HIGH / merged, public verification pending: yesterday's pension-lump-sum label and editorial review claims (#267/#268); do not recreate. MEDIUM / verify other comma-bearing labels with live evidence before changing. PIA bill/provider watch remains owned by dedicated programme (#270 active); shares #254, rent #168, pension matching #175 still open; fuel #274 active. No overlapping edit.
- No invented query volume, ranking, traffic or new thin pages.

See [content.md](content.md) for linking, official source checks, exact PR state and handoff.
