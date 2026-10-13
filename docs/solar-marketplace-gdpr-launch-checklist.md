# Compound Solar Marketplace — lean GDPR checklist

**Status:** prelaunch checklist. It is not evidence that the marketplace is compliant or operational.

Keep the customer journey simple. These behind-the-scenes checks are required before taking personal details for a real marketplace.

## The homeowner must understand exactly what happens

- [ ] Using the compass/calculator does **not** require personal details or sharing permission.
- [ ] On the separate quote request, homeowner actively selects **1, 2 or 3** installers (no default), with an **unticked** clear sharing/quote-contact checkbox.
- [ ] Near the checkbox, explain that **county, rough area and non-identifying project information** may be previewed to approved installers; once purchased, the **name, contact details and project brief** are shared with no more than the chosen number of approved installers so they can provide the requested quotations.
- [ ] Explicitly disclose Compound receives payment for introductions; do not bundle permission for unrelated promotional email/SMS/phone marketing.
- [ ] Link a short, accurate privacy notice: controller, purposes, lawful bases, recipient identities or categories, retention, data rights and a published withdrawal/contact email.
- [ ] Record the choice, wording/notice version, timestamp and selected maximum. Confirm to homeowners **which actual companies** received details as introductions occur, and provide an easy route to stop future introductions.
- [ ] Confirm the legal basis and the sufficiency of category-based recipient notice for independent installer companies with a qualified Irish data-protection adviser before go-live; use named-company approval if that specific arrangement requires it.

## Privacy and access behind the scenes

- [ ] Only verified, authenticated installers see project previews. Avoid potentially identifying small localities and distinctive detail combinations.
- [ ] No purchaser sees full contact info for a project they haven't bought and been authorised to access; payers never gain access to another installer's purchased projects.
- [ ] One purchase per company per project; max 1/2/3 slots based on homeowner choice; prevent double sale on concurrent checkouts.
- [ ] Unlock only after a **verified Stripe webhook** and a final check that the customer has not withdrawn/closed the request; no personal data in receipts, checkout metadata, analytics, public pages or emails.
- [ ] Set sensible retention/deletion rules for contact details and project briefs; handle access/deletion/withdrawal requests by email initially, with manual records of actions taken.
- [ ] Document the processing purpose and Article 6 lawful basis, appropriate vendor data-processing agreements/installer data-sharing terms, breach handling, and whether a DPIA is legally required. Keep reasonable security controls (MFA for admins/installers, encryption, access logs).
- [ ] Test opt-in, permission withdrawal during payment, privacy notice, no-public-PII, installer A vs B access and slot exhaustion before launch.

## Customer-facing copy

Use the exact checkbox text and quote choice in [the lean marketplace spec](solar-lead-marketplace-spec.md), after privacy/legal sign-off. This is **not** currently a live consent/submission flow.

## Guidance

- DPC transparency: https://www.dataprotection.ie/en/organisations/know-your-obligations/transparency
- DPC consent evidence and withdrawal: https://www.dataprotection.ie/en/dpc-guidance/case-studies/transparency/sharing-personal-data-third-parties-without-consent
- DPC self-assessment: https://dataprotection.ie/en/organisations/resources-organisations/self-assessment-checklist
- DPC ePrivacy/electronic marketing: https://www.dataprotection.ie/en/organisations/rules-electronic-and-direct-marketing
