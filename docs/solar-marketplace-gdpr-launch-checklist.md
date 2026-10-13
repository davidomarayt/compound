# Compound Solar Marketplace — GDPR launch controls

Status: **pre-launch requirements, not a declaration of compliance**.
Owner: Compound.ie / responsible operating legal entity (to be confirmed).
Applies to: `/solar/get-quotes/`, homeowner request dashboard, private installer marketplace, Stripe purchases, support and admin access.
Reviewed against Irish Data Protection Commission (DPC) guidance on 13 October 2026. Requires qualified Irish privacy/legal review before real homeowner data is collected or sold.

## Non-negotiable launch rule

No personal homeowner information is released to an installer unless all conditions are satisfied **at the moment of disclosure**:
1. A verified, genuine quote request exists.
2. The homeowner specified a maximum of 1, 2 or 3 introductions.
3. The homeowner affirmatively approved **this named company** after being informed of the purpose, categories of data and commercial nature of the introduction.
4. The request is still open, in date and not withdrawn; the installer is verified, approved, in-area and not already a purchaser.
5. Payment is confirmed by a verified, idempotently processed Stripe webhook.
6. Access is granted to that installer account only, with a recorded release event.

Never release on redirect/receipt/email, based solely on payment, or based on a blanket 'up to three companies' statement.

## Before implementing live submissions

- [ ] Map data flows and inventory all processors, subprocessors and third-party scripts; confirm the legal entity acting as controller.
- [ ] Create a Record of Processing Activities (RoPA): collection, validation, matching, referral/disclosure, payments, support, security logs and optional marketing, with purpose, lawful basis, recipients and retention for each.
- [ ] Select and document an **appropriate Article 6 lawful basis for each purpose**, reviewed by counsel. Do not automatically label all processing 'consent': processing needed for requested services, compliance, security and payments may rely on different bases. If sharing depends on consent, obtain GDPR-valid consent and honour withdrawal.
- [ ] Determine whether Compound and installers are independent controllers for respective quote activity or joint controllers for any jointly determined purpose; set controller-to-controller data sharing terms as needed. Identify and execute Article 28 data-processing agreements with processors (e.g., hosting/auth/payment vendors where applicable).
- [ ] Screen and document whether a DPIA is necessary; conduct it **before processing** if likely high-risk. Even if not legally required, complete a lightweight threat/privacy risk assessment.
- [ ] Assess international transfers and vendor/subprocessor safeguards; document lawful transfer mechanisms where relevant.
- [ ] Publish a clear privacy notice **before** asking for name, Eircode, phone or email. Include responsible entity/contact, purposes and lawful bases, named recipients or categories, paid-introduction model, vendors/transfers, retention, rights/withdrawal, DPC complaint right, and how homeowner data is used after disclosure.
- [ ] Set a written retention/deletion schedule. Expire stale market listings (pilot proposal: 30 days); separately set justified deletion periods for contacts, project data, backups, audit events and legally required financial records. Expiry is **not** itself evidence all personal information has been deleted.
- [ ] Establish an incident and breach response owner; where a breach creates risk, notify the DPC without undue delay and where feasible within **72 hours of awareness**, and notify affected people without undue delay where high risk. Log all incidents and decisions.
- [ ] Establish an identity-verified rights-request workflow (access, correction, erasure where applicable, objection, portability where applicable); target the GDPR standard **one-month response period**, subject to lawful exceptions/extension.

## Homeowner UI and auditable permissions

- Free compass/calculators and locally generated project brief remain accessible without identifying themselves or agreeing to third-party sharing.
- Quote-request submission is a separate, deliberate action; choose exactly **1, 2, or 3** quotes, never default to 3 or expand the number later.
- Require a clear affirmative action for the quote-introduction request and provide privacy information in context. No bundled terms/privacy/marketing consent and no pre-ticked optional box.
- Proposed first-layer wording, subject to legal review:
  > I request up to **[1 / 2 / 3]** solar quotations. I understand Compound may receive a fee from approved installers for introductions. My contact details and completed project brief will be shown **only to installers I separately approve by name**, for preparing/contacting me about my requested quote. I can stop future introductions at any time; information already shared cannot automatically be recalled.
- Distinct **optional**, unticked marketing permission for Compound newsletters/promotions; do not treat quote-request approval as consent to marketing by Compound or any installer.
- Show installer name, business details, intended contact methods, request summary, and data categories before each named recipient approval.
- Store server-side append-only permission events: homeowner ID, project ID, recipient installer ID, purpose, max slots, consent/permission text version, privacy notice version, UTC timestamp, channel and subsequent withdrawal. Minimise IP/device evidence; never place contact details into analytics/audit logs.
- Homeowner dashboard: review/update brief, see approvals and *actual released recipients*, revoke pending authorisations, reduce unfilled slots, close request, view privacy notice and submit rights requests.
- When permission is withdrawn, **immediately block future checkout/release**. Do not promise automatic deletion of already disclosed information; display already-released recipients and facilitate rights requests to them.

## Installer, admin and Stripe access controls

