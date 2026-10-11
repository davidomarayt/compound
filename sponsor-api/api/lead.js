import {allowBrowser,originHeaders,readJson,normalizeHomeownerLead,verifyTurnstile,rpc,db,sendEmail,htmlSafe,json,err,catchError,failClosed} from '../lib/core.js';
export function OPTIONS(request){return new Response(null,{status:204,headers:originHeaders(request)});}
export async function POST(request){
 const cors=originHeaders(request);
 if(!allowBrowser(request))return json({ok:false,error:'Not allowed'},403,cors);
 if(!failClosed('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','TURNSTILE_SECRET','RESEND_API_KEY','MAIL_FROM','ADMIN_EMAIL'))return json({ok:false,error:'The solar quote service is not yet available'},503,cors);
 try{
  const raw=await readJson(request);
  const lead=normalizeHomeownerLead(raw);
  if(!await verifyTurnstile(raw.turnstileToken,request))return json({ok:false,error:'Spam verification failed'},400,cors);
  const payload={
   p_county:lead.county,p_sponsor_id:lead.sponsor_application_id,p_named_sponsor:lead.named_sponsor,
   p_customer_name:lead.customer_name,p_customer_email:lead.customer_email,
   p_customer_phone:lead.customer_phone,p_eircode:lead.eircode_or_postcode,
   p_electricity:lead.electricity_details,p_message:lead.message,p_consent:true
  };
  // DB transaction checks named sponsor, county exclusivity, live subscription status,
  // and consent before logging the lead. It returns sponsor email SERVER SIDE only.
  const result=await rpc('solar_submit_homeowner_lead',payload);
  const sponsor=Array.isArray(result)?result[0]:result;
  if(!sponsor?.lead_id||!sponsor.sponsor_email)throw new Error('Lead could not be stored or routed');
  const brief='<p><b>County:</b> '+htmlSafe(lead.county)+'</p>'+
   '<p><b>Name:</b> '+htmlSafe(lead.customer_name)+'</p>'+
   '<p><b>Email:</b> '+htmlSafe(lead.customer_email)+'</p>'+
   '<p><b>Phone:</b> '+htmlSafe(lead.customer_phone)+'</p>'+
   '<p><b>Postcode/Eircode:</b> '+htmlSafe(lead.eircode_or_postcode)+'</p>'+
   '<p><b>Electricity:</b> '+htmlSafe(lead.electricity_details)+'</p>'+
   '<p><b>Project details:</b> '+htmlSafe(lead.message)+'</p>'+
   '<p><b>Lead reference:</b> '+htmlSafe(sponsor.lead_id)+'</p>';
  let delivered=false;
  try{
   await sendEmail({to:sponsor.sponsor_email,subject:'Compound Solar — new consented homeowner enquiry ('+lead.county+')',
     html:'<h2>New homeowner solar quote request</h2><p>The homeowner explicitly agreed to send these details to '+htmlSafe(sponsor.sponsor_company)+'.</p>'+brief});
   delivered=true;
   await db('solar_homeowner_leads?id=eq.'+encodeURIComponent(sponsor.lead_id),
     {method:'PATCH',body:{delivered_at:new Date().toISOString()}});
  }catch(error){console.error('Sponsor lead delivery pending: '+error.message);}
  try{
   await sendEmail({to:process.env.ADMIN_EMAIL,subject:'Compound Solar '+(delivered?'lead logged':'LEAD DELIVERY NEEDS REVIEW')+' — '+lead.county,
    html:'<p><b>Sponsor:</b> '+htmlSafe(sponsor.sponsor_company)+'</p><p><b>Delivery status:</b> '+(delivered?'Sent':'Pending — retry from private leads records')+'</p>'+brief});
  }catch(error){console.error('Owner lead notification failed: '+error.message);}
  // Keep lead private and never claim email delivery succeeded if it did not.
  return json({ok:true,received:true,deliveryPending:!delivered,reference:sponsor.lead_id},delivered?201:202,cors);
 }catch(error){
  if(/Invalid|required|Named sponsor|consent|Spam|Payload|Expected/.test(error.message))return json({ok:false,error:error.message},400,cors);
  if(/No matching active/.test(error.message))return json({ok:false,error:'The selected county sponsor is no longer available. Please refresh the page.'},409,cors);
  const res=catchError(error);return json(await res.json(),503,cors);
 }
}
