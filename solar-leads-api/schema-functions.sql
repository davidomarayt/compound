-- Apply docs/sql/solar-installer-portal-schema.sql FIRST, then this file.
-- Deployment requires a dedicated Supabase project owned by Compound.
-- No real users, Stripe charges or leads are created by this migration.

begin;

alter table public.solar_lead_teasers
  add column if not exists verified_at timestamptz;
alter table public.solar_lead_teasers
  add column if not exists permission_version text;

create table if not exists compound_private.solar_email_verifications (
  project_id uuid primary key references public.solar_lead_teasers(id) on delete restrict,
  token_digest text not null unique check (token_digest ~ '^[0-9a-f]{64}$'),
  expires_at timestamptz not null,
  used_at timestamptz
);
create table if not exists compound_private.solar_stripe_events (
  event_id text primary key,
  handled_at timestamptz not null default now(),
  outcome text not null
);
revoke all on compound_private.solar_email_verifications,
  compound_private.solar_stripe_events from public, anon, authenticated;
alter table compound_private.solar_email_verifications enable row level security;
alter table compound_private.solar_stripe_events enable row level security;

-- Revoke default public EXECUTE on functions; only the server's service role
-- can create listings / reserve inventory / grant paid access.
create or replace function public.solar_create_quote(
  p_teaser jsonb, p_private jsonb, p_permission jsonb, p_token_digest text
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare
  v_id uuid := gen_random_uuid();
  v_max smallint := (p_permission->>'requested_max')::smallint;
  v_sku text;
begin
  if v_max not between 1 and 3
     or p_permission->>'consent' <> 'true'
     or p_permission->>'wording_version' is null
     or p_permission->>'privacy_version' is null
     or p_private->>'name' is null
     or p_private->>'email' is null
     or p_teaser->>'county' is null
     or p_token_digest !~ '^[0-9a-f]{64}$'
  then raise exception 'Invalid quote request'; end if;

  v_sku := 'SOL-' || upper(substr(replace(v_id::text,'-',''),1,14));
  insert into public.solar_lead_teasers
   (id,sku,county,area_general,property_type,project_type,system_kwp,
    roof_orientation,battery_preference,installation_timeframe,
    max_introductions,price_cents,status,permission_version,expires_at)
  values
   (v_id,v_sku,p_teaser->>'county',p_teaser->>'area_general',
    p_teaser->>'property_type',p_teaser->>'project_type',
    nullif(p_teaser->>'system_kwp','')::numeric,
    p_teaser->>'roof_orientation',p_teaser->>'battery_preference',
    p_teaser->>'installation_timeframe',v_max,6500,'pending_review',
    p_permission->>'wording_version',now()+interval '30 days');

  insert into public.solar_lead_details
   (project_id,homeowner_name,homeowner_email,homeowner_phone,eircode,brief)
  values (v_id,p_private->>'name',p_private->>'email',p_private->>'phone',
          p_private->>'eircode',coalesce(p_private->'brief','{}'::jsonb));

  insert into compound_private.solar_homeowner_permissions
   (project_id,requested_max,affirmative_opt_in,wording_version,
    privacy_notice_version,permitted_contact_method)
  values (v_id,v_max,true,p_permission->>'wording_version',
          p_permission->>'privacy_version',p_permission->>'contact_method');

  insert into compound_private.solar_email_verifications
   (project_id,token_digest,expires_at)
  values(v_id,p_token_digest,now()+interval '48 hours');

  return jsonb_build_object('project_id',v_id,'sku',v_sku,'status','pending_verification');
end
$$;

create or replace function public.solar_confirm_email(
  p_project_id uuid, p_token_digest text
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare v_token compound_private.solar_email_verifications%rowtype;
begin
  select * into v_token from compound_private.solar_email_verifications
  where project_id=p_project_id for update;
  if not found or v_token.token_digest<>p_token_digest or v_token.expires_at<now()
     then raise exception 'Invalid or expired verification'; end if;
  if v_token.used_at is null then
    update compound_private.solar_email_verifications set used_at=now()
      where project_id=p_project_id;
    update public.solar_lead_teasers set verified_at=now(),status='active'
      where id=p_project_id and status='pending_review' and expires_at>now()
        and exists (
          select 1 from compound_private.solar_homeowner_permissions p
          where p.project_id=p_project_id and p.withdrawn_at is null
        );
  end if;
  return jsonb_build_object('status','verified');
end
$$;

-- Transactional reservation serializes all purchasers by locking the project.
-- expired slots are reclaimed before checking available inventory.
create or replace function public.solar_reserve_introduction(
  p_project_id uuid,p_user_id uuid
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare
  v_project public.solar_lead_teasers%rowtype;
  v_installer public.solar_installer_accounts%rowtype;
  v_order public.solar_lead_purchases%rowtype;
  v_n int;
begin
  select * into v_project from public.solar_lead_teasers
    where id=p_project_id for update;
  if not found then raise exception 'Project unavailable'; end if;

  select * into v_installer from public.solar_installer_accounts
    where owner_user_id=p_user_id and verification_status='approved';
  if not found or not v_project.county=any(v_installer.service_counties)
     then raise exception 'Installer not authorised'; end if;

  -- Clean up checkout reservations older than 40m; a paid but delayed
  -- webhook can never unlock a reclaimed slot, and must be refunded.
  update public.solar_lead_purchases set status='expired'
    where project_id=p_project_id and status='reserved'
      and created_at<now()-interval '40 minutes';
  get diagnostics v_n = row_count;
  if v_n>0 then
    update public.solar_lead_teasers set reserved_count=reserved_count-v_n
      where id=p_project_id;
  end if;

  if v_project.status<>'active' or v_project.expires_at<=now()
     or v_project.verified_at is null
     or not exists (
       select 1 from compound_private.solar_homeowner_permissions p
       where p.project_id=p_project_id and p.affirmative_opt_in
         and p.withdrawn_at is null
     )
     then raise exception 'Project no longer open'; end if;

  select * into v_order from public.solar_lead_purchases
    where project_id=p_project_id and installer_id=v_installer.id for update;
  if found and v_order.status in ('reserved','paid','access_granted','refunded')
     then raise exception 'Already purchased or reserved'; end if;
  if (select sold_count+reserved_count from public.solar_lead_teasers where id=p_project_id)
       >= v_project.max_introductions
     then raise exception 'No introduction slots left'; end if;

  if found then
    update public.solar_lead_purchases
      set status='reserved',stripe_checkout_session_id=null,
          stripe_payment_intent_id=null,created_at=now(),
          amount_cents=v_project.price_cents,purchased_at=null
      where id=v_order.id returning * into v_order;
  else
    insert into public.solar_lead_purchases
      (project_id,installer_id,amount_cents,status)
    values (p_project_id,v_installer.id,v_project.price_cents,'reserved')
    returning * into v_order;
  end if;
  update public.solar_lead_teasers set reserved_count=reserved_count+1
    where id=p_project_id;

  return jsonb_build_object('order_id',v_order.id,'sku',v_project.sku,
          'price_cents',v_project.price_cents,'project_id',p_project_id);
end
$$;

create or replace function public.solar_attach_checkout(
  p_order_id uuid,p_checkout_id text
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare v_order public.solar_lead_purchases%rowtype;
begin
  if p_checkout_id !~ '^cs_(test|live)_' then raise exception 'Invalid checkout id'; end if;
  update public.solar_lead_purchases
    set stripe_checkout_session_id=p_checkout_id
    where id=p_order_id and status='reserved' and stripe_checkout_session_id is null
    returning * into v_order;
  if not found then raise exception 'Reservation not available'; end if;
  return jsonb_build_object('status','reserved','order_id',v_order.id);
end
$$;

create or replace function public.solar_cancel_reservation(
  p_order_id uuid
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare v_order public.solar_lead_purchases%rowtype;
        v_project_id uuid;
begin
  select project_id into v_project_id from public.solar_lead_purchases where id=p_order_id;
  if not found then return jsonb_build_object('cancelled',false); end if;
  perform 1 from public.solar_lead_teasers where id=v_project_id for update;
  select * into v_order from public.solar_lead_purchases where id=p_order_id for update;
  if v_order.status<>'reserved' then return jsonb_build_object('cancelled',false); end if;
  update public.solar_lead_purchases set status='cancelled' where id=p_order_id;
  update public.solar_lead_teasers set reserved_count=reserved_count-1
    where id=v_order.project_id;
  return jsonb_build_object('cancelled',true);
end
$$;

-- Idempotent paid release, with explicit blocking of withdrawn permission,
-- expired listings and unexpected amount/currency.
create or replace function public.solar_complete_checkout(
  p_order_id uuid,p_checkout_id text,p_payment_intent_id text,
  p_amount_cents integer,p_currency text,p_stripe_event_id text
) returns jsonb language plpgsql security definer set search_path = ''
as $$
declare
  v_order public.solar_lead_purchases%rowtype;
  v_teaser public.solar_lead_teasers%rowtype;
  v_project_id uuid;
begin
  select project_id into v_project_id from public.solar_lead_purchases where id=p_order_id;
  if not found then return jsonb_build_object('released',false,'reason','order_not_found'); end if;
  select * into v_teaser from public.solar_lead_teasers
    where id=v_project_id for update;
  select * into v_order from public.solar_lead_purchases
    where id=p_order_id for update;
  if not found or v_order.stripe_checkout_session_id is distinct from p_checkout_id
    then return jsonb_build_object('released',false,'reason','order_not_found'); end if;

  if v_order.status='access_granted' then
    return jsonb_build_object('released',true,'already_processed',true,'project_id',v_order.project_id);
  end if;

  if v_order.status<>'reserved'
    or v_teaser.status<>'active'
    or v_teaser.expires_at<=now()
    or v_teaser.verified_at is null
    or lower(p_currency)<>'eur'
    or p_amount_cents<>v_order.amount_cents
    or not exists (
      select 1 from compound_private.solar_homeowner_permissions p
       where p.project_id=v_order.project_id and p.withdrawn_at is null
    )
  then
    return jsonb_build_object('released',false,'reason','not_authorised_or_expired');
  end if;

  update public.solar_lead_purchases
    set status='access_granted',stripe_payment_intent_id=p_payment_intent_id,
      purchased_at=now() where id=v_order.id;
  update public.solar_lead_teasers
    set reserved_count=reserved_count-1,sold_count=sold_count+1,
        status=(case when sold_count+1=max_introductions then 'sold_out' else status end)
    where id=v_order.project_id;
  insert into compound_private.solar_release_events(project_id,installer_id,purchase_id)
  values(v_order.project_id,v_order.installer_id,v_order.id)
  on conflict(purchase_id) do nothing;

  insert into compound_private.solar_stripe_events(event_id,outcome)
  values(p_stripe_event_id,'released')
  on conflict(event_id) do nothing;

  return jsonb_build_object('released',true,'already_processed',false,'project_id',v_order.project_id);
end
$$;

create or replace function public.solar_mark_homeowner_notified(p_order_id uuid)
returns void language plpgsql security definer set search_path = ''
as $$
begin
  update compound_private.solar_release_events set homeowner_notified_at=now()
    where purchase_id=p_order_id and homeowner_notified_at is null;
end
$$;

-- Simple manual email-request workflow: Compound staff validates the
-- homeowner's identity, then closes all unsold slots immediately.
create or replace function public.solar_withdraw_quote(p_project_id uuid)
returns jsonb language plpgsql security definer set search_path = ''
as $
declare v_project public.solar_lead_teasers%rowtype;
        v_num integer;
begin
  select * into v_project from public.solar_lead_teasers
  where id=p_project_id for update;
  if not found then raise exception 'Project not found'; end if;
  update compound_private.solar_homeowner_permissions
    set withdrawn_at=coalesce(withdrawn_at,now())
    where project_id=p_project_id;
  update public.solar_lead_purchases set status='cancelled'
    where project_id=p_project_id and status='reserved';
  get diagnostics v_num = row_count;
  update public.solar_lead_teasers
    set reserved_count=0,status='closed' where id=p_project_id;
  return jsonb_build_object('closed',true,'cancelled_reservations',v_num);
end
$;

-- Suppress all PUBLIC invoker access to administrative RPC operations.
revoke all on function public.solar_withdraw_quote(uuid) from public,anon,authenticated;
revoke all on function public.solar_create_quote(jsonb,jsonb,jsonb,text) from public,anon,authenticated;
revoke all on function public.solar_confirm_email(uuid,text) from public,anon,authenticated;
revoke all on function public.solar_reserve_introduction(uuid,uuid) from public,anon,authenticated;
revoke all on function public.solar_attach_checkout(uuid,text) from public,anon,authenticated;
revoke all on function public.solar_cancel_reservation(uuid) from public,anon,authenticated;
revoke all on function public.solar_complete_checkout(uuid,text,text,integer,text,text) from public,anon,authenticated;
revoke all on function public.solar_mark_homeowner_notified(uuid) from public,anon,authenticated;
grant execute on function public.solar_withdraw_quote(uuid) to service_role;
grant execute on function public.solar_create_quote(jsonb,jsonb,jsonb,text) to service_role;
grant execute on function public.solar_confirm_email(uuid,text) to service_role;
grant execute on function public.solar_reserve_introduction(uuid,uuid) to service_role;
grant execute on function public.solar_attach_checkout(uuid,text) to service_role;
grant execute on function public.solar_cancel_reservation(uuid) to service_role;
grant execute on function public.solar_complete_checkout(uuid,text,text,integer,text,text) to service_role;
grant execute on function public.solar_mark_homeowner_notified(uuid) to service_role;

commit;
