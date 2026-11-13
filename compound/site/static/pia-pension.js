/* Compound PIA vs pension: illustrative incremental contributions, browser-only. */
(function () {
  "use strict";
  const monthEnds=[31,59,90,120,151,181,212,243,273,304,334,365];
  const fmt=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  const euro=n=>fmt.format(Math.max(0,Number.isFinite(n)?n:0));
  const bounded=(v,min,max)=>Math.min(max,Math.max(min,Number(v)));
  function calculate(v) {
    const budget=bounded(v.monthly_net,0,1000);
    const years=Math.round(bounded(v.years,1,40));
    const currentAge=Math.round(bounded(v.current_age,18,75));
    const relief=bounded(v.relief_rate,0,40)/100;
    const headroom=bounded(v.relief_headroom,0,100000);
    const employerMonthly=bounded(v.extra_employer,0,10000);
    const annualNet=budget*12;
    // Pension relief is limited to the entered annual headroom, not assumed for all contributions.
    const fullReliefGross=annualNet/(1-relief);
    const pensionEmployeeYear=fullReliefGross<=headroom?fullReliefGross:annualNet+headroom*relief;
    const qualifying=Math.min(headroom,pensionEmployeeYear);
    const reliefValue=qualifying*relief;
    const pensionMonthly=pensionEmployeeYear/12;
    const piaMonthly=budget;
    const annualReturn=bounded(v.return_rate,-20,30)/100;
    const piaFee=bounded(v.pia_fee,0,5)/100;
    const pensionFee=bounded(v.pension_fee,0,5)/100;
    const piaDaily=Math.pow((1+annualReturn)*(1-piaFee),1/365);
    const pensionDaily=Math.pow((1+annualReturn)*(1-pensionFee),1/365);
    let pia=0,pension=0,totalPiaTax=0;
    const rows=[{year:0,pia:0,pension:0}];
    for(let year=1;year<=years;year++){
      let sumDailyPia=0,monthIndex=0;
      for(let day=1;day<=365;day++){
        pia=Math.max(0,pia*piaDaily);
        pension=Math.max(0,pension*pensionDaily);
        if(day===monthEnds[monthIndex]){
          pia+=piaMonthly;
          pension+=pensionMonthly+employerMonthly;
          monthIndex++;
        }
        sumDailyPia+=pia;
      }
      const average=sumDailyPia/365;
      const charge=Math.min(pia,Math.max(0,average-50000)*.01);
      pia=Math.max(0,pia-charge);
      totalPiaTax+=charge;
      rows.push({year,pia,pension,average,piaTax:charge});
    }
    const freePct=bounded(v.tax_free_lump_pct,0,25)/100;
    const freeCap=bounded(v.tax_free_cap,0,200000);
    const freeLump=Math.min(pension*freePct,freeCap);
    // One user-supplied effective deduction assumption on the remaining pension.
    // Not a statutory retirement tax calculation or a projection of drawdown.
    const exitRate=bounded(v.retirement_tax_rate,0,60)/100;
    const illustrativeNetPension=freeLump+(pension-freeLump)*(1-exitRate);
    const endAge=currentAge+years;
    return {
      years,currentAge,endAge,annualNet,monthlyNet:budget,piaMonthly,pensionMonthly,
      pensionEmployeeYear,qualifying,reliefValue,employerMonthly,
      totalPersonal:annualNet*years,
      totalPensionEmployee:pensionEmployeeYear*years,
      totalEmployer:employerMonthly*12*years,
      pia,pension,illustrativeNetPension,freeLump,totalPiaTax,
      pensionAccessWarning:endAge<60,
      rows
    };
  }
  if(typeof module!=="undefined" && module.exports) module.exports={calculate};
  if(typeof document==="undefined")return;
  const root=document.querySelector("[data-pia-pension-tool]");
  if(!root)return;
  const form=root.querySelector("form");
  const error=root.querySelector("[data-pp-error]");
  const outputs={};
  root.querySelectorAll("[data-pp-result]").forEach(el=>{outputs[el.dataset.ppResult]=el;});
  const explanation=root.querySelector("[data-pp-explanation]");
  const chart=root.querySelector("[data-pp-chart]");
  const tableBody=root.querySelector("[data-pp-year-rows]");
  const access=root.querySelector("[data-pp-access]");
  function values(){
    const v={};
    form.querySelectorAll("[name]").forEach(el=>{v[el.name]=Number(el.value);});
    return v;
  }
  function paintChart(rows){
    const W=760,H=265,L=70,R=18,T=18,B=43,usableW=W-L-R,usableH=H-T-B;
    const peak=Math.max(1,...rows.map(r=>Math.max(r.pia,r.pension)));
    const max=peak*1.08;
    const posX=i=>L+(rows.length===1?0:i/(rows.length-1)*usableW);
    const posY=v=>T+(max-v)/max*usableH;
    const series=[
      {key:"pia",stroke:"#99603e",name:"PIA"},
      {key:"pension",stroke:"#282b42",name:"Pension before retirement tax"}
    ];
    let out='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Projected PIA and gross pension balances in euros over '+(rows.length-1)+' years">';
    for(let i=0;i<=4;i++){
      const y=posY(max*i/4);
      out+='<line x1="'+L+'" y1="'+y+'" x2="'+(W-R)+'" y2="'+y+'" stroke="#ddd7d3" stroke-width="1"/>';
      out+='<text x="'+(L-10)+'" y="'+(y+4)+'" text-anchor="end" fill="#5c5660" font-size="12">'+euro(max*i/4)+'</text>';
    }
    const tick=Math.max(1,Math.ceil((rows.length-1)/6));
    rows.forEach((r,i)=>{if(i%tick===0||i===rows.length-1){
      out+='<text x="'+posX(i)+'" y="'+(H-12)+'" text-anchor="middle" fill="#5c5660" font-size="12">'+r.year+'y</text>';
    }});
    series.forEach(s=>{
      out+='<polyline fill="none" stroke="'+s.stroke+'" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="';
      rows.forEach((r,i)=>{out+=posX(i).toFixed(1)+','+posY(r[s.key]).toFixed(1)+' ';});
      out+='"><title>'+s.name+'</title></polyline>';
    });
    out+='</svg>';
    chart.innerHTML=out;
  }
  function render() {
    const data=calculate(values());
    function set(key,val){if(outputs[key])outputs[key].textContent=val;}
    set("pia",euro(data.pia));
    set("pension",euro(data.pension));
    set("pension-net",euro(data.illustrativeNetPension));
    set("pia-tax",euro(data.totalPiaTax));
    set("employee-pension",euro(data.pensionEmployeeYear));
    set("relief",euro(data.reliefValue));
    set("employer",euro(data.employerMonthly*12));
    set("cost",euro(data.annualNet));
    set("total-cost",euro(data.totalPersonal));
    set("exit-lump",euro(data.freeLump));
    set("year-age",String(data.endAge));
    const qualifies=data.qualifying<data.pensionEmployeeYear-0.01;
    explanation.textContent="For the same "+euro(data.monthlyNet)+" monthly take-home cost, the model puts "+
      euro(data.piaMonthly)+" a month into the proposed PIA and "+euro(data.pensionMonthly)+
      " a month into the pension. "+(data.employerMonthly?"It adds "+euro(data.employerMonthly)+
      " monthly from the employer. ":"")+ (qualifies?"Only part of the pension contribution qualifies for the selected tax relief headroom. ":"")+
      "Investment performance, fees and retirement tax could change which outcome provides more usable money.";
    access.textContent=data.pensionAccessWarning
      ?"At age "+data.endAge+", this model's pension value is NOT an amount you can assume you may withdraw. Normal pension access rules and scheme exceptions must be checked."
      :"At age "+data.endAge+", pension access is still subject to the particular scheme's rules. The after-tax pension figure is illustrative, not a pension provider or Revenue quote.";
    tableBody.replaceChildren();
    data.rows.forEach(r=>{
      if(r.year!==0 && r.year!==data.years && r.year%5!==0)return;
      const tr=document.createElement("tr");
      [r.year===0?"Start":"Year "+r.year,euro(r.pia),euro(r.pension)].forEach(value=>{
        const cell=document.createElement("td");cell.textContent=value;tr.appendChild(cell);
      });
      tableBody.appendChild(tr);
    });
    paintChart(data.rows);
    return data;
  }
  form.addEventListener("input",()=>{
    if(!form.checkValidity()){error.textContent="Check the highlighted inputs to calculate.";return;}
    error.textContent="";render();
  });
  form.addEventListener("submit",event=>{
    event.preventDefault();
    if(!form.reportValidity()){error.textContent="Correct the inputs before calculating.";return;}
    error.textContent="";render();
    try{
      if(localStorage.getItem("compound_analytics_consent")==="granted" && typeof window.gtag==="function"){
        window.gtag("event","pia_pension_calculate",{tool_name:"pia-vs-pension"});
      }
    }catch(err){}
  });
  render();
})();