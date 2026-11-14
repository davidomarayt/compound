# Compound overnight research — 2026-11-14 (Europe/Dublin)

**Stage:** 03:00 Research + Engineering; distinct agents **5. Original Research** and **6. Private Company Intelligence**. **Production/default and GitHub Pages push branch checked before work:** `claude/clever-babbage-uibieq` (GitHub repository metadata and `.github/workflows/site.yml`). Runbook `docs/overnight-agents.md`, `AGENTS.md`, `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, `data/content-inventory.json`, `content/company-watchlist.json`, `tests/test_company_watchlist.py`, active PR #138 and other overlapping PRs examined. 13 November's inventory snapshot lists 285 editorial articles/guides, 64 calculators, 511 public-stock registry profiles and 13 private-company profiles; **these are source-inventory counts, not search or analytics results**. No publication, auto-merge, invented human editorial review or schedule change by this worker.

## 5. Original Research — original attributable CPI arithmetic; research brief only

**Primary source:** [CSO, Consumer Price Index October 2026](https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/), **released 11 November 2026, 11:00 Irish time**; retrieved and checked **14 November 2026**. The associated [CSO data page](https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/data/) links relevant CPM20, CPM21, CPM22 and CPM23 tables. Neither third-party forecasts nor scraped price anecdotes substituted for the original release.

| Published period / measure | Official reported rate | Interpretation |
| --- | ---: | --- |
| CPI year-on-year, Oct 2026 versus Oct 2025 | +4.3% | Headline consumer-price index; national reference basket, **not** an individual's spend change |
| CPI year-on-year, Sep 2026 versus Sep 2025 | +4.1% | Different 12-month comparison period |
| CPI monthly Sep–Oct 2026 | +0.7% | **Not** the 0.2 percentage-point change between the annual rates |
| HICP annual Oct 2026 | +4.2% | Different harmonised methodology; CSO states CPI includes mortgage interest, whereas HICP does not |
| CPI excluding energy and unprocessed food, annual Oct 2026 | +3.1% | Not the all-items headline; scope/exclusions matter |
| Housing, water, electricity, gas and other fuels division, annual | +10.7% | Division-wide price index, not any family's measured bills |
| Transport division, annual | +9.0% | Division index, not automatically a motorist's personal fuel inflation |

**Reproducible illustrated calculation:** Set a hypothetical Oct **2025** basket cost to €2,500 and assume it tracks the **all-items CPI** exactly: Oct 2026 price-equivalent `€2,500 × (1 + 4.3/100) = €2,607.50`; difference `€107.50` over the comparable **one-year** window. An illustrative €1,000 basket under the housing-division index alone gives `€1,000 × (1 + 10.7/100) = €1,107`, or €107 more; that should not be treated as a representative family's rent or electricity bill. The annual-rate change from September to October is `4.3 - 4.1 = 0.2 percentage points`, not 0.2% month-on-month. No annualisation of the 0.7% October monthly rate was attempted. Index methodology, category weighting and individual consumption differ, and one-month data cannot predict next year's rate.

**Deduplication:** The source index already has `/news/ireland-inflation-september-2026-energy-prices/`, `/news/personal-inflation-rate-ireland-households-2026/` and the `/inflation-calculator/`. An earlier 12 November overnight CSO brief also exists. This run documents a different, reproducible all-items/HICP-versus-division comparison but **does not create another competing inflation article or new calculator**. A future existing-page update would require contextual source checking and canonical selection; no new unreviewed ad-supported page was published.

**Disposition:** completed primary-source brief and quantitative review; no substantive research-led source edit or publication.

## 6. Private Company Intelligence — issuer fact checks, no duplicate 07:00 story

**Source-checked 14 Nov against published issuer announcements and the canonical watchlist:**

1. **OpenAI:** [9 Nov 2026 announcement, ChatGPT Enterprise in AWS Marketplace](https://openai.com/index/chatgpt-enterprise-aws-marketplace/) documents availability through AWS Marketplace and enterprise procurement, **not** measurable incremental bookings, revenue, margin or cash flow. The site already has the topic-specific `/wealth/openai-aws-marketplace-enterprise-procurement-economics/` and `/companies/openai/`'s newer **10 Nov** dated Business Agents update. No duplicate AWS article, estimated financial outcome or backwards-moving dated development.
2. **Anthropic:** [10 Nov 2026 issuer announcement](https://www.anthropic.com/news/roadshow-launch) describes a **proposed** IPO roadshow of **825,000,000** Class A shares, comprising **801,351,354 issuer shares** and **23,648,646 selling-shareholder shares**, an **indicative** offer range of **US$70–78**, and proposed Nasdaq symbol **ANT**. The registration statement was stated **not effective** at the announcement date: this is **not** a confirmed listing, tradeable market price, completed fundraising or final valuation. The existing canonical `/companies/anthropic/` and the IPO economics article exist; its watchlist source now carries a later **12 Nov** Anvil update, so no older replacement was made.
3. **Blue Origin:** [5 Nov 2026 issuer announcement](https://www.blueorigin.com/news/new-glenn-expands-reach-with-gs3) describes the New Glenn GS3 third stage and a contracted **2028** cislunar mission; a mission schedule is not recognised revenue. The watchlist's **10 Nov** BE-4 valve-qualification update is later and remains untouched. SpaceX's public presence in the source inventory is under listed-company `/stocks/spcx/` research, **not** a basis to invent a currently tradable SpaceX security or market price.

**Canonical-intent and publicity protections:** `EDITORIAL_TOPIC_INDEX.md`, master inventory, current watchlist and prior editorial items were searched for the issuer announcements, profile URLs and closely competing articles. No fresh trustworthy issuer financial disclosure requires superseding the more recent already documented company development. No edits to stocks, private-company financials, investment valuations, images, licenses, published story dates or 07:00 private-company workflow. Rumours and third-party estimates were not used as verified figures.

**Handoff:** agent 7's separate deterministic directory/profile structured-data patch (draft [PR #139](https://github.com/davidomarayt/compound/pull/139)) is reported in `engineering.md`, **not** a new issuer article. Final independent Editor-in-Chief QA at 06:30 decides eligibility; this worker never merges or publishes.
