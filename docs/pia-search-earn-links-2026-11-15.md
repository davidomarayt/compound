# PIA search growth and ethical citations — 15 November 2026

## What changed
The existing PIA provider comparison now includes five firms with directly verifiable primary sources (AIB, Bank of Ireland, Irish Life, PTSB, Zurich), up from three. Each entry says it is pre-launch and retains its source URL and date. A simple CSV is published at https://compound.ie/static/pia-provider-sources.csv for journalists, advisers and researchers. The CSV is generated from the curated YAML and checked against it by a regression test; no provider fees or live products are invented.

## Keyword and landing-page map
- Broad PIA / PIA Ireland: https://compound.ie/pia/
- PIA providers / who offers PIA: https://compound.ie/pia/providers/
- PIA calculator: https://compound.ie/pia-calculator/
- What is PIA / rules: https://compound.ie/wealth/personal-investment-account-ireland/
- PIA vs pension: https://compound.ie/pia/vs-pension/

Do not publish thin new pages for these same questions; keep improving canonicals.

## Search Console status
Google Search Console source GW in Supermetrics reported NOT_AUTHENTICATED on 15 November 2026. No reliable current query impressions, clicks, rank positions, volumes or CTR can be reported. The site owner must reconnect authorised Search Console read access before using those numbers. Do not present hypothetical estimates as actuals.

Once data access is available, establish a rolling last-28-completed-days vs previous-28-days dataset filtered to Ireland, Web search:
- exact query pia
- pia ireland and personal investment account ireland variants
- pia calculator, pia providers, pia vs pension
- page/query cross-tab with /pia/, /pia-calculator/, /pia/providers/, /wealth/personal-investment-account-ireland/
- impressions, clicks, CTR and average position; distinguish branded and unrelated PIA searches.
Include account and date range in any report, and treat low-volume query privacy suppressions and GSC rounding carefully.

## Citation/outreach asset and rules
An editorially compiled record of direct provider statements, not proprietary competitor reporting. Relevant Irish finance journalists, consumer-investing educators, professional bodies and financial-literacy publishers can check and cite the source-linked tracker when it helps their audience.

Optional one-paragraph individually tailored outreach note for later sending after verifying each editorial contact:

> We're maintaining a dated, independently sourced comparison of the Irish Personal Investment Account (PIA) announcements. It records only providers with verifiable statements on their own websites and explicitly shows when fees are unpublished. The underlying source table is downloadable for checking or citation at https://compound.ie/pia/providers/. Please feel free to use it if relevant to your coverage.

Do not automate unsolicited bulk outreach, buy links, offer quid-pro-quo links, misrepresent independent provider announcements, claim exclusivity, or publish externally without verified permission. Earned links are editorial decisions, not guaranteed.

## Maintenance
For a new source, verify a provider's own HTTPS statement and details before updating content/pia-providers.yml, then run `python scripts/export_pia_provider_sources.py` and the full tests and build. All provider-source updates must change the checked date only for genuinely reviewed records. Keep the PIA guide's proposed legislation separate from final law.
