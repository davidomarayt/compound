/* Compound Solar homeowner quote API adapter.
 * Staged and FAIL-CLOSED. No homeowner data is sent while data-solar-leads-active != "true".
 * Personal data is only sent on explicit, consented submit following a Turnstile challenge.
 */
(() => {
  'use strict';
  const root=document.querySelector('[data-solar-project]');
  if(!root) return;
  const stage=root.querySelector('[data-sp-live-request]');
  if(!stage) return;
  const enabled=root.dataset.solarLeadsActive==='true';
  const key=root.dataset.turnstileSitekey||'';
  const base=root.dataset.solarLeadsApi||'';
  // The web form is deliberately switched OFF until the secure API,
  // privacy notice, verified mail, Stripe testing and deletion flow are ready.
  if(!enabled || !/^https:\/\/[a-z0-9.-]+$/.test(base) || !/^0x[a-z0-9_-]{20,}$/i.test(key)) {
    // Prelaunch panel stays visible. Nothing is transmitted.
    stage.hidden=true;
    return;
  }
  // Only replace the prelaunch panel after launch configuration is complete.
  const prelaunch=root.querySelector('[data-sp-prelaunch-request]');
  if(prelaunch) prelaunch.hidden=true;
  stage.hidden=false;
  const byName=k=>root.querySelector('[data-sp="'+k+'"]');
  const consent=stage.querySelector('[data-sp-quote-consent]');
  const submit=stage.querySelector('[data-sp-quote-submit]');
  const status=stage.querySelector('[data-sp-quote-status]');
  const countLabel=stage.querySelector('[data-sp-sharing-count]');
  const challenge=stage.querySelector('[data-sp-turnstile]');
  let turnstileId=null;
  let challengeToken='';
  const consentVersion='solar-leads-v1-2026-10-13';
  const setStatus=(message,kind='')=>{status.textContent=message;status.dataset.state=kind;};
  const get=k=>byName(k)?.value?.trim()||'';
  const count=()=>Number(get('installerCount'));
  const update=()=>{
    const n=count();
    countLabel.textContent=[1,2,3].includes(n)?String(n):'the number you choose';
    submit.disabled=!consent.checked || ![1,2,3].includes(n) || !challengeToken;
  };
  async function loadTurnstile(){
    const script=document.createElement('script');
    script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async=true;
    script.onload=()=>{
      if(!window.turnstile) return setStatus('Verification is currently unavailable. Please try again later.','error');
      turnstileId=window.turnstile.render(challenge,{
        sitekey:key, theme:'light',
        callback:(value)=>{challengeToken=value;update();},
        'expired-callback':()=>{challengeToken='';update();},
        'error-callback':()=>{challengeToken='';update();setStatus('Please retry the verification.','error');}
      });
    };
    script.onerror=()=>setStatus('Verification could not load; no data has been submitted.','error');
    document.head.appendChild(script);
  }
  function collectBrief(){
    const keys=['area','role','building','project','timing','budget','protected','roof','faces','azimuth',
      'pitch','azimuth2','pitch2','areaM2','areaM22','material','shade','obstacles','roofCondition',
      'storeys','access','demand','bill','daytime','smartMeter','phase','board','ev','heatPump',
      'immersion','existingPV','kwp','battery','batteryKwh','evCharger','diverter','backup','grant',
      'finance','quotes'];
    const brief={};
    for(const k of keys){
      if(get(k)) brief[k==='quotes'?'existingQuotes':k]=get(k);
    }
    return brief;
  }
  function buildPayload(){
    const role=get('role'),timing=get('timing'),n=count(),email=get('email'),name=get('name');
    if(!['Owner','Joint owner','Authorised decision-maker'].includes(role)) throw Error('Only an owner or authorised decision-maker can request quotes.');
    if(!timing||timing==='Researching options') throw Error('Choose an installation timeframe when you are ready for quotations.');
    if(!get('county')) throw Error('Select your county.');
    if(get('area').length<2) throw Error('Enter the nearest town or general area.');
    if(!get('building')) throw Error('Choose the property type.');
    if(!name||!email||!byName('email').checkValidity()) throw Error('Enter your name and valid email address.');
    if(get('contactMethod')!=='Email'&&!get('phone')) throw Error('Enter your phone number for phone contact.');
    if(![1,2,3].includes(n)||!consent.checked) throw Error('Choose the number of quotes and confirm the sharing notice.');
    if(!challengeToken) throw Error('Please complete the verification.');
    return {
      county:get('county'),area:get('area'),name,email,phone:get('phone'),eircode:get('eircode'),
      requestedMax:n,contactMethod:get('contactMethod'),consent:true,consentVersion,
      turnstileToken:challengeToken,building:get('building'),project:get('project'),
      roofOrientation:get('azimuth')?get('azimuth')+'°':'',kwp:get('kwp'),
      battery:get('battery'),timing,brief:collectBrief()
    };
  }
  stage.querySelector('[data-sp-quote-form]').addEventListener('submit',async e=>{
    e.preventDefault();
    if(!enabled) return;
    let body;
    try{body=buildPayload();}catch(err){setStatus(err.message,'error');return;}
    submit.disabled=true;setStatus('Submitting securely…');
    try{
      const response=await fetch(base+'/api/intake',{
        method:'POST',mode:'cors',credentials:'omit',cache:'no-store',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(body)
      });
      const data=await response.json();
      if(!response.ok||!data.ok)throw Error(data.message||'Submission is unavailable.');
      setStatus('Check your email to confirm this quote request. Your project is not listed until verified.','success');
      consent.checked=false;
    }catch(err){
      setStatus(err.message||'We could not submit the request. Please try again.','error');
    }finally{
      challengeToken='';
      if(window.turnstile&&turnstileId!==null)window.turnstile.reset(turnstileId);
      update();
    }
  });
  byName('installerCount')?.addEventListener('change',update);
  consent.addEventListener('change',update);
  update();
  loadTurnstile();
})();