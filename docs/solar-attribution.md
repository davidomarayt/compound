# Compound Solar: source-to-tool attribution (GA4)

Implemented 12 October 2026. Applies to every internal solar link on every current and future page, without inserting manual tracking attributes into articles. The shared base.html loads static/solar-funnel.js when GA4 is configured and previews are off.

## What is measured

**Event:** solar_journey_click — once per qualifying internal link click while analytics consent is granted.

| Event parameter | Meaning | Example |
| --- | --- | --- |
| source_path | Page containing the clicked link; pathname only | /news/no-energy-credit-budget-2027-electricity-bills-winter/ |
| destination_path | Internal solar destination; pathname only | /solar/ |
| destination_step | Classification of linked page | hub, payback_calculator, quote_brief, installer_directory |
| journey_origin | First tracked source path in the past 30 minutes in this browser tab, retained while moving through the hub and calculators | /wealth/electricity-tariffs-ireland/ |
| source_type | Current page group | news, evergreen, solar_hub, tool, homepage, other |
| link_area | Link placement | article_body, related_content, solar_hub_content, site_navigation, site_footer, page_content |
| audience | homeowner_research or installer_business | homeowner_research |

The transport_type=beacon parameter is a delivery hint, not a reporting dimension.

Automatically included destinations:

- /solar/ and all existing/future /solar/.../ subpages, including grants, quote comparison, quote preparation and the installer directory.
- /solar-payback-calculator/ and /solar-ev-battery-optimiser/.
- Existing and future news/evergreen articles with solar in the slug and the CEG/SRESS guide.
- /solar/for-installers/ is measured with installer_business; it must never be mixed with homeowner enquiries.

The system intentionally does not treat a click on a quote brief as a submitted lead or contact request. The quote template is self-service, and Compound currently does not operate a paid installer lead marketplace. Existing solar interaction events remain separate (for example: a quote comparator being used versus a page link being clicked).

## GA4 configuration needed to view the attribution

1. In GA4 → Admin → Data display → Custom definitions, create event-scoped custom dimensions for source_path, destination_path, destination_step, journey_origin, source_type, link_area and audience. The Event parameter names must match exactly. GA4 may take time before new custom dimensions are populated.
2. In Explore → Free form, filter event name = solar_journey_click and audience = homeowner_research. Set rows to journey_origin, source_path and destination_step and values to Event count. This identifies which older/new articles sent readers to the hub, and the onward stages.
3. Save separate comparisons for destination_step = hub, payback_calculator, quote_comparison, installer_directory and quote_brief. Add a separately verified lead-submission event only if a live lead collection system is deployed.
4. Compare GSC page clicks/impressions with GA4 solar link clicks over the same dates, joining by article URL. GSC organic clicks and GA4 internal-link clicks represent different behaviours.

## Interpretation and privacy

- GA4 measures events on consented visits only; no retroactive click counts exist. Historical articles are covered automatically from the date the new script goes live, not for visits in the past.
- journey_origin persists per browser tab for a rolling 30-minute window only after a consented solar link click. It is not a permanent identity or cross-device user journey. Rejecting analytics clears it.
- No full URLs, query parameters, form contents, electricity usage, customer information, IP addresses or email addresses are added to these events.
- Same-page anchors, external links and downloadable files are excluded. The www canonical alias is considered internal.
- Only one solar_journey_click is sent per qualifying link click. Legacy duplicated link entry events were removed; actual interaction events are independent.
- Clicks measure interest, not approved leads, quotations or sales. Sponsor reports must not call every quote_brief click a qualified enquiry.
- Do not create new articles solely for tracking. Existing and future solar links work through the shared event listener.
