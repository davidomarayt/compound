import {json,rpc,readJson,adminAuthorised} from '../lib/core.js';

// Called only after staff has validated an email/identity-based withdrawal
// request. The admin token must never be exposed to browser code.
export async function POST(request) {
 if(!adminAuthorised(request))return json({ok:false},403);
 try{
   const b=await readJson(request,1500);
   if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(b?.project_id||''))
     return json({ok:false,message:'Invalid project id'},400);
   const result=await rpc('solar_withdraw_quote',{p_project_id:b.project_id});
   return json({ok:true,result});
 }catch{return json({ok:false,message:'Unable to close quote'},400);}
}
