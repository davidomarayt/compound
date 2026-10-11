
/* Compound Solar: client-only calculators; no inputs sent to a server. */
(function () {
  "use strict";
  /* Only consented GA4 event names are recorded. No amounts or form entries. */
  function solarTrack(name){try{
    if(localStorage.getItem('compound_analytics_consent')==='granted'&&typeof window.gtag==='function')window.gtag('event','solar_'+name);
  }catch(_){}}
  function solarTrackOnce(node,flag,name){if(!node.dataset[flag]){node.dataset[flag]='1';solarTrack(name);}}
  var money = new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  var number = new Intl.NumberFormat("en-IE",{maximumFractionDigits:1});
  function clamp(n,low,high){return Number.isFinite(n)?Math.min(high,Math.max(low,n)):NaN;}
  function value(el,low,high){if(!el||el.value.trim()==="")return NaN;return clamp(Number(el.value),low,high);}
  function pvGrant(kwp){return Number.isFinite(kwp)&&kwp>0?Math.min(1800,Math.min(kwp,2)*700+Math.max(0,Math.min(kwp-2,2))*200):0;}
  function setText(el,text){if(el)el.textContent=text;}
  function round(n){return Number.isFinite(n)?number.format(n):"—";}
  function create(parent,tag,className,txt){var el=document.createElement(tag);if(className)el.className=className;if(txt!==undefined)el.textContent=txt;parent.appendChild(el);return el;}

  var root=document.querySelector("[data-solar-quotes]");
  if(root){
    function qinput(q,f){return root.querySelector('[data-q="'+q+'"][data-f="'+f+'"]');}
    function sfield(f){return root.querySelector('[data-sq="'+f+'"]');}
    var table=root.querySelector("[data-sq-rows]"),bars=root.querySelector("[data-sq-bars]");
    function calcQuotes(){
      var eligible=sfield("grant").value==="yes",onSite=value(sfield("self"),0,100),importRate=value(sfield("import"),0,150),exportRate=value(sfield("export"),0,150);
      var validShared=[onSite,importRate,exportRate].every(Number.isFinite);
      var quotes=["a","b","c"].map(function(id){
        var price=value(qinput(id,"price"),0,200000),kwp=value(qinput(id,"kwp"),0,100),yieldKwh=value(qinput(id,"yield"),0,150000);
        var battery=value(qinput(id,"battery"),0,200),warranty=value(qinput(id,"warranty"),0,30);
        var valid=price>0&&kwp>0&&yieldKwh>0&&validShared;
        var pv=valid&&eligible?pvGrant(kwp):0,net=valid?Math.max(0,price-pv):NaN;
        var annual=valid?yieldKwh*(onSite/100*importRate/100+(1-onSite/100)*exportRate/100):NaN;
        return {id:id,valid:valid,price:price,kwp:kwp,yieldKwh:yieldKwh,battery:battery||0,warranty:warranty||0,
          grant:pv,net:net,perKwp:valid?price/kwp:NaN,unitYield:valid?yieldKwh/kwp:NaN,annual:annual,
          payback:valid&&annual>0?net/annual:NaN};
      });
      var specs=[
        ["Gross installed price",function(q){return money.format(q.price);}],
        ["Standard PV grant included",function(q){return money.format(q.grant);}],
        ["After assumed PV grant",function(q){return money.format(q.net);}],
        ["Gross installed €/kWp*",function(q){return money.format(q.perKwp);}],
        ["Annual generation",function(q){return number.format(q.yieldKwh)+" kWh";}],
        ["Generation per kWp",function(q){return number.format(q.unitYield)+" kWh";}],
        ["Battery capacity included",function(q){return number.format(q.battery)+" kWh";}],
        ["Workmanship warranty",function(q){return number.format(q.warranty)+" years";}],
        ["Illustrative annual energy value",function(q){return money.format(q.annual);}],
        ["Simple payback estimate",function(q){return Number.isFinite(q.payback)?number.format(q.payback)+" years":"Not reached";}]
      ];
      table.replaceChildren();
      specs.forEach(function(spec){var tr=create(table,"tr");create(tr,"td","",spec[0]);quotes.forEach(function(q){create(tr,"td","",q.valid?spec[1](q):"—");});});
      bars.replaceChildren();
      var validQuotes=quotes.filter(function(q){return q.valid;}),maxCost=Math.max.apply(null,validQuotes.map(function(q){return q.perKwp;}).concat([1]));
      validQuotes.forEach(function(q){
        var r=create(bars,"div","sol-bar-row");create(r,"span","", "Quote "+q.id.toUpperCase());var track=create(r,"div","sol-bar-track");
        var fill=create(track,"span","sol-bar-fill");fill.style.width=Math.max(2,100*q.perKwp/maxCost).toFixed(1)+"%";
        create(r,"strong","",money.format(q.perKwp)+"/kWp");
      });
      var mixed=validQuotes.some(function(q){return q.battery>0;});
      var msg=validQuotes.length<2?"Enter at least two complete quotes to compare.":"Comparison uses your shared electricity assumptions; verify each company's predicted annual yield.";
      if(validQuotes.length>=2&&mixed)msg+=" Battery-inclusive prices are not comparable with solar-only €/kWp and the model excludes separate battery benefits.";
      else if(validQuotes.length>=2)msg+=" Gross €/kWp is a starting metric, not a quality ranking.";
      setText(root.querySelector("[data-sq-summary]"),msg);
    }
    root.addEventListener("input",function(){solarTrackOnce(root,'solarUsed','quote_comparison_used');calcQuotes();});
    root.addEventListener("change",calcQuotes);
    var printer=root.querySelector('[data-sq-print]');
    if(printer)printer.addEventListener('click',function(){solarTrack('quote_comparison_printed');window.print();});
    calcQuotes();
  }

  var grants=document.querySelector("[data-solar-grants]");
  if(grants){
    function gv(key){return grants.querySelector('[data-sg="'+key+'"]');}
    function calcGrants(){
      var kwp=value(gv("kwp"),0,100),battery=value(gv("battery"),0,200);
      var common=gv("age").value==="yes"&&gv("mprn").value==="yes";
      var pv=common&&gv("priorpv").value==="no"?pvGrant(kwp):0;
      // SEAI permits a battery-only application, including a later upgrade after existing solar PV.
      var bg=common&&gv("priorbattery").value==="no"&&Number.isFinite(battery)&&battery>=5?600:0;
      var total=pv+bg;
      setText(grants.querySelector("[data-sg-total]"),money.format(total));
      setText(grants.querySelector("[data-sg-pv]"),money.format(pv));
      setText(grants.querySelector("[data-sg-battery]"),money.format(bg));
      var message=!common?"Basic property/MPRN conditions are not confirmed; this estimate excludes both grants.":
        total>0?"Potential standard grant under the entries above, subject to SEAI review, registered installation and approval before work begins.":
        "No standard grant is modelled for these inputs. Check with SEAI, particularly for an enhanced scheme.";
      setText(grants.querySelector("[data-sg-msg]"),message);
    }
    grants.addEventListener("input",function(){solarTrackOnce(grants,'solarUsed','grant_checker_used');calcGrants();});
    grants.addEventListener("change",function(){solarTrackOnce(grants,'solarUsed','grant_checker_used');calcGrants();});
    calcGrants();
  }
  var sizing=document.querySelector("[data-solar-size]");
  if(sizing){
    function calcSize(){
      var demand=value(sizing.querySelector('[data-ss="demand"]'),0,100000),kwhPerKwp=value(sizing.querySelector('[data-ss="yield"]'),100,1500);
      var estimate=Number.isFinite(demand)&&Number.isFinite(kwhPerKwp)&&kwhPerKwp>0?demand/kwhPerKwp:NaN;
      setText(sizing.querySelector("[data-ss-size]"),Number.isFinite(estimate)?round(estimate)+" kWp":"—");
      setText(sizing.querySelector("[data-ss-explain]"),Number.isFinite(estimate)?"This produces roughly the same annual energy as you consume, not necessarily the most economical array.":"Enter positive household demand and generation assumptions.");
    }
    sizing.addEventListener("input",function(){solarTrackOnce(sizing,'solarUsed','size_estimator_used');calcSize();});calcSize();
  }
  var checklist=document.querySelector('[data-solar-checklist]');
  if(checklist){
    var checks=Array.prototype.slice.call(checklist.querySelectorAll('[data-sol-check]'));
    function updateChecks(){
      var n=checks.filter(function(box){return box.checked;}).length;
      setText(checklist.querySelector('[data-sol-check-count]'),n+' of '+checks.length+' checks complete');
      var progress=checklist.querySelector('[data-sol-check-progress]');if(progress){progress.max=checks.length;progress.value=n;}
      if(n===checks.length)solarTrackOnce(checklist,'solarCompleted','installer_checklist_completed');
    }
    checks.forEach(function(box){box.addEventListener('change',updateChecks);});
    checklist.querySelector('[data-sol-check-reset]').addEventListener('click',function(){checks.forEach(function(b){b.checked=false;});checklist.dataset.solarCompleted='';updateChecks();});
    updateChecks();
  }
  document.querySelectorAll('[data-sol-register]').forEach(function(a){a.addEventListener('click',function(){solarTrack('seai_register_opened');});});
  document.querySelectorAll('[data-sol-partner-email]').forEach(function(a){a.addEventListener('click',function(){solarTrack('installer_pilot_contact');});});
  var county=document.querySelector("[data-solar-county]");
  if(county){var select=county.querySelector("[data-sc-county]");select.addEventListener("change",function(){
    setText(county.querySelector("[data-sc-message]"),select.value?"On SEAI's official register, select "+select.value+" from its county filter. Verify each current company record before requesting a quote.":"Select a county, then search SEAI's live company list.");
  });}
  var brief=document.querySelector("[data-solar-brief]");
  if(brief){
    function bv(k){return brief.querySelector('[data-sb="'+k+'"]');}
    function updateBrief(){
      var demand=value(bv("demand"),0,100000);
      var text=[
        "Subject: Request for an itemised domestic solar PV quotation",
        "",
        "Hello,",
        "",
        "Please provide a written solar PV installation quote for a property in "+bv("county").value+".",
        "Roof: "+bv("roof").value+".",
        "Approximate annual electricity use: "+(Number.isFinite(demand)?number.format(demand)+" kWh":"to be confirmed")+".",
        "Battery preference: "+(bv("battery").value==="quote-both"?"price solar-only and solar-plus-battery separately":bv("battery").value==="solar-only"?"solar-only":"solar plus storage")+".",
        "",
        "Please specify:",
        "1. Solar array size (kWp), number and exact model of panels.",
        "2. Inverter model and rating; battery model and usable kWh if applicable.",
        "3. Expected annual generation (kWh), roof/shading assumptions and monitoring.",
        "4. Fully itemised installed price before grants and VAT treatment.",
        "5. SEAI grant handling, ESB Networks paperwork and post-works BER.",
        "6. Scaffolding, electrical upgrade costs, exclusions and additional charges.",
        "7. Panel, inverter, battery and workmanship warranty terms.",
        "8. Timeline, payment stages, references and aftercare arrangements.",
        "",
        "Please include a clear written contract and explain the grant-approval process before works begin.",
        "",
        "Thank you."
      ].join("\n");
      bv("output").value=text;
      setText(brief.querySelector("[data-sb-copy-status]"),"");
    }
    ["county","demand","battery","roof"].forEach(function(key){bv(key).addEventListener("input",updateBrief);bv(key).addEventListener("change",updateBrief);});
    brief.querySelector("[data-sb-copy]").addEventListener("click",function(){
      var out=bv("output"),status=brief.querySelector("[data-sb-copy-status]");
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(out.value).then(function(){setText(status,"Copied.");solarTrack("quote_brief_copied");},function(){out.focus();out.select();setText(status,"Select and copy the text manually.");});
      }else{out.focus();out.select();setText(status,"Select and copy the text manually.");}
    });updateBrief();
  }
})();
