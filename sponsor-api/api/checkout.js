import {rpc,sha256,stripe,PRICE_ID,UPFRONT_PRICE_ID,BASE_URL,FOUNDING_TRIAL_END_UNIX,err,catchError,failClosed} from '../lib/core.js';
export async function GET(request){
 // Public paid checkout must never run without the fully operational CRM, county lock,
 // tax configuration and Stripe webhook. The static application form stays separate.
 if(process.env.SPONSOR_BILLING_READY!=='true'||process.env.SPONSOR_TAX_READY!=='true'||!failClosed('STRIPE_SECRET_KEY','SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','STRIPE_WEBHOOK_SECRET'))return err('Checkout not yet available',503);
 const token=new URL(request.url).searchParams.get('token')||'';
 if(!/^[A-Za-z0-9_-]{40,80}$/.test(token))return err('Invalid or expired invitation',400);
 const now=Math.floor(Date.now()/1000);
 if(now>=Date.UTC(2027,0,1)/1000)return err('2026 founding offer closed. Request current terms from Compound.',410);
 try{
  const result=await rpc('solar_get_invite',{p_invite_hash:sha256(token)});
  const app=Array.isArray(result)?result[0]:result;
  if(!app||!app.id)return err('Invitation expired or county no longer available',409);
  // Reuse the existing open Checkout rather than creating competing sessions.
  // A completed Checkout must never be replayed to sell the same county twice.
  const previous=app.stripe_checkout_id||null;
  if(previous){
   const session=await stripe('checkout/sessions/'+encodeURIComponent(previous),null,'GET');
   if(session.status==='complete')return err('This invitation has already been used',409);
   if(session.status==='open'&&Number(session.expires_at)>now&&session.client_reference_id===app.id){
     return Response.redirect(session.url,303);
   }
   if(session.status==='open')return err('Existing checkout needs administrator review',409);
   if(session.status!=='expired')return err('Existing checkout status requires review',409);
  }
  const qty=app.requested_counties?.length;
  if(!Number.isInteger(qty)||qty<1||qty>32)return err('Invalid county selection',409);
  const form=new URLSearchParams();
  form.set('mode','subscription');
  form.set('line_items[0][price]',PRICE_ID);
  form.set('line_items[0][quantity]',String(qty));
  form.set('line_items[1][price]',UPFRONT_PRICE_ID);
  form.set('line_items[1][quantity]',String(qty)); // Charge Q1 2027 immediately at checkout.
  form.set('payment_method_collection','always');
  form.set('payment_method_types[0]','card');
  form.set('subscription_data[trial_end]',String(FOUNDING_TRIAL_END_UNIX));
  form.set('subscription_data[trial_settings][end_behavior][missing_payment_method]','cancel');
  form.set('customer_email',app.email);
  form.set('client_reference_id',app.id);
  form.set('metadata[solar_application_id]',app.id);
  form.set('subscription_data[metadata][solar_application_id]',app.id);
  form.set('subscription_data[metadata][offer]','founders_q1_2027_prepaid_now');
  form.set('success_url',BASE_URL+'?payment=processing');
  form.set('cancel_url',BASE_URL+'?payment=cancelled');
  form.set('billing_address_collection','required');
  form.set('automatic_tax[enabled]','true');
  form.set('consent_collection[terms_of_service]','required');
  form.set('tax_id_collection[enabled]','true');
  // Subscription trial covers the free 2026 months and the Q1 2027 term already prepaid
  // by the one-time upfront line item. Next recurring charge is 1 April 2027.
  // Stripe Tax requires verified tax registrations/product tax category and a published
  // terms of service link in the Stripe Dashboard before SPONSOR_TAX_READY=true.
  form.set('expires_at',String(now+1800));
  const checkout=await stripe('checkout/sessions',form);
  await rpc('solar_store_checkout',{p_application_id:app.id,p_session_id:checkout.id,p_previous_session_id:previous});
  return Response.redirect(checkout.url,303);
 }catch(error){return catchError(error);}
}
