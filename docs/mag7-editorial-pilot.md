# Mag 7 research pilot (16 October – 12 November 2026)

## Schedule

A four-week schedule, beginning with the commissioned Tesla Roadster piece on
Friday 16 October. The repeating seven-day order is Tesla, Microsoft, Nvidia,
Apple, Amazon, Alphabet and Meta. The scheduled Mag 7 Research Desk workflow
runs at 08:17 UTC each day. The Python scheduler will not generate new review
issues outside the four-week period, even though GitHub's cron remains in place.

## How a scheduled run works

1. Resolve the assigned ticker for the day (date-specific and deterministic).
2. Read the company's SEC-verified financial profile, preserving its genuine
   fiscal calendar and numbers from the original filing.
3. Gather recent news-feed headlines as DISCOVERY ONLY. Verify material
   claims from official statements, filings and independent reporting.
4. Check the existing editorial title inventory for possibly duplicated intent.
5. Produce a detailed research brief.
6. If the ANTHROPIC_API_KEY Actions secret is present, request a sourced
   article draft. MAG7_MODEL is an optional Actions variable. A draft failure
   results in a research brief, not a silently lowered quality standard.
7. Create one GitHub issue per date and ticker. Re-runs check for existing
   issues and never create duplicate tasks.

## Publication gate

No scheduled job publishes content, social posts or market orders. A human
editor verifies the full article, primary sources, calculations, originality,
balanced argument, SEC dates, copyright, and a genuinely story-specific cover
with working Open Graph/Twitter preview. The editor then commits a single
canonical article under content/wealth; new stories link to the relevant
/stocks/TICKER/ dashboard and earnings archive. Quarterly earnings are NEVER
republished as individual article spam.

If a company has no meaningful verifiable news or original evergreen angle,
skip the slot rather than publishing filler. After four weeks, review indexing,
GSC impressions, clicks, stock-page referrals, engagement and ad earnings
before expanding or considering unattended publishing.
