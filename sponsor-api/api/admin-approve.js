import {authorised,readJson,rpc,makeToken,sha256,sendEmail,htmlSafe,json,err,catchError,failClosed} from '../lib/core.js';
export async function POST(request){
 if(!authorised(request))return err('Unauthorized',401);
 if(!failClosed('RESEND_API_KEY','MAIL_FROM','API_PUBLIC_URL'))return err('Invite email is not configured',503);
 try{
  const {applicationId}=await readJson(request);
  if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/.test(applicationId||''))return err('Invalid application ID');
  const token=makeToken(),expires=new Date(Date.now()+48*3600*1000).toISOString();
  const result=await rpc('solar_approve_application',{p_application_id:applicationId,p_invite_hash:sha256(token),p_expires:expires});
  const app=Array.isArray(result)?result[0]:result;
  if(!app?.email)throw new Error('Approval returned no application');
  const checkout=process.env.API_PUBLIC_URL.replace(/\/$/,'')+'/api/checkout?token='+encodeURIComponent(token);
  // If sending fails, preserve reservation and return an error for manual investigation.
  await sendEmail({to:app.email,subject:'Compound Solar — your sponsorship counties are approved',
    html:'<p>Hello '+htmlSafe(app.contact)+',</p><p>Your Compound Solar county application has been approved for: <b>'+app.requested_counties.map(htmlSafe).join(', ')+'</b>.</p><p>Price: €'+(app.requested_counties.length*250)+' per month before applicable VAT.</p><p><a href="'+checkout+'">Complete secure Stripe subscription checkout</a></p><p>The private checkout invitation expires after 48 hours. County exclusivity begins only after successful payment and verification. No minimum lead volume is guaranteed.</p>'});
  return json({ok:true,applicationId:app.id,expires,invitationSent:true});
 }catch(error){
  if(/County unavailable|not pending|not found/.test(error.message))return err(error.message,409);
  return catchError(error);
 }
}
