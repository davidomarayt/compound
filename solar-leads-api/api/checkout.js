import {json,ready,safeHeaders,allowedOrigin,paymentEnabled,readJson,
  authenticatedInstaller,rpc,stripe,options,token,databaseSecretReady} from '../lib/core.js';
export function OPTIONS(request){return options(request);}
export async function POST(request){
 const headers=safeHeaders(request);
 if(!allowedOrigin(request))return json({ok:false,message:'Not allowed'},403,headers);
 if(!paymentEnabled()||!databaseSecretReady()||!ready(
      'SUPABASE_PUBLISHABLE_KEY','STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET'))
   return json({ok:false,message:'Purchasing has not opened yet'},503,headers);
 let orderId=null;
 try{
   const user=await authenticatedInstaller(request);
   const body=await readJson(request,3000);
   if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(body?.project_id||''))
     return json({ok:false,message:'Invalid project'},400,headers);
   const reserved=await rpc('solar_reserve_introduction',
     {p_project_id:body.project_id,p_user_id:user.id});
   if(!reserved?.order_id||!Number.isInteger(reserved.price_cents))
     throw new Error('Project is not available');
   orderId=reserved.order_id;
   const now=Math.floor(Date.now()/1000);
   const form=new URLSearchParams({
     mode:'payment',
     'payment_method_types[0]':'card',
     'line_items[0][price_data][currency]':'eur',
     'line_items[0][price_data][unit_amount]':String(reserved.price_cents),
     'line_items[0][price_data][product_data][name]':'Qualified Solar Installation Introduction',
     'line_items[0][quantity]':'1',
     'metadata[solar_order_id]':orderId,
     'metadata[solar_project_id]':reserved.project_id,
     client_reference_id:orderId,
     success_url:'https://compound.ie/solar/installer-portal/?checkout=processing',
     cancel_url:'https://compound.ie/solar/installer-portal/?checkout=cancelled',
     expires_at:String(now+1800)
   });
   const checkout=await stripe('checkout/sessions',form,'POST','solar-order-'+orderId+'-'+token().slice(0,12));
   if(checkout?.status!=='open'||!/^https:\/\/checkout\.stripe\.com\//.test(checkout.url||''))
     throw new Error('Payment provider unavailable');
   await rpc('solar_attach_checkout',{p_order_id:orderId,p_checkout_id:checkout.id});
   return json({url:checkout.url},200,headers);
 }catch(e){
   if(orderId)try{await rpc('solar_cancel_reservation',{p_order_id:orderId});}catch{}
   const auth=/Not signed in|Invalid session/.test(e.message||'');
   return json({ok:false,message:auth?'Sign in again to continue':'This project is not currently available for purchase'},
      auth?401:409,headers);
 }
}
