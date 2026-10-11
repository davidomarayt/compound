import {json} from '../lib/core.js';
export function GET(){
 return json({service:'compound-solar-sponsor-api',status:'ready-for-configuration',paymentsEnabled:false});
}
