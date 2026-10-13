-- Compound Solar private installer portal: staging schema only.
-- Not yet applied to any Supabase project. Use a dedicated Compound-owned
-- database after the owner authorises its organisation and cost.
-- RLS must be verified on that project before storing any homeowner PII.
begin;

create table if not exists public.solar_installer_accounts (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null unique references auth.users(id) on delete restrict,
  company_name text not null check (char_length(company_name) between 2 and 150),
  seai_registration text,
  service_counties text[] not null default '{}'::text[],
  verification_status text not null default 'pending'
    check (verification_status in ('pending', 'approved', 'suspended', 'rejected')),
  created_at timestamptz not null default now()
);

create table if not exists public.solar_lead_teasers (
  id uuid primary key default gen_random_uuid(),
  sku text not null unique check (sku ~ '^SOL-[A-Z0-9-]{6,40}$'),
  county text not null,
  area_general text,
  property_type text,
  project_type text,
  system_kwp numeric(6,2) check (system_kwp is null or system_kwp > 0),
  roof_orientation text,
  battery_preference text,
  installation_timeframe text,
  price_cents integer not null default 6500 check (price_cents between 100 and 100000),
  max_introductions smallint not null check (max_introductions between 1 and 3),
  sold_count smallint not null default 0 check (sold_count >= 0),
  reserved_count smallint not null default 0 check (reserved_count >= 0),
  status text not null default 'pending_review' check (status in ('pending_review','active','sold_out','closed','expired')),
  expires_at timestamptz not null default (now() + interval '30 days'),
  created_at timestamptz not null default now(),
  constraint solar_slots_never_oversold check (sold_count + reserved_count <= max_introductions)
);
create index if not exists solar_teasers_county_active on public.solar_lead_teasers (county, created_at desc)
  where status = 'active';

create table if not exists public.solar_lead_purchases (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.solar_lead_teasers(id) on delete restrict,
  installer_id uuid not null references public.solar_installer_accounts(id) on delete restrict,
  amount_cents integer not null check (amount_cents > 0),
  status text not null default 'reserved' check
    (status in ('reserved','paid','access_granted','expired','cancelled','refunded')),
  stripe_checkout_session_id text unique,
  stripe_payment_intent_id text unique,
  purchased_at timestamptz,
  created_at timestamptz not null default now(),
  unique (project_id, installer_id)
);
create index if not exists solar_purchases_installer_idx on public.solar_lead_purchases (installer_id, created_at desc);

-- Sensitive customer details are deliberately separated from the anonymous listing.
-- No client grants for INSERT, UPDATE, or DELETE. Only trusted server functions can
-- create leads, reserve slots, verify Stripe payments and record a release.
create table if not exists public.solar_lead_details (
  project_id uuid primary key references public.solar_lead_teasers(id) on delete restrict,
  homeowner_name text not null,
  homeowner_email text not null,
  homeowner_phone text,
  eircode text,
  brief jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Permission records are server-only and in a non-API schema.
create schema if not exists compound_private;
revoke all on schema compound_private from public, anon, authenticated;
create table if not exists compound_private.solar_homeowner_permissions (
  project_id uuid primary key references public.solar_lead_teasers(id) on delete restrict,
  requested_max smallint not null check (requested_max between 1 and 3),
  affirmative_opt_in boolean not null check (affirmative_opt_in = true),
  wording_version text not null,
  privacy_notice_version text not null,
  permitted_contact_method text not null,
  approved_at timestamptz not null default now(),
  withdrawn_at timestamptz
);
create table if not exists compound_private.solar_release_events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.solar_lead_teasers(id) on delete restrict,
  installer_id uuid not null references public.solar_installer_accounts(id) on delete restrict,
  purchase_id uuid not null unique references public.solar_lead_purchases(id) on delete restrict,
  released_at timestamptz not null default now(),
  homeowner_notified_at timestamptz
);
revoke all on all tables in schema compound_private from public, anon, authenticated;

alter table public.solar_installer_accounts enable row level security;
alter table public.solar_lead_teasers enable row level security;
alter table public.solar_lead_purchases enable row level security;
alter table public.solar_lead_details enable row level security;
alter table compound_private.solar_homeowner_permissions enable row level security;
alter table compound_private.solar_release_events enable row level security;

-- Force server-side authorisation for all writes. Never grant browser write access.
revoke all on public.solar_installer_accounts, public.solar_lead_teasers,
  public.solar_lead_purchases, public.solar_lead_details from anon, authenticated;
grant select on public.solar_installer_accounts, public.solar_lead_teasers,
  public.solar_lead_purchases, public.solar_lead_details to authenticated;
-- The dedicated Vercel API uses an elevated server-only secret key.
-- Explicit GRANTs are needed on projects with automatic table exposure disabled.
-- Browser users retain SELECT-only access filtered through RLS.
grant select, insert, update, delete
  on table public.solar_installer_accounts, public.solar_lead_teasers,
           public.solar_lead_purchases, public.solar_lead_details
  to service_role;

create policy "installer can read own profile"
  on public.solar_installer_accounts for select to authenticated
  using (owner_user_id = (select auth.uid()));

create policy "approved installer can read own region projects and purchases"
  on public.solar_lead_teasers for select to authenticated
  using (
    exists (
      select 1 from public.solar_installer_accounts i
      where i.owner_user_id = (select auth.uid())
        and i.verification_status = 'approved'
        and (
          (
            solar_lead_teasers.status = 'active'
            and solar_lead_teasers.expires_at > now()
            and solar_lead_teasers.county = any(i.service_counties)
          )
          or exists (
            select 1 from public.solar_lead_purchases p
            where p.project_id = solar_lead_teasers.id
              and p.installer_id = i.id and p.status = 'access_granted'
          )
        )
    )
  );

create policy "installer only sees own orders"
  on public.solar_lead_purchases for select to authenticated
  using (
    exists (
      select 1 from public.solar_installer_accounts i
      where i.id = solar_lead_purchases.installer_id
        and i.owner_user_id = (select auth.uid())
        and i.verification_status = 'approved'
    )
  );

create policy "only purchased installer may read private quote brief"
  on public.solar_lead_details for select to authenticated
  using (
    exists (
      select 1 from public.solar_lead_purchases p
      join public.solar_installer_accounts i on i.id = p.installer_id
      where p.project_id = solar_lead_details.project_id
        and p.status = 'access_granted'
        and i.owner_user_id = (select auth.uid())
        and i.verification_status = 'approved'
    )
  );

-- In particular, no policy allows public or merely authenticated
-- users to read or insert homeowner contact records or permission events.
commit;
