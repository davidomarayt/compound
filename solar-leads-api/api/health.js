import {SOLAR_MATCHING_PAUSED} from '../lib/service-status.js';
import {json,intakeEnabled,paymentEnabled,pilotIntakeEnabled,databaseSecretReady,rest} from '../lib/core.js';

// Public readiness probe; deliberately returns no account details, project
// counts, keys or customer records. A read-only database query validates
// that the configured Supabase secret actually works.
export async function GET(){
  if(SOLAR_MATCHING_PAUSED)return json({service:'compound-solar-leads-api',status:'paused',installerMatchingEnabled:false,intakeEnabled:false,paymentsEnabled:false,privatePilotEnabled:false},200);
  const safe={
    service:'compound-solar-leads-api',
    status:pilotIntakeEnabled() ? 'homeowner_intake_open' : 'prelaunch',
    installerMatchingEnabled:false,
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
