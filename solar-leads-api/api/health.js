import {json,intakeEnabled,paymentEnabled,pilotIntakeEnabled,databaseSecretReady,rest} from '../lib/core.js';

// Public readiness probe; deliberately returns no account details, project
// counts, keys or customer records. A read-only database query validates
// that the configured Supabase secret actually works.
export async function GET(){
  const safe={
    service:'compound-solar-leads-api',
    status:'prelaunch',
    intakeEnabled:intakeEnabled(),
    paymentsEnabled:paymentEnabled(),
    privatePilotEnabled:pilotIntakeEnabled(),
    database:'not_configured'
  };
  if(!databaseSecretReady())return json(safe,503);
  try{
    await rest('solar_lead_teasers?select=id&limit=1');
    return json({...safe,database:'connected'},200);
  }catch{
    return json({...safe,database:'unavailable'},503);
  }
}
