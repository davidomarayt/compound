-- Compound Solar sponsorship database. Run in a NEW dedicated Supabase project.
-- Never install in unrelated MyClinician or PlotMap databases.
-- Only backend service_role can access customer/application records.
create extension if not exists pgcrypto;
create table if not exists public.solar_counties (
 county text primary key,
 country_code text not null check(country_code in ('IE','GB-NIR'))
);
insert into public.solar_counties(county,country_code)
values
('Carlow','IE'),('Cavan','IE'),('Clare','IE'),('Cork','IE'),('Donegal','IE'),('Dublin','IE'),('Galway','IE'),('Kerry','IE'),
('Kildare','IE'),('Kilkenny','IE'),('Laois','IE'),('Leitrim','IE'),('Limerick','IE'),('Longford','IE'),('Louth','IE'),
('Mayo','IE'),('Meath','IE'),('Monaghan','IE'),('Offaly','IE'),('Roscommon','IE'),('Sligo','IE'),
('Tipperary','IE'),('Waterford','IE'),('Westmeath','IE'),('Wexford','IE'),('Wicklow','IE'),
('Antrim','GB-NIR'),('Armagh','GB-NIR'),('Derry / Londonderry','GB-NIR'),('Down','GB-NIR'),('Fermanagh','GB-NIR'),('Tyrone','GB-NIR')
on conflict(county) do nothing;

