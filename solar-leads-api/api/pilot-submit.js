import {createHmac} from 'node:crypto';
import {json,ready,pilotIntakeEnabled,databaseSecretReady,readJson,normalizePrivatePilot,
 allowedOrigin,safeHeaders,options,rpc} from '../lib/core.js';
export function OPTIONS(request){return options(request);}
export async function POST(request){
 const headers=safeHeaders(request);
 if(!allowedOrigin(request))return json({ok:false,message:'Not allowed'},403,headers);
 if(!pilotIntakeEnabled()||!databaseSecretReady())return json({ok:false,message:'Private project submissions are temporarily unavailable'},503,headers);
 try {
   const raw=await readJson(request,16000);
   // Silent rejection of automated form fills. No data is stored.
   if(typeof raw.website==='string' && raw.website.trim())return json({ok:true,message:'Thank you.'},202,headers);
   const p=normalizePrivatePilot(raw);
   const pepper=process.env.SUPABASE_SECRET_KEY||process.env.SUPABASE_SERVICE_ROLE_KEY;
   const hash=x=>createHmac('sha256',pepper).update(x).digest('hex');
   // Rate-limit by server-observed IP; never trust a browser-supplied fingerprint.
   const ip=(request.headers.get('x-vercel-forwarded-for')||
      request.headers.get('x-forwarded-for')||'unknown').split(',')[0].trim().slice(0,80);
   const created=await rpc('solar_submit_private_pilot',{
     p:{...p,ip_hash:hash(ip),email_hash:hash(p.email)}
   });
   if(!created?.reference)throw Error('Storage unavailable');
   return json({ok:true,reference:created.reference,message:'Project received for private Compound Solar review. No installer has access.'},201,headers);
 }catch(err){
   const message=String(err?.message||'');
   const invalid=/^(Invalid|Select|Name and|Consent|Only an owner)/.test(message);
   return json({ok:false,message:invalid?message:'Unable to accept your project right now. Please try again later.'},invalid?400:503,headers);
 }
}
