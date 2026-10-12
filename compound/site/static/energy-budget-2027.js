/* Consent-respecting, aggregate CTA measurement; no household inputs are collected. */
(function(){
  'use strict';
  const events={
    electricity_tool:'energy_electricity_tool_click',
    solar_payback:'energy_solar_payback_click',
    quote_brief:'energy_quote_brief_click',
    winter_article:'energy_winter_article_click',
    solar_hub:'energy_solar_hub_click'
  };
  document.addEventListener('click',function(e){
    const a=e.target.closest('a[data-energy-funnel]');
    if(!a)return;
    const eventName=events[a.dataset.energyFunnel];
    if(!eventName)return;
    try{
      if(localStorage.getItem('compound_analytics_consent')==='granted' && typeof window.gtag==='function'){
        window.gtag('event',eventName,{source_page:location.pathname});
      }
    }catch(_){}
  });
})();
