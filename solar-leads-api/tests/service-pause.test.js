import test from 'node:test';
import assert from 'node:assert/strict';
import { POST as handler0 } from '../api/intake.js';
import { POST as handler1 } from '../api/pilot-submit.js';
import { POST as handler2 } from '../api/checkout.js';
test('paused entry points never make external requests', async()=>{
 const original=globalThis.fetch; let calls=0; globalThis.fetch=async()=>{calls++;throw new Error('Unexpected external call');};
 try {
  for(const handler of [handler0,handler1,handler2]){
   const response=await handler(new Request('https://example.test/api',{method:'POST',headers:{origin:'https://compound.ie'}}));
   assert.equal(response.status,503); assert.match((await response.json()).message,/paused/);
  }
  assert.equal(calls,0);
 }finally{globalThis.fetch=original;}
});
