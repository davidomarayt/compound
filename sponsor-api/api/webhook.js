import {stripeSignature,rpc,stripe,PRICE_ID,FOUNDING_TRIAL_END_UNIX,json,err,catchError,failClosed} from '../lib/core.js';
async function subscriptionById(id){if(!id)return null;return stripe('subscriptions/'+encodeURIComponent(id),null,'GET');}
function subscriptionIdFromInvoice(invoice){
 return typeof invoice.subscription==='string'?invoice.subscription:
   (typeof invoice.parent?.subscription_details?.subscription==='string'?invoice.parent.subscription_details.subscription:null);
}
function correctFoundingSubscription(sub,qty){
 const items=sub?.items?.data||[];
 return items.length===1&&items[0]?.price?.id===PRICE_ID&&items[0]?.quantity===qty&&sub.trial_end===FOUNDING_TRIAL_END_UNIX;
}
async function processStripeEvent(event){
 const obj=event.data?.object||{};
 if(event.type==='checkout.session.completed'&&obj.mode==='subscription'){
   if(!obj.subscription||!obj.client_reference_id)return;
   const sub=await subscriptionById(obj.subscription);
   const qty=sub?.items?.data?.[0]?.quantity;
   if(!correctFoundingSubscription(sub,qty)||sub.status!=='trialing'||!sub.default_payment_method)throw new Error('Checkout founding terms/payment method invalid');
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:'trialing',p_application_id:obj.client_reference_id,p_subscription_id:sub.id,p_customer_id:sub.customer||'',p_checkout_id:obj.id,p_quantity:qty});
 }else if(['invoice.paid','invoice.payment_failed'].includes(event.type)){
   const subId=subscriptionIdFromInvoice(obj);if(!subId)return;
   const sub=await subscriptionById(subId);
   const appId=sub?.metadata?.solar_application_id;
   if(!appId||sub?.items?.data?.[0]?.price?.id!==PRICE_ID)return;
   // A €0 invoice during the complimentary trial must NOT count as the paid Q1 commitment.
   const isFirstPaid=event.type==='invoice.paid'&&sub.status==='active'&&Number(obj.amount_paid)>=75000*Number(sub.items.data[0].quantity);
   const kind=isFirstPaid?'paid':event.type==='invoice.payment_failed'?'failed':'ignored';
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,p_application_id:appId,p_subscription_id:sub.id,p_customer_id:sub.customer||'',p_checkout_id:'',p_quantity:Number(sub.items.data[0].quantity)||0});
 }else if(['customer.subscription.deleted','customer.subscription.updated'].includes(event.type)){
   const appId=obj.metadata?.solar_application_id;if(!appId)return;
   const sub=await subscriptionById(obj.id).catch(()=>obj);
   const kind=sub.status==='canceled'?'cancelled':
     ['past_due','unpaid','paused','incomplete_expired'].includes(sub.status)?'failed':'ignored';
   // Payment, not status=active alone, establishes a paid quarter.
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,p_application_id:appId,p_subscription_id:obj.id,p_customer_id:obj.customer||'',p_checkout_id:'',p_quantity:Number(sub?.items?.data?.[0]?.quantity)||0});
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
