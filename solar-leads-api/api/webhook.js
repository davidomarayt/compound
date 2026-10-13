import {json,ready,rest,rpc,stripe,stripeSignature,sendEmail,escapeHtml,
 paymentEnabled} from '../lib/core.js';

async function notifyHomeowner(orderId,projectId){
 // An independent receipt email never contains private homeowner information.
 const rows=await rest('solar_lead_details?project_id=eq.'+encodeURIComponent(projectId)+'&select=homeowner_email,homeowner_name');
 if(!Array.isArray(rows)||rows.length!==1)return;
 const orders=await rest('solar_lead_purchases?id=eq.'+encodeURIComponent(orderId)+'&select=installer_id');
 if(!Array.isArray(orders)||orders.length!==1)return;
 const firms=await rest('solar_installer_accounts?id=eq.'+encodeURIComponent(orders[0].installer_id)+'&select=company_name');
 if(!Array.isArray(firms)||firms.length!==1)return;
 const homeowner=rows[0],company=firms[0].company_name;
 await sendEmail({to:homeowner.homeowner_email,subject:'Your Compound Solar quote introduction',
   html:'<p>Your requested solar project has been shared with <strong>'+escapeHtml(company)+
     '</strong> so that this company can contact you about a quotation.</p>'+
     '<p>If you no longer want further introductions, contact <a href="mailto:david@compound.ie">david@compound.ie</a>.</p>'});
 await rpc('solar_mark_homeowner_notified',{p_order_id:orderId});
}
export async function POST(request){
 if(!paymentEnabled()||!ready('STRIPE_WEBHOOK_SECRET','STRIPE_SECRET_KEY',
    'SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'))return json({received:false},503);
 const raw=await request.text();
 if(raw.length>130000)return json({received:false},413);
 if(!stripeSignature(raw,request.headers.get('stripe-signature'),process.env.STRIPE_WEBHOOK_SECRET))
   return json({received:false},400);
 let event;
 try{event=JSON.parse(raw);}catch{return json({received:false},400);}
 const session=event.data?.object;
 try{
   if((event.type==='checkout.session.completed'||event.type==='checkout.session.async_payment_succeeded')
     && session?.mode==='payment'){
     if(session.payment_status!=='paid')return json({received:true});
     const orderId=session.client_reference_id;
     if(!/^[0-9a-f-]{36}$/i.test(orderId||'')||session.metadata?.solar_order_id!==orderId)
       return json({received:false},400);
     const result=await rpc('solar_complete_checkout',{
       p_order_id:orderId,p_checkout_id:session.id,
       p_payment_intent_id:typeof session.payment_intent==='string'?session.payment_intent:'',
       p_amount_cents:Number(session.amount_total),p_currency:session.currency,
       p_stripe_event_id:event.id
     });
     if(!result?.released) {
       // Failed release after payment (withdrawal, oversell or stale permission):
       // automatically initiate idempotent refund, never release private data.
       if(typeof session.payment_intent==='string') {
         await stripe('refunds',new URLSearchParams({payment_intent:session.payment_intent}),
           'POST','solar-refund-'+orderId);
       }
       await rpc('solar_cancel_reservation',{p_order_id:orderId});
       return json({received:true,released:false});
     }
     // A failed notification is retried on the next signed Stripe delivery;
     // no contact information is included in Stripe's receipt itself.
     const pending=await rpc('solar_release_notification_pending',{p_order_id:orderId});
     if(pending===true)await notifyHomeowner(orderId,result.project_id);
   } else if(event.type==='checkout.session.expired'&&session?.client_reference_id){
     await rpc('solar_cancel_reservation',{p_order_id:session.client_reference_id});
   }
   return json({received:true});
 }catch{return json({received:false},500);}
}
