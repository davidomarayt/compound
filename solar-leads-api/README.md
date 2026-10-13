# Compound Solar — private lead marketplace backend

**Implementation status (13 October 2026):** Dedicated **Compound Life Ltd / Compound Solar** Supabase project created in Ireland (`guifxtijipkpvjjyhatq`); base schema and transactional SQL functions **applied and permission-checked**. Synthetic SKU/email verification was executed inside a rollback transaction with no records retained. Vercel API functions are **not deployed**, and homeowner intake/Stripe remain OFF; no live PII or payments.\n
This is a standalone Vercel Functions root, separate from the existing `sponsor-api/` and its abandoned county-sponsorship model.

## Where everything lives

- `api/intake.js` — validates an explicit 1–3 quote request, spam check and structured project brief, saves a new private SKU and emails a verification link. **Disabled** until secure onboarding/notice checks are signed off.
- `api/verify.js` — confirmation link requires a human POST; successful verification publishes only a sanitised, private, county-level project teaser to approved installers.
- `api/checkout.js` — checks the logged-in installer JWT against Supabase Auth, atomically reserves an eligible project slot in PostgreSQL, and creates a €65 hosted Stripe Checkout Session. No PII goes to Stripe metadata or receipts. **Disabled** until Stripe test mode, webhooks, RLS and tax handling have been verified.
- `api/webhook.js` — verifies the Stripe signature, reconciles price/currency/status, grants only this installer secure detail access, updates slot counts and notifies the homeowner with the recipient company name. Withdrawn/stale/incorrect payments fail closed and attempt a refund.
- `api/admin-withdraw.js` — staff-only, bearer-token-protected manual close/permission withdrawal after verifying a homeowner request.
- `api/health.js` — operational gating status without secrets.
- `lib/core.js` — validation, Supabase REST RPC/auth, Stripe API signing/payments, no-store CORS, Resend email.
- `schema-functions.sql` — transactional procedures, email verification records, SKU creation, permission logs, slot reservations, idempotent unlock, and closure functions. Apply **after** `../docs/sql/solar-installer-portal-schema.sql`.
- `tests/core.test.js` — Node unit tests (no real payment secrets or personal records).

## Provisioning order

1. **Completed:** Dedicated Compound Solar project in `eu-west-1`, isolated from MyClinician and PlotMap.
2. **Completed (first pass):** Base SQL and `schema-functions.sql` applied on 13 October 2026; all tables have RLS and no administrative RPC can be executed by `anon` or `authenticated`. All privacy-schema tables have intentionally no client policies. Full two-installer integration testing still required.
3. Establish a new Vercel project rooted at `solar-leads-api/`, configure all variables in `.env.example` using Vercel secret storage, and choose a trusted API URL. The Vercel team/project must be accessible first.
4. Set Supabase Auth Site URL and redirect allowlist to Compound and its private installer portal, configure the OTP email template to send `{{ .Token }}` rather than a Magic Link, configure SMTP, then manually approve two test installers with different service counties. Set `shouldCreateUser:false` in the client (already done).
5. Wire nonsecret `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` into the installer portal's `data-` attributes and checkout endpoint URL only after verifying CORS, OTP and RLS. Never paste `service_role`, Stripe secret or webhook secrets into public static files.
6. Configure Stripe **test** secret and `checkout.session.completed` / `checkout.session.expired` signing secret; simulate successful payment, retry/replay, session expiry, withdrawals and two installers racing for one slot. The attached Stripe account is **live only** at present; do not use it for checkout testing.
7. Configure a domain-verified Resend sender and Cloudflare Turnstile for homeowner intake; review the exact single unticked consent and link to the privacy notice. Connect the existing browser-local form to the API only after those checks, with intake gate still OFF until ready.
8. Document controller roles, installer terms, minimal data retention/erasure process, data processor terms, VAT/tax treatment, incident contact and proportional Irish GDPR review. Test no PII in public assets, analytics, logs, Stripe emails or unpurchased dashboards.
9. Enable `SOLAR_LEADS_INTAKE_ENABLED=true` only after intake and verification work end-to-end. Enable `SOLAR_LEADS_PAYMENTS_ENABLED=true` only after separately testing RLS, refund, webhook, concurrency, emails and invoicing.
10. Add secure routine cleanup for unverified and expired homeowner contacts and backups under the agreed retention policy before live collection. Stale listings already fail closed for selling, but **expiration alone does not purge PII**.

## Approval model

Pilot enrolment is manually reviewed. The marketing page has an installer application email action; the owner approves a company in Supabase Admin and creates its `solar_installer_accounts` row with `owner_user_id` (Supabase Auth UID), approved status and verified service counties. There is **no** public signup. OTP sign-in never creates new users.

Only installers authenticated to their own approved account can see private teasers and only purchasers of a specific lead have RLS access to its contact/brief. No customer dashboard or upload/photos are part of the pilot.

## Data and quote pricing

One verified request becomes one SKU with user-requested capacity **1, 2 or 3**. Pilot price is €65 / introduction. One verified firm may buy once per SKU. Zero slots means sold out. Price and inventory are always enforced **on the server**, not by HTML.

The system generates SKUs internally; Stripe is used for **a Checkout Session per purchase** with an inline line item, not a distinct Stripe Product for each homeowner.

## Test

```sh
cd solar-leads-api
node --check lib/core.js
node --check api/checkout.js
npm test
```

GitHub workflow `solar leads api` runs syntax, unit and SQL presence tests. This is not a substitute for integration tests with a real isolated Supabase instance and Stripe test-mode account.

## Dependencies / authorisation blockers

- **Resolved:** Compound Life Ltd Supabase organisation and Compound Solar project are connected and initial schema is applied.
- **Pending:** Vercel integration still lists FairPath and MyClinician but returns no selectable teams. Create/authorise a new Compound Solar API deployment rooted at `solar-leads-api/` before adding its secret configuration.
- Connected Stripe account is **Compound Life Ltd, live mode**, with no test-mode account visible. No live charges should be attempted.

Everything fails closed until the owner approves the service account/project and the correct deployment and secrets exist.
