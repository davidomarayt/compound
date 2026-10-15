import test from 'node:test';
import assert from 'node:assert/strict';
import {createHmac} from 'node:crypto';
import {normalizeQuote,CONSENT_VERSION,PRICE_CENTS,COUNTIES,
 stripeSignature,escapeHtml,ready,paymentEnabled,intakeEnabled,digest,rest,databaseSecretReady,normalizePrivatePilot,PILOT_CONSENT_VERSION,pilotIntakeEnabled} from '../lib/core.js';

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

test('Supabase modern secret is sent in apikey header only, never bearer',async()=>{
 const prior={url:process.env.SUPABASE_URL,key:process.env.SUPABASE_SECRET_KEY,legacy:process.env.SUPABASE_SERVICE_ROLE_KEY};
 const originalFetch=globalThis.fetch;
 try{
   process.env.SUPABASE_URL='https://test-project.supabase.co';
   process.env.SUPABASE_SECRET_KEY='sb_secret_test_only_random_x1234';
   delete process.env.SUPABASE_SERVICE_ROLE_KEY;
   let captured;
   globalThis.fetch=async (_url,options)=>{captured=options.headers;return new Response('[]',{status:200,headers:{'Content-Type':'application/json'}});};
   assert.equal(databaseSecretReady(),true);
   await rest('solar_lead_teasers?select=id');
   assert.equal(captured.apikey,process.env.SUPABASE_SECRET_KEY);
   assert.equal(captured.authorization,undefined);
 }finally{
   globalThis.fetch=originalFetch;
   for(const [key,val] of Object.entries({SUPABASE_URL:prior.url,SUPABASE_SECRET_KEY:prior.key,SUPABASE_SERVICE_ROLE_KEY:prior.legacy})){
     if(val===undefined)delete process.env[key];else process.env[key]=val;
   }
 }
});
test('real Stripe charges require a separate explicit approval',()=>{
 const old={pay:process.env.SOLAR_LEADS_PAYMENTS_ENABLED,key:process.env.STRIPE_SECRET_KEY,live:process.env.SOLAR_LEADS_REAL_CHARGES_APPROVED};
 try{
   process.env.SOLAR_LEADS_PAYMENTS_ENABLED='true';
   process.env.STRIPE_SECRET_KEY='sk_live_inert_for_unit_test';
   delete process.env.SOLAR_LEADS_REAL_CHARGES_APPROVED;
   assert.equal(paymentEnabled(),false);
   process.env.STRIPE_SECRET_KEY='sk_test_inert_for_unit_test';
   assert.equal(paymentEnabled(),true);
 }finally{
   for(const [k,v] of Object.entries({SOLAR_LEADS_PAYMENTS_ENABLED:old.pay,STRIPE_SECRET_KEY:old.key,SOLAR_LEADS_REAL_CHARGES_APPROVED:old.live})){
     if(v===undefined)delete process.env[k];else process.env[k]=v;
   }
 }
});

const pilotRequest=()=>({
 county:'Meath',name:'Synthetic Test',email:'test@example.invalid',phone:'',
 requestedMax:2,contactMethod:'Email',privateConsent:true,pilotVersion:PILOT_CONSENT_VERSION,
 brief:{role:'Owner',timing:'Within 3 months',area:'Kells',building:'Detached house',notes:'Roof access issue',
  unexpectedField:'drop me'}
});
test('private pilot request never authorises installer sharing and whitelists the brief',()=>{
 const result=normalizePrivatePilot(pilotRequest());
 assert.equal(result.county,'Meath');
 assert.equal(result.requested_max,2);
 assert.equal(result.consent_version,PILOT_CONSENT_VERSION);
 assert.equal(result.brief.notes,'Roof access issue');
 assert.equal(result.brief.unexpectedField,undefined);
 assert.equal(result.consent,undefined);
 assert.equal(result.permission,undefined);
});
test('private pilot requires standalone informed consent and quote-ready authorisation',()=>{
 assert.throws(()=>normalizePrivatePilot({...pilotRequest(),privateConsent:false}),/Consent/);
 assert.throws(()=>normalizePrivatePilot({...pilotRequest(),brief:{role:'Not yet the decision-maker',timing:'Within 3 months'}}),/Only an owner/);
 assert.throws(()=>normalizePrivatePilot({...pilotRequest(),requestedMax:4}),/Select one/);
});
test('live homeowner intake rejects missing county-local details even if browser validation is bypassed',()=>{
 const missingArea=pilotRequest(); delete missingArea.brief.area;
 assert.throws(()=>normalizePrivatePilot(missingArea),/nearest town/);
 const missingProperty=pilotRequest(); delete missingProperty.brief.building;
 assert.throws(()=>normalizePrivatePilot(missingProperty),/property type/);
});
test('private pilot requires a separate launch switch',()=>{
 const value=process.env.SOLAR_PILOT_INTAKE_ENABLED;
 try{
  delete process.env.SOLAR_PILOT_INTAKE_ENABLED;
  assert.equal(pilotIntakeEnabled(),false);
  process.env.SOLAR_PILOT_INTAKE_ENABLED='true';
  assert.equal(pilotIntakeEnabled(),true);
 }finally{
  if(value===undefined)delete process.env.SOLAR_PILOT_INTAKE_ENABLED;else process.env.SOLAR_PILOT_INTAKE_ENABLED=value;
 }
});
