import {rpc,sha256,stripe,PRICE_ID,BASE_URL,FOUNDING_TRIAL_END_UNIX,err,catchError,failClosed} from '../lib/core.js';
export async function GET(request){
 // Public paid checkout must never run without the fully operational CRM, county lock,
 // tax configuration and Stripe webhook. The static application form stays separate.
 if(process.env.SPONSOR_BILLING_READY!=='true'||!failClosed('STRIPE_SECRET_KEY','SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','STRIPE_WEBHOOK_SECRET'))return err('Checkout not yet available',503);
 const token=new URL(request.url).searchParams.get('token')||'';
 if(!/^[A-Za-z0-9_-]{40,80}$/.test(token))return err('Invalid or expired invitation',400);
 const now=Math.floor(Date.now()/1000);
 if(now>FOUNDING_TRIAL_END_UNIX-48*3600)return err('2026 founders offer closed. Please contact Compound for current sponsorship terms.',410);
 try{
  const result=await rpc('solar_get_invite',{p_invite_hash:sha256(token)});
  const app=Array.isArray(result)?result[0]:result;
  if(!app||!app.id)return err('Invitation expired or county no longer available',409);
  const qty=app.requested_counties?.length;
  if(!Number.isInteger(qty)||qty<1||qty>32)return err('Invalid county selection',409);
  const form=new URLSearchParams();
  form.set('mode','subscription');
  form.set('line_items[0][price]',PRICE_ID);
  form.set('line_items[0][quantity]',String(qty));
  form.set('payment_method_collection','always');
  form.set('payment_method_types[0]','card');
  form.set('subscription_data[trial_end]',String(FOUNDING_TRIAL_END_UNIX));
  form.set('subscription_data[trial_settings][end_behavior][missing_payment_method]','cancel');
  form.set('customer_email',app.email);
  form.set('client_reference_id',app.id);
  form.set('metadata[solar_application_id]',app.id);
  form.set('subscription_data[metadata][solar_application_id]',app.id);
  form.set('subscription_data[metadata][offer]','founders_free_remainder_2026');
  form.set('success_url',BASE_URL+'?payment=processing');
  form.set('cancel_url',BASE_URL+'?payment=cancelled');
  form.set('billing_address_collection','required');
  form.set('tax_id_collection[enabled]','true');
  // Must be paired with approved Stripe Tax or explicitly specified tax rates before
  // SPONSOR_BILLING_READY=true. Price is VAT-exclusive; no arbitrary tax rate is assumed here.
  form.set('expires_at',String(now+1800));
  const checkout=await stripe('checkout/sessions',form);
  await rpc('solar_store_checkout',{p_application_id:app.id,p_session_id:checkout.id});
  return Response.redirect(checkout.url,303);
 }catch(error){return catchError(error);}
}
