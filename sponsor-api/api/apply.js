import {allowBrowser,originHeaders,readJson,normalizeApplication,verifyTurnstile,db,sendEmail,htmlSafe,json,err,catchError,failClosed} from '../lib/core.js';
export function OPTIONS(request){return new Response(null,{status:204,headers:originHeaders(request)});}
export async function POST(request){
 const cors=originHeaders(request);
 if(!allowBrowser(request))return err('Not allowed',403);
 if(!failClosed('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','TURNSTILE_SECRET','RESEND_API_KEY','MAIL_FROM','ADMIN_EMAIL'))return json({ok:false,error:'Applications are not open yet'},503,cors);
 try{
  const raw=await readJson(request);
  // Honeypot is deliberately not enough on its own.
  if(raw.website_confirm)return json({ok:true,received:true},200,cors);
  const app=normalizeApplication(raw);
  if(!await verifyTurnstile(raw.turnstileToken,request))return json({ok:false,error:'Spam check failed'},400,cors);
  const result=await db('solar_sponsor_applications',{method:'POST',body:app});
  const saved=result?.[0];
  if(!saved?.id)throw new Error('Application not saved');
  const list=app.requested_counties.map(htmlSafe).join(', ');
  try{
   await sendEmail({to:process.env.ADMIN_EMAIL,subject:'New solar sponsor application — '+app.company,html:
     '<h2>New solar sponsor founders application</h2><p><b>Company:</b> '+htmlSafe(app.company)+'</p><p><b>Contact:</b> '+htmlSafe(app.contact)+' — '+htmlSafe(app.email)+'</p><p><b>Counties:</b> '+list+'</p><p><b>Q1 2027 upfront payment on approval:</b> €'+(app.requested_counties.length*750)+' before applicable VAT</p><p><b>Next quarterly renewal:</b> 1 April 2027 (30-day cancellation notice)</p><p><b>Application ID:</b> '+saved.id+'</p>'});
  }catch(error){console.error('Owner notification failed: '+error.message);}
  try{
   await sendEmail({to:app.email,subject:'Compound Solar — application received',html:'<p>Thank you, '+htmlSafe(app.contact)+'. We received your request for '+list+'.</p><p>This is an expression of interest. Your application is free and no counties are reserved yet. Once verified, approved installers will prepay €750 per county for January–March 2027 at secure Stripe checkout; the rest of 2026 is included without an additional sponsorship fee. Quarterly renewals begin 1 April 2027 with at least 30 days written notice required before a renewal. The service and checkout are not live yet.</p><p>Compound.ie</p>'});
  }catch(error){console.error('Applicant confirmation failed: '+error.message);}
  return json({ok:true,id:saved.id,received:true},201,cors);
 }catch(error){
  if(/Invalid|valid counties|required|Spam|application|Payload|Expected/.test(error.message))return json({ok:false,error:error.message},400,cors);
  const result=catchError(error);return json(await result.json(),503,cors);
 }
}
