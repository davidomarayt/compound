import {db,json,catchError} from '../lib/core.js';
export async function GET(){
 try{
   const rows=await db('solar_county_slots?select=county,status,hold_until');
   const now=Date.now();
   const slots=Object.fromEntries(rows.filter(r=>r.status!=='held'||Date.parse(r.hold_until)>now).map(r=>[r.county,r.status]));
   return json({counties:slots,notice:'County information is subject to approval and payment; do not treat this as a guaranteed reservation.'});
 }catch(error){return catchError(error);}
}
