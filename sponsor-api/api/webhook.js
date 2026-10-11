import {stripeSignature,rpc,stripe,json,err,catchError,failClosed} from '../lib/core.js';
async function subscriptionById(id){
 if(!id)return null;
 return stripe('subscriptions/'+encodeURIComponent(id),null,'GET');
}
function subscriptionIdFromInvoice(invoice){
 return typeof invoice.subscription==='string'?invoice.subscription:
   (invoice.parent?.subscription_details?.subscription||null);
}
async function processStripeEvent(event){
 const obj=event.data?.object||{};
 if(event.type==='checkout.session.completed'&&obj.mode==='subscription'){
   if(!obj.subscription)return;
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:'checkout',p_application_id:obj.client_reference_id||obj.metadata?.solar_application_id,p_subscription_id:obj.subscription,p_customer_id:obj.customer||'',p_checkout_id:obj.id});
 }else if(['invoice.paid','invoice.payment_failed'].includes(event.type)){
   const subId=subscriptionIdFromInvoice(obj);
   if(!subId)return;
   const sub=await subscriptionById(subId);
   const appId=sub?.metadata?.solar_application_id;
   if(!appId)return;
   // A paid invoice alone is insufficient if the current subscription is cancelled.
   const kind=event.type==='invoice.paid'&&sub.status==='active'?'paid':event.type==='invoice.payment_failed'?'failed':'ignored';
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,p_application_id:appId,p_subscription_id:sub.id,p_customer_id:sub.customer||'',p_checkout_id:''});
 }else if(['customer.subscription.deleted','customer.subscription.updated'].includes(event.type)){
   const appId=obj.metadata?.solar_application_id;
   if(!appId)return;
   const sub=await subscriptionById(obj.id).catch(()=>obj);
   const kind=sub.status==='canceled'?'cancelled':sub.status==='active'?'status_active':sub.status==='past_due'||sub.status==='unpaid'||sub.status==='paused'?'failed':'ignored';
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,p_application_id:appId,p_subscription_id:obj.id,p_customer_id:obj.customer||'',p_checkout_id:''});
 }
}
export async function POST(request){
 if(!failClosed('STRIPE_WEBHOOK_SECRET','SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','STRIPE_SECRET_KEY'))return err('Webhook not configured',503);
 try{
   const raw=await request.text();
   if(raw.length>150000)return err('Payload too large',413);
   if(!stripeSignature(raw,request.headers.get('stripe-signature'),process.env.STRIPE_WEBHOOK_SECRET))return err('Invalid signature',400);
   const event=JSON.parse(raw);
   if(!event.id||!event.type||!event.data)return err('Invalid event');
   await processStripeEvent(event);
   return json({received:true});
 }catch(error){return catchError(error);}
}
