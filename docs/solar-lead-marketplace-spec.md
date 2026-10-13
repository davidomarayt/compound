# Compound Solar — homeowner project intake and installer marketplace specification

Status: product specification / browser-local project brief (not a live lead marketplace).
The existing canonical quote page is `/solar/get-quotes/`. Do not create SEO-competing pages or imply that a provider can already pay to access homeowners.

## Objective
Let a homeowner explore Compound's solar tools anonymously, optionally build one reusable **Solar Project Brief** and request quotations from up to **three verified installers they approve**. An informed estimate is not an installer quote and no online-only brief guarantees a final installed price.

## Consumer workflow
1. Research (articles → roof orientation → payback → quote brief). No account required for public tools.
2. Fill a progressive four-section project brief. Essential fields are clearly labelled; all specialist details are optional with "not sure".
3. Preview a homeowner-editable technical summary, flag unknowns and estimate readiness. Copy/print locally without transmitting PII.
4. **Future, not live:** private homeowner account, verified phone/email, verified eligible installers, and explicit homeowner selection of 1, 2 or 3 recipient companies. No photograph collection.
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
- Third-party ads and analytics must never receive personal form fields, contact details, full URLs containing identifiers, Eircodes, MPRNs, or person-linked project IDs.
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

## Approved private SKU inventory and purchase workflow (13 October 2026)

**Product decision:** The customer-facing Solar Project Builder remains at `/solar/get-quotes/`. The lead marketplace is **private to approved installers**, not a public directory. No live submission, Stripe payment, or release of homeowner data is authorised by this specification alone. The existing browser-local builder must not pretend to submit leads until its secure backend is operational.

### Creation and qualification

1. A homeowner fills out the public Solar Project Builder, including the built-in 360° roof compass. Technical unknowns are allowed; **no photo uploads or photograph checklist**.
2. Completing the optional quote-request step is a distinct action from completing the calculator. Ask for a clear request to obtain quotations, their preferred maximum of **1, 2, or 3** installers, preferred contact channel, and acknowledgement of the privacy notice. Quote-request submission requires securely collected contact details, an independently verified email or phone, project intent/ownership screening, and a qualifying project brief. Optional fields must not prevent completion.
3. Store a structured project, private contacts, a versioned consent/authorisation log, expiry and status in an authenticated backend. Create a unique non-guessable internal project identifier and a human-readable display SKU such as `SOL-MH-2026-00421`; do **not** encode personal details in the SKU. Sequential public SKUs must never confer access to any data.
4. **Only after** the request is verified and classified as quote-ready, create one private listing at the pilot **€65 per verified introduction** price. Default stock is exactly the homeowner-selected maximum (1–3), never an unconditional three. Status begins `pending_review`; only `active` projects show as anonymised inventory. An admin can reject or hold poor-quality/duplicate projects. An optional research-only brief must never create a paid listing.

### Private installer browse and purchase

