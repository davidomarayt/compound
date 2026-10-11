import {authorised,readJson,rpc,makeToken,sha256,sendEmail,htmlSafe,json,err,catchError,failClosed} from '../lib/core.js';
export async function POST(request){
 if(!authorised(request))return err('Unauthorized',401);
 if(process.env.SPONSOR_BILLING_READY!=='true'||process.env.SPONSOR_TAX_READY!=='true'||!failClosed('RESEND_API_KEY','MAIL_FROM','API_PUBLIC_URL','STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET'))return err('Invite email is not configured',503);
 try{
  const {applicationId}=await readJson(request);
  if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/.test(applicationId||''))return err('Invalid application ID');
  const token=makeToken(),expires=new Date(Date.now()+48*3600*1000).toISOString();
  const result=await rpc('solar_approve_application',{p_application_id:applicationId,p_invite_hash:sha256(token),p_expires:expires});
  const app=Array.isArray(result)?result[0]:result;
  if(!app?.email)throw new Error('Approval returned no application');
  const checkout=process.env.API_PUBLIC_URL.replace(/\/$/,'')+'/api/checkout?token='+encodeURIComponent(token);
  // If sending fails, preserve reservation and return an error for manual investigation.
  await sendEmail({to:app.email,subject:'Compound Solar — founding county sponsorship approved',
    html:'<p>Hello '+htmlSafe(app.contact)+',</p>'+
      '<p>We have verified and approved your requested solar sponsorship counties: <b>'+app.requested_counties.map(htmlSafe).join(', ')+'</b>.</p>'+
      '<p><b>Payment due now at checkout:</b> €'+(app.requested_counties.length*750)+
      ' plus applicable VAT. This prepays the January–March 2027 quarter; the rest of 2026 is included free once sponsorship activates.</p>'+
      '<p><b>Next automatic charge:</b> 1 April 2027 for April–June, then every three months.</p>'+
      '<p><b>Cancellation:</b> 30 days written notice before renewal; for 1 April, by 1 March 2027. The initial paid Jan–Mar term remains committed, subject to applicable refund rights and agreed service delivery.</p>'+
      '<p><a href="'+checkout+'">Review terms and pay securely with Stripe</a></p>'+
      '<p>Invitation expires after 48 hours. No guaranteed enquiry volume. We do not charge until the sponsor matching service and company verification requirements are met.</p>'});
  return json({ok:true,applicationId:app.id,expires,invitationSent:true});
 }catch(error){
  if(/County unavailable|not pending|not found/.test(error.message))return err(error.message,409);
  return catchError(error);
 }
}
