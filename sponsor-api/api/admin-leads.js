import {authorised,db,json,err,catchError} from '../lib/core.js';
export async function GET(request){
 if(!authorised(request))return err('Unauthorized',401);
 try{
  const rows=await db('solar_homeowner_leads?select=id,county,sponsor_application_id,sponsor_name_at_consent,customer_name,customer_email,customer_phone,eircode_or_postcode,electricity_details,message,submitted_at,delivered_at&order=submitted_at.desc&limit=100');
  return json({ok:true,leads:rows,undelivered:rows.filter(row=>!row.delivered_at).length});
 }catch(error){return catchError(error);}
}
