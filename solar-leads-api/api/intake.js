import {json,error,ready,readJson,allowedOrigin,safeHeaders,intakeEnabled,
 normalizeQuote,verifyTurnstile,token,digest,rpc,sendEmail,escapeHtml,options,databaseSecretReady} from '../lib/core.js';

export function OPTIONS(request){return options(request);}
export async function POST(request){
 const headers=safeHeaders(request);
 if(!allowedOrigin(request))return error('Not allowed',403);
 if(!intakeEnabled()||!databaseSecretReady()||!ready('TURNSTILE_SECRET',
   'RESEND_API_KEY','MAIL_FROM','PUBLIC_API_URL'))return json({ok:false,message:'Quote requests are not open yet'},503,headers);
 try{
   const form=normalizeQuote(await readJson(request));
   if(!await verifyTurnstile(form.turnstileToken))return json({ok:false,message:'Please complete the spam check'},403,headers);
   const verification=token();
   const created=await rpc('solar_create_quote',{
     p_teaser:form.teaser,p_private:form.privateData,
     p_permission:form.permission,p_token_digest:digest(verification)
   });
   if(!created?.project_id)throw new Error('Unable to save quote');
   const root=process.env.PUBLIC_API_URL.replace(/\/$/,'');
   const verificationUrl=root+'/api/verify?project='+encodeURIComponent(created.project_id)+'&token='+encodeURIComponent(verification);
   await sendEmail({to:form.privateData.email,subject:'Confirm your Compound Solar quote request',
     html:'<p>Confirm your request for up to '+form.permission.requested_max+
     ' solar quotes:</p><p><a href="'+escapeHtml(verificationUrl)+'">Confirm my email and publish my anonymous project preview</a></p>'+
     '<p>Your name and contact details remain private until an approved installer purchases an introduction.</p>'+
     '<p>If you did not request this, ignore the email. The request will not be published without confirmation.</p>'});
   return json({ok:true,message:'Check your email to confirm your quote request.'},202,headers);
 }catch(e){
   // Do not expose private inputs or backend error details in responses.
   const userInput=/^(Invalid|Select|Name,|Quote-sharing|Complete|Payload|Expected)/.test(e.message||'');
   return json({ok:false,message:userInput?e.message:'Unable to accept quote requests right now'},userInput?400:503,headers);
 }
}
