# Compound overnight research — 26 November 2026 (Europe/Dublin)

Production branch `claude/clever-babbage-uibieq` (site.yml push target), base caf84557f698837f1021e8a345a274a85ba6ebd3. Read the runbook incl. 14 Nov efficiency gates, AGENTS.md, 12–25 Nov research/engineering records, today's discovery/content (on draft #289), open PRs and the private-company ledgers. No merges, no publishing.

## 5. Original Research — REVIEW-ONLY, distinct primary release

Fingerprint: `CSO-FEC-September-2026-release-2026-11-25|kerosene-ytd-fall-vs-petrol-rise`. Source: [CSO Fuel Excise Clearances September 2026](https://www.cso.ie/en/releasesandpublications/ep/p-fec/fuelexciseclearancesseptember2026/), "CSO statistical release, 25 November 2026, 11am", plus its Background Notes. Deduplication: no prior overnight record, title-index entry or open PR uses the FEC series (grep for "fuel excise", "clearances", "p-fec" in monitoring/, content/ and the indexes found only three older excise-*rate* news pieces, not this dataset). The other 25 Nov CSO items were rejected: the Housing Hub press statement recycles RPPI (18 Nov brief) and first-time-buyer income (17 Nov brief); the construction output index has no personal-finance angle.

CSO Table A, percentage change, calculated by CSO from thousands of litres:

| Fuel | Jan–Sep 2026 vs Jan–Sep 2025 | 12 months to Sep 2026 vs prior 12 months |
| --- | ---: | ---: |
| Autodiesel | -1.1% | -1.9% |
| Unleaded petrol | +5.7% | +6.1% |
| Marked gas oil | -1.2% | 0.0% |
| Kerosene | -11.0% | -4.3% |

CSO text: kerosene fell 67 million litres year to date; September 2026 kerosene was the lowest September since 2014; Jan–Sep petrol was the highest since 2017. Annual 2025: autodiesel 3.4 billion litres, unleaded petrol 1.1 billion litres.

Derived (ours, not CSO's): implied Jan–Sep 2025 kerosene base = 67 / 0.110 ≈ 609 million litres, so Jan–Sep 2026 ≈ 542 million litres. Because both inputs are rounded, the base could be roughly 602–616 million litres. Petrol share of 2025 road-fuel clearances (petrol + autodiesel) = 1.1 / (1.1 + 3.4) ≈ 24%.

Limits (CSO Background Notes): clearances are duty paid on product withdrawn from bonded warehouses and "do not reflect actual consumption"; they move with traders' withdrawal timing, home-heating clearances swing with price and weather, HVO used as a standalone diesel alternative is excluded, and recent months are subject to revision. No inference about household heating bills, EV adoption or tax receipts is made from this series alone. Monthly litre volumes (data.cso.ie FPM01) were not fetched, so no September-only volume is quoted.

Disposition: review-only context for the existing fuel-cost calculator (open #274 owns that page; do not duplicate) or a future home-heating cost guide, subject to its own deduplication and editorial gate. Owner Original Research, priority low–medium, checked 26 Nov. No search or analytics metrics claimed.

## 6. Private Company Intelligence — SKIPPED / NO_MATERIAL_PROFILE_CHANGE

Listing status: Anthropic is listed (Nasdaq ANT, 19 Nov 2026) and SpaceX is listed (SPCX), so both belong to the stocks workflow. OpenAI remains private. The 07:00 publisher's 25 Nov output is held in draft #281 (OpenWorks, Frontier Safeguards, Deel Card) and 24 Nov in #269; those topics stay with that publisher. A web search for OpenAI announcements dated 25–26 Nov returned no dated primary-source item beyond those already assessed on 25 Nov. No profile edited; no estimate or rumour promoted to fact.
