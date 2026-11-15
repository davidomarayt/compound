# PIA Ireland 2027 — editorial launch tracker

Canonical public page: https://compound.ie/pia/#pia-launch-tracker

## Maintained source
- Source data: `content/pia-launch-tracker.yml`; the site validates it with `compound/site/pia.py:load_pia_launch_tracker` and renders it in `pia_centre.html`.
- Stage labels deliberately distinguish *a historically verified event* (`confirmed`) from an unverified future/final milestone (`unverified`) and a conditional Government opening target (`target`).
- Neither a bar percentage nor a live countdown is used: the timeline does not measure actual operational readiness.
- `checked` is the date the sources were **actually** verified; do not increment it automatically on an unattended run that could not inspect fresh sources.
- Finance (No. 2) Bill 2026 as *introduced* is not enacted law. The Bill text uses the draft label **Individual Investment Account (IIA)**; PIA is common editorial/provider shorthand.

## Existing daily PIA Content & Growth programme
On each daily run, examine **the tracker source file** and official Oireachtas Bill record, Revenue releases and provider original statements *before choosing a new article*. If and only if a material verifiable change exists:
1. Confirm the actual current legislative stage or provider terms from a primary source. If a source is unavailable, record the blocker, and leave that item `unverified`.
2. Edit just the affected milestone(s); include their exact event dates and original public HTTPS source links. Add a milestone only for a genuinely new stage, not generic SEO volume.
3. Advance the `checked` date only after checking all existing tracker sources; otherwise keep the previous global date and document item-level verification in the PR.
4. For verified provider opening status, synchronise `content/pia-providers.yml` and regenerate `compound/site/static/pia-provider-sources.csv` using `python scripts/export_pia_provider_sources.py`; preserve no-invented-fees guard. Do not mark a launch complete merely because the announced 1 July date passes.
5. Test `pytest -q tests/test_pia_launch_tracker.py tests/test_pia_centre.py`, whole pytest, static build and link/canonical/ad/consent checks on the exact PR head before any merge; confirm production deployment and fetch the public canonical HTML.
6. Keep the primary `/pia/` canonical and `/pia-calculator/` search intent intact. No new duplicate launch landing URL, and no claims of real-time sync.

## Original evidence as of 15 November 2026
- Revenue's 7 October 2026 technical group notice: https://www.revenue.ie/ga/corporate/press-office/press-releases/2026/pr-100726-irish-investment-account.aspx
- Oireachtas Finance (No. 2) Bill 2026 / 98 (introduced 19 October, later stage not independently confirmed in this dataset): https://www.oireachtas.ie/en/bills/bill/2026/98/
- Budget 2027 reporting 6 October: https://www.rte.ie/news/business/2026/1006/1594235-investment-accounts-budget-2027/
- Provider statements: https://compound.ie/pia/providers/

The launch tracker is updated by verified editorial changes, not by a direct live Revenue API or a promise that updates arrive instantly.
