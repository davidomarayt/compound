# Compound Solar — homeowner project intake and installer marketplace specification

Status: product specification / browser-local project brief (not a live lead marketplace).
The existing canonical quote page is `/solar/get-quotes/`. Do not create SEO-competing pages or imply that a provider can already pay to access homeowners.

## Objective
Let a homeowner explore Compound's solar tools anonymously, optionally build one reusable **Solar Project Brief** and request quotations from up to **three verified installers they approve**. An informed estimate is not an installer quote and no online-only brief guarantees a final installed price.

## Consumer workflow
1. Research (articles → roof orientation → payback → quote brief). No account required for public tools.
2. Fill a progressive four-section project brief. Essential fields are clearly labelled; all specialist details are optional with "not sure".
3. Preview a homeowner-editable technical summary, flag unknowns and estimate readiness. Copy/print locally without transmitting PII.
5. **Future:** record per-provider authorisation; provider pays **only after** matched approval and valid lead verification. Server releases personal contact details to each paid, authorised installer with short-lived access and full audit logs. Provider feedback and homeowner controls complete the loop.

## Intake schema: field names and qualification
Required for quote enquiry, not necessarily to use calculator:
- `project_county` (county) and `area` (town or approximate area). Never expose Eircode or exact address at listing stage.
- `property_role` (owner / joint owner / authorised decision maker / other). Only decision makers eligible for sale.
- `building_type` (detached / semi / terrace / bungalow / apartment / commercial / other), `project_type` (new PV / expand existing PV / battery retrofit / ground mount), `planning_constraints` (listed / protected / conservation / none / unsure).
- `timeframe` (ASAP / 1-3 months / 3-6 / 6-12 / research), `budget` (optional band), and `ready_for_quote` (yes, soliciting prices / research).
- `contact_name`, `email`, `phone` and `eircode` — **secure private contact step only**, never analytics, unauthenticated public listing, email notifications, URLs, HTML output pages or ad scripts.
- `chosen_installer_ids`, `share_approval_timestamp`, `privacy_notice_version`, `allowed_channels`, `contact_until` and withdrawn/revoked status, all server-side, recorded individually per recipient.

Roof/siting details (optional unless reliable answer available):
- `mount_type` (pitched roof/flat roof/ground mount), `roof_material`, `roof_condition`, `roof_age_range`, `storeys`, `roof_obstacles`, `roof_replacement_planned`, `scaffold_or_access`.
- Up to two or more arrays `roof_faces[]`: `compass_azimuth_deg` (0=N/90=E/180=S/270=W), `tilt_deg`, `usable_area_m2` or rough length×width, expected shade (none/some/heavy/unsure) and `array_kwp` if proposed.
- Roof angle/output imported from the compass marked as **self-reported approximate** rather than verified system design. Never auto-present preliminary projection as installer-confirmed yield.

Electricity + grid:
- `annual_consumption_kwh` (from bill ideally, or "unsure"); monthly average (€ optional); import/export tariffs; smart meter and daytime/overnight occupancy or load profile.
- `ev_count` and vehicle charging plans, `heat_pump`, electric hot water, electric immersion, future EV or load growth.
- `supply_type` (single/three phase/unknown), `main_fuse` or board condition if known, `inverter_location`, `cable_route` and `meter_location` (all optional / validated at site survey). Avoid asking homeowners to open consumer units, access roofs or expose MPRNs early.

Design and preferences:
- `desired_kwp` (optional), `battery_choice` (none/yes/compare/unsure), `battery_kwh` (optional), `ev_charger`, `diverter`, `backup_power` requirements, warranties/brands (optional).
- `grant_eligibility` (unknown/eligible/not eligible/previous grant), `finance_preference` (cash/finance/unsure), `existing_quotes` (yes/no, anonymised ranges optional).
- `time_to_quote` and best method (phone/email) at recipient consent step only.

## Disclosure + access classes
- Anonymous installer teaser: county/approximate area (no pinpointing for sparsely populated districts), dwelling class, approximate PV size, broad roof orientation and shading, intent/timing, safe non-unique project attributes, date qualified. Suppress rare combinations that enable re-identification.
- Selected paying installer: full homeowner-authorised project brief and contact details strictly for that quote request, released to that named installer only after paid access is approved.
- Internal Compound: verified access limited to fulfilment and fraud prevention.
- Homeowner: see chosen recipients, price/terms transparency if relevant, see request states, withdraw future introductions, close enquiry, request deletion.
- Never sell a bulk export; never reuse address/phone for unrelated marketing or resale.

## Lead economics and auction rules
- Default `max_installer_introductions = 3`, configurable by the **homeowner**, not sellers.
- Test EUR 50, EUR 65, EUR 75 per **nonexclusive**, verified, homeowner-approved introduction; cap one purchase by each installer and one charge per unique installer/project.
- Model exclusive introductions as a separate homeowner-selected option, with separate higher test prices and an explicit prohibition on further sale.
- Providers see truthful number of remaining slots and whether other suppliers have already been approved, but **never competing installer quotations or identities** unless clearly agreed.
- Cash is charged on confirmed introduction; never charge for a speculative, unverified draft. Define refund/replacement policy, duplicate handling, out-of-area, fraudulent, unverifiable, non-consented and nonresponsive leads.
- No purchase if homeowner no longer wants quotes, permission is withdrawn, 30-day lead freshness expired, duplicate within recent period or an installer is unverified.
- Do not guarantee quote, survey, installation, savings or conversion. Installer must confirm roof structure, loading, electrical panel, cable routing, grant, planning, scaffolding and final installed cost at site survey.

## Security / GDPR go-live gates
- Use authenticated DB with RLS and separate private contact vs anonymised market tables; never static-site storage or FormSubmit for consumer lead personal data.
- Written privacy notice explaining controller, processing purposes, lawful basis, permitted recipients, retention, exercise of rights and deletion, and separately opt-in marketing (default OFF).
- Per-installer-specific affirmative consent/other vetted lawful basis for introduction; do not assume generic checkbox is sufficient. Provide an easily accessible withdrawal route; withdrawal must prevent future releases, even though already disclosed data cannot be technically retracted.
- Data-processing agreements and controller-to-controller sharing terms as applicable; breach detection, rate limits, MFA for installers, payments server-side, idempotent lead releases, audit trail and explicit retention/deletion jobs.
- Contract review for consumer law, VAT, GDPR/ePrivacy, installer accreditation and advertising before collecting or selling live leads.

## Measurement
`solar_project_brief_started`, `solar_project_brief_completed`, `solar_project_quote_intent` (no PII in analytics).
Server-side `verified_lead`, `opt_in_captured`, `matched`, `installer_authorised`, `lead_purchased`, `details_released`, `installer_contacted`, `survey_booked`, `quote_delivered`, `job_won`, `lead_refunded`, `repeat_installer_purchase`.
Funnel attribution is permitted only when analytics consent exists and no personal form values are pushed to GA4.

## Pilot milestones
- No live marketplace/sales until at least 2-3 verified registered installers, consent architecture and payment release are working.
- Validate quality on matched homeowner-authorised enquiries, price and repeat buying.
