import {json,allowedOrigin,safeHeaders,options,databaseSecretReady,authenticatedInstaller,rest} from '../lib/core.js';
export function OPTIONS(request){return options(request);}
export async function GET(request){
 const headers=safeHeaders(request);
 if(!allowedOrigin(request))return json({ok:false,message:'Not allowed'},403,headers);
 if(!databaseSecretReady())return json({ok:false,message:'Unavailable'},503,headers);
 try {
   // Check authenticated Supabase JWT against the server-only admin registry.
   const user=await authenticatedInstaller(request);
   const admins=await rest('solar_pilot_admins?user_id=eq.'+encodeURIComponent(user.id)+'&select=user_id&limit=1');
   if(!Array.isArray(admins)||admins.length!==1)return json({ok:false,message:'Not authorised'},403,headers);
   const rows=await rest('solar_pilot_requests?select=id,reference,county,requested_max,contact_method,homeowner_name,homeowner_email,homeowner_phone,eircode,brief,status,created_at&order=created_at.desc&limit=100');
   return json({ok:true,requests:Array.isArray(rows)?rows:[]},200,headers);
 }catch{
   return json({ok:false,message:'Unable to load private submissions'},401,headers);
 }
}
