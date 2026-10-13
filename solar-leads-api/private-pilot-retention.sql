-- Daily data minimisation for private homeowner pilot requests.
-- Permanently delete raw contact details after 90 days.
create extension if not exists pg_cron with schema pg_catalog;
grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;
select cron.schedule(
 'compound-solar-pilot-retain-90-days',
 '20 2 * * *',
 'delete from public.solar_pilot_requests where created_at < now() - interval ''90 days'';'
);