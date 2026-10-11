import {stripeSignature,rpc,stripe,PRICE_ID,UPFRONT_PRICE_ID,FOUNDING_TRIAL_END_UNIX,json,err,catchError,failClosed} from '../lib/core.js';

async function subscriptionById(id){
 if(!id)return null;
 return stripe('subscriptions/'+encodeURIComponent(id),null,'GET');
}
function subscriptionIdFromInvoice(invoice){
 return typeof invoice.subscription==='string'?invoice.subscription:
  (typeof invoice.parent?.subscription_details?.subscription==='string'?invoice.parent.subscription_details.subscription:null);
}
function quantity(sub){return Number(sub?.items?.data?.[0]?.quantity)||0;}
function validFoundingSubscription(sub){
 const items=sub?.items?.data||[];
 return items.length===1&&items[0]?.price?.id===PRICE_ID
   &&Number.isInteger(quantity(sub))&&quantity(sub)>0&&quantity(sub)<=32
   &&Number(sub.trial_end)===FOUNDING_TRIAL_END_UNIX;
}
export function validUpfrontCheckout(session,sub){
 const qty=quantity(sub);
 return session?.mode==='subscription'
   &&session?.subscription===sub?.id
   &&session?.payment_status==='paid'
   &&session?.currency==='eur'
   &&Number(session?.amount_subtotal)===qty*75000
   &&Number(session?.amount_total)>=qty*75000
   &&validFoundingSubscription(sub)
   &&sub.status==='trialing'
   &&!!sub.default_payment_method
   &&!!session.client_reference_id
   &&!!session.invoice; // Paid first invoice includes the one-time Q1 price.
}
async function processStripeEvent(event){
 const obj=event.data?.object||{};
 if(event.type==='checkout.session.completed'&&obj.mode==='subscription'){
   if(!obj.subscription||!obj.client_reference_id)return;
   const sub=await subscriptionById(obj.subscription);
   if(!validUpfrontCheckout(obj,sub))throw new Error('Initial Q1 prepayment or founding subscription could not be verified');
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:'upfront_paid',
      p_application_id:obj.client_reference_id,p_subscription_id:sub.id,p_customer_id:sub.customer||'',
      p_checkout_id:obj.id,p_quantity:quantity(sub)});
 }else if(['invoice.paid','invoice.payment_failed'].includes(event.type)){
   const subId=subscriptionIdFromInvoice(obj);if(!subId)return;
   const sub=await subscriptionById(subId);
   const appId=sub?.metadata?.solar_application_id;
   if(!appId||sub?.items?.data?.[0]?.price?.id!==PRICE_ID)return;
   // The initial payment is processed by checkout.session.completed, not this invoice
   // event. It can arrive before the paid checkout event: never activate from a
   // zero-value trial invoice, and avoid treating a Q1 one-off as a renewal.
   if(obj.billing_reason==='subscription_create')return;
   const qty=quantity(sub);
   let kind='ignored';
   if(event.type==='invoice.paid'&&sub.status==='active'
      &&obj.billing_reason==='subscription_cycle'
      &&Number(obj.amount_paid)>=qty*75000
      &&Number(obj.amount_subtotal)>=qty*75000)kind='paid';
   else if(event.type==='invoice.payment_failed'&&sub.status!=='trialing')kind='failed';
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,
      p_application_id:appId,p_subscription_id:sub.id,p_customer_id:sub.customer||'',
      p_checkout_id:'',p_quantity:qty});
 }else if(['customer.subscription.deleted','customer.subscription.updated'].includes(event.type)){
   const appId=obj.metadata?.solar_application_id;if(!appId)return;
   const sub=await subscriptionById(obj.id).catch(()=>obj);
   const kind=sub.status==='canceled'?'cancelled':
     ['past_due','unpaid','paused','incomplete_expired'].includes(sub.status)?'failed':'ignored';
   // "active" alone is never proof that the next renewal invoice was paid.
   await rpc('solar_apply_billing_event',{p_event_id:event.id,p_kind:kind,
      p_application_id:appId,p_subscription_id:obj.id,p_customer_id:obj.customer||'',
      p_checkout_id:'',p_quantity:quantity(sub)});
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
