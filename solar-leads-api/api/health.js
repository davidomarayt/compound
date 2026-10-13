import {json,intakeEnabled,paymentEnabled} from '../lib/core.js';
export function GET(){return json({service:'compound-solar-leads-api',status:'prelaunch',intakeEnabled:intakeEnabled(),paymentsEnabled:paymentEnabled()});}
