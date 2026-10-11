import { createHmac, createHash, timingSafeEqual, randomBytes } from 'node:crypto';

export const COUNTIES = Object.freeze(["Carlow","Cavan","Clare","Cork","Donegal","Dublin","Galway","Kerry","Kildare","Kilkenny","Laois","Leitrim","Limerick","Longford","Louth","Mayo","Meath","Monaghan","Offaly","Roscommon","Sligo","Tipperary","Waterford","Westmeath","Wexford","Wicklow","Antrim","Armagh","Derry / Londonderry","Down","Fermanagh","Tyrone"]);
export const PRICE_ID = 'price_1UPQ3s2R63yYze0g066vmFgW';
export const BASE_URL = 'https://compound.ie/solar/for-installers/';

export function json(data, status=200, headers={}) {
  return Response.json(data, {status,headers:{"Cache-Control":"no-store",...headers}});
}
export function err(message,status=400){return json({ok:false,error:message},status);}
export function failClosed(...vars) {
  return vars.every(v=>typeof process.env[v]==='string'&&process.env[v].length>5);
}
export function originHeaders(request) {
  const origin=request.headers.get('origin')||'';
  const approved=origin==='https://compound.ie'||origin==='https://www.compound.ie';
  return approved?{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Vary':'Origin'}:{'Vary':'Origin'};
}
export function allowBrowser(request){
  const origin=request.headers.get('origin');
  return origin==='https://compound.ie'||origin==='https://www.compound.ie';
}
export async function readJson(request) {
  if(request.headers.get('content-type')?.split(';')[0]?.trim()!=='application/json')throw new Error('Expected application/json');
  if(Number(request.headers.get('content-length')||0)>18000)throw new Error('Payload too large');
  const body=await request.text();if(body.length>18000)throw new Error('Payload too large');
  return JSON.parse(body);
}
export function normalizeApplication(v){
  if(!v||typeof v!=='object'||Array.isArray(v))throw new Error('Invalid application');
  const trim=(key,max)=>{const s=v[key];if(s===null||s===undefined)return '';if(typeof s!=='string'||s.length>max*2)throw new Error('Invalid '+key);return s.trim().slice(0,max);};
  const company=trim('company',120),contact=trim('contact',100),email=trim('email',160).toLowerCase(),phone=trim('phone',50),website=trim('website',180),accreditation=trim('accreditation',100),notes=trim('notes',450);
  const counties=v.counties;
  if(!company||!contact||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))throw new Error('Company, contact and valid business email required');
  if(!Array.isArray(counties)||counties.length<1||counties.length>32||new Set(counties).size!==counties.length||counties.some(c=>!COUNTIES.includes(c)))throw new Error('Select valid counties');
  if(v.accepted!==true)throw new Error('Application acknowledgement required');
  if(!v.turnstileToken||typeof v.turnstileToken!=='string')throw new Error('Spam check required');
  return {company,contact,email,phone,website,accreditation,notes,requested_counties:counties};
}
export async function verifyTurnstile(token,request){
  if(!failClosed('TURNSTILE_SECRET'))throw new Error('Spam protection not configured');
  const body=new URLSearchParams({secret:process.env.TURNSTILE_SECRET,response:token});
  const result=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',body});
  if(!result.ok)return false;
  const data=await result.json();
  return !!data.success&&(!data.hostname||['compound.ie','www.compound.ie'].includes(data.hostname));
}
export async function db(path,{method='GET',body,headers={}}={}){
  if(!failClosed('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'))throw new Error('Database not configured');
  const url=process.env.SUPABASE_URL.replace(/\/$/,'')+'/rest/v1/'+path;
  const result=await fetch(url,{method,headers:{
    apikey:process.env.SUPABASE_SERVICE_ROLE_KEY,
    authorization:'Bearer '+process.env.SUPABASE_SERVICE_ROLE_KEY,
    'Content-Type':'application/json',
    Prefer:method==='POST'?'return=representation':'',
    ...headers
  },body:body===undefined?undefined:JSON.stringify(body)});
  const text=await result.text();
  let data;try{data=text?JSON.parse(text):null;}catch{data=text;}
  if(!result.ok)throw new Error('Database request failed: '+result.status+' '+(data?.code||''));
  return data;
}
export async function rpc(name,args){return db('rpc/'+name,{method:'POST',body:args});}
export function sha256(str){return createHash('sha256').update(str).digest('hex');}
export function makeToken(){return randomBytes(32).toString('base64url');}
export function authorised(request){
  const provided=request.headers.get('authorization')||'';
  const expected=process.env.ADMIN_API_TOKEN||'';
  if(expected.length<32||!provided.startsWith('Bearer '))return false;
  const actual=provided.slice(7);
  return actual.length===expected.length&&timingSafeEqual(Buffer.from(actual),Buffer.from(expected));
}
export async function sendEmail({to,subject,html}){
  if(!failClosed('RESEND_API_KEY','MAIL_FROM'))throw new Error('Mail not configured');
  const response=await fetch('https://api.resend.com/emails',{method:'POST',headers:{
    Authorization:'Bearer '+process.env.RESEND_API_KEY,'Content-Type':'application/json'
  },body:JSON.stringify({from:process.env.MAIL_FROM,to:[to],subject,html})});
  if(!response.ok)throw new Error('Email service error '+response.status);
  return response.json();
}
export function htmlSafe(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
export async function stripe(path,form,method='POST'){
  if(!failClosed('STRIPE_SECRET_KEY'))throw new Error('Stripe credentials not configured');
  const response=await fetch('https://api.stripe.com/v1/'+path,{method,headers:{
    Authorization:'Bearer '+process.env.STRIPE_SECRET_KEY,
    ...(method==='POST'?{'Content-Type':'application/x-www-form-urlencoded'}:{})
  },body:method==='POST'?form?.toString():undefined});
  const data=await response.json();
  if(!response.ok)throw new Error('Stripe request failed '+response.status+': '+(data.error?.code||'unknown'));
  return data;
}
export function stripeSignature(body,signature,secret,now=Math.floor(Date.now()/1000)){
  const ts=/\bt=(\d+)/.exec(signature||'')?.[1];
  const values=[...(signature||'').matchAll(/(?:^|,)v1=([a-f0-9]{64})(?:,|$)/g)].map(x=>x[1]);
  if(!ts||Math.abs(now-Number(ts))>300||values.length===0)return false;
  const expected=createHmac('sha256',secret).update(ts+'.'+body).digest('hex');
  return values.some(value=>timingSafeEqual(Buffer.from(expected,'hex'),Buffer.from(value,'hex')));
}
export const catchError=(error)=>{console.error(error?.message||'Unexpected error');return err('Service temporarily unavailable',503);};
