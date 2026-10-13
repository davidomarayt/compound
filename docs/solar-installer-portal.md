# Compound Solar — Installer Portal implementation

**Status as of 13 October 2026:** portal **frontend committed**, with a design-only preview. **No live login, storage of homeowner contacts, Stripe Checkout or paid unlocking is activated.** This is intentional: the connected Supabase account exposes MyClinician and PlotMap projects only, neither of which should store Compound.ie homeowner data. A separate, owner-approved Compound Supabase project must be created and configured.

## Routes and assets

- Public landing / secure login entry: `https://compound.ie/solar/installer-portal/`.
- Synthetic design preview: `https://compound.ie/solar/installer-portal/?preview=1`. **Examples are fictional and cannot be purchased.**
- Page source: `content/pages/solar-installer-portal.md`.
- Styles: `compound/site/static/solar-installer-portal.css`.
- Client: `compound/site/static/solar-installer-portal.js`.
- Security-first database schema and RLS policies: `docs/sql/solar-installer-portal-schema.sql`.

The portal route is **noindex and excluded from the sitemap**, but these settings are not access controls. All real lead data lives in a secure database, never in static HTML, JS or client-side demo fixtures. GA and AdSense are suppressed on the portal; the login entry page itself is publicly visible, but authenticated data is gated server-side.

## Customer experience (pilot)

1. Company emails Compound to apply and provides business registration, email, and service counties. There is no automated onboarding or public account creation.
2. Admin vets the firm, creates an `auth.users` entry and associates it with a `solar_installer_accounts` record marked `approved` (using trusted admin tools only).
3. Installer enters approved business email; Supabase sends a **six-digit OTP**. Entering it authenticates the existing account; `shouldCreateUser:false` prohibits auto-signup.
4. Approved installer sees matched county projects under **Available Projects**. Anonymised cards show project SKU, county/broad area, technical summary, price and remaining slots.
5. **Purchased Leads** shows only completed, authorised, paid projects. Private contact/brief is fetched on demand from `solar_lead_details` under RLS and never inserted in the static site.
6. **My Account** displays company registration, approved service counties and verification status.

## Connection checklist (do not skip)

- [ ] Owner selects a dedicated Supabase organisation/project for Compound and approves any project-creation cost. Do not reuse MyClinician or PlotMap.
- [ ] Verify current Supabase Auth, email OTP, RLS and PostgREST documentation and apply/review the schema in that new project. Run security advisors and independent installer A/B access tests.
- [ ] Configure Auth settings: email provider, approved redirect/site URLs (Compound domain only), and **Magic Link email template containing `{{ .Token }}`** so users receive a six-digit OTP rather than a magic link. Configure appropriate delivery provider, rate limits and MFA where needed.
- [ ] Embed the **public, non-secret** Supabase project URL and publishable key in the portal root's `data-supabase-url` and `data-supabase-publishable-key` values. **Do not** put the service-role key, admin token or Stripe secret in HTML, GitHub or JS.
- [ ] Review an end-to-end flow with two independently approved installer accounts in staging: A can see local teasers, B cannot see A's purchased PII; unapproved accounts see nothing. Check URL tampering, unrelated counties and expired projects.
- [ ] Build a server-side SKU/quote request intake and Stripe Checkout endpoint. Populate `data-checkout-api-url` **only after** that API validates Auth JWT, approval, county, active homeowner permission, availability and price, and atomically reserves a slot. The client currently disables purchases when this URL is empty.
- [ ] Verify signed Stripe webhooks with idempotency and a fresh consent check, transition orders to `access_granted`, and release PII only to the paid account. Protect refunds, concurrent checkouts and withdrawal races. Mail receipts with dashboard links only.
- [ ] Complete short privacy notice and consent language, retention and incident plan and scoped Irish compliance review before receiving actual homeowner data.
- [ ] Do not advertise or accept live lead payments until both homeowner intake and seller portal fulfilment are fully tested.

## Pricing and security assumptions

- Pilot price: €65 per introduction, not a subscription.
- Per-homeowner selected availability: 1, 2 or 3 slots.
- Distinct firms each buy at most one introduction per project.
- All business applications are reviewed manually.
- No homeowner portal, lead auction, images or photo uploads in this first phase.
- Database authentication, RLS and Stripe webhooks are **not optional**, even though the visual workflow is deliberately minimal.

## Example (safe synthetic records)

The `?preview=1` demo renders three invented SKUs, blank purchased history and non-functional checkout controls; it is a design review aid, not a source of actual leads. Do not ever populate demo data with a real person's name, phone, Eircode or address.
