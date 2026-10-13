-- Compound Solar private collection pilot.
-- No installer access, no Stripe checkout, no public/authenticated table grants.
-- Review is restricted to an explicit invited Compound owner auth user.
begin;

create table if not exists public.solar_pilot_admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.solar_pilot_admins enable row level security;
revoke all on public.solar_pilot_admins from public, anon, authenticated;
grant select on public.solar_pilot_admins to service_role;

insert into public.solar_pilot_admins(user_id)
select a.owner_user_id from public.solar_installer_accounts a
join auth.users u on u.id=a.owner_user_id
where a.company_name='Compound Solar Internal Test'
  and a.verification_status='approved'
  and u.invited_at is not null and u.email_confirmed_at is not null
on conflict (user_id) do nothing;

do $$
begin
 if not exists (select 1 from public.solar_pilot_admins) then
  raise exception 'Refusing private pilot: no confirmed internal reviewer';
 end if;
end $$;

create table if not exists public.solar_pilot_requests (
  id uuid primary key default gen_random_uuid(),
  reference text not null unique,
  county text not null,
  requested_max smallint not null check (requested_max between 1 and 3),
  contact_method text not null check (contact_method in ('Email','Phone','Either')),
  homeowner_name text not null,
  homeowner_email text not null,
  homeowner_phone text,
  eircode text,
  brief jsonb not null,
  consent_version text not null check(consent_version='solar-private-pilot-2026-10-13'),
  ip_hash text not null check (ip_hash ~ '^[0-9a-f]{64}$'),
  email_hash text not null check (email_hash ~ '^[0-9a-f]{64}$'),
  status text not null default 'new' check (status in ('new','reviewed','withdrawn')),
  created_at timestamptz not null default now()
);
create index if not exists solar_pilot_created_idx
 on public.solar_pilot_requests (created_at desc);
create index if not exists solar_pilot_ip_rate_idx
 on public.solar_pilot_requests (ip_hash,created_at desc);
create index if not exists solar_pilot_email_rate_idx
 on public.solar_pilot_requests (email_hash,created_at desc);
alter table public.solar_pilot_requests enable row level security;
revoke all on public.solar_pilot_requests from public, anon, authenticated;
grant select, insert, update on public.solar_pilot_requests to service_role;

-- Service-only RPC, transaction-scoped rate limit, no public execute.
create or replace function public.solar_submit_private_pilot(p jsonb)
returns jsonb language plpgsql security definer set search_path=''
as $$
declare
 v_id uuid := pg_catalog.gen_random_uuid();
 v_ref text;
 v_ip text := p->>'ip_hash';
 v_email text := p->>'email_hash';
 v_email_address text := lower(trim(p->>'email'));
 v_name text := trim(p->>'name');
 v_count integer := (p->>'requested_max')::integer;
begin
 if v_ip is null or v_ip !~ '^[0-9a-f]{64}$'
 or v_email is null or v_email !~ '^[0-9a-f]{64}$'
 or v_count not between 1 and 3
 or p->>'consent_version'<>'solar-private-pilot-2026-10-13'
 or length(v_name) < 2 or length(v_name)>100
 or v_email_address !~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
 or p->>'county' is null
 or p->>'contact_method' not in ('Email','Phone','Either')
 or p->'brief' is null
 then raise exception 'Invalid private quote request'; end if;
 -- Serialize requests per IP; cap spray attempts even if email changes.
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_ip,7));
 if (select count(*) from public.solar_pilot_requests
       where ip_hash=v_ip and created_at>pg_catalog.now()-interval '1 hour') >= 4
    or (select count(*) from public.solar_pilot_requests
       where ip_hash=v_ip and created_at>pg_catalog.now()-interval '1 day') >= 10
    or (select count(*) from public.solar_pilot_requests
       where email_hash=v_email and created_at>pg_catalog.now()-interval '1 day') >= 3
 then raise exception 'Private quote request rate limited'; end if;
 v_ref := 'SOL-P-'||upper(substr(replace(v_id::text,'-',''),1,12));
 insert into public.solar_pilot_requests
 (id,reference,county,requested_max,contact_method,homeowner_name,
  homeowner_email,homeowner_phone,eircode,brief,consent_version,ip_hash,email_hash)
 values
 (v_id,v_ref,p->>'county',v_count,p->>'contact_method',v_name,
  v_email_address,nullif(p->>'phone',''),nullif(p->>'eircode',''),
  p->'brief',p->>'consent_version',v_ip,v_email);
 return pg_catalog.jsonb_build_object('ok',true,'reference',v_ref);
end
$$;
revoke all on function public.solar_submit_private_pilot(jsonb)
 from public,anon,authenticated;
grant execute on function public.solar_submit_private_pilot(jsonb) to service_role;

commit;
