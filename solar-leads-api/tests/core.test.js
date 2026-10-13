import test from 'node:test';
import assert from 'node:assert/strict';
import {createHmac} from 'node:crypto';
import {normalizeQuote,CONSENT_VERSION,PRICE_CENTS,COUNTIES,
 stripeSignature,escapeHtml,ready,paymentEnabled,intakeEnabled,digest} from '../lib/core.js';

const valid=()=>({
 county:'Meath',name:'Test Homeowner',email:'sample@example.invalid',phone:'0871111111',
 requestedMax:2,contactMethod:'Email',consent:true,consentVersion:CONSENT_VERSION,
 turnstileToken:'example-bot-challenge-token-long-enough',area:'Kells',
 building:'Detached house',project:'Rooftop PV',roofOrientation:'SW',kwp:6,
 battery:'Compare options',timing:'Within 3 months',
 brief:{role:'Owner',azimuth:'225',pitch:'35',battery:'Quote both',name:'Unexpected field',demand:'6200'}
});
test('price and installer maximum are fixed',()=>{
 assert.equal(PRICE_CENTS,6500);assert.equal(COUNTIES.length,26);
 assert.equal(normalizeQuote(valid()).permission.requested_max,2);
});
test('PII never appears in anonymous teaser',()=>{
 const v=normalizeQuote(valid());
 assert.equal(v.teaser.county,'Meath');
 assert.equal(v.teaser.area_general,null);
 assert.equal(JSON.stringify(v.teaser).includes('Test Homeowner'),false);
 assert.equal(JSON.stringify(v.teaser).includes('sample@example.invalid'),false);
 assert.equal(v.privateData.brief.name,undefined);
});
test('rejects missing opt-in, stale version and invalid slot requests',()=>{
 const a=valid();a.consent=false;assert.throws(()=>normalizeQuote(a),/permission/);
 const b=valid();b.consentVersion='old';assert.throws(()=>normalizeQuote(b),/permission/);
 const c=valid();c.requestedMax=4;assert.throws(()=>normalizeQuote(c),/three/);
 const d=valid();d.requestedMax=0;assert.throws(()=>normalizeQuote(d),/three/);
 const e=valid();e.county='Timbuktu';assert.throws(()=>normalizeQuote(e),/county/);
});
test('technical fields are optional; photos and MPRNs never enter brief',()=>{
 const a=valid();delete a.kwp;a.brief={role:'Owner'};
 const result=normalizeQuote(a);
 assert.equal(result.teaser.system_kwp,null);
 assert.deepEqual(result.privateData.brief,{role:'Owner',area:'Kells'});
 const b=valid();b.brief={role:'Owner',photoRoof:'private.png',MPRN:'12345',demand:7500};
 assert.deepEqual(normalizeQuote(b).privateData.brief,{role:'Owner',demand:7500,area:'Kells'});
});
test('Stripe signature is checked against raw body and timestamp',()=>{
 const body='{"id":"evt_test","type":"checkout.session.completed"}',secret='whsec_example';
 const now=1781359500;
 const signature=createHmac('sha256',secret).update(now+'.'+body).digest('hex');
 const header='t='+now+',v1='+signature;
 assert.equal(stripeSignature(body,header,secret,now),true);
 assert.equal(stripeSignature(body+'x',header,secret,now),false);
 assert.equal(stripeSignature(body,header,secret,now+301),false);
 assert.equal(stripeSignature(body,'t='+now+',v1=notvalid',secret,now),false);
});
test('HTML-safe confirmation and feature flag fail-closed',()=>{
 assert.equal(escapeHtml('<x a="b">'), '&lt;x a=&quot;b&quot;&gt;');
 assert.equal(ready('A_NONEXISTENT_ENV_VARIABLE'),false);
 assert.equal(paymentEnabled(),false);
 assert.equal(intakeEnabled(),false);
 assert.equal(digest('same'),digest('same'));
});

test('only authorised quote-ready homeowners create saleable requests',()=>{
 const a=valid();a.brief.role='Not yet the decision-maker';
 assert.throws(()=>normalizeQuote(a),/owners or authorised/);
 const b=valid();b.timing='Researching options';
 assert.throws(()=>normalizeQuote(b),/quote-ready/);
});
