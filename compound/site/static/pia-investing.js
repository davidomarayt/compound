/* Compound.ie | Educational PIA vs accumulating ETF vs direct shares simulator.
 * Same-return comparisons only; user financial inputs stay in the browser.
 * Proposed PIA and 2027 fund exit-tax rules are not enacted as of 13 Nov 2026.
 */
(function () {
  "use strict";
  const MONTH_ENDS=[31,59,90,120,151,181,212,243,273,304,334,365];
  const formatEUR=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  const euro=n=>formatEUR.format(Number.isFinite(n)?n:0);
  function bounded(v,lower,upper,fallback){
    const n=Number(v);
    return Number.isFinite(n)?Math.max(lower,Math.min(upper,n)):fallback;
  }
  function estimate(input){
    const monthly=bounded(input.monthly,0,1000,500);
    const years=Math.round(bounded(input.years,1,30,10));
    const annualReturn=bounded(input.annual_return,-20,30,6)/100;
    const feePIA=bounded(input.pia_fee,0,5,.25)/100;
    const feeETF=bounded(input.etf_fee,0,5,.25)/100;
    const feeShares=bounded(input.shares_fee,0,5,.25)/100;
    const exitRate=bounded(input.etf_exit_rate,0,50,35)/100;
    const cgtRate=.31;
    const unusedCGTExemption=bounded(input.cgt_exemption,0,1270,1270);
    const dividendYield=bounded(input.dividend_yield,0,15,0)/100;
    const dividendTax=bounded(input.dividend_tax,0,65,40)/100;
    const piaFactor=Math.pow((1+annualReturn)*(1-feePIA),1/365);
    const etfFactor=Math.pow((1+annualReturn)*(1-feeETF),1/365);
    const sharePriceFactor=Math.pow((1+annualReturn)/(1+dividendYield)*(1-feeShares),1/365);
    const shareDividendFactor=Math.pow(1+dividendYield,1/365)-1;
    let pia=0,shares=0,sharesBasis=0;
    let piaTaxes=0,etfDeemedTaxes=0,sharesDividendTaxes=0;
    let netContributed=0;
    const lots=[];
    const chart=[{year:0,pia:0,etf:0,shares:0,etfHolding:0,sharesHolding:0}];
    function etfHypotheticalDisposal(){
      let holding=0,finalTax=0;
      for(const lot of lots){
        holding+=lot.value;
        finalTax+=Math.max(0,lot.value-lot.basis)*exitRate;
      }
      return {holding,tax:finalTax,afterTax:Math.max(0,holding-finalTax)};
    }
    function shareHypotheticalDisposal(){
      const taxable=Math.max(0,shares-sharesBasis-unusedCGTExemption);
      return {tax:taxable*cgtRate,afterTax:Math.max(0,shares-taxable*cgtRate)};
    }
    for(let year=1;year<=years;year++){
      let dailyPIASum=0,month=0;
      for(let day=1;day<=365;day++){
        pia=Math.max(0,pia*piaFactor);
        for(const lot of lots)lot.value=Math.max(0,lot.value*etfFactor);
        shares=Math.max(0,shares*sharePriceFactor);
        // For direct shares, dividends are assumed to be paid throughout the year,
        // personally taxed and immediately reinvested, increasing CGT cost basis.
        const grossDividend=shares*shareDividendFactor;
        const dividendTaxPaid=grossDividend*dividendTax;
        const reinvested=grossDividend-dividendTaxPaid;
        shares+=reinvested;
        sharesBasis+=reinvested;
        sharesDividendTaxes+=dividendTaxPaid;
        if(day===MONTH_ENDS[month]){
          // Each outside-fund purchase lot has its own eight-year anniversary.
          // Simplified: charge positive gain since the last deemed event, fund
          // tax from the holding, and reset the remaining lot's basis.
          for(const lot of lots){
            lot.months+=1;
            if(lot.months%96===0){
              const due=Math.min(lot.value,Math.max(0,lot.value-lot.basis)*exitRate);
              lot.value-=due;
              lot.basis=lot.value;
              etfDeemedTaxes+=due;
            }
          }
          pia+=monthly;
          lots.push({value:monthly,basis:monthly,months:0});
          shares+=monthly;
          sharesBasis+=monthly;
          netContributed+=monthly*3; // Report per-wrapper contribution separately below.
          month++;
        }
        dailyPIASum+=pia;
      }
      const averagePIA=dailyPIASum/365;
      const charge=Math.min(pia,Math.max(0,averagePIA-50000)*.01);
      pia-=charge;
      piaTaxes+=charge;
      const etf=etfHypotheticalDisposal();
      const sh=shareHypotheticalDisposal();
      chart.push({year,pia,etf:etf.afterTax,shares:sh.afterTax,etfHolding:etf.holding,sharesHolding:shares,averagePIA,piaCharge:charge});
    }
    const etf=etfHypotheticalDisposal();
    const sh=shareHypotheticalDisposal();
    return {
      years,monthly,contributed:monthly*12*years,
      pia,etf:etf.afterTax,shares:sh.afterTax,
      etfHolding:etf.holding,sharesHolding:shares,
      piaTaxes,etfDeemedTaxes,etfFinalExitTax:etf.tax,
      sharesCGT:sh.tax,sharesDividendTaxes,
      etfTaxTotal:etfDeemedTaxes+etf.tax,
      shareTaxTotal:sh.tax+sharesDividendTaxes,
      annualReturn,exitRate,cgtRate,unusedCGTExemption,dividendYield,
      rows:chart
    };
  }
  if(typeof module!=="undefined"&&module.exports)module.exports={estimate};
  if(typeof document==="undefined")return;
  const root=document.querySelector("[data-pia-investing-tool]");
  if(!root)return;
  const form=root.querySelector("form");
  const outputs={};
  root.querySelectorAll("[data-pit-result]").forEach(el=>{outputs[el.dataset.pitResult]=el;});
  const info=root.querySelector("[data-pit-explain]");
  const chart=root.querySelector("[data-pit-chart]");
  const tbody=root.querySelector("[data-pit-rows]");
  const warning=root.querySelector("[data-pit-warning]");
  function inputs(){const o={};form.querySelectorAll("[name]").forEach(el=>{o[el.name]=Number(el.value);});return o;}
  function plot(rows){
    const W=760,H=275,left=72,top=18,right=16,bottom=43;
    const peak=Math.max(1,...rows.map(x=>Math.max(x.pia,x.etf,x.shares)))*1.08;
    const x=i=>left+i/(rows.length-1)*(W-left-right);
    const y=v=>top+(1-v/peak)*(H-top-bottom);
    let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Illustrative after-tax liquidation values for the proposed PIA, an outside accumulating ETF, and direct shares over '+(rows.length-1)+' years">';
    for(let i=0;i<=4;i++){
      const v=peak*i/4,yy=y(v);
      svg+='<line x1="'+left+'" y1="'+yy+'" x2="'+(W-right)+'" y2="'+yy+'" stroke="#ddd6d4"/>';
      svg+='<text x="'+(left-8)+'" y="'+(yy+4)+'" text-anchor="end" font-size="11" fill="#514a50">'+euro(v)+'</text>';
    }
    const step=Math.max(1,Math.ceil((rows.length-1)/6));
    rows.forEach((r,i)=>{if(i%step===0||i===rows.length-1)svg+='<text x="'+x(i)+'" y="'+(H-12)+'" text-anchor="middle" font-size="12" fill="#514a50">'+i+'y</text>';});
    [["pia","#a2573a"],["etf","#343f70"],["shares","#366b60"]].forEach(([key,color])=>{
      svg+='<polyline fill="none" stroke="'+color+'" stroke-width="3" stroke-linejoin="round" points="'+rows.map((r,i)=>x(i).toFixed(1)+','+y(r[key]).toFixed(1)).join(" ")+'"/>';
    });
    chart.innerHTML=svg+"</svg>";
  }
  function render(){
    const r=estimate(inputs());
    const set=(key,val)=>{if(outputs[key])outputs[key].textContent=val;};
    set("pia",euro(r.pia));set("etf",euro(r.etf));set("shares",euro(r.shares));
    set("contributed",euro(r.contributed));set("pia-tax",euro(r.piaTaxes));
    set("etf-tax",euro(r.etfTaxTotal));set("shares-tax",euro(r.shareTaxTotal));
    set("etf-gross",euro(r.etfHolding));set("shares-gross",euro(r.sharesHolding));
    info.textContent="All three approaches receive "+euro(r.monthly)+" monthly for "+r.years+" years and use the same assumed pre-tax total return. The results show account value after the modelled PIA charge, or the amount left if the outside ETF or shares were sold at the comparison date.";
    warning.textContent=r.exitRate===.35
      ?"The 35% ETF/fund rate is proposed for 2027 in the Finance (No. 2) Bill, not yet enacted. Change it to 38% to compare the current 2026 rate."
      :"The 38% fund exit-tax rate reflects current 2026 guidance. A 35% rate is proposed for relevant events from 2027, subject to legislation.";
    tbody.replaceChildren();
    r.rows.forEach(row=>{
      if(row.year!==0&&row.year!==r.years&&![5,10,20,30].includes(row.year))return;
      const tr=document.createElement("tr");
      [row.year===0?"Start":row.year+" years",euro(row.pia),euro(row.etf),euro(row.shares)].forEach(value=>{
        const td=document.createElement("td");td.textContent=value;tr.append(td);
      });
      tbody.append(tr);
    });
    plot(r.rows);
    return r;
  }
  function refresh(){if(form.checkValidity())render();}
  form.addEventListener("change",refresh);
  form.addEventListener("input",refresh);
  form.addEventListener("submit",event=>{
    event.preventDefault();
    if(!form.reportValidity())return;
    render();
    try{if(localStorage.getItem("compound_analytics_consent")==="granted"&&typeof window.gtag==="function"){
      window.gtag("event","pia_investing_compare",{tool_name:"pia-vs-ordinary-investing"});
    }}catch(error){}
  });
  render();
})();