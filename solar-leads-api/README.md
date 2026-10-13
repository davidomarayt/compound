# Compound Solar — private lead marketplace backend

**Implementation status:** GitHub code and automated validation are available, but **the backend is NOT deployed**. There is no dedicated Compound Supabase project in the connected account, and the Vercel integration did not expose a deployable team. **No homeowner PII or real payments are flowing.** Both launch flags default OFF.

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

1. Obtain approval for a **new** Compound-owned Supabase project (Ireland closest region `eu-west-1`) in the **chosen** organisation. **Never** use MyClinician or PlotMap databases.
2. Check Supabase product docs / auth settings; apply base SQL, then `schema-functions.sql`. Review all RLS policies and default grants with the Supabase security advisor. Do not enable API Data API access for private schema; public schema tables use restrictive RLS.
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

- Supabase shows only one organisation, named **MyClinician**. Project creation needs explicit organisation selection and any cost authorisation; no new project has been created.
- Connected Vercel integration shows no available teams, and existing projects are FairPath and MyClinician. A Compound API deployment cannot be performed from this connection until Vercel access is authorised.
- Connected Stripe account is **Compound Life Ltd, live mode**, with no test-mode account visible. No live charges should be attempted.

Everything fails closed until the owner approves the service account/project and the correct deployment and secrets exist.
