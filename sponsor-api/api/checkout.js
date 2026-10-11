import {rpc,sha256,stripe,PRICE_ID,BASE_URL,err,catchError,failClosed} from '../lib/core.js';
export async function GET(request){
 if(!failClosed('STRIPE_SECRET_KEY','SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'))return err('Checkout not yet available',503);
 const token=new URL(request.url).searchParams.get('token')||'';
 if(!/^[A-Za-z0-9_-]{40,80}$/.test(token))return err('Invalid or expired invitation',400);
 try{
  const result=await rpc('solar_get_invite',{p_invite_hash:sha256(token)});
  const app=Array.isArray(result)?result[0]:result;
  if(!app||!app.id)return err('Invitation expired or county no longer available',409);
  const form=new URLSearchParams();
  form.set('mode','subscription');
  form.set('line_items[0][price]',PRICE_ID);
  form.set('line_items[0][quantity]',String(app.requested_counties.length));
  form.set('customer_email',app.email);
  form.set('client_reference_id',app.id);
  form.set('metadata[solar_application_id]',app.id);
  form.set('subscription_data[metadata][solar_application_id]',app.id);
  form.set('success_url',BASE_URL+'?payment=processing');
  form.set('cancel_url',BASE_URL+'?payment=cancelled');
  form.set('billing_address_collection','required');
  form.set('tax_id_collection[enabled]','true');
  // Do not switch on automatic_tax until VAT registrations and Stripe Tax are configured.
  form.set('expires_at',String(Math.floor(Date.now()/1000)+1800));
  const checkout=await stripe('checkout/sessions',form);
  await rpc('solar_store_checkout',{p_application_id:app.id,p_session_id:checkout.id});
  return Response.redirect(checkout.url,303);
 }catch(error){return catchError(error);}
}
