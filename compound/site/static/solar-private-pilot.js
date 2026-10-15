/* Compound Solar — private owner-review pilot, no installer distribution.
 * Server permissions + database RLS enforce privacy. Browser is never trusted.
 */
(() => {
 'use strict';
 const root=document.querySelector('[data-solar-project]');
 if(!root||root.dataset.solarPilotActive!=='true')return;
 const form=root.querySelector('[data-sp-private-pilot-form]');
 if(!form)return;
 const api=root.dataset.solarLeadsApi||'';
 if(!/^https:\/\/[a-z0-9.-]+$/i.test(api))return;
 const submit=root.querySelector('[data-sp-private-pilot-submit]');
 const agree=root.querySelector('[data-sp-private-pilot-consent]');
 const status=root.querySelector('[data-sp-private-pilot-status]');
 let submitted=false;
 const get=k=>root.querySelector('[data-sp="'+k+'"]')?.value?.trim()||'';
 const report=(message,kind='')=>{status.textContent=message;status.dataset.state=kind;};
 const ready=()=>{
   if(!submitted)submit.disabled=!agree.checked;
 };
 const fields=['area','role','building','project','timing','budget','protected','roof',
  'faces','azimuth','pitch','azimuth2','pitch2','areaM2','areaM22','material','shade',
  'obstacles','roofCondition','storeys','access','demand','bill','daytime','smartMeter',
  'phase','board','ev','heatPump','immersion','existingPV','kwp','battery',
  'batteryKwh','evCharger','diverter','backup','grant','finance','cable','notes'];
 function payload(){
  const county=get('county'),name=get('name'),email=get('email'),
        phone=get('phone'),contactMethod=get('contactMethod'),
        count=Number(get('installerCount'));
  if(!county)throw Error('Select your county in the Property section.');
  if(!['Owner','Joint owner','Authorised decision-maker'].includes(get('role')))throw Error('Confirm that you own or are authorised to make decisions for this property.');
  if(!get('timing')||get('timing')==='Researching options')throw Error('Select your intended installation timeframe in the Property section.');
  if(!name||name.length<2)throw Error('Enter your name in the Sharing section.');
  if(!email||!root.querySelector('[data-sp="email"]').checkValidity())throw Error('Enter a valid email in the Sharing section.');
  if(contactMethod!=='Email'&&!phone)throw Error('Enter your phone number for phone contact.');
  if(![1,2,3].includes(count))throw Error('Choose whether you prefer 1, 2 or 3 quotations.');
  if(!agree.checked)throw Error('Tick the private review permission to submit.');
  const brief={};
  for(const k of fields){if(get(k))brief[k]=get(k);}
  const existingQuotes=get('quotes');
  if(existingQuotes)brief.existingQuotes=existingQuotes;
  return {county,name,email,phone,eircode:get('eircode'),contactMethod,
    requestedMax:count,brief,privateConsent:true,pilotVersion:'solar-private-pilot-2026-10-13',
    website:root.querySelector('[data-sp-pilot-website]')?.value||''};
 }
 form.addEventListener('submit',async e=>{
  e.preventDefault();if(submitted)return;
  let body;
  try{body=payload();}catch(err){report(err.message,'error');return;}
  submit.disabled=true;report('Sending your project securely…');
  try{
   const response=await fetch(api+'/api/pilot-submit',{
    method:'POST',mode:'cors',credentials:'omit',cache:'no-store',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
   });
   const data=await response.json();
   if(!response.ok||!data.ok||!data.reference)throw Error(data.message||'Unable to submit your project right now.');
   submitted=true;
   // Emit a conversion ONLY after the secure endpoint confirms storage.
   // This deliberately contains no homeowner details, county or reference.
   try {
     if(localStorage.getItem('compound_analytics_consent')==='granted' && typeof window.gtag==='function'){
       window.gtag('event','solar_project_submitted',{
         submission_stage:'private_pilot',
         source_path:'/solar/get-quotes/',
         transport_type:'beacon'
       });
     }
   }catch(_){}
   report('Project received. Your reference is '+data.reference+'. Compound Solar will review it privately. No installer has access.','success');
   submit.textContent='Project received';
  }catch(err){
   report(err?.message||'Unable to submit your project right now. Please try again.','error');
   ready();
  }
 });
 agree.addEventListener('change',ready);
 ready();
 report('Only Compound Solar can review your private submission. No installer will receive it at this stage.');
})();
