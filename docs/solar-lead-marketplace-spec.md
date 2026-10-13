# Compound Solar — lean private lead marketplace (pilot)

Status: **specification only**. The existing `/solar/get-quotes/` page remains browser-local and does not submit homeowner information or create paid leads. No real submission or paid introduction is authorised until the secure backend and checks below exist.

## Simple homeowner journey

1. Use the Solar Project Builder with its on-page interactive 360° compass; no photo upload and no account needed for browsing/calculating.
2. To **request quotes**, explicitly choose **1, 2 or 3 installers** (no preselected choice) and provide required contact details. A separate, unticked acknowledgement explains limited listing previews, paid introductions, full-data disclosure and permission for quote-related contact. Quote-sharing is optional and must not be a condition of using the calculator.
3. Compound verifies contact and genuine quote intent, securely saves the brief, creates a non-identifying project identifier and human-readable SKU (e.g. `SOL-MH-2026-00421`), and makes an **anonymised teaser** visible only to logged-in, approved installers.
4. An approved installer purchases one €65 pilot introduction through Stripe. Following verified payment, **only that installer** unlocks the quote brief and contact details. Available slots fall by one; each installer may purchase the SKU once.
5. After each disclosure, tell the homeowner **which named installer** received their details. A simple email contact is sufficient initially for stopping future introductions and privacy requests—no customer dashboard or per-installer approval screen is planned for the pilot unless legal review identifies a reason.
6. Expire/close requests promptly. Never disclose more than the selected maximum. Stop future releases immediately after withdrawal; do not claim prior disclosures can be undone.

## Proposed first-layer quote-request wording (legal review needed)

**Quote choice:** "How many solar installation quotes would you like? [1] [2] [3]"

**Required, unticked affirmative checkbox only for quote requests:**

> I request up to **[chosen number]** solar installation quotations. I understand that Compound.ie will show approved solar installers a limited project preview, which may include my **county, approximate area and broad installation requirements**, but not my name or contact details. I agree that Compound.ie may share my **name, contact details and completed project brief** with up to **[chosen number]** approved solar installers, who may contact me by **[chosen method]** about my requested quotes. Compound.ie may receive payment from installers for these introductions. I can stop future sharing at **[published privacy email]**. [Privacy notice]

The checkbox is not newsletter/marketing consent and is not a substitute for a complete privacy notice. Inform customers of the identities of actual recipients when sharing takes place. Confirm the appropriate GDPR lawful basis and whether partner-controller details need to be given before sharing during prelaunch privacy review; **do not imply a category-only checkbox guarantees compliance in every arrangement**.

## What appears in the private installer listing

- SKU; county and **only as broad a general area as is safe**; property/project type; approximate PV kWp; broad roof orientation; battery interest; rough installation timeframe; price per introduction; available slots.
- Suppress town or other combinations that could identify individual rural households.
- **Never display name, precise address, Eircode, email, phone or free-text details before purchase.**
- No public feed, web-indexed listings, static JSON or publicly accessible API.

## After an installer purchases

- Installer is a verified approved business, eligible in area, and not already a purchaser.
- Server verifies payment and homeowner permission is current; grant access to **that installer account only**; update slot count atomically, without overselling.
- An installer receives a private dashboard link rather than personal data in a Stripe receipt or email.
- Record the actual recipient company and notification to the homeowner.
- If the lead is closed, withdrawn or stale during checkout, **do not release details**; handle refunds safely.

## Form data kept from the existing project builder

The existing fields are valuable for quoting; retain them, but make uncertain specialist answers optional.
- **Project**: county, approximate area, authorisation to install, property/building type, project type, timing, indicative budget, restrictions.
- **Roof**: 360° compass readings (azimuth/pitch for up to two roof faces), approximate area, material/condition, shading, obstructions, access.
- **Usage**: annual kWh/bill, day-night pattern, EV/heat pump, smart meter, electrical supply if known.
- **Scope**: PV size, battery/charger/diverter, backup, grants, finance, existing quotes.
- **Private contact**: name, email/phone, selected contact method and optionally Eircode (never teased).

Any projection made from self-reported roof information remains indicative; an installer must verify site design and final pricing.

## Minimal back-end records

- `project`: secure ID, display SKU, structured brief, status, expiry, requested_max (1–3), reserved/sold count.
- `homeowner_private`: contact details and contact preferences, restricted separately from teaser.
- `permission`: project, chosen maximum, affirmative choice, wording version, privacy notice version, UTC timestamp, permitted contact channels, withdrawal time (if any).
- `purchase`: unique (project,installer), slot reservation, Stripe Checkout ID, webhook/payment/refund status.
- `release`: project, purchaser/recipient, UTC release time, proof current permission, homeowner notification status.
- `installer`: identity/business verification, status, servicing counties, secure login.

## Must-pass launch checks — lean, but not optional

- Correct information notice including controller, lawful basis, purposes, recipient companies/categories, paid introductions, retention, withdrawal/rights contact and vendor details; retain a record of each affirmative quote-sharing permission. Separate any unrelated marketing permission.
- Appropriate Article 6 basis documented; necessary processor contracts, privacy risk/DPIA screening and installer terms assessed. Do not collect live identifying data until these are in place.
- Access enforced **server-side**, not just hidden visually: an unpaid or different installer cannot open full details even with a guessed SKU/URL.
- Accurate, race-safe capacity: homeowner-selected max 1/2/3, each business once; Stripe signed webhook and idempotent fulfilment; revoked/expired entries blocked.
- Secure storage, minimal retention and deletion practice, rights-request and incident contact/process. No identifiable data in analytics, ads, receipt, URL, logs or Stripe metadata; no ads on contact/payment dashboards.
- Test the actual quote opt-in, privacy notice, withdrawal and emails, then seek a proportionate qualified Irish privacy/legal check before live sales.

Reference: [Lean GDPR checklist](solar-marketplace-gdpr-launch-checklist.md).

## What we're **not** building in the pilot

No homeowner privacy portal, no separate approval request for each prospective installer, no auction, no subscriptions, no lead bulk exports, and no photo uploads. These are product choices, not blanket exemptions from GDPR. If legal review identifies a need for narrower recipient approval or further disclosures, adapt before launch.

Pilot price **€65 per homeowner-authorised introduction**, with up to **three** purchases. This is a pricing test, not guaranteed revenue or conversion.
