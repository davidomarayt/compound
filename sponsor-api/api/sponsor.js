import {COUNTIES,db,json,err,catchError,originHeaders} from '../lib/core.js';
// Public locator returns only the company name/id of a paying ACTIVE county sponsor.
// Contact details never leave the server until a homeowner explicitly opts in.
export async function GET(request){
 const cors=originHeaders(request);
 const county=new URL(request.url).searchParams.get('county')||'';
 if(!COUNTIES.includes(county))return json({available:false,error:'Select a valid county'},400,cors);
 try{
  const row=await db('solar_county_slots?county=eq.'+encodeURIComponent(county)+'&status=eq.active&select=application_id&limit=1');
  if(!row?.[0]?.application_id)return json({available:false,county},200,cors);
  const app=await db('solar_sponsor_applications?id=eq.'+encodeURIComponent(row[0].application_id)+'&status=eq.active&select=id,company&limit=1');
  if(!app?.[0]?.company)return json({available:false,county},200,cors);
  return json({available:true,county,sponsorId:app[0].id,sponsorName:app[0].company,advertisement:true},200,cors);
 }catch(error){return catchError(error);}
}