- [ ] Secure server-side authentication; verify each business and relevant installer accreditation before approval; MFA for installers/admins; disable access when verification lapses.
- [ ] Separate `project_teaser` and private `project_contact`/full-brief tables or equivalent access-controlled views. Deny unauthorised DB/API access by default; enforce row-level constraints on every object reference and use unguessable internal IDs. Human-readable SKU never authorises access.
- [ ] Display only broadly described, carefully minimised listings in logged-in installer marketplace. A project can remain identifiable by location plus uncommon details even if name is omitted: test re-identification and suppress rare combinations.
- [ ] Only approved installer company may request the listing; keep named homeowner approval pending before paid checkout.
- [ ] Stripe Checkout Session created server-side after installer/approval/slot checks; send only non-sensitive metadata (internal opaque ID/transaction reference). **Never send the homeowner's name, phone, Eircode, precise address or brief to Stripe metadata, product descriptors, receipt or email.**
- [ ] Reserve slots atomically and release them on expiry/failure. Validate signed webhook, recheck permission at release, handle duplicates idempotently, and **do not release if withdrawal/revocation occurred while checkout was open**; initiate refund/exception handling where necessary.
- [ ] Distinct purchasers get distinct grants; each purchaser can only view their own already-paid, already-authorised projects. No cross-company access from changed URLs, SKU enumeration, cached pages, exports, search indexes or browser history.
- [ ] Encryption in transit and at rest, role-restricted production access, credential/secret rotation, logging that redacts PII, backups with tested restoration and retention, throttling, suspicious-access monitoring and patching policy.
- [ ] No advertising tags or behavioural marketing trackers on contact, submission, approval, checkout-confirmation, or purchased-lead screens. Check cookie/ePrivacy consent requirements on public pages.

## Installer contractual conditions

- Quotes and scheduling only: no unrelated marketing, data resale, enriching marketing lists or sharing with subcontractors without an assessed lawful basis/notice and suitable arrangements.
- Installer explains its separate controller status and privacy contact at first engagement (subject to counsel-confirmed allocation).
- Only retain homeowner data for the justified quote/service period; securely delete when unnecessary, except legally required records.
- Contact the homeowner only by the permitted channels and within the requested quote scope. Any **subsequent promotional marketing** needs its own ePrivacy/GDPR compliance analysis; never infer it from the referral.
- Define breach notification/cooperation, security controls, complaint handling, data subject request handoff, audit/termination and penalties for misuse in the installer agreement.

## Mandatory automated negative tests (no deployment with failures)

1. Completing the free compass without submitting a quote request creates no sellable SKU and does not transmit contact data.
2. Homeowner choosing 1 or 2 quotes produces exactly 1 or 2 available slots; never 3.
3. Unauthenticated/denied/expired installer sees no inventory or private endpoints (including direct API/object references).
4. An approved installer sees **only** teaser before purchase; unapproved installer cannot purchase even with a guessed SKU.
5. Installer A pays: only A unlocks; B and C still see teasers; A cannot buy again.
6. Homeowner declines B: B cannot pay or unlock.
7. Homeowner withdraws during pending checkout: webhook never releases PII, slot closes and refund/exception workflow fires.
8. Stripe return-page success without a valid signed webhook does **not** release PII; duplicated webhook never duplicates slot charge/release.
9. Three simultaneous purchases for one remaining slot result in **at most one** confirmed release, without double charges.
10. Expired/closed/sold-out/deleted projects cannot be purchased or re-opened by guessing identifiers.
11. Network, error tracking, GA4, AdSense, logs, Stripe metadata, receipts, URLs, caching and outbound emails contain **no** homeowner contact data or full briefs.
12. Withdrawal, export/access request, correction, erasure/retention job, backup lifecycle and admin audit are exercised in staging.
13. An anonymised teaser for a distinctive rural property is reviewed for re-identification risk; redact/suppress if necessary.
14. Verify date/time, notice version, named recipient and purpose can be reconstructed for **every** release event.

## Release sign-off record

| Required approval | Status |
|---|---|
| Controller identity and Article 6 lawful-basis matrix | Not completed |
| DPA/controller-to-controller contracts and vendor/transfer review | Not completed |
| DPIA screening and documented risk controls | Not completed |
| Final homeowner privacy notice and per-installer permission UX | Not completed |
| Installer terms and identity/accreditation process | Not completed |
| Server-side access, Stripe and concurrency tests | Not completed |
| Retention, rights and incident response procedures tested | Not completed |
| Qualified Irish privacy/legal review | Not completed |

**Default deployment setting:** Paid introduction purchases and release of homeowner data OFF until all sign-offs pass.

## Official Irish regulatory references

- DPC legal bases: https://www.dataprotection.ie/en/dpc-guidance/guidance-legal-bases-processing-personal-data
- DPC consent/transparency case: https://www.dataprotection.ie/en/dpc-guidance/case-studies/transparency/sharing-personal-data-third-parties-without-consent
- DPC transparency: https://dataprotection.ie/en/individuals/know-your-rights/right-be-informed-transparency-article-13-14-gdpr
- DPC DPIAs: https://www.dataprotection.ie/en/organisations/know-your-obligations/data-protection-impact-assessments
- DPC controller/processor contracts: https://www.dataprotection.ie/en/dpc-guidance/data-processing-agreements
- DPC electronic marketing: https://www.dataprotection.ie/en/organisations/rules-electronic-and-direct-marketing
- DPC RoPA: https://www.dataprotection.ie/en/dpc-guidance/records-of-processing-article-30-guidance
- DPC rights timing: https://www.dataprotection.ie/en/faqs/access-and-rectification/how-long-does-organisation-have-respond-my-access-request
- DPC breaches: https://www.dataprotection.ie/en/faqs/responsibilities-data-controllers/what-do-i-do-if-there-security-breach
