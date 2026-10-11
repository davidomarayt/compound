import {authorised,readJson,db,stripe,cancellationEffectiveAt,json,err,catchError,sendEmail,htmlSafe,failClosed} from '../lib/core.js';

// Admin-only processing of a written installer cancellation notice.
// Customer self-service must verify ownership before using any of this logic.
export async function POST(request){
 if(!authorised(request))return err('Unauthorized',401);
 if(process.env.SPONSOR_BILLING_READY!=='true'||!failClosed('STRIPE_SECRET_KEY','SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'))return err('Billing not available',503);
 try{
  const input=await readJson(request);
  const applicationId=input?.applicationId;
  if(typeof applicationId!=='string'||!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/.test(applicationId))return err('Invalid application ID');
  const receivedAt=input?.noticeReceivedAt?Date.parse(input.noticeReceivedAt):Date.now();
  const now=Date.now();
  if(!Number.isFinite(receivedAt)||receivedAt>now||now-receivedAt>31*86400000)return err('Notice date must be within the last 31 days and not in the future',422);
  const apps=await db('solar_sponsor_applications?id=eq.'+encodeURIComponent(applicationId)+'&select=id,email,company,stripe_subscription_id,status&limit=1');
  const app=apps?.[0];
  if(!app?.stripe_subscription_id||!['active','paused'].includes(app.status))return err('No active sponsorship found',404);
  const sub=await stripe('subscriptions/'+encodeURIComponent(app.stripe_subscription_id),null,'GET');
  if(sub.metadata?.solar_application_id!==app.id)return err('Subscription mapping mismatch',409);
  if(sub.status==='canceled')return err('Already cancelled',409);
  const effectiveAt=cancellationEffectiveAt(Math.floor(receivedAt/1000));
  if(sub.cancel_at&&Number(sub.cancel_at)<=effectiveAt)return json({ok:true,alreadyScheduled:true,effectiveAt:new Date(sub.cancel_at*1000).toISOString()});
  const form=new URLSearchParams({cancel_at:String(effectiveAt)});
  const result=await stripe('subscriptions/'+encodeURIComponent(sub.id),form);
  if(Number(result.cancel_at)!==effectiveAt)throw new Error('Stripe cancellation scheduling was not confirmed');
  await db('solar_sponsor_applications?id=eq.'+encodeURIComponent(app.id),{
    method:'PATCH',body:{cancellation_requested_at:new Date(receivedAt).toISOString()}
  });
  try{
   await sendEmail({to:app.email,subject:'Compound Solar — subscription cancellation scheduled',
    html:'<p>Your written cancellation notice has been processed.</p><p>Company: '+htmlSafe(app.company)+
     '</p><p>Your sponsorship will end on '+htmlSafe(new Date(effectiveAt*1000).toISOString().slice(0,10))+
     ' (UTC), and scheduled quarterly renewals cease from that date. Previously paid subscription periods are not automatically refunded; any applicable refund rights or service-delivery remedies remain unaffected.</p>'});
  }catch(e){console.error('Cancellation notice email delivery failed',e.message);}
  return json({ok:true,effectiveAt:new Date(effectiveAt*1000).toISOString(),stripeSubscriptionId:sub.id});
 }catch(error){return catchError(error);}
}
