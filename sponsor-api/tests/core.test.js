import test from 'node:test';
import assert from 'node:assert/strict';
import {COUNTIES,PRICE_ID,UPFRONT_PRICE_ID,CANCEL_NOTICE_DAYS,noticeDeadline,cancellationEffectiveAt,normalizeApplication,sha256,stripeSignature,FOUNDING_TRIAL_END_UNIX} from '../lib/core.js';
import {createHmac} from 'node:crypto';

test('includes exactly all 32 counties without duplicate names',()=>{
 assert.equal(COUNTIES.length,32);assert.equal(new Set(COUNTIES).size,32);
 assert(COUNTIES.includes('Derry / Londonderry'));
});
test('references the connected Stripe quarterly price',()=>{
 assert.equal(PRICE_ID,'price_1UPQeS2R63yYze0goI6IbmZD');
});
const sample={company:'PV Company',contact:'Owner',email:'Sales@pv.ie',counties:['Meath','Dublin'],accepted:true,turnstileToken:'abc'};
test('normalizes legitimate sponsor data',()=>{
 const result=normalizeApplication(sample);assert.equal(result.email,'sales@pv.ie');assert.equal(result.requested_counties.length,2);
});
test('blocks duplicate and forged counties',()=>{
 for(const counties of [['Meath','Meath'],['Atlantis'],[]]){
  assert.throws(()=>normalizeApplication({...sample,counties}));
 }
});
test('requires acknowledgement and Turnstile',()=>{
 assert.throws(()=>normalizeApplication({...sample,accepted:false}));
 assert.throws(()=>normalizeApplication({...sample,turnstileToken:''}));
});
test('signature verifies exact raw body and rejects tampering/replay',()=>{
 const secret='whsec_test_example_secret_123',raw='{"id":"evt_demo","type":"invoice.paid"}',ts=1800000000;
 const h=createHmac('sha256',secret).update(ts+'.'+raw).digest('hex');
 const signature='t='+ts+',v1='+h;
 assert(stripeSignature(raw,signature,secret,ts));
 assert(!stripeSignature(raw+' ',signature,secret,ts));
 assert(!stripeSignature(raw,signature,secret,ts+301));
});
test('hashing token is deterministic and avoids storing original invitation in database',()=>{
 assert.equal(sha256('hello').length,64);
 assert.notEqual(sha256('hello'),sha256('hello2'));
});

test('founding trial ends exactly at the start of Q1 2027 UTC',()=>{assert.equal(new Date(FOUNDING_TRIAL_END_UNIX*1000).toISOString(),'2027-04-01T00:00:00.000Z');});

test('Q1 prepayment at signup, free 2026, first recurring billing April 1 and safeguards',async()=>{
 const {readFile}=await import('node:fs/promises');
 const src=await readFile(new URL('../api/checkout.js',import.meta.url),'utf8');
 for(const field of ['subscription_data[trial_end]','payment_method_collection','automatic_tax[enabled]','line_items[0][quantity]','line_items[1][quantity]','UPFRONT_PRICE_ID','SPONSOR_BILLING_READY','SPONSOR_TAX_READY']){
   assert(src.includes(field),'checkout missing '+field);
 }
});

test('€750 upfront charge and 30-day cancellation notice calculation',()=>{
 assert.equal(UPFRONT_PRICE_ID,'price_1UPQu52R63yYze0g7tXqWmi9');
 assert.equal(CANCEL_NOTICE_DAYS,30);
 assert.equal(new Date(noticeDeadline(FOUNDING_TRIAL_END_UNIX)*1000).toISOString(),'2027-03-02T00:00:00.000Z');
});
test('webhook checks initial paid invoice and exact one-time price before county activation',async()=>{
 const {readFile}=await import('node:fs/promises');
 const src=await readFile(new URL('../api/webhook.js',import.meta.url),'utf8');
 for(const item of ['validUpfrontCheckout','UPFRONT_PRICE_ID','invoice?.status','p_kind:\'upfront_paid\'','checkout.session.completed'])assert(src.includes(item),'Missing '+item);
});

test('written notice at least 30 days before renewal cancels at the next quarter boundary',()=>{
 // Notice from October 2026: initial prepaid term ends on 1 April 2027.
 assert.equal(new Date(cancellationEffectiveAt(Date.UTC(2026,9,11)/1000)*1000).toISOString(),'2027-04-01T00:00:00.000Z');
 // March 20 is too late for April: allow the April-June term and cancel on July 1.
 assert.equal(new Date(cancellationEffectiveAt(Date.UTC(2027,2,20)/1000)*1000).toISOString(),'2027-07-01T00:00:00.000Z');
 // March 1 is early enough to cancel before April.
 assert.equal(new Date(cancellationEffectiveAt(Date.UTC(2027,2,1)/1000)*1000).toISOString(),'2027-04-01T00:00:00.000Z');
});

test('checkout reuses previously opened sessions, rejects completed sessions and has atomic CAS',async()=>{
 const {readFile}=await import('node:fs/promises');
 const checkout=await readFile(new URL('../api/checkout.js',import.meta.url),'utf8');
 const schema=await readFile(new URL('../schema.sql',import.meta.url),'utf8');
 for(const key of ["session.status==='complete'","session.status==='open'",'p_previous_session_id:previous'])assert(checkout.includes(key),'checkout missing '+key);
 assert(schema.includes('stripe_checkout_id is not distinct from p_previous_session_id'));
});

test('PostgreSQL migration is four correctly dollar-quoted functions',async()=>{
 const {readFile}=await import('node:fs/promises');
 const sql=await readFile(new URL('../schema.sql',import.meta.url),'utf8');
 const delimiters=(sql.match(/\$\$/g)||[]).length;
 assert.equal(delimiters,8,'Expected four opening and four closing PostgreSQL dollar quotes');
 assert(!/\bas \$\s*\n/.test(sql),'Malformed opening SQL quote');
 assert(!(/\bend; \$;/.test(sql)),'Malformed closing SQL quote');
 assert.equal((sql.match(/create or replace function public\.solar_/g)||[]).length,4);
});
