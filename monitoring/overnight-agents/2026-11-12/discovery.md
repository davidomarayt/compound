# Compound overnight discovery — 2026-11-12

**Status:** completed source/inventory checks; no ranking-derived edits; one link-oriented content PR handed to the content record. **Source:** `claude/clever-babbage-uibieq`, verified repository default at run start. This is not evidence of live publication.

## 1. Search Console Growth Agent

- **Google Search Console:** NOT_AUTHENTICATED through the available Supermetrics connector (data source `GW`, checked on 2026-11-12). No direct authenticated GSC query/page report was accessible; 7/28-day clicks, impressions, CTR, positions and indexing metrics **not verified**. GA4 source `GAWA` likewise NOT_AUTHENTICATED. No fabricated data or ranking predictions.
- Site/repository snapshot in `CONTENT_INVENTORY.md` and `data/content-inventory.json` (2026-11-11): **276 editorial articles/guides, 64 tools, 511 public stock directory profiles and 13 private-company directory profiles**. Inventory counts are content/URL counts, **not search traffic**.
- Inspected canonical page and on-site headings: https://compound.ie/wealth/buying-home-budget-deposit-ireland/ ; existing title, summary and course navigation are present. The target tool is independently accessible at https://compound.ie/house-deposit-calculator/ . No unsupported metadata overhaul was made.
- **Action:** preserve existing titles until actual query-level Search Console evidence is available. Revisit opportunities on 7/28-day comparison once the account owner authenticates a supported connector; no connection or account change attempted.

## 2. Content Gap Agent

Prioritised by reader usefulness and verified factual sources; **not measured search volume**, and **no new content URL or draft published**.

1. **High — How does broker failure protection differ from bank deposit protection?** Existing destination: `/wealth/choose-investment-broker-ireland/`. The guide already explains the Irish Investor Compensation Scheme and its **90%-up-to-€20,000** coverage in certain covered-firm failures, but contains no explicit DGS comparison. An expansion should explain that eligible bank deposits typically have **€100,000 per person per institution** DGS coverage and clarify that neither guarantees protection against investment market losses. Verify relevant firm's authorisation and jurisdiction, because protections can differ for cross-border brokers. **Sources:** https://www.centralbank.ie/consumer-hub/explainers/what-compensation-schemes-protect-consumers-of-authorised-firms ; https://www.ccpc.ie/manage-your-money/saving-and-investments/types-of-investment/ics-protection ; https://www.centralbank.ie/consumer-hub/deposit-guarantee-scheme . Improve the *existing canonical*, not a duplicate standalone guide.
2. **High — Are the 2026 PIA guide's statutory status, valuation assumptions and displayed review date consistent?** Existing destination: `/wealth/personal-investment-account-ireland/`. The source article has `reviewed: 2026-11-07` while a rendered inline banner still says “Last checked: 6 October 2026”; it also uses some pre-Bill language although the Finance (No. 2) Bill 2026 was introduced on **19 October 2026**. Verify the latest actual Finance Bill stage and precise enacted/proposed distinctions from the official Oireachtas source before any change, and preserve original publication date. Secondary leads for locating specific measures: https://kpmg.com/ie/en/insights/tax/finance-bill-2026/investment-account.html and https://www.forvismazars.com/ie/en/insights/news-opinions/finance-no.-2-bill-2026 . Do **not** invent enacted status or imply the Bill is law.
3. **Lower — Do not commission a separate 2026 CGT due-dates article.** Existing `/wealth/capital-gains-tax-ireland/` already explains **15 December**, **31 January** and **31 October** deadlines with 2026/2027 examples. Revenue independently confirms the underlying split: https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/when-and-how-do-you-pay-and-file-cgt.aspx . Improve the canonical if future changes warrant, avoid competing search-intent pages.

## Coordination / changes

- Checked editorial index, JSON inventory and related content source files; recent open PR #107 (private companies) and #57 (electricity/solar pilot), plus merged #108 (PIA quick-start) and #113 (standard ads). No overlapping edit on the selected home-deposit article or tool was identified.
- Handoff: [draft PR #115](https://github.com/davidomarayt/compound/pull/115) is an existing-article internal-link improvement. Owned by Internal Linking Agent; details in `content.md`.
- Changes merged: **0**. Confirmed live changes caused by this run: **0**. No ads/consent/production settings changed; no account-policy compliance claim.