create table if not exists public.solar_sponsor_applications (
 id uuid primary key default gen_random_uuid(),
 company text not null check(length(company) between 1 and 120),
 contact text not null check(length(contact) between 1 and 100),
 email text not null check(length(email) between 3 and 160),
 phone text not null default '',
 website text not null default '',
 accreditation text not null default '',
 notes text not null default '',
 requested_counties text[] not null check(cardinality(requested_counties) between 1 and 32),
 status text not null default 'pending' check(status in ('pending','approved','active','paused','expired','rejected','cancelled')),
 invite_hash text unique,
 expires_at timestamptz,
 stripe_checkout_id text,
 stripe_subscription_id text unique,
 stripe_customer_id text,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.solar_sponsor_applications
 add column if not exists q1_prepaid_at timestamptz,
 add column if not exists cancellation_requested_at timestamptz;
create index if not exists idx_solar_sponsor_app_status on public.solar_sponsor_applications(status,created_at desc);

-- PRIMARY KEY county is the final exclusivity guarantee even across concurrent checkouts.
create table if not exists public.solar_county_slots (
 county text primary key references public.solar_counties(county),
 application_id uuid not null references public.solar_sponsor_applications(id) on delete cascade,
 status text not null check(status in ('held','active','paused')),
 hold_until timestamptz,
 stripe_subscription_id text,
 updated_at timestamptz not null default now()
);
create index if not exists idx_solar_slots_app on public.solar_county_slots(application_id);

create table if not exists public.solar_stripe_events(
 id text primary key,
 kind text not null,
 created_at timestamptz not null default now()
);

create table if not exists public.solar_homeowner_leads (
 id uuid primary key default gen_random_uuid(),
 sponsor_application_id uuid not null references public.solar_sponsor_applications(id),
 county text not null references public.solar_counties(county),
 customer_name text not null,
 customer_email text not null,
 customer_phone text not null,
 eircode_or_postcode text not null default '',
 electricity_details text not null default '',
 message text not null default '',
 customer_consent boolean not null check(customer_consent),
 submitted_at timestamptz not null default now(),
 delivered_at timestamptz
);
create index if not exists idx_solar_leads_sponsor_created on public.solar_homeowner_leads(sponsor_application_id,submitted_at desc);

alter table public.solar_counties enable row level security;
alter table public.solar_sponsor_applications enable row level security;
alter table public.solar_county_slots enable row level security;
alter table public.solar_stripe_events enable row level security;
alter table public.solar_homeowner_leads enable row level security;
-- No public policies: anon and authenticated clients cannot read/write the data.
revoke all on public.solar_counties,public.solar_sponsor_applications,public.solar_county_slots,
 public.solar_stripe_events,public.solar_homeowner_leads from anon,authenticated;
grant select,insert,update,delete on public.solar_counties,public.solar_sponsor_applications,
 public.solar_county_slots,public.solar_stripe_events,public.solar_homeowner_leads to service_role;

-- This transaction serializes approvals so simultaneous sales never allocate the same county.
create or replace function public.solar_approve_application(
 p_application_id uuid,p_invite_hash text,p_expires timestamptz
) returns jsonb language plpgsql security invoker set search_path = public as $$
declare
 a public.solar_sponsor_applications%rowtype;
 c text;
begin
 perform pg_advisory_xact_lock(8460121);
 select * into a from solar_sponsor_applications where id=p_application_id for update;
 if not found or a.status <> 'pending' then raise exception 'Application not pending'; end if;
 if p_expires <= now() or p_expires > now()+interval '3 days' then raise exception 'Invalid expiry'; end if;
 if p_invite_hash !~ '^[a-f0-9]{64}$' then raise exception 'Invalid token hash'; end if;
 -- Expired checkout invitations lose their reservation, but never an active sponsor's slot.
 update solar_sponsor_applications set status='expired',updated_at=now()
 where id in (select application_id from solar_county_slots where status='held' and hold_until<now())
   and status='approved';
 delete from solar_county_slots where status='held' and hold_until<now();
 if (select count(distinct x) from unnest(a.requested_counties) x)
      <>cardinality(a.requested_counties) then raise exception 'Invalid duplicate counties'; end if;
 if (select count(*) from solar_counties where county=any(a.requested_counties))
      <>cardinality(a.requested_counties) then raise exception 'Invalid counties'; end if;
 foreach c in array a.requested_counties loop
   if exists(select 1 from solar_county_slots where county=c) then
     raise exception 'County unavailable: %',c;
   end if;
 end loop;
 insert into solar_county_slots(county,application_id,status,hold_until)
 select unnest(a.requested_counties),a.id,'held',p_expires;
 update solar_sponsor_applications set invite_hash=p_invite_hash,expires_at=p_expires,
 status='approved',updated_at=now() where id=a.id;
 return jsonb_build_object('id',a.id,'email',a.email,'company',a.company,
   'contact',a.contact,'requested_counties',a.requested_counties);
end; $$;

create or replace function public.solar_get_invite(p_invite_hash text)
returns jsonb language sql stable security invoker set search_path = public as $$
select jsonb_build_object('id',a.id,'email',a.email,'requested_counties',a.requested_counties,'stripe_checkout_id',a.stripe_checkout_id)
from solar_sponsor_applications a
where a.invite_hash=p_invite_hash and a.status='approved' and a.expires_at>now()
  and (select count(*) from solar_county_slots s where s.application_id=a.id
      and s.status='held' and s.hold_until>now())=cardinality(a.requested_counties)
limit 1; $$;

create or replace function public.solar_store_checkout(p_application_id uuid,p_session_id text,p_previous_session_id text)
returns void language plpgsql security invoker set search_path=public as $
begin
 -- Compare-and-swap ensures parallel requests cannot overwrite the live
 -- Checkout session reference, leaving a paid customer without entitlement.
 update solar_sponsor_applications set stripe_checkout_id=p_session_id,updated_at=now()
 where id=p_application_id and status='approved' and expires_at>now()
 and stripe_checkout_id is not distinct from p_previous_session_id;
 if not found then raise exception 'Checkout session changed; retry original invitation'; end if;
end; $;

-- Process Stripe events exactly once, with entitlement status updated in same transaction.
create or replace function public.solar_apply_billing_event(
 p_event_id text,p_kind text,p_application_id uuid,p_subscription_id text,
 p_customer_id text,p_checkout_id text,p_quantity integer
) returns jsonb language plpgsql security invoker set search_path=public as $$
declare
 a public.solar_sponsor_applications%rowtype;
 own_count integer;
begin
 perform pg_advisory_xact_lock(8460121);
 insert into solar_stripe_events(id,kind) values(p_event_id,p_kind) on conflict do nothing;
 if not found then return jsonb_build_object('duplicate',true); end if;
 select * into a from solar_sponsor_applications where id=p_application_id for update;
 if not found then raise exception 'Application not found'; end if;
 if p_kind='upfront_paid' then
   -- Signed paid checkout proves prepaid Jan–Mar 2027, with 2026 free.
   if a.status<>'approved' or a.stripe_checkout_id is distinct from p_checkout_id
      or a.expires_at<=now() then raise exception 'Founding checkout not approved or expired'; end if;
   if p_quantity<>cardinality(a.requested_counties) or p_quantity not between 1 and 32 then
     raise exception 'Subscription county quantity mismatch';
   end if;
   select count(*) into own_count from solar_county_slots
     where application_id=a.id and status='held' and hold_until>now();
   if own_count<>p_quantity then raise exception 'County reservation no longer available'; end if;
   update solar_sponsor_applications set status='active',q1_prepaid_at=now(),
     stripe_subscription_id=p_subscription_id,stripe_customer_id=p_customer_id,updated_at=now()
     where id=a.id;
   update solar_county_slots set status='active',hold_until=null,
     stripe_subscription_id=p_subscription_id,updated_at=now() where application_id=a.id;
 elsif p_kind='paid' then
   if a.status not in ('active','paused') then
     raise exception 'Cannot activate application in state %',a.status;
   end if;
   if a.stripe_subscription_id is distinct from p_subscription_id then
     raise exception 'Subscription does not match application';
   end if;
   if p_quantity is distinct from cardinality(a.requested_counties) then
     raise exception 'Paid invoice county quantity mismatch';
   end if;
   select count(*) into own_count from solar_county_slots where application_id=a.id
     and status in ('held','active','paused') and (status<>'held' or hold_until>now());
   if own_count<>cardinality(a.requested_counties) then
     raise exception 'County reservation no longer valid. Manual payment review required';
   end if;
   update solar_sponsor_applications set status='active',
     stripe_subscription_id=p_subscription_id,stripe_customer_id=p_customer_id,updated_at=now()
   where id=a.id;
   update solar_county_slots set status='active',hold_until=null,
     stripe_subscription_id=p_subscription_id,updated_at=now() where application_id=a.id;
 elsif p_kind='failed' then
   if a.status='active' and a.stripe_subscription_id=p_subscription_id then
     update solar_sponsor_applications set status='paused',updated_at=now() where id=a.id;
     update solar_county_slots set status='paused',updated_at=now() where application_id=a.id;
   end if;
 elsif p_kind='cancelled' then
   if a.stripe_subscription_id=p_subscription_id and a.status in ('approved','active','paused') then
     delete from solar_county_slots where application_id=a.id;
     update solar_sponsor_applications set status='cancelled',invite_hash=null,updated_at=now()
       where id=a.id;
   end if;
 end if;
 return jsonb_build_object('ok',true,'kind',p_kind,'application_id',a.id);
end; $$;

-- Only privileged server functions should invoke these RPCs.
revoke all on function public.solar_approve_application(uuid,text,timestamptz) from PUBLIC,anon,authenticated;
revoke all on function public.solar_get_invite(text) from PUBLIC,anon,authenticated;
revoke all on function public.solar_store_checkout(uuid,text,text) from PUBLIC,anon,authenticated;
revoke all on function public.solar_apply_billing_event(text,text,uuid,text,text,text,integer) from PUBLIC,anon,authenticated;
grant execute on function public.solar_approve_application(uuid,text,timestamptz) to service_role;
grant execute on function public.solar_get_invite(text) to service_role;
grant execute on function public.solar_store_checkout(uuid,text,text) to service_role;
grant execute on function public.solar_apply_billing_event(text,text,uuid,text,text,text,integer) to service_role;
