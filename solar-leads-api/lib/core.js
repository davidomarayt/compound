import { randomBytes, createHash, createHmac, timingSafeEqual } from 'node:crypto';

// No confidential values in static HTML or API responses.
export const PRICE_CENTS = 6500;
export const CONSENT_VERSION = 'solar-leads-v1-2026-10-13';
export const COUNTIES = Object.freeze(['Carlow','Cavan','Clare','Cork','Donegal','Dublin','Galway','Kerry','Kildare','Kilkenny','Laois','Leitrim','Limerick','Longford','Louth','Mayo','Meath','Monaghan','Offaly','Roscommon','Sligo','Tipperary','Waterford','Westmeath','Wexford','Wicklow']);
const allowedOrigins = new Set(['https://compound.ie','https://www.compound.ie']);

export function json(data,status=200,extra={}) {
  return Response.json(data,{status,headers:{'Cache-Control':'no-store, max-age=0','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',...extra}});
}
export function error(message,status=400){return json({ok:false,message},status);}
export function safeHeaders(request) {
  const origin=request.headers.get('origin');
  return origin && allowedOrigins.has(origin)
    ? {'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'GET,POST,OPTIONS',
       'Access-Control-Allow-Headers':'Authorization, Content-Type','Vary':'Origin','Cache-Control':'no-store'}
    : {'Vary':'Origin','Cache-Control':'no-store'};
}
export function options(request){return new Response(null,{status:204,headers:safeHeaders(request)});}
export function allowedOrigin(request){const origin=request.headers.get('origin');return !!origin && allowedOrigins.has(origin);}
export function ready(...names){return names.every(x=>typeof process.env[x]==='string' && process.env[x].length>8);}
export const paymentEnabled=()=>process.env.SOLAR_LEADS_PAYMENTS_ENABLED==='true';
export const intakeEnabled=()=>process.env.SOLAR_LEADS_INTAKE_ENABLED==='true';
export function digest(str){return createHash('sha256').update(str).digest('hex');}
export function token(){return randomBytes(32).toString('base64url');}
export function adminAuthorised(request) {
 const expected=process.env.ADMIN_API_TOKEN||'';
 const supplied=(request.headers.get('authorization')||'').replace(/^Bearer /,'');
 return expected.length>=32 && supplied.length===expected.length &&
   timingSafeEqual(Buffer.from(expected),Buffer.from(supplied));
}
export async function readJson(request,max=20000){
 if(request.headers.get('content-type')?.split(';')[0].trim()!=='application/json')throw new Error('Expected JSON');
 const text=await request.text();
 if(text.length>max)throw new Error('Payload too large');
 return JSON.parse(text);
}
export async function rest(path,method='GET',body=undefined){
 if(!ready('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'))throw new Error('Service not configured');
 const resp=await fetch(process.env.SUPABASE_URL.replace(/\/$/,'')+'/rest/v1/'+path,{
   method,
   headers:{apikey:process.env.SUPABASE_SERVICE_ROLE_KEY,
     authorization:'Bearer '+process.env.SUPABASE_SERVICE_ROLE_KEY,
     'Content-Type':'application/json','Prefer':'return=representation'},
   body:body===undefined?undefined:JSON.stringify(body)
 });
 const text=await resp.text();
 let data;try{data=text?JSON.parse(text):null;}catch{data=null;}
 if(!resp.ok)throw new Error('Storage rejected request');
 return data;
}
export async function rpc(name,args){
 const result=await rest('rpc/'+encodeURIComponent(name),'POST',args);
 return Array.isArray(result)&&result.length===1?result[0]:result;
}
export async function authenticatedInstaller(request){
 const auth=request.headers.get('authorization')||'';
 if(!/^Bearer [A-Za-z0-9._-]{60,}$/.test(auth))throw new Error('Not signed in');
 if(!ready('SUPABASE_URL','SUPABASE_PUBLISHABLE_KEY'))throw new Error('Authentication not configured');
 const response=await fetch(process.env.SUPABASE_URL.replace(/\/$/,'')+'/auth/v1/user',{
   headers:{apikey:process.env.SUPABASE_PUBLISHABLE_KEY,Authorization:auth}
 });
 if(!response.ok)throw new Error('Invalid session');
 const user=await response.json();
 if(!/^[0-9a-f-]{36}$/i.test(user.id||''))throw new Error('Invalid user');
 return user;
}
export function normalizeQuote(payload){
 if(!payload || typeof payload!=='object' || Array.isArray(payload))throw new Error('Invalid request');
 const pick=(field,max=100)=>{
   const x=payload[field];
   if(x==null)return '';
   if(typeof x!=='string'||x.length>max)throw new Error('Invalid '+field);
   return x.trim();
 };
 const county=pick('county',35);
 if(!COUNTIES.includes(county))throw new Error('Select a valid county');
 const name=pick('name',100),email=pick('email',160).toLowerCase();
 const phone=pick('phone',50),eircode=pick('eircode',12);
 const requested_max=Number(payload.requestedMax);
 const method=pick('contactMethod',15);
 if(name.length<2||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||(!phone&&method!=='Email'))throw new Error('Name, email and requested contact details are required');
 if(!Number.isInteger(requested_max)||requested_max<1||requested_max>3)throw new Error('Select one, two or three quotes');
 if(!['Email','Phone','Either'].includes(method))throw new Error('Invalid contact method');
 if(payload.consent!==true||pick('consentVersion',70)!==CONSENT_VERSION)throw new Error('Quote-sharing permission is required');
 const tokenValue=pick('turnstileToken',2000);
 if(tokenValue.length<10)throw new Error('Complete the spam check');
 const area=pick('area',70),property=pick('building',80),project=pick('project',80);
 const timeframe=pick('timing',50),battery=pick('battery',60);
 const orientation=pick('roofOrientation',40),size=payload.kwp==null||payload.kwp===''?null:Number(payload.kwp);
 if(size!==null&&(!Number.isFinite(size)||size<=0||size>100))throw new Error('Invalid system size');
 // Only whitelisted structured quote fields are accepted. No photos, documents,
 // arbitrary free-text or MPRN/meter ID should be stored in public listings.
 const brief={};
 for(const field of ['area','role','building','project','timing','budget','protected','roof',
   'faces','azimuth','pitch','azimuth2','pitch2','areaM2','areaM22','material','shade',
   'obstacles','roofCondition','storeys','access','demand','bill','daytime','smartMeter',
   'phase','board','ev','heatPump','immersion','existingPV','kwp','battery',
   'batteryKwh','evCharger','diverter','backup','grant','finance','existingQuotes']){
   const v=payload.brief?.[field];
   if(typeof v==='string' && v.length<=160)brief[field]=v.trim();
   else if(typeof v==='number' && Number.isFinite(v))brief[field]=v;
 }
 return {
   teaser:{county,
     // Rural areas may pinpoint properties; hold location at county until reviewed.
     area_general:null,property_type:property,project_type:project,system_kwp:size,
     roof_orientation:orientation,battery_preference:battery,
     installation_timeframe:timeframe},
   privateData:{name,email,phone,eircode,brief:{...brief,area}},
   permission:{requested_max,consent:true,wording_version:CONSENT_VERSION,privacy_version:'2026-10-13',contact_method:method},
   turnstileToken:tokenValue
 };
}
export async function verifyTurnstile(value) {
 if(!ready('TURNSTILE_SECRET'))throw new Error('Spam protection not configured');
 const data=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{
   method:'POST',
   body:new URLSearchParams({secret:process.env.TURNSTILE_SECRET,response:value})
 });
 if(!data.ok)return false;
 const result=await data.json();
 return !!result.success && (!result.hostname || ['compound.ie','www.compound.ie'].includes(result.hostname));
}
export async function sendEmail({to,subject,html}){
 if(!ready('RESEND_API_KEY','MAIL_FROM'))throw new Error('Email not configured');
 const resp=await fetch('https://api.resend.com/emails',{
   method:'POST',headers:{Authorization:'Bearer '+process.env.RESEND_API_KEY,'Content-Type':'application/json'},
   body:JSON.stringify({from:process.env.MAIL_FROM,to:[to],subject,html})
 });
 if(!resp.ok)throw new Error('Email delivery unavailable');
}
export function escapeHtml(str){
 return String(str).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
export function stripeSignature(raw,signature,secret,nowSeconds=Math.floor(Date.now()/1000)){
 if(!signature||!secret)return false;
 const parts=Object.fromEntries(signature.split(',').map(part=>part.trim().split('=')));
 const stamp=Number(parts.t);
 if(!Number.isInteger(stamp)||Math.abs(nowSeconds-stamp)>300)return false;
 const expected=createHmac('sha256',secret).update(stamp+'.'+raw).digest('hex');
 const actual=parts.v1||'';
 if(!/^[a-f0-9]{64}$/.test(actual))return false;
 return timingSafeEqual(Buffer.from(expected,'hex'),Buffer.from(actual,'hex'));
}
export async function stripe(path,form,method='POST',key=null){
 if(!ready('STRIPE_SECRET_KEY'))throw new Error('Stripe not configured');
 const headers={'Authorization':'Bearer '+process.env.STRIPE_SECRET_KEY};
 if(form)headers['Content-Type']='application/x-www-form-urlencoded';
 if(key)headers['Idempotency-Key']=key;
 const resp=await fetch('https://api.stripe.com/v1/'+path,{method,headers,body:form?.toString()});
 let body;try{body=await resp.json();}catch{body=null;}
 if(!resp.ok)throw new Error('Payment provider request rejected');
 return body;
}
