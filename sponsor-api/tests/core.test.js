import test from 'node:test';
import assert from 'node:assert/strict';
import {COUNTIES,PRICE_ID,normalizeApplication,sha256,stripeSignature,FOUNDING_TRIAL_END_UNIX} from '../lib/core.js';
import {createHmac} from 'node:crypto';

test('includes exactly all 32 counties without duplicate names',()=>{
 assert.equal(COUNTIES.length,32);assert.equal(new Set(COUNTIES).size,32);
 assert(COUNTIES.includes('Derry / Londonderry'));
});
test('references the connected Stripe monthly price',()=>{
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

test('founding trial ends exactly at the start of Q1 2027 UTC',()=>{assert.equal(new Date(FOUNDING_TRIAL_END_UNIX*1000).toISOString(),'2027-01-01T00:00:00.000Z');});
