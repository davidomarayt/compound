import {authorised,db,json,err,catchError} from '../lib/core.js';
export async function GET(request){
 if(!authorised(request))return err('Unauthorized',401);
 try{
  const rows=await db('solar_sponsor_applications?select=id,company,contact,email,phone,website,accreditation,requested_counties,status,created_at&order=created_at.desc&limit=100');
  return json({ok:true,applications:rows});
 }catch(error){return catchError(error);}
}
