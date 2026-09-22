(() => {
  const euro = new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:2});
  const number = new Intl.NumberFormat('en-IE',{maximumFractionDigits:2});
  const pct = v => number.format(v) + '%';
  const money = v => euro.format(Number.isFinite(v) ? v : 0);
  const num = v => number.format(Number.isFinite(v) ? v : 0);
  const duration = months => {
    if (!Number.isFinite(months)) return 'Not reached';
    if (months <= 0) return 'Already reached';
    const y = Math.floor(months/12), m = Math.round(months%12);
    if (!y) return m + ' month' + (m===1?'':'s');
    if (!m) return y + ' year' + (y===1?'':'s');
    return y + ' yr ' + m + ' mo';
  };
  const monthlyPayment = (p, annual, months) => {
    if (months <= 0) return NaN;
    const r = annual/100/12;
    return r === 0 ? p/months : p*r/(1-Math.pow(1+r,-months));
  };
  const parseDateOnly = value => {
    if(!value) return null;
    const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if(!m) return null;
    const d=new Date(Date.UTC(Number(m[1]),Number(m[2])-1,Number(m[3])));
    return Number.isNaN(d.getTime())?null:d;
  };
  const addDaysUTC = (date,days) => new Date(date.getTime()+days*86400000);
  const formatDateIE = date => new Intl.DateTimeFormat('en-IE',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(date);
  const balloonPayment = (principal, annual, months, balloon) => {
    if(months<=0) return NaN;
    const r=annual/100/12, p=Math.max(0,principal), b=Math.max(0,balloon);
    if(r===0) return Math.max(0,(p-b)/months);
    const pvBalloon=b/Math.pow(1+r,months);
    return Math.max(0,(p-pvBalloon)*r/(1-Math.pow(1+r,-months)));
  };
  const lptBands = [
    [240000,95],[315000,235],[420000,333],[525000,428],[630000,523],[735000,618],[840000,713],
    [945000,808],[1050000,903],[1155000,998],[1260000,1094],[1365000,1272],[1470000,1535],
    [1575000,1797],[1680000,2060],[1785000,2322],[1890000,2585],[1995000,2847],[2100000,3110]
  ];
  const lptAdjust = {
    carlow:.15,cavan:.15,clare:.15,cork_city:.12,cork_county:.15,donegal:.15,dublin_city:0,dlr:-.15,
    fingal:-.05,galway_city:.15,galway_county:.15,kerry:.10,kildare:.10,kilkenny:.15,laois:.15,
    leitrim:.15,limerick:.15,longford:.15,louth:0,mayo:.10,meath:0,monaghan:.15,offaly:.15,
    roscommon:.15,sligo:.15,south_dublin:-.075,tipperary:.15,waterford:.15,westmeath:.15,wexford:.15,wicklow:.06
  };
  const pensionPct = age => age < 30 ? .15 : age < 40 ? .20 : age < 50 ? .25 : age < 55 ? .30 : age < 60 ? .35 : .40;

  const incomeTax2026 = (income, band, credits) => {
    const taxable=Math.max(0,income), standard=Math.min(taxable,Math.max(0,band));
    const gross=standard*.20 + Math.max(0,taxable-standard)*.40;
    return {taxable,standard,higher:Math.max(0,taxable-standard),gross,net:Math.max(0,gross-Math.max(0,credits))};
  };
  const usc2026 = income => {
    const x=Math.max(0,income);
    if(x<=13000) return 0;
    let left=x, tax=0;
    const bands=[[12012,.005],[16688,.02],[41344,.03],[Infinity,.08]];
    for(const [size,rate] of bands){ const slice=Math.min(left,size); if(slice<=0) break; tax+=slice*rate; left-=slice; }
    return tax;
  };
  const weeklyPrsiCredit = weekly => weekly>352 && weekly<=424 ? Math.max(0,12-(weekly-352.01)/6) : 0;
  const weeklyClassA = (weekly,rate) => weekly<=352 ? 0 : Math.max(0,weekly*rate-weeklyPrsiCredit(weekly));
  const annualClassA2026 = salary => {
    const weekly=Math.max(0,salary)/52;
    const before=weeklyClassA(weekly,.042), after=weeklyClassA(weekly,.0435);
    return {weekly,before,after,annual:before*39+after*13};
  };
  const employeeNet2026 = (salary,pension,band=44000,extraCredits=0) => {
    const employeeCredit=Math.min(2000,Math.max(0,salary)*.20);
    const credits=2000+employeeCredit+Math.max(0,extraCredits);
    const tax=incomeTax2026(Math.max(0,salary-pension),band,credits).net;
    const usc=usc2026(salary), prsi=annualClassA2026(salary).annual;
    return {tax,usc,prsi,credits,net:salary-pension-tax-usc-prsi};
  };
  const selfEmployedNet2026 = (profit,pension=0) => {
    const x=Math.max(0,profit), earnedCredit=Math.min(2000,x*.20), credits=2000+earnedCredit;
    const tax=incomeTax2026(Math.max(0,x-pension),44000,credits).net;
    const usc=usc2026(x);
    const prsi=x<5000?0:Math.max(650,x*.042375);
    return {tax,usc,prsi,credits,net:x-pension-tax-usc-prsi};
  };
  const stampDutyResidential = price => Math.min(price,1000000)*.01 + Math.max(0,Math.min(price,1500000)-1000000)*.02 + Math.max(0,price-1500000)*.06;
  const projectMonthly = (initial,monthly,annualRate,years) => {
    const r=annualRate/100/12, points=[Math.max(0,initial)]; let bal=Math.max(0,initial);
    for(let y=1;y<=years;y++){ for(let m=0;m<12;m++){ bal*=1+r; bal+=monthly; } points.push(bal); }
    return points;
  };

  const amortisationSeries = (principal,annual,months,payment) => {
    const r=annual/100/12, values=[Math.max(0,principal)], labels=['Start']; let bal=Math.max(0,principal);
    for(let m=1;m<=months && bal>0.005;m++){
      const interest=bal*r;
      bal=Math.max(0,bal+interest-payment);
      if(m%12===0 || m===months || bal<=0.005){ values.push(bal); labels.push(m%12===0?'Year '+(m/12):'Month '+m); }
    }
    return {labels,values};
  };
  const fallbackChart = (name,v) => {
    switch(name){
      case 'mortgage': {
        const months=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,months), s=amortisationSeries(v.amount,v.rate,months,p);
        return {type:'line',title:'Mortgage balance over time',caption:'Scheduled balance if the entered rate stayed unchanged for the full term.',labels:s.labels,series:[{label:'Mortgage balance',values:s.values}]};
      }
      case 'mortgage_overpayment': {
        const months=Math.round(v.years*12), base=monthlyPayment(v.balance,v.rate,months);
        const a=amortisationSeries(v.balance,v.rate,months,base), b=amortisationSeries(v.balance,v.rate,months,base+v.overpayment);
        const n=Math.max(a.values.length,b.values.length), labels=Array.from({length:n},(_,i)=>i===0?'Start':'Year '+i);
        const pad=arr=>Array.from({length:n},(_,i)=>arr[i]??0);
        return {type:'line',title:'How the balance falls',caption:'Standard repayment versus the monthly overpayment scenario.',labels,series:[{label:'Standard',values:pad(a.values)},{label:'With overpayment',values:pad(b.values)}]};
      }
      case 'mortgage_borrowing': {
        const multiple=v.buyer_type==='ftb'?4:3.5, byIncome=v.income*multiple+v.deposit, byDeposit=v.deposit/.10;
        return {type:'bar',title:'Which constraint is tighter?',caption:'Indicative purchase price supported by income versus the 10% deposit assumption.',labels:['Income + deposit','Deposit constraint'],series:[{label:'Purchase price',values:[byIncome,byDeposit]}]};
      }
      case 'house_deposit': {
        const rate=v.buyer_type==='btl'?.30:.10;
        return {type:'bar',title:'How the purchase is funded',caption:'Deposit and mortgage amounts implied by the selected LTV assumption.',labels:['Deposit','Mortgage'],series:[{label:'Amount',values:[v.price*rate,v.price*(1-rate)]}]};
      }
      case 'stamp_duty': {
        const p=v.price, a=Math.min(p,1000000)*.01, b=Math.max(0,Math.min(p,1500000)-1000000)*.02, d=Math.max(0,p-1500000)*.06;
        return {type:'bar',title:'Stamp Duty by rate band',caption:'Each rate applies only to the relevant slice of the residential consideration.',labels:['1% band','2% band','6% band'],series:[{label:'Duty',values:[a,b,d]}]};
      }
      case 'lpt': {
        let base=0; if(v.value<=2100000){const band=lptBands.find(b=>v.value<=b[0]);base=band?band[1]:0;} else {base=1260000*.000906+(2100000-1260000)*.0025+(v.value-2100000)*.003;}
        const total=base*(1+(lptAdjust[v.authority]??0));
        return {type:'bar',title:'Basic versus locally adjusted LPT',caption:'The local adjustment is applied to the basic amount.',labels:['Basic LPT','After local adjustment'],series:[{label:'Annual LPT',values:[base,total]}]};
      }
      case 'loan': {
        const months=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,months), s=amortisationSeries(v.amount,v.rate,months,p);
        return {type:'line',title:'Loan balance over time',caption:'Scheduled balance under the entered fixed-rate assumptions.',labels:s.labels,series:[{label:'Loan balance',values:s.values}]};
      }
      case 'savings_goal': {
        const r=v.rate/100/12, labels=['Start'], vals=[v.current], target=[v.target]; let bal=v.current;
        for(let m=1;m<=1200 && bal<v.target;m++){bal*=1+r;bal+=v.monthly;if(m%12===0||bal>=v.target){labels.push('Year '+Math.ceil(m/12));vals.push(bal);target.push(v.target);}}
        return {type:'line',title:'Path to the savings goal',caption:'Modelled balance against the target using the contribution and return assumptions entered.',labels,series:[{label:'Projected balance',values:vals},{label:'Target',values:target}]};
      }
      case 'regular_savings': {
        const bal=projectMonthly(v.current,v.monthly,v.rate,Math.round(v.years)), contrib=Array.from({length:Math.round(v.years)+1},(_,i)=>v.current+v.monthly*12*i);
        return {type:'line',title:'Contributions versus projected balance',caption:'Shows how much comes from money added versus modelled growth.',labels:bal.map((_,i)=>i===0?'Start':'Year '+i),series:[{label:'Projected balance',values:bal},{label:'Contributions',values:contrib}]};
      }
      case 'pension_relief': {
        const earnings=Math.min(v.earnings,115000), limit=earnings*pensionPct(v.age), eligible=Math.min(v.contribution,limit), relief=eligible*(Number(v.tax_rate)/100);
        return {type:'bar',title:'Contribution and tax-relief envelope',caption:'Illustrative personal contribution amounts under the entered age, earnings and tax-rate assumptions.',labels:['Contribution','Eligible','Tax relief','Net cost'],series:[{label:'Amount',values:[v.contribution,eligible,relief,v.contribution-relief]}]};
      }
      case 'cgt': {
        const gain=v.sale-v.purchase-v.costs, taxable=Math.max(0,Math.max(0,gain-v.losses)-1270), tax=taxable*.33;
        return {type:'bar',title:'From gain to estimated CGT',caption:'Shows the gain, taxable amount after entered losses/exemption, and estimated tax.',labels:['Gain','Taxable gain','CGT'],series:[{label:'Amount',values:[Math.max(0,gain),taxable,tax]}]};
      }
      case 'vat': {
        const r=Number(v.rate)/100; let net,vat,gross;if(v.direction==='gross'){gross=v.amount;net=r===0?gross:gross/(1+r);vat=gross-net;}else{net=v.amount;vat=net*r;gross=net+vat;}
        return {type:'bar',title:'Net, VAT and gross price',caption:'A simple breakdown at the selected VAT rate.',labels:['Net','VAT','Gross'],series:[{label:'Amount',values:[net,vat,gross]}]};
      }
      case 'inflation': {
        const years=Math.round(v.years), labels=Array.from({length:years+1},(_,i)=>i===0?'Today':'Year '+i);
        const future=labels.map((_,i)=>v.amount*Math.pow(1+v.rate/100,i)), power=labels.map((_,i)=>v.amount/Math.pow(1+v.rate/100,i));
        return {type:'line',title:'Inflation compounds in both directions',caption:'Future cost of today’s amount and purchasing power of a fixed nominal amount.',labels,series:[{label:'Future cost',values:future},{label:'Purchasing power',values:power}]};
      }
      case 'emergency': {
        const target=v.expenses*Number(v.months);
        return {type:'bar',title:'Emergency-fund position',caption:'Current reserve compared with the target and remaining gap.',labels:['Current','Target','Gap'],series:[{label:'Amount',values:[v.current,target,Math.max(0,target-v.current)]}]};
      }
      case 'ev': {
        const battery=v.distance*v.efficiency/100, wall=battery/(1-v.loss/100);
        return {type:'bar',currency:false,title:'Battery energy versus grid energy',caption:'Charging losses mean the grid supplies more energy than reaches the battery.',labels:['Battery','From grid'],series:[{label:'kWh',values:[battery,wall]}]};
      }
      case 'electricity': {
        const monthly=v.watts/1000*v.hours*v.days*v.price, labels=Array.from({length:12},(_,i)=>'M'+(i+1)), vals=labels.map((_,i)=>monthly*(i+1));
        return {type:'line',title:'Cumulative running cost over a year',caption:'Assumes the same monthly usage pattern continues for 12 months.',labels,series:[{label:'Cumulative cost',values:vals}]};
      }
      case 'usc_2026': {
        const x=Math.max(0,v.income); if(x<=13000) return null; let left=x; const vals=[]; for(const [size,rate] of [[12012,.005],[16688,.02],[41344,.03],[Infinity,.08]]){const slice=Math.min(left,size);vals.push(Math.max(0,slice*rate));left-=slice;if(left<=0){while(vals.length<4)vals.push(0);break;}}
        return {type:'bar',title:'USC by rate band',caption:'Each rate applies only to income within that USC band.',labels:['0.5%','2%','3%','8%'],series:[{label:'USC',values:vals}]};
      }
      case 'cat': {
        const thresholds={A:400000,B:40000,C:20000}, threshold=thresholds[v.group]||0, remaining=Math.max(0,threshold-v.prior), small=v.benefit_type==='gift'?Math.min(3000,v.benefit):0, current=Math.max(0,v.benefit-small), afterTax=Math.max(0,v.prior+current-threshold)*.33, beforeTax=Math.max(0,v.prior-threshold)*.33;
        return {type:'bar',title:'Benefit versus remaining CAT threshold',caption:'Uses the selected relationship group and prior aggregated benefits.',labels:['Current benefit','Threshold remaining','Estimated CAT'],series:[{label:'Amount',values:[current,remaining,Math.max(0,afterTax-beforeTax)]}]};
      }
      case 'rent_credit': {
        const rentBased=v.rent*.20, cap=v.joint==='yes'?2000:1000, credit=Math.min(rentBased,cap,v.income_tax_liability);
        return {type:'bar',title:'What limits the Rent Tax Credit?',caption:'The claim is constrained by rent-based calculation, statutory cap and available Income Tax liability.',labels:['Rent-based','Statutory cap','Usable credit'],series:[{label:'Amount',values:[rentBased,cap,Math.max(0,credit)]}]};
      }
      case 'help_to_buy': {
        const valueCap=v.property_value*.10, ltv=v.property_value>0?v.mortgage/v.property_value*100:0, basic=v.property_value<=500000&&ltv>=70, claim=basic?Math.min(30000,valueCap,v.tax_paid):0;
        return {type:'bar',title:'Help to Buy constraints',caption:'Illustrates the property-value cap, qualifying tax paid and resulting basic claim estimate.',labels:['10% value cap','Tax paid','Estimated claim'],series:[{label:'Amount',values:[valueCap,v.tax_paid,claim]}]};
      }
      case 'first_home_scheme': {
        const htb=v.htb==='yes'?Math.min(v.htb_amount,v.property_value):0, gap=Math.max(0,v.property_value-v.mortgage-v.deposit-htb), max=v.property_value*(v.htb==='yes'?.20:.30);
        return {type:'bar',title:'Funding gap versus scheme maximum',caption:'A funding-stack view before formal eligibility and property-price-ceiling checks.',labels:['Funding gap','Maximum share'],series:[{label:'Amount',values:[gap,max]}]};
      }
      case 'dirt': {
        const tax=v.interest*.33, net=v.interest-tax;
        return {type:'bar',title:'Gross interest after DIRT',caption:'Shows the entered gross deposit interest, DIRT and amount retained.',labels:['Gross interest','DIRT','Net interest'],series:[{label:'Amount',values:[v.interest,tax,net]}]};
      }
      default: return null;
    }
  };
  const compact = new Intl.NumberFormat('en-IE',{notation:'compact',maximumFractionDigits:1});
  const esc = s => String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const renderToolChart = (root,spec) => {
    const panel=root.querySelector('[data-tool-chart]'); if(!panel) return;
    if(!spec || !spec.labels || !spec.series || !spec.series.length){ panel.hidden=true; return; }
    panel.hidden=false;
    const title=panel.querySelector('[data-chart-title]'), caption=panel.querySelector('[data-chart-caption]');
    if(title) title.textContent=spec.title||'Scenario chart';
    if(caption) caption.textContent=spec.caption||'';
    const labels=spec.labels.map(String), series=spec.series.filter(s=>Array.isArray(s.values));
    const all=series.flatMap(s=>s.values).filter(Number.isFinite);
    if(!all.length){ panel.hidden=true; return; }
    let min=Math.min(0,...all), max=Math.max(0,...all); if(max===min){max=min+1;}
    const W=760,H=300,L=64,R=24,T=18,B=54,plotW=W-L-R,plotH=H-T-B;
    const y=v=>T+(max-v)/(max-min)*plotH;
    let svg='<svg class="tool-chart-svg" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(spec.title||'Calculator chart')+'">';
    for(let i=0;i<=4;i++){const val=min+(max-min)*i/4, yy=y(val);svg+='<line class="tool-chart-grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+yy.toFixed(1)+'" y2="'+yy.toFixed(1)+'"/><text class="tool-chart-axis" x="'+(L-8)+'" y="'+(yy+4).toFixed(1)+'" text-anchor="end">'+esc((spec.currency===false?compact.format(val):'€'+compact.format(val)))+'</text>';}
    const zeroY=y(0); svg+='<line class="tool-chart-grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+zeroY.toFixed(1)+'" y2="'+zeroY.toFixed(1)+'"/>';
    if(spec.type==='bar'){
      const n=Math.max(1,labels.length), group=plotW/n, totalBar=Math.min(group*.72,80), bw=totalBar/Math.max(1,series.length);
      labels.forEach((lab,i)=>{ const cx=L+group*(i+.5); svg+='<text class="tool-chart-axis" x="'+cx.toFixed(1)+'" y="'+(H-18)+'" text-anchor="middle">'+esc(lab)+'</text>'; series.forEach((s,j)=>{const v=Number(s.values[i])||0,x=cx-totalBar/2+j*bw,yy=y(Math.max(0,v)),y0=y(Math.min(0,v)),top=Math.min(yy,y0),h=Math.max(1,Math.abs(y0-yy));svg+='<rect class="tool-chart-bar tool-chart-series-'+(j%3)+(v<0?' tool-chart-negative':'')+'" x="'+x.toFixed(1)+'" y="'+top.toFixed(1)+'" width="'+Math.max(2,bw-3).toFixed(1)+'" height="'+h.toFixed(1)+'"><title>'+esc(s.label)+': '+esc(money(v))+'</title></rect>';});});
    } else {
      const n=Math.max(1,labels.length-1);
      series.forEach((s,j)=>{let pts='';s.values.forEach((v,i)=>{const x=L+plotW*(i/n),yy=y(Number(v)||0);pts+=x.toFixed(1)+','+yy.toFixed(1)+' ';});svg+='<polyline class="tool-chart-line tool-chart-series-'+(j%3)+'" points="'+pts.trim()+'"/>';s.values.forEach((v,i)=>{if(i===0||i===s.values.length-1||i%Math.max(1,Math.ceil(s.values.length/12))===0){const x=L+plotW*(i/n),yy=y(Number(v)||0);svg+='<circle class="tool-chart-point tool-chart-series-'+(j%3)+'" cx="'+x.toFixed(1)+'" cy="'+yy.toFixed(1)+'" r="4"><title>'+esc(labels[i])+': '+esc(s.label)+' '+esc(money(Number(v)||0))+'</title></circle>';}});});
      const ticks=[0,Math.round(n*.25),Math.round(n*.5),Math.round(n*.75),n].filter((v,i,a)=>a.indexOf(v)===i);
      ticks.forEach(i=>{const x=L+plotW*(i/n);svg+='<text class="tool-chart-axis" x="'+x.toFixed(1)+'" y="'+(H-18)+'" text-anchor="middle">'+esc(labels[i])+'</text>';});
    }
    svg+='</svg>';
    const canvas=panel.querySelector('[data-chart-canvas]'); if(canvas) canvas.innerHTML=svg;
    const legend=panel.querySelector('[data-chart-legend]'); if(legend) legend.innerHTML=series.map((s,i)=>'<span><i class="series-'+(i%3)+'"></i>'+esc(s.label)+'</span>').join('');
  };

  const calculators = {
    mortgage(v){
      const n=v.years*12, p=monthlyPayment(v.amount,v.rate,n), total=p*n;
      return {monthly:money(p),interest:money(total-v.amount),total:money(total)};
    },
    mortgage_overpayment(v){
      const n=Math.round(v.years*12), base=monthlyPayment(v.balance,v.rate,n), pay=base+v.overpayment, r=v.rate/100/12;
      let b=v.balance, interest=0, months=0;
      while(b>0.005 && months<1200){
        const i=b*r;
        interest+=i;
        if(pay<=i && b>0) return {payment:money(base),new_payment:money(pay),time_saved:'Loan would not amortise',interest_saved:'—'};
        b=Math.max(0,b+i-pay); months++;
      }
      const standardInterest=base*n-v.balance;
      return {payment:money(base),new_payment:money(pay),time_saved:duration(Math.max(0,n-months)),interest_saved:money(Math.max(0,standardInterest-interest))};
    },
    mortgage_borrowing(v){
      const multiple=v.buyer_type==='ftb'?4:3.5, lti=v.income*multiple, depPrice=v.deposit/.10, maxPrice=Math.min(lti+v.deposit,depPrice);
      return {lti_limit:money(lti),deposit_limit:money(depPrice),purchase_price:money(Math.max(0,maxPrice))};
    },
    house_deposit(v){
      const rate=v.buyer_type==='btl'?.30:.10, dep=v.price*rate;
      return {deposit_rate:pct(rate*100),deposit:money(dep),mortgage:money(v.price-dep)};
    },
    stamp_duty(v){
      const p=v.price;
      const duty=Math.min(p,1000000)*.01 + Math.max(0,Math.min(p,1500000)-1000000)*.02 + Math.max(0,p-1500000)*.06;
      return {duty:money(duty),effective_rate:pct(p?duty/p*100:0),total_cost:money(p+duty)};
    },
    lpt(v){
      let base=0;
      if(v.value<=2100000){ const band=lptBands.find(b=>v.value<=b[0]); base=band?band[1]:0; }
      else { base=1260000*.000906 + (2100000-1260000)*.0025 + (v.value-2100000)*.003; }
      const factor=lptAdjust[v.authority]??0, adj=base*factor, total=base+adj;
      return {base_lpt:money(base),adjustment:(factor>=0?'+':'')+money(adj),lpt:money(total)};
    },
    loan(v){
      const n=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,n), total=p*n;
      return {monthly:money(p),interest:money(total-v.amount),total:money(total)};
    },
    savings_goal(v){
      if(v.current>=v.target) return {time:'Already reached',contributions:money(0),growth:money(0)};
      const r=v.rate/100/12; let bal=v.current, months=0, contributed=0;
      while(bal<v.target && months<1200){
        bal*=1+r; bal+=v.monthly; contributed+=v.monthly; months++;
        if(v.monthly<=0 && r<=0) break;
      }
      return {time:bal>=v.target?duration(months):'Not reached within 100 years',contributions:money(contributed),growth:money(bal-v.current-contributed)};
    },
    net_worth(v){
      const advanced=Boolean(v.__advanced);
      const cash=Math.max(0,v.cash), investments=Math.max(0,v.investments), pensions=Math.max(0,v.pensions), home=Math.max(0,v.home_value);
      const otherProperty=advanced?Math.max(0,v.other_property):0;
      const vehicles=advanced?Math.max(0,v.vehicles):0;
      const business=advanced?Math.max(0,v.business_value):0;
      const otherAssets=advanced?Math.max(0,v.other_assets):0;
      const mortgage=Math.max(0,v.mortgage);
      const otherPropertyMortgage=advanced?Math.max(0,v.other_property_mortgage):0;
      const loans=Math.max(0,v.loans), cards=Math.max(0,v.credit_cards), otherDebt=Math.max(0,v.other_debt);
      const taxLiabilities=advanced?Math.max(0,v.tax_liabilities):0;

      const totalAssets=cash+investments+pensions+home+otherProperty+vehicles+business+otherAssets;
      const totalLiabilities=mortgage+otherPropertyMortgage+loans+cards+otherDebt+taxLiabilities;
      const net=totalAssets-totalLiabilities;
      const propertyEquity=home+otherProperty-mortgage-otherPropertyMortgage;
      const financialAssets=cash+investments+pensions;
      const netExPension=net-pensions;
      const debtAsset=totalAssets>0?totalLiabilities/totalAssets*100:null;

      const labels=['Cash','Investments','Pensions','Main home'];
      const values=[cash,investments,pensions,home];
      if(advanced){
        if(otherProperty>0){labels.push('Other property');values.push(otherProperty);}
        if(vehicles>0){labels.push('Vehicles');values.push(vehicles);}
        if(business>0){labels.push('Business');values.push(business);}
        if(otherAssets>0){labels.push('Other assets');values.push(otherAssets);}
      }
      labels.push('All liabilities'); values.push(-totalLiabilities);

      return {
        net_worth:money(net),
        total_assets:money(totalAssets),
        total_liabilities:money(totalLiabilities),
        property_equity:money(propertyEquity),
        financial_assets:money(financialAssets),
        net_ex_pension:money(netExPension),
        debt_asset_ratio:debtAsset===null?'Not meaningful with €0 assets':pct(debtAsset),
        __chart:{
          type:'bar',
          title:'What is driving your balance sheet?',
          caption:'Asset categories are shown above zero. Total liabilities are shown below zero so you can see the scale of debt against the assets entered.',
          labels,
          series:[{label:'Balance-sheet value',values}]
        }
      };
    },
    regular_savings(v){
      const months=Math.round(v.years*12), r=v.rate/100/12; let bal=v.current;
      for(let i=0;i<months;i++){ bal*=1+r; bal+=v.monthly; }
      const contributed=v.current+v.monthly*months;
      return {final:money(bal),contributed:money(contributed),growth:money(bal-contributed)};
    },
    pension_relief(v){
      const earnings=Math.min(v.earnings,115000), limit=earnings*pensionPct(v.age), eligible=Math.min(v.contribution,limit), relief=eligible*(Number(v.tax_rate)/100);
      return {limit:money(limit),eligible:money(eligible),relief:money(relief),net_cost:money(v.contribution-relief)};
    },
    cgt(v){
      const gain=v.sale-v.purchase-v.costs, afterLoss=Math.max(0,gain-v.losses), taxable=Math.max(0,afterLoss-1270), tax=taxable*.33;
      return {gain:money(gain),taxable:money(taxable),tax:money(tax)};
    },
    vat(v){
      const r=Number(v.rate)/100; let net,vat,gross;
      if(v.direction==='gross'){ gross=v.amount; net=r===0?gross:gross/(1+r); vat=gross-net; }
      else { net=v.amount; vat=net*r; gross=net+vat; }
      return {net:money(net),vat:money(vat),gross:money(gross)};
    },
    inflation(v){
      const factor=Math.pow(1+v.rate/100,v.years), future=v.amount*factor, power=factor===0?0:v.amount/factor;
      return {future_cost:money(future),purchasing_power:money(power),lost_power:money(v.amount-power)};
    },
    emergency(v){
      const target=v.expenses*Number(v.months), gap=Math.max(0,target-v.current), months=v.monthly>0?Math.ceil(gap/v.monthly):Infinity;
      return {target:money(target),gap:money(gap),time:gap===0?'Already reached':duration(months)};
    },
    salary_hourly(v){
      const weekly=v.weeks?v.salary/v.weeks:0, monthly=v.salary/12, daily=v.days?weekly/v.days:0, hourly=(v.hours&&v.weeks)?v.salary/(v.hours*v.weeks):0;
      return {monthly:money(monthly),weekly:money(weekly),daily:money(daily),hourly:money(hourly)};
    },
    fuel(v){
      const distance=v.distance*v.trips, litres=distance*v.consumption/100, cost=litres*v.price, per100=v.consumption*v.price;
      return {litres:num(litres)+' L',cost:money(cost),per100:money(per100)};
    },
    ev(v){
      const battery=v.distance*v.efficiency/100, wall=battery/(1-v.loss/100), cost=wall*v.price, per100=(v.efficiency/(1-v.loss/100))*v.price;
      return {battery_kwh:num(battery)+' kWh',wall_kwh:num(wall)+' kWh',cost:money(cost),per100:money(per100)};
    },
    electricity(v){
      const kwh=v.watts/1000*v.hours*v.days, monthly=kwh*v.price;
      return {kwh:num(kwh)+' kWh',monthly:money(monthly),annual:money(monthly*12)};
    },
    take_home_2026(v){
      const pension=Math.max(0,v.salary*v.pension_pct/100), net=employeeNet2026(v.salary,pension,v.band,v.other_credits);
      return {
        annual_net:money(net.net),monthly_net:money(net.net/12),paye:money(net.tax),usc:money(net.usc),prsi:money(net.prsi),pension:money(pension),
        __chart:{type:'bar',title:'Where the gross salary goes',caption:'Estimated 2026 annual amounts using the inputs above.',labels:['Take-home','PAYE','USC','PRSI','Pension'],series:[{label:'Annual amount',values:[net.net,net.tax,net.usc,net.prsi,pension]}]}
      };
    },
    income_tax_2026(v){
      const t=incomeTax2026(Math.max(0,v.income-v.pension),v.band,v.credits);
      return {
        taxable:money(t.taxable),tax20:money(t.standard*.20),tax40:money(t.higher*.40),gross_tax:money(t.gross),final_tax:money(t.net),
        __chart:{type:'bar',title:'Income Tax calculation',caption:'Tax charged in each band, before and after the credits entered.',labels:['20% band tax','40% band tax','Credits','Final tax'],series:[{label:'Amount',values:[t.standard*.20,t.higher*.40,Math.min(v.credits,t.gross),t.net]}]}
      };
    },
    usc_2026(v){
      const u=usc2026(v.income); return {usc:money(u),effective:pct(v.income?u/v.income*100:0),monthly:money(u/12)};
    },
    prsi_2026(v){
      const p=annualClassA2026(v.salary); return {weekly_before:money(p.before),weekly_after:money(p.after),annual:money(p.annual),effective:pct(v.salary?p.annual/v.salary*100:0)};
    },
    cat(v){
      const thresholds={A:400000,B:40000,C:20000}, threshold=thresholds[v.group]||0, small=v.benefit_type==='gift'?Math.min(3000,v.benefit):0;
      const current=Math.max(0,v.benefit-small), beforeTax=Math.max(0,v.prior-threshold)*.33, afterTax=Math.max(0,v.prior+current-threshold)*.33, cat=Math.max(0,afterTax-beforeTax);
      return {threshold:money(threshold),current_taxable_value:money(current),threshold_remaining:money(Math.max(0,threshold-v.prior)),cat:money(cat)};
    },
    rent_credit(v){
      const rentBased=v.rent*.20, cap=v.joint==='yes'?2000:1000, credit=Math.min(rentBased,cap,v.income_tax_liability);
      return {rent_based:money(rentBased),statutory_cap:money(cap),credit:money(Math.max(0,credit))};
    },
    help_to_buy(v){
      const ltv=v.property_value>0?v.mortgage/v.property_value*100:0, valueCap=v.property_value*.10, basic=v.property_value<=500000&&ltv>=70;
      const claim=basic?Math.min(30000,valueCap,v.tax_paid):0;
      return {ltv:pct(ltv),value_cap:money(valueCap),claim:money(claim),eligibility:basic?'Passes basic value/LTV check':'Fails basic value/LTV check'};
    },
    first_home_scheme(v){
      const htb=v.htb==='yes'?Math.min(v.htb_amount,v.property_value):0, gap=Math.max(0,v.property_value-v.mortgage-v.deposit-htb), maxShare=v.htb==='yes'?.20:.30, maxFhs=v.property_value*maxShare, minFhs=Math.max(v.property_value*.025,10000), share=v.property_value?gap/v.property_value*100:0;
      let check='Within basic funding range'; if(gap===0)check='No funding gap'; else if(gap<minFhs)check='Gap is below the FHS minimum'; else if(gap>maxFhs)check='Gap exceeds the percentage maximum';
      return {gap:money(gap),share:pct(share),max_fhs:money(maxFhs),check};
    },
    dirt(v){ const tax=v.interest*.33, net=v.interest-tax; return {dirt:money(tax),net:money(net),retained:pct(v.interest?net/v.interest*100:0)}; },
    contractor_vs_salary(v){
      const employee=employeeNet2026(v.salary,0,44000,0), revenue=v.day_rate*v.billable_days, profit=Math.max(0,revenue-v.contractor_costs), pension=Math.min(v.contractor_pension,profit), contractor=selfEmployedNet2026(profit,pension), diff=contractor.net-employee.net;
      return {
        employee_net:money(employee.net),contractor_revenue:money(revenue),contractor_profit:money(profit),contractor_net:money(contractor.net),net_difference:(diff>=0?'+':'')+money(diff),
        __chart:{type:'bar',title:'Gross and estimated net comparison',caption:'The contractor side excludes the value of employment benefits and uses the stated self-employed assumptions.',labels:['Employee','Contractor'],series:[{label:'Gross / profit',values:[v.salary,profit]},{label:'Estimated take-home',values:[employee.net,contractor.net]}]}
      };
    },
    investment_fees(v){
      const low=projectMonthly(v.initial,v.monthly,v.gross_return-v.fee_low,v.years), high=projectMonthly(v.initial,v.monthly,v.gross_return-v.fee_high,v.years), labels=Array.from({length:v.years+1},(_,i)=>'Year '+i);
      return {
        low_balance:money(low[low.length-1]),high_balance:money(high[high.length-1]),fee_gap:money(low[low.length-1]-high[high.length-1]),
        __chart:{type:'line',title:'Fee drag over time',caption:'Same before-fee return and contributions; only the annual fee assumption changes.',labels,series:[{label:'Lower fee',values:low},{label:'Higher fee',values:high}]}
      };
    },
    fire_number(v){
      const target=v.withdrawal_rate>0?v.annual_spend/(v.withdrawal_rate/100):Infinity, r=v.return_rate/100/12, monthly=v.annual_contribution/12; let bal=v.current, months=0;
      while(bal<target&&months<1200){bal=bal*(1+r)+monthly;months++;}
      const years=Math.min(60,Math.max(1,Math.ceil(Math.min(months,1200)/12))), labels=[], vals=[], targets=[]; bal=v.current;
      labels.push('Now');vals.push(bal);targets.push(target);
      for(let y=1;y<=years;y++){for(let m=0;m<12;m++)bal=bal*(1+r)+monthly;labels.push('Year '+y);vals.push(bal);targets.push(target);}
      return {
        target:money(target),gap:money(Math.max(0,target-v.current)),years:months>=1200&&bal<target?'Not reached within 100 years':duration(months),
        __chart:{type:'line',title:'Portfolio path towards the FIRE target',caption:'Constant-return illustration using the spending, withdrawal and contribution assumptions entered.',labels,series:[{label:'Projected portfolio',values:vals},{label:'FIRE target',values:targets}]}
      };
    },
    retirement_income(v){
      const portfolio=v.pot*v.withdrawal_rate/100, total=portfolio+v.state_pension+v.other_income;
      return {
        portfolio_income:money(portfolio),annual_income:money(total),monthly_income:money(total/12),
        __chart:{type:'bar',title:'Illustrative retirement income mix',caption:'Gross annual income before tax.',labels:['Portfolio','State Pension','Other'],series:[{label:'Annual income',values:[portfolio,v.state_pension,v.other_income]}]}
      };
    },
    pension_projection(v){
      const years=Math.max(0,Math.floor(v.retirement_age-v.age)), monthly=v.monthly_employee+v.monthly_employer, netRate=v.return_rate-v.annual_fee, labels=['Age '+v.age], pots=[v.current], contribs=[v.current]; let bal=v.current, contrib=v.current, r=netRate/100/12;
      for(let y=1;y<=years;y++){for(let m=0;m<12;m++){bal=bal*(1+r)+monthly;contrib+=monthly;}labels.push('Age '+(v.age+y));pots.push(bal);contribs.push(contrib);}
      return {
        years:years+' years',projected:money(bal),contributed:money(contrib),growth:money(bal-contrib),
        __chart:{type:'line',title:'Pension projection to retirement',caption:'Projected fund versus cumulative money contributed, using the return and fee assumptions entered.',labels,series:[{label:'Projected pension',values:pots},{label:'Contributions + starting pot',values:contribs}]}
      };
    },
    rent_vs_buy(v){
      const mortgage=Math.max(0,v.house_price-v.deposit), n=v.mortgage_years*12, payment=monthlyPayment(mortgage,v.mortgage_rate,n), mr=v.mortgage_rate/100/12, hr=Math.pow(1+v.house_growth/100,1/12)-1, rr=Math.pow(1+v.annual_rent_growth/100,1/12)-1, ir=Math.pow(1+v.renter_return/100,1/12)-1;
      let house=v.house_price, balance=mortgage, rent=v.monthly_rent, renter=v.deposit, ownerInvest=0; const labels=['Now'], ownerVals=[v.deposit], renterVals=[renter];
      for(let month=1;month<=v.years*12;month++){
        house*=1+hr; rent*=1+rr; renter*=1+ir; ownerInvest*=1+ir;
        const interest=balance*mr, principal=Math.max(0,Math.min(balance,payment-interest)); balance=Math.max(0,balance-principal);
        const maintenance=house*(v.maintenance_pct/100)/12, ownerCost=(balance>0?payment:0)+maintenance;
        if(ownerCost>rent) renter+=ownerCost-rent; else ownerInvest+=rent-ownerCost;
        if(month%12===0){labels.push('Year '+(month/12));ownerVals.push(house-balance+ownerInvest);renterVals.push(renter);}
      }
      const owner=ownerVals[ownerVals.length-1], renterEnd=renterVals[renterVals.length-1], diff=owner-renterEnd;
      return {
        mortgage_payment:money(payment),owner_equity:money(owner),renter_portfolio:money(renterEnd),difference:(diff>=0?'+':'')+money(diff),
        __chart:{type:'line',title:'Illustrative net-wealth paths',caption:'Both paths invest any monthly cost advantage; the renter starts by investing the deposit.',labels,series:[{label:'Buy scenario',values:ownerVals},{label:'Rent scenario',values:renterVals}]}
      };
    },
    mortgage_affordability(v){
      const lti=v.income*(v.buyer_type==='ftb'?4:3.5), capacity=Math.max(0,v.income/12*v.max_payment_pct/100-v.other_debt), r=v.rate/100/12, n=v.term*12, paymentBased=r===0?capacity*n:capacity*(1-Math.pow(1+r,-n))/r, mortgage=Math.max(0,Math.min(lti,paymentBased)), price=Math.min(mortgage+v.deposit,v.deposit>0?v.deposit/.10:mortgage);
      return {
        lti_mortgage:money(lti),payment_capacity:money(capacity),payment_based_mortgage:money(paymentBased),indicative_mortgage:money(mortgage),indicative_price:money(Math.max(0,price)),
        __chart:{type:'bar',title:'Which limit is binding?',caption:'The lower mortgage amount between the LTI ceiling and your chosen cash-flow limit drives this illustration.',labels:['LTI ceiling','Payment-based','Indicative'],series:[{label:'Mortgage amount',values:[lti,paymentBased,mortgage]}]}
      };
    },
    house_buying_costs(v){
      const deposit=v.price*v.deposit_pct/100, stamp=stampDutyResidential(v.price), other=v.legal+v.survey+v.valuation+v.moving+v.other, total=deposit+stamp+other;
      return {
        deposit:money(deposit),stamp:money(stamp),other_costs:money(other),total_upfront:money(total),
        __chart:{type:'bar',title:'Upfront cash budget',caption:'Deposit plus stamp duty and the other costs entered above.',labels:['Deposit','Stamp duty','Legal','Survey','Valuation','Moving','Other'],series:[{label:'Estimated cost',values:[deposit,stamp,v.legal,v.survey,v.valuation,v.moving,v.other]}]}
      };
    },
    solar_payback(v){
      const generation=Math.max(0,v.kwp*v.generation_per_kwp);
      const rawGrant=Math.min(1800,Math.min(Math.max(0,v.kwp),2)*700+Math.max(0,Math.min(v.kwp-2,2))*200);
      const grant=v.grant_eligible?rawGrant:0;

      const homeDemand=Math.max(0,v.annual_home_kwh);
      const directHome=Math.min(generation*Math.max(0,Math.min(100,v.direct_solar_pct))/100,homeDemand);
      let remainingSolar=Math.max(0,generation-directHome);

      let evHomeDemand=0, directEv=0;
      if(v.has_ev){
        const chargeEfficiency=Math.max(.01,1-Math.max(0,Math.min(40,v.ev_loss_pct))/100);
        const vehicleEnergy=Math.max(0,v.annual_ev_km)*Math.max(0,v.ev_efficiency)/100;
        evHomeDemand=vehicleEnergy/chargeEfficiency*Math.max(0,Math.min(100,v.ev_home_charge_pct))/100;
        directEv=Math.min(remainingSolar,evHomeDemand*Math.max(0,Math.min(100,v.ev_solar_share_pct))/100);
        remainingSolar=Math.max(0,remainingSolar-directEv);
      }

      const totalDemand=homeDemand+evHomeDemand;
      const efficiency=v.has_battery?Math.max(.01,Math.min(1,v.battery_efficiency/100)):1;
      const batteryCapacity=v.has_battery?Math.max(0,v.battery_kwh):0;
      const annualBatteryInputCapacity=batteryCapacity*365;
      const remainingDemandBeforeBattery=Math.max(0,totalDemand-directHome-directEv);

      let solarBatteryInput=0, solarBatteryDelivered=0;
      if(v.has_battery&&batteryCapacity>0){
        const requestedSolarInput=remainingSolar*Math.max(0,Math.min(100,v.solar_to_battery_pct))/100;
        solarBatteryInput=Math.min(requestedSolarInput,annualBatteryInputCapacity,remainingDemandBeforeBattery/efficiency);
        solarBatteryDelivered=solarBatteryInput*efficiency;
        remainingSolar=Math.max(0,remainingSolar-solarBatteryInput);
      }

      const exported=remainingSolar;
      const directHomeValue=directHome*Math.max(0,v.import_rate);
      const directEvValue=directEv*Math.max(0,v.ev_alternative_rate);
      const batterySolarValue=solarBatteryDelivered*Math.max(0,v.import_rate);
      const exportValue=exported*Math.max(0,v.export_rate);
      const solarValue=directHomeValue+directEvValue+batterySolarValue+exportValue;

      let nightInput=0, nightDelivered=0, arbitrage=0;
      if(v.has_battery&&v.night_charge&&batteryCapacity>0){
        const remainingAnnualBatteryInput=Math.max(0,annualBatteryInputCapacity-solarBatteryInput);
        const requestedNightInput=Math.max(0,v.night_battery_kwh_day)*365;
        const remainingGridDemand=Math.max(0,totalDemand-directHome-directEv-solarBatteryDelivered);
        nightInput=Math.min(requestedNightInput,remainingAnnualBatteryInput,remainingGridDemand/efficiency);
        nightDelivered=nightInput*efficiency;
        arbitrage=nightDelivered*Math.max(0,v.import_rate)-nightInput*Math.max(0,v.night_rate);
      }

      const batteryCost=v.has_battery?Math.max(0,v.battery_cost):0;
      const solarOnlyNet=Math.max(0,v.system_cost-grant);
      const net=Math.max(0,solarOnlyNet+batteryCost);
      const annual=solarValue+arbitrage;
      const payback=annual>0?net/annual:Infinity;

      const solarOnlyExport=Math.max(0,generation-directHome-directEv);
      const solarOnlyAnnual=directHomeValue+directEvValue+solarOnlyExport*Math.max(0,v.export_rate);
      const labels=['Install'],full=[-net],solarOnly=[-solarOnlyNet];
      for(let year=1;year<=20;year++){
        labels.push('Year '+year);
        full.push(-net+annual*year);
        solarOnly.push(-solarOnlyNet+solarOnlyAnnual*year);
      }
      const series=v.has_battery
        ? [{label:'Solar + battery scenario',values:full},{label:'Solar-only comparison',values:solarOnly}]
        : [{label:'Solar scenario',values:full}];

      return {
        grant:money(grant),
        net_cost:money(net),
        annual_generation:num(generation)+' kWh',
        total_demand:num(totalDemand)+' kWh',
        solar_used:num(directHome+directEv+solarBatteryDelivered)+' kWh',
        exported:num(exported)+' kWh',
        solar_value:money(solarValue),
        battery_arbitrage:(arbitrage>=0?'':'-')+money(Math.abs(arbitrage)),
        annual_value:money(annual),
        payback:Number.isFinite(payback)?number.format(payback)+' years':'Not reached',
        __chart:{type:'line',title:'Cumulative payback under your assumptions',caption:'Solar-only is shown separately when a battery is selected. Constant annual savings are assumed; degradation and tariff changes are not modelled.',labels,series}
      };
    },
    ber_energy(v){
      const current=v.area*v.current_kwh_m2, target=v.area*v.target_kwh_m2, currentCost=current*v.energy_price, targetCost=target*v.energy_price;
      return {
        current_use:num(current)+' kWh',target_use:num(target)+' kWh',current_cost:money(currentCost),target_cost:money(targetCost),saving:money(currentCost-targetCost),
        __chart:{type:'bar',title:'Current versus target energy-cost illustration',caption:'Uses the same blended energy-price assumption for both scenarios.',labels:['Current','Target'],series:[{label:'Annual energy cost',values:[currentCost,targetCost]}]}
      };
    },
    solar_optimizer(v){
      const generation=Math.max(0,v.kwp*v.generation_per_kwp);
      const grant=v.grant_eligible?Math.min(1800,Math.min(v.kwp,2)*700+Math.max(0,Math.min(v.kwp-2,2))*200):0;
      const solarNet=Math.max(0,v.solar_cost-grant);
      const directHome=Math.min(generation*Math.max(0,Math.min(100,v.direct_home_pct))/100,Math.max(0,v.home_kwh));
      const surplus0=Math.max(0,generation-directHome);
      let evDemand=0,directEv=0;
      if(v.has_ev){
        const chargeEff=Math.max(.01,1-Math.max(0,Math.min(40,v.ev_loss_pct))/100);
        evDemand=Math.max(0,v.ev_km)*Math.max(0,v.ev_efficiency)/100/chargeEff*Math.max(0,Math.min(100,v.ev_home_pct))/100;
        directEv=Math.min(surplus0,evDemand*Math.max(0,Math.min(100,v.ev_solar_pct))/100);
      }
      const solarOnlyAnnual=directHome*v.day_rate+surplus0*v.export_rate;
      const evSurplus=Math.max(0,surplus0-directEv);
      const evAnnual=directHome*v.day_rate+directEv*v.ev_grid_rate+evSurplus*v.export_rate;

      const batteryEff=Math.max(.01,Math.min(1,v.battery_efficiency/100));
      const annualInputCap=Math.max(0,v.battery_kwh)*365;
      const homeRemaining=Math.max(0,v.home_kwh-directHome);
      const batteryInput=Math.min(surplus0*Math.max(0,Math.min(100,v.solar_capture_pct))/100,annualInputCap,homeRemaining/batteryEff);
      const batteryDelivered=batteryInput*batteryEff;
      const batteryExport=Math.max(0,surplus0-batteryInput);
      const remainingCap=Math.max(0,annualInputCap-batteryInput);
      const remainingHome=Math.max(0,homeRemaining-batteryDelivered);
      const nightInput=v.use_night_charge?Math.min(Math.max(0,v.night_kwh_day)*365,remainingCap,remainingHome/batteryEff):0;
      const nightDelivered=nightInput*batteryEff;
      const nightValue=nightDelivered*v.day_rate-nightInput*v.night_rate;
      const batteryAnnual=directHome*v.day_rate+batteryDelivered*v.day_rate+batteryExport*v.export_rate+nightValue;

      const combinedHomeRemaining=Math.max(0,v.home_kwh-directHome);
      const combinedSurplus=Math.max(0,surplus0-directEv);
      const combinedBatteryInput=Math.min(combinedSurplus*Math.max(0,Math.min(100,v.solar_capture_pct))/100,annualInputCap,combinedHomeRemaining/batteryEff);
      const combinedDelivered=combinedBatteryInput*batteryEff;
      const combinedExport=Math.max(0,combinedSurplus-combinedBatteryInput);
      const combinedCap=Math.max(0,annualInputCap-combinedBatteryInput);
      const combinedHomeGrid=Math.max(0,combinedHomeRemaining-combinedDelivered);
      const combinedNightInput=v.use_night_charge?Math.min(Math.max(0,v.night_kwh_day)*365,combinedCap,combinedHomeGrid/batteryEff):0;
      const combinedNightDelivered=combinedNightInput*batteryEff;
      const combinedNightValue=combinedNightDelivered*v.day_rate-combinedNightInput*v.night_rate;
      const combinedAnnual=directHome*v.day_rate+directEv*v.ev_grid_rate+combinedDelivered*v.day_rate+combinedExport*v.export_rate+combinedNightValue;

      const withBatteryCost=solarNet+Math.max(0,v.battery_cost);
      const pb=a=>a>0?solarNet/a:Infinity;
      const pbb=a=>a>0?withBatteryCost/a:Infinity;
      const benefits=[
        {name:'Solar only',value:solarOnlyAnnual*20-solarNet},
        {name:'Solar + smart EV',value:evAnnual*20-solarNet},
        {name:'Solar + battery',value:batteryAnnual*20-withBatteryCost},
        {name:'Solar + EV + battery',value:combinedAnnual*20-withBatteryCost}
      ];
      const best=benefits.reduce((a,b)=>b.value>a.value?b:a,benefits[0]);
      return {
        generation:num(generation)+' kWh',ev_demand:num(evDemand)+' kWh',best_scenario:best.name,
        solar_payback:Number.isFinite(pb(solarOnlyAnnual))?number.format(pb(solarOnlyAnnual))+' years':'Not reached',
        ev_payback:Number.isFinite(pb(evAnnual))?number.format(pb(evAnnual))+' years':'Not reached',
        battery_payback:Number.isFinite(pbb(batteryAnnual))?number.format(pbb(batteryAnnual))+' years':'Not reached',
        combined_payback:Number.isFinite(pbb(combinedAnnual))?number.format(pbb(combinedAnnual))+' years':'Not reached',
        __chart:{type:'bar',title:'20-year net benefit by configuration',caption:'Annual values are held constant and upfront solar/battery costs are deducted.',labels:benefits.map(x=>x.name),series:[{label:'20-year net benefit',values:benefits.map(x=>x.value)}]}
      };
    },
    retrofit_planner(v){
      const costs={
        attic:v.attic?v.attic_cost:0,wall:v.external_wall?v.wall_cost:0,windows:v.windows?v.windows_cost:0,
        heat:v.heat_pump?v.heat_pump_cost:0,solar:v.solar?v.solar_cost:0,doors:v.doors?v.doors_cost:0,
        ventilation:v.ventilation?v.ventilation_cost:0,airtight:v.airtightness?v.airtightness_cost:0,other:v.other_cost
      };
      const gross=Object.values(costs).reduce((a,b)=>a+b,0);
      let grants=0;
      if(v.oss_eligible){
        const type=v.home_type;
        const atticStandard={detached:2000,semi:1500,mid:1400,apartment:1100};
        const atticFtb={detached:2500,semi:1900,mid:1800,apartment:1400};
        const wallGrant={detached:8000,semi:6000,mid:3500,apartment:3000};
        const windowGrant={detached:4000,semi:3000,mid:1800,apartment:1500};
        if(v.attic) grants+=Math.min(v.attic_cost,(v.first_time_buyer?atticFtb:atticStandard)[type]||0);
        if(v.external_wall) grants+=Math.min(v.wall_cost,wallGrant[type]||0);
        if(v.windows) grants+=Math.min(v.windows_cost,windowGrant[type]||0);
        if(v.heat_pump) grants+=Math.min(v.heat_pump_cost,type==='apartment'?4500:6500);
        if(v.solar) grants+=Math.min(v.solar_cost,Math.min(1800,Math.min(v.solar_kwp,2)*700+Math.max(0,Math.min(v.solar_kwp-2,2))*200));
        if(v.doors) grants+=Math.min(v.doors_cost,Math.min(2,Math.max(0,v.door_count))*800);
        if(v.ventilation) grants+=Math.min(v.ventilation_cost,1500);
        if(v.airtightness) grants+=Math.min(v.airtightness_cost,1000);
      }
      const net=Math.max(0,gross-grants), annual=v.annual_energy_bill*Math.max(0,Math.min(100,v.saving_pct))/100, payback=annual>0?net/annual:Infinity;
      const labels=['Start'],vals=[-net];for(let y=1;y<=20;y++){labels.push('Year '+y);vals.push(-net+annual*y);}
      return {
        gross_cost:money(gross),grants:money(grants),net_cost:money(net),annual_saving:money(annual),payback:Number.isFinite(payback)?number.format(payback)+' years':'Not reached',
        __chart:{type:'line',title:'Simple retrofit cash payback',caption:'Uses the energy-saving percentage entered and holds annual savings constant.',labels,series:[{label:'Cumulative cash position',values:vals}]}
      };
    },
    myfuturefund(v){
      let status;
      if(v.workplace_pension) status='Employment normally exempt';
      else if(v.age>=23&&v.age<60&&v.salary>=20000) status='Likely auto-enrolled';
      else if(v.age>=18&&v.age<66) status='May opt in';
      else status='Outside current participation age';
      const rateForYear=year=>year<=2028?.015:year<=2031?.03:year<=2034?.045:.06;
      const stateRateForYear=year=>rateForYear(year)/3;
      const participating=!v.workplace_pension&&v.age>=18&&v.age<66;
      const baseEarnings=Math.min(Math.max(0,v.salary),80000);
      const er2026=participating?baseEarnings*rateForYear(2026):0, sr2026=participating?baseEarnings*stateRateForYear(2026):0;
      let fund=Math.max(0,v.current_fund), salary=Math.max(0,v.salary), employeeTotal=0, labels=['Age '+v.age],funds=[fund],employeeCum=[0];
      const years=Math.max(0,Math.floor(v.retirement_age-v.age));
      for(let i=0;i<years;i++){
        const year=2026+i, age=v.age+i;
        fund*=1+v.return_rate/100;
        if(participating&&age<66){
          const earnings=Math.min(salary,80000), emp=earnings*rateForYear(year), employer=emp, state=earnings*stateRateForYear(year);
          fund+=emp+employer+state; employeeTotal+=emp;
        }
        salary*=1+v.salary_growth/100;
        labels.push('Age '+(v.age+i+1));funds.push(fund);employeeCum.push(employeeTotal);
      }
      return {
        status,employee_2026:money(er2026),employer_2026:money(er2026),state_2026:money(sr2026),total_2026:money(er2026*2+sr2026),projected:money(fund),employee_total:money(employeeTotal),
        __chart:{type:'line',title:'Projected MyFutureFund balance',caption:'Uses the statutory calendar-year contribution phases plus the salary-growth and investment-return assumptions entered.',labels,series:[{label:'Projected fund',values:funds},{label:'Cumulative employee contributions',values:employeeCum}]}
      };
    },
    childcare_return(v){
      const pension=v.salary*Math.max(0,v.pension_pct)/100, net=employeeNet2026(v.salary,pension,44000,0);
      const gross=v.children*v.childcare_hours*v.childcare_fee*v.childcare_weeks;
      const subsidisedHours=Math.min(45,Math.max(0,v.childcare_hours));
      const ncs=v.children*subsidisedHours*Math.min(v.childcare_fee,v.ncs_rate)*v.childcare_weeks;
      const childcare=Math.max(0,gross-ncs), workCosts=(v.commute_weekly+v.work_cost_weekly)*v.childcare_weeks+v.other_annual;
      const gain=net.net-childcare-workCosts, hours=v.work_hours*v.childcare_weeks, hourly=hours>0?gain/hours:0;
      return {
        take_home:money(net.net),childcare_gross:money(gross),ncs_support:money(ncs),childcare_net:money(childcare),work_costs:money(workCosts),household_gain:(gain>=0?'+':'-')+money(Math.abs(gain)),effective_hourly:(hourly>=0?'+':'-')+money(Math.abs(hourly))+'/hour',
        __chart:{type:'bar',title:'What remains after returning-to-work costs',caption:'Estimated take-home pay compared with net childcare, commuting/work costs and the resulting annual household cash gain.',labels:['Take-home','Net childcare','Work costs','Financial gain'],series:[{label:'Annual amount',values:[net.net,childcare,workCosts,gain]}]}
      };
    },
    mortgage_switch(v){
      const n1=Math.round(v.current_years*12),n2=Math.round(v.new_years*12),p1=monthlyPayment(v.balance,v.current_rate,n1),p2=monthlyPayment(v.balance,v.new_rate,n2);
      const total1=p1*n1,total2=p2*n2,netCost=Math.max(0,v.switching_costs+v.break_fee-v.cashback),monthlySaving=p1-p2;
      const breakEven=monthlySaving>0?(netCost<=0?'Immediate':duration(netCost/monthlySaving)):'No monthly saving';
      const diff=total1-(total2+netCost);
      const labels=['Now'],a=[v.balance],b=[v.balance];let bal1=v.balance,bal2=v.balance,r1=v.current_rate/100/12,r2=v.new_rate/100/12;
      const years=Math.max(v.current_years,v.new_years);
      for(let y=1;y<=years;y++){
        for(let m=0;m<12;m++){
          if(bal1>0){const i=bal1*r1;bal1=Math.max(0,bal1-(p1-i));}
          if(bal2>0){const i=bal2*r2;bal2=Math.max(0,bal2-(p2-i));}
        }
        labels.push('Year '+y);a.push(bal1);b.push(bal2);
      }
      return {
        current_payment:money(p1),new_payment:money(p2),monthly_change:(monthlySaving>=0?'-':'+')+money(Math.abs(monthlySaving)),net_switch_cost:money(netCost),break_even:breakEven,lifetime_difference:(diff>=0?'+':'-')+money(Math.abs(diff)),
        __chart:{type:'line',title:'Scheduled mortgage balance',caption:'Current mortgage versus the alternative rate/term entered.',labels,series:[{label:'Current mortgage',values:a},{label:'Alternative mortgage',values:b}]}
      };
    },
    lifetime_cost(v){
      const years=Math.max(0,Math.floor(v.end_age-v.current_age)), inflation=v.inflation/100;
      const monthlyBase=v.food_monthly+v.utilities_monthly+v.transport_monthly+v.leisure_monthly+v.other_monthly;
      const baseAnnual=monthlyBase*12+v.travel_annual+v.insurance_health_annual;
      const todayAnnual=baseAnnual+(v.current_age<v.housing_until?v.housing_monthly*12:0)+(v.childcare_years>0?v.childcare_annual:0)+(v.major_interval>0?v.major_purchase/v.major_interval:0);
      let nominal=0,todayMoney=0,housingTotal=0,majorTotal=0,cumulative=0;const labels=['Age '+v.current_age],vals=[0];
      for(let y=0;y<years;y++){
        const factor=Math.pow(1+inflation,y),age=v.current_age+y;
        let annual=baseAnnual*factor, annualToday=baseAnnual;
        if(age<v.housing_until){annual+=v.housing_monthly*12*factor;annualToday+=v.housing_monthly*12;housingTotal+=v.housing_monthly*12*factor;}
        if(y<v.childcare_years){annual+=v.childcare_annual*factor;annualToday+=v.childcare_annual;}
        if(v.major_interval>0&&(y+1)%Math.round(v.major_interval)===0){const mp=v.major_purchase*factor;annual+=mp;annualToday+=v.major_purchase;majorTotal+=mp;}
        nominal+=annual;todayMoney+=annualToday;cumulative+=annual;labels.push('Age '+(age+1));vals.push(cumulative);
      }
      return {
        years:years+' years',today_annual:money(todayAnnual),lifetime_nominal:money(nominal),lifetime_today_money:money(todayMoney),housing_total:money(housingTotal),major_total:money(majorTotal),
        __chart:{type:'line',title:'Cumulative projected lifetime spending',caption:'Future cash spending rises with the inflation assumption and follows the time limits entered for housing and childcare.',labels,series:[{label:'Cumulative spending',values:vals}]}
      };
    },
    car_finance(v){
      const advanced=Boolean(v.__advanced);
      const price=Math.max(0,v.car_price), deposit=Math.min(price,Math.max(0,v.deposit)), financed=Math.max(0,price-deposit);
      const loanYears=advanced?v.loan_term_years:v.term_years;
      const hpYears=advanced?v.hp_term_years:v.term_years;
      const pcpYears=advanced?v.pcp_term_years:v.term_years;
      const loanMonths=Math.max(1,Math.round(loanYears*12)), hpMonths=Math.max(1,Math.round(hpYears*12)), pcpMonths=Math.max(1,Math.round(pcpYears*12));
      const loanFee=advanced?Math.max(0,v.loan_fee):0, hpDoc=advanced?Math.max(0,v.hp_doc_fee):0, hpCompletion=advanced?Math.max(0,v.hp_completion_fee):0;
      const pcpDoc=advanced?Math.max(0,v.pcp_doc_fee):0, pcpCompletion=advanced?Math.max(0,v.pcp_completion_fee):0;
      const balloon=Math.max(0,v.pcp_balloon);
      const loanMonthly=monthlyPayment(financed,v.loan_rate,loanMonths);
      const hpMonthly=monthlyPayment(financed,v.hp_rate,hpMonths);
      const pcpMonthly=balloonPayment(financed,v.pcp_rate,pcpMonths,balloon);
      const loanTotal=deposit+loanFee+loanMonthly*loanMonths;
      const hpTotal=deposit+hpDoc+hpMonthly*hpMonths+hpCompletion;
      const pcpKeep=deposit+pcpDoc+pcpMonthly*pcpMonths+balloon+pcpCompletion;
      let returnCharges=0, equityText='Switch to Advanced for end-value estimate';
      if(advanced){
        const excessAnnual=Math.max(0,v.expected_annual_mileage-v.annual_mileage_limit);
        returnCharges=excessAnnual*pcpYears*Math.max(0,v.excess_km_charge)+Math.max(0,v.condition_charge);
        const equity=Math.max(0,v.estimated_value)-balloon;
        equityText=(equity>=0?'+':'-')+money(Math.abs(equity));
      }
      const pcpReturn=deposit+pcpDoc+pcpMonthly*pcpMonths+returnCharges;
      const maxYears=Math.ceil(Math.max(loanYears,hpYears,pcpYears));
      const labels=['Start'],loanLine=[deposit+loanFee],hpLine=[deposit+hpDoc],pcpLine=[deposit+pcpDoc];
      for(let y=1;y<=maxYears;y++){
        labels.push('Year '+y);
        loanLine.push(deposit+loanFee+loanMonthly*Math.min(loanMonths,y*12));
        hpLine.push(deposit+hpDoc+hpMonthly*Math.min(hpMonths,y*12)+(y*12>=hpMonths?hpCompletion:0));
        pcpLine.push(deposit+pcpDoc+pcpMonthly*Math.min(pcpMonths,y*12)+(y*12>=pcpMonths?balloon+pcpCompletion:0));
      }
      return {
        loan_monthly:money(loanMonthly),hp_monthly:money(hpMonthly),pcp_monthly:money(pcpMonthly),
        loan_total:money(loanTotal),hp_total:money(hpTotal),pcp_keep_total:money(pcpKeep),pcp_return_total:money(pcpReturn),
        pcp_equity:equityText,
        ownership_summary:'Loan: owned from day 1 • HP: after final payment • PCP: only if balloon is paid',
        __chart:{type:'line',title:'Cumulative cash paid if you ultimately keep the car',caption:'PCP rises at the end when the balloon/GMFV is paid. Advanced mode uses separate terms and entered fees.',labels,series:[{label:'Personal loan',values:loanLine},{label:'Hire Purchase',values:hpLine},{label:'PCP — keep car',values:pcpLine}]}
      };
    },
    nutrition_needs(v){
      const sexConst=v.sex==='female'?-161:5;
      const resting=10*Math.max(0,v.weight)+6.25*Math.max(0,v.height)-5*Math.max(0,v.age)+sexConst;
      const pal=Number(v.activity)||1.4, maintenance=resting*pal;
      const factor=v.energy_scenario==='lower10'?.90:v.energy_scenario==='higher10'?1.10:1;
      const target=maintenance*factor;
      const proteinRate=v.protein_context==='resistance'?1.6:.83;
      const proteinG=Math.max(0,v.weight)*proteinRate;
      const fatG=Math.max(0,target*.30/9);
      const carbG=Math.max(0,(target-proteinG*4-fatG*9)/4);
      return {
        resting:num(Math.round(resting))+' kcal/day',
        maintenance:num(Math.round(maintenance))+' kcal/day',
        target:num(Math.round(target))+' kcal/day',
        protein:num(proteinG)+' g/day',
        fat:num(fatG)+' g/day',
        carbs:num(carbG)+' g/day',
        fibre:'At least 25 g/day',
        __chart:{type:'bar',currency:false,title:'Energy estimates under your selected assumptions',caption:'Resting energy is predicted from Mifflin–St Jeor. Maintenance multiplies that estimate by the selected EFSA-style PAL; the third bar is the scenario you selected.',labels:['Resting','Maintenance','Selected scenario'],series:[{label:'kcal/day',values:[resting,maintenance,target]}]}
      };
    },
    pregnancy_timeline(v){
      const lmp=parseDateOnly(v.lmp), assigned=parseDateOnly(v.assigned_due_date);
      if(!lmp&&!assigned) return {due_date:'Enter a date above',gestational_age:'—',trimester:'—',conception_estimate:'—',week12:'—',anatomy_window:'—',week37:'—',week42:'—'};
      const due=assigned||addDaysUTC(lmp,280);
      const baseLmp=assigned?addDaysUTC(due,-280):lmp;
      const todayLocal=new Date();
      const today=new Date(Date.UTC(todayLocal.getFullYear(),todayLocal.getMonth(),todayLocal.getDate()));
      const gestDays=Math.floor((today-baseLmp)/86400000);
      let gestational='Not yet at LMP date',trimester='Not yet in pregnancy timeline';
      if(gestDays>=0){
        const weeks=Math.floor(gestDays/7),days=gestDays%7;
        gestational=weeks+' week'+(weeks===1?'':'s')+' '+days+' day'+(days===1?'':'s');
        trimester=gestDays<98?'First trimester':gestDays<196?'Second trimester':'Third trimester';
      }
      const conception=addDaysUTC(due,-266);
      return {
        due_date:formatDateIE(due)+(assigned?' (assigned date used)':' (LMP estimate)'),
        gestational_age:gestational,
        trimester,
        conception_estimate:formatDateIE(conception),
        week12:formatDateIE(addDaysUTC(baseLmp,84)),
        anatomy_window:formatDateIE(addDaysUTC(baseLmp,126))+' – '+formatDateIE(addDaysUTC(baseLmp,154)),
        week37:formatDateIE(addDaysUTC(baseLmp,259)),
        week42:formatDateIE(addDaysUTC(baseLmp,294))
      };
    },
    alcohol_ireland(v){
      const grams=(ml,abv,count)=>Math.max(0,ml)*Math.max(0,abv)/100*.789*Math.max(0,count);
      const total=
        grams(568,v.beer_abv,v.beer_pints)+
        grams(v.wine_ml,v.wine_abv,v.wine_glasses)+
        grams(v.spirit_ml,v.spirit_abv,v.spirits)+
        grams(v.can_ml,v.can_abv,v.cans);
      const drinks=total/10, weeklyKcal=total*7, annualKcal=weeklyKcal*52, annualSpend=Math.max(0,v.weekly_spend)*52;
      const reduction=Math.max(0,Math.min(100,v.reduction_pct))/100;
      let guideline='Not compared';
      if(v.guideline_group==='woman') guideline=drinks<=11?'Within current HSE weekly low-risk limit':'Above current HSE weekly low-risk limit';
      if(v.guideline_group==='man') guideline=drinks<=17?'Within current HSE weekly low-risk limit':'Above current HSE weekly low-risk limit';
      return {
        standard_drinks:num(drinks),
        grams:num(total)+' g/week',
        guideline,
        weekly_kcal:num(Math.round(weeklyKcal))+' kcal/week',
        annual_kcal:num(Math.round(annualKcal))+' kcal/year',
        annual_spend:money(annualSpend),
        reduced_drinks:num(drinks*(1-reduction)),
        annual_saving:money(annualSpend*reduction),
        __chart:{type:'bar',currency:false,title:'Current intake and modelled reduction',caption:'Irish standard drinks are based on 10 g of pure alcohol. The reduced scenario applies the percentage you entered to the same weekly pattern.',labels:['Current','After reduction'],series:[{label:'Standard drinks/week',values:[drinks,drinks*(1-reduction)]}]}
      };
    }
  };

  document.querySelectorAll('[data-calculator]').forEach(root => {
    const form=root.querySelector('[data-tool-form]'), error=root.querySelector('[data-tool-error]');
    const run=(showErrors=true)=>{
      const values={}; let invalid=false;
      root.querySelectorAll('[data-field]').forEach(el=>{
        const raw=el.value;
        if(el.type==='checkbox'){ values[el.dataset.field]=el.checked; return; }
        if(el.type==='date'){ if(!raw&&el.dataset.optional==='true'){values[el.dataset.field]='';return;} if(!/^\d{4}-\d{2}-\d{2}$/.test(raw)){invalid=true;return;} values[el.dataset.field]=raw; return; }
        if(el.tagName==='SELECT'){ values[el.dataset.field]=raw; return; }
        const n=Number(raw); if(!Number.isFinite(n)){invalid=true; return;} values[el.dataset.field]=n;
      });
      values.__advanced=root.dataset.advancedMode==='true';
      if(invalid){ if(showErrors) error.textContent='Check the numbers entered and try again.'; return; }
      error.textContent='';
      const fn=calculators[root.dataset.calculator]; if(!fn) return;
      try{
        const results=fn(values);
        Object.entries(results).forEach(([k,v])=>{
          if(k.startsWith('__')) return;
          const el=root.querySelector('[data-result="' + k + '"]');
          if(el) el.textContent=v;
        });
        renderToolChart(root,results.__chart || fallbackChart(root.dataset.calculator,values));
        renderScenarioSummary(values);
        if(window.gtag) window.gtag('event','tool_calculate',{tool_name:root.dataset.toolName});
      }catch(e){ if(showErrors) error.textContent='This combination could not be calculated. Check the values and try again.'; }
    };
    const params=new URLSearchParams(window.location.search);
    root.dataset.advancedMode=params.get('advanced')==='1'?'true':'false';
    root.querySelectorAll('[data-field]').forEach(el=>{
      const key=el.dataset.field;
      if(!params.has(key)) return;
      const val=params.get(key);
      if(el.type==='checkbox') el.checked=val==='1'||val==='true';
      else el.value=val;
    });
    const renderScenarioSummary=()=>{
      const wrap=root.querySelector('[data-tool-scenario-summary]'), chips=root.querySelector('[data-tool-scenario-chips]');
      if(!wrap||!chips) return;
      const pieces=[];
      root.querySelectorAll('.tool-field:not([hidden]) [data-field]').forEach(el=>{
        if(pieces.length>=5 || (el.type==='checkbox'&&!el.checked)) return;
        const field=el.closest('.tool-field'), label=field?.querySelector('label')?.textContent?.trim()||el.dataset.field;
        let value=el.tagName==='SELECT'?(el.options[el.selectedIndex]?.text||el.value):el.type==='checkbox'?'Included':el.value;
        if(!value) return;
        if(el.type!=='checkbox'&&el.tagName!=='SELECT'){
          const prefix=field?.querySelector('.tool-affix:not(.tool-affix-right)')?.textContent?.trim()||'';
          const suffix=field?.querySelector('.tool-affix-right')?.textContent?.trim()||'';
          value=(prefix?prefix:'')+value+(suffix?' '+suffix:'');
        }
        pieces.push(label+': '+value);
      });
      chips.innerHTML='';
      pieces.forEach(piece=>{const span=document.createElement('span');span.className='tool-scenario-chip';span.textContent=piece;chips.appendChild(span);});
      wrap.hidden=!pieces.length;
    };
    const syncVisibility=()=>{
      root.querySelectorAll('.tool-field').forEach(wrapper=>{
        let show=true;
        if(wrapper.dataset.showIf){
          const controller=root.querySelector('[data-field="'+wrapper.dataset.showIf+'"]');
          if(controller){
            if(controller.type==='checkbox') show=controller.checked;
            else show=controller.value!==''&&controller.value!=='no'&&controller.value!=='false'&&controller.value!=='0';
          } else show=false;
        }
        if(wrapper.hasAttribute('data-advanced-field')&&root.dataset.advancedMode!=='true') show=false;
        wrapper.hidden=!show;
      });
    };
    const modeButtons=[...root.querySelectorAll('[data-tool-mode]')];
    modeButtons.forEach(b=>{const active=(root.dataset.advancedMode==='true')===(b.dataset.toolMode==='advanced');b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',active?'true':'false');});
    const initialNote=root.querySelector('[data-tool-mode-note]');
    if(initialNote) initialNote.textContent=root.dataset.advancedMode==='true'?(initialNote.dataset.advancedNote||'Advanced mode: add optional detail for a more complete scenario.'):(initialNote.dataset.basicNote||'Start with the core figures. Switch to Advanced for optional detail.');
    modeButtons.forEach(button=>button.addEventListener('click',()=>{
      const advanced=button.dataset.toolMode==='advanced';
      root.dataset.advancedMode=advanced?'true':'false';
      modeButtons.forEach(b=>{const active=b===button;b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',active?'true':'false');});
      const note=root.querySelector('[data-tool-mode-note]');
      if(note) note.textContent=advanced?(note.dataset.advancedNote||'Advanced mode: add optional detail for a more complete scenario.'):(note.dataset.basicNote||'Start with the core figures. Switch to Advanced for optional detail.');
      syncVisibility();run();
    }));
    if(form){
      let inputTimer=null;
      form.addEventListener('submit',e=>{e.preventDefault();run(true);});
      form.addEventListener('change',()=>{syncVisibility();run(false);});
      form.addEventListener('input',()=>{clearTimeout(inputTimer);inputTimer=setTimeout(()=>{syncVisibility();run(false);},180);});
      form.addEventListener('reset',()=>setTimeout(()=>{
        root.dataset.advancedMode='false';
        modeButtons.forEach(b=>{const active=b.dataset.toolMode==='basic';b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',active?'true':'false');});
        const note=root.querySelector('[data-tool-mode-note]'); if(note) note.textContent=note.dataset.basicNote||'Start with the core figures. Switch to Advanced for optional detail.';
        syncVisibility();run();
      },0));
    }
    const shareButton=root.querySelector('[data-tool-share]'), printButton=root.querySelector('[data-tool-print]'), actionStatus=root.querySelector('[data-tool-action-status]');
    if(shareButton) shareButton.addEventListener('click',async()=>{
      const url=new URL(window.location.href); url.search='';
      root.querySelectorAll('[data-field]').forEach(el=>{
        if(el.type==='checkbox') url.searchParams.set(el.dataset.field,el.checked?'1':'0');
        else if(el.value!=='') url.searchParams.set(el.dataset.field,el.value);
      });
      if(root.dataset.advancedMode==='true') url.searchParams.set('advanced','1');
      const value=url.toString();
      let copied=false;
      try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value);copied=true;}}catch(e){}
      if(!copied){
        const ta=document.createElement('textarea');ta.value=value;ta.setAttribute('readonly','');ta.style.position='absolute';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();
        try{copied=document.execCommand('copy');}catch(e){} ta.remove();
      }
      if(actionStatus) actionStatus.textContent=copied?'Scenario link copied.':'Copy the current page URL to share this scenario.';
      if(window.gtag) window.gtag('event','tool_share',{tool_name:root.dataset.toolName});
    });
    if(printButton) printButton.addEventListener('click',()=>window.print());
    syncVisibility();
    run(false);
  });

  const search=document.querySelector('[data-tool-search]');
  if(search){
    const cards=[...document.querySelectorAll('[data-tool-card]')], groups=[...document.querySelectorAll('[data-tool-group]')], none=document.querySelector('[data-tool-no-results]');
    const filter=()=>{
      const q=search.value.trim().toLowerCase(); let shown=0;
      cards.forEach(card=>{const hit=!q||(card.dataset.toolText||card.textContent).toLowerCase().includes(q);card.hidden=!hit;if(hit)shown++;});
      groups.forEach(group=>{group.hidden=![...group.querySelectorAll('[data-tool-card]')].some(c=>!c.hidden);});
      none.hidden=shown>0;
    };
    search.addEventListener('input',filter);
  }
})();
