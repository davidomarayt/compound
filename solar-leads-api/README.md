# Compound Solar — private lead marketplace backend

**Implementation status (13 October 2026):** Isolated Compound Life Ltd / Compound Solar Supabase project in Ireland (`guifxtijipkpvjjyhatq`) has the initial secure schema and transactional SKU / payment release functions installed. Vercel **compound-solar-api** project is deployed from `solar-leads-api/` in Dublin, and the installer portal uses Supabase's public publishable key. Vercel's elevated `SUPABASE_SECRET_KEY` has been configured in production, and an authenticated server-only read-only health check returned HTTP 200 with `database: connected`. Homeowner form submission is coded but hidden behind an OFF flag. Both API launch flags remain OFF, and live Stripe charges require a second separate approval switch. **No real customers, installer accounts, payments or homeowner PII are stored.**
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
3. **Completed (deployment only):** Vercel `compound-solar-api` is deployed from `solar-leads-api/`. Public Supabase URL and publishable key are configured as Vercel environment variables. **Completed:** Elevated `SUPABASE_SECRET_KEY` was added to Vercel production settings by the owner, and secure backend database access was verified via `/api/health` (HTTP 200). Never paste this key into GitHub, chat or public HTML.
4. **Pending UI configuration:** Set Supabase Auth Site URL and redirect allowlist to `https://compound.ie/solar/installer-portal/`; configure the email template to send the six-digit `{{ .Token }}` code (or allow a magic-link fallback), set verified SMTP for reliable sign-ins, then manually approve two test installer accounts with different counties. `shouldCreateUser:false` is already enforced in the portal.
5. **Partially complete:** Installer portal is now connected to Supabase with the non-secret URL and publishable key; real login requires the Supabase Auth settings and approved test installer accounts. Checkout API URL remains deliberately blank until server-side Stripe test flow has passed.
6. **Pending:** Configure Stripe *test-mode* `sk_test_...` secret and webhook signing secret directly in Vercel; test payment completion, duplicate/replayed events, expiry, withdrawal and simultaneous buyers. The connected Stripe app currently exposes **live mode only**; no real Stripe charges have been attempted.
7. **Staged, disabled:** The homeowner form now contains an explicit unticked sharing agreement and opt-in for 1, 2 or 3 installers, and a gated adapter (`solar-lead-intake.js`) for the live API. It does **not send** personal information while `data-solar-leads-active="false"`. Still requires a verified Resend sending domain, Turnstile site key/secret and an accurate final privacy notice.
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
- **Resolved:** Vercel project `compound-solar-api` is created and deployed in Dublin with the correct GitHub root. Elevated credentials, Supabase Auth OTP template and Stripe test mode are **not configured yet**.
- Connected Stripe account is **Compound Life Ltd, live mode**, with no test-mode account visible; use its Dashboard's test environment and a `sk_test_` key, never `sk_live_` for pilot tests.

Everything fails closed until the owner approves the service account/project and the correct deployment and secrets exist.

## Deployment verification (13 October 2026)

- Vercel project: `compound-solar-api`, Dublin region; automatic GitHub deployments.
- Safe status endpoint `https://compound-solar-api.vercel.app/api/health`: HTTP 200, `database: connected`.
- Public write/checkout features: disabled by separate Vercel environment flags.
- Added explicit `service_role` table privileges to the original base SQL and applied them as `compound_solar_server_service_role_privileges`; required for REST access on this Supabase project where new tables are not auto-exposed.
- Supabase health check does not expose keys, rows, PII or detailed errors.
- Still pending before pilot access: configure Auth OTP email template and allowed URLs, provision one or two test installer accounts, RLS cross-account tests, a verified email sender, spam checks, Stripe test-mode credentials and signed webhooks.