- Only authenticated, Compound-approved, currently SEAI-registered solar installation businesses with their service areas configured can browse listings. Enforce permission in server-side API/DB row-level access controls; no public listing page, indexable routes, static JSON, or crawler-accessible previews. Show only matching geographic listings and sanitised structured fields: broad county, dwelling type, project category, general roof orientation, approximate system size/annual kWh, battery preference, broad timeframe, non-identifying readiness status, price, number of introduction slots left, and listing expiry. Suppress any sparse, distinctive combinations with re-identification risk. Do not include exact Eircode, full address, homeowner name, email, phone, property photos or unrestricted free-text notes.
- A listing displays `SKU`, `€65 introduction price`, `X of N available`, and an action to `Request introduction`. An installer can purchase **at most once per project** and should know that this is a **shared lead** unless the customer explicitly selected exclusive treatment. An installer must never see another installer's identity, customer quote, or purchase history.
- Before allowing payment/release, obtain and record homeowner approval **for that identified installer**, either by pre-approving a shown set of named eligible businesses or by accepting a pending request. Selecting `up to 3 quotes` alone does not authorise disclosure to arbitrary purchasers. If the homeowner declines or does not respond, do not charge or release details. Homeowner may withdraw permission for *future* introductions, reduce unfilled slots, close the project, and see who was authorised. Previously disclosed data cannot be automatically recalled.
- On an approved, eligible purchase, reserve one of the listing's remaining slots in a transaction, create a short-lived **server-generated** Stripe Checkout payment for the specified SKU and agreed price, and restore the slot if payment fails or expires. Ensure one purchase per installer/project, no overselling under simultaneous checkouts, no duplicate charging, and no payments on stale, revoked or sold-out projects.
- Treat a verified Stripe **server-side webhook** as payment authority; do not release on a return URL alone. Idempotently mark the purchase paid, consume its reserved slot, write an immutable release/audit event and unlock the complete approved brief/contact information in **that installer's private dashboard**, visible only to the paid recipient. The receipt/email includes invoice details and a secure link to access the brief — **never** personal homeowner information.
- Remaining stock displays `3 → 2 → 1 → 0` when three introductions sell, or the corresponding 1/2 maximum. `0` becomes `sold_out` and unavailable; withdrawal/expiry closes the listing and prevents additional charges. A single installer never buys multiple slots to circumvent homeowner contact limits.

### Installer and homeowner dashboard minimum viable features

**Installer:** sign up/log in, business verification and service area, browse filtered anonymised inventory, SKU/price/availability, request access, pay, order history, secure purchased project details, contact/quote/survey status and refund request. The installer must have no access to any unpurchased project's private data and only receive information necessary to prepare the requested quote.

**Homeowner:** review their brief, request one/two/three quotations, verify contact, see and explicitly approve proposed installers, see number of authorised/released introductions and quote progress, withdraw remaining availability, close project, obtain a copy or request deletion. Approval should use intelligible named recipients, not a generic `we may share your data` checkbox.

**Admin:** approve/reject projects and installers, verify registration and matching area, screen duplicates, see fraud and validity flags, manage expiry, authorisation and payment disputes, apply refunds, audit access, honour deletion/withdrawal requests and monitor lead quality. A fair refund/replacement policy must be published before charging.

### Status and invariants

`draft → submitted → verified → pending_review → active → sold_out / closed / expired` for projects. Per-installer requests: `requested → homeowner_approved → reserved → paid → access_granted`, with distinct `declined`, `cancelled`, `expired`, and `refunded` branches.

- `max_slots ∈ {1,2,3}`, `0 ≤ reserved + sold ≤ max_slots`, and `one paid purchase per (project_id, installer_id)`.
- No marketing consent is inferred from a request for quotes. No personal data in analytics, server logs, email receipts, URLs, public assets or ad tags; no ads or third-party marketing scripts in authenticated workflows.
- Test price €65 is a commercial hypothesis, not a guaranteed sale price or commitment. A project only earns up to `€65 × actual paid introductions` (maximum €195 with 3), before refunds, VAT where applicable, payment fees and operating costs.

### Implementation phases / go-live gate

1. Keep the browser-local form working and add an optional **simulation** of the private, anonymised installer preview only if clearly labelled as non-live; this never transmits any personal field.
2. Implement authenticated, access-controlled server-side data storage, private homeowner request/verification, installer vetting, admin review, explicit named-recipient approval and anonymised private listing queries; perform threat modelling and privacy review before collecting live PII.
3. Add atomic slot reservations, Stripe Checkout/webhooks, private release and audit logs, support/refund/expiry handling; test simultaneous purchases, revoked approval, identity/role isolation, and cancelled checkouts.
4. Pilot in limited counties with real homeowner-approved requests and 2–3 verified installers. Do not enable paid sales until security, privacy notice, deletion/retention, and end-to-end refund/release tests pass.
