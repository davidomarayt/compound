# Compound Solar Sponsorship API (pre-launch backend)

This folder hosts Vercel Node.js functions for the **existing** ad-free page at
https://compound.ie/solar/for-installers/.

## Status
Stripe LIVE product and recurring per-county price are created on Compound Life Ltd:
- Product: `prod_VQGaMl7eAUUEry`
- Price: `price_1UPQ3s2R63yYze0g066vmFgW` (€250/month per unit, VAT-exclusive)
- **No checkout, charges, webhook endpoint, Supabase project, or private admin dashboard is live.**
- The current published registration page continues using FormSubmit until the API is fully configured.

## Setup before switching the public form

1. Create **a new dedicated Supabase project** for Compound Solar; do not put sponsor and homeowner PII in unrelated projects. Review any charge first.
2. Apply `schema.sql` with the new project's SQL editor. Check the RLS/security advisors and validate an atomic county conflict test before accepting money.
3. Link only `sponsor-api/` as a standalone Vercel project, with Node.js 22+ and production branch set to Compound's actual publishing branch. Test `/api/health`.
4. Enter all values from `.env.example` in Vercel project environment settings (encrypted). Never put Stripe secret keys, Supabase service-role keys, Turnstile secret or Resend keys in Compound's public repository.
5. Configure a verified Resend sender domain, confirm receipt at david@compound.ie and applicant emails, and provision Cloudflare Turnstile. Update the frontend to use the Vercel API URL and render the public Turnstile widget.
6. Configure a Stripe **live-mode** webhook to `https://YOUR_BACKEND_DOMAIN/api/webhook` and subscribe to: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`. Add its signing secret to Vercel.
7. Verify tax registrations and configure Stripe Tax or tax rates **before allowing payment**. The price is tax-exclusive and the code intentionally does NOT assume every buyer has the same VAT treatment.
8. Verify payment and cancellation flows in Stripe test mode with separate sandbox credentials and sandbox price IDs before enabling public live checkout.
9. Update the ad-free installer page to POST JSON to `/api/apply`. Only then remove the temporary hosted FormSubmit integration.

## Endpoints
- `GET /api/health`: readiness response, no secrets.
- `POST /api/apply`: website origin, Cloudflare Turnstile and field validation, secure database record, admin/installer email notification.
- `GET /api/admin-applications`: confidential pending and current applications; requires `Authorization: Bearer <ADMIN_API_TOKEN>`.
- `POST /api/admin-approve`: checks installer approval token, locks requested counties transactionally, emails a 48-hour private checkout invitation.
- `GET /api/checkout?token=...`: validates invitation, creates short-lived Stripe-hosted subscription checkout with quantity equal to assigned county count.
- `POST /api/webhook`: verifies Stripe HMAC signature against raw body, reconciles invoice and subscription lifecycle in an atomic database RPC.
- `GET /api/counties`: public county availability status without company names or applicant information.

## Security and reliability

- One row per county in `solar_county_slots` with PRIMARY KEY and transactional advisory lock prevents double booking under concurrency.
- Pending applications do **not** reserve counties until manually verified.
- Paid invoices activate slots only if all requested counties are still assigned to the same application.
- Failed renewal suspends lead delivery; cancellation frees the slots.
- No standalone public payment link: paid Checkout always goes through backend validation and customer-specific reference.
- Admin APIs require a random 32+ character bearer token from Vercel secrets and must not be called directly from public browser code.
- Stripe event deduplication is in the same DB transaction as status changes. Out-of-order events cannot reactivate cancelled counties.
- A checkout can outlive the reservation only in edge cases; such payments fail closed and require manual settlement/reconciliation; set operational alerts before opening checkout.
- For homeowner leads, build a separately consented form disclosing the sponsor and route only to `active` county slots.

## Test commands

```
cd sponsor-api
npm test
```

The **published Compound.ie pages must remain ad-free at /solar/for-installers/**.
