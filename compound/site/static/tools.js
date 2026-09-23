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
  const fhsPriceCeilings = {
    carlow:375000,cavan:375000,clare:400000,cork_city:500000,cork_county:450000,donegal:400000,
    dublin_city:500000,dlr:500000,fingal:500000,galway_city:475000,galway_county:450000,kerry:425000,
    kildare:475000,kilkenny:400000,laois:400000,leitrim:400000,limerick:450000,longford:375000,
    louth:425000,mayo:425000,meath:475000,monaghan:375000,offaly:375000,roscommon:400000,sligo:400000,
    south_dublin:500000,tipperary:375000,waterford:{house:400000,apartment:450000,self_build:400000},
    westmeath:400000,wexford:400000,wicklow:500000
  };
  const fhsPriceCeiling = (authority,propertyType) => {
    const ceiling=fhsPriceCeilings[authority];
    if(typeof ceiling==='number') return ceiling;
    return ceiling?.[propertyType] ?? ceiling?.house ?? 0;
  };
  const pensionPct = age => age < 30 ? .15 : age < 40 ? .20 : age < 50 ? .25 : age < 55 ? .30 : age < 60 ? .35 : .40;

  const incomeTax2026 = (income, band, credits) => {
    const taxable=Math.max(0,income), standard=Math.min(taxable,Math.max(0,band));
    const gross=standard*.20 + Math.max(0,taxable-standard)*.40;
    return {taxable,standard,higher:Math.max(0,taxable-standard),gross,net:Math.max(0,gross-Math.max(0,credits))};
  };
  const usc2026 = (income,reduced=false) => {
    const x=Math.max(0,income);
    if(x<=13000) return 0;
    if(reduced && x<=60000) return Math.min(x,12012)*.005 + Math.max(0,x-12012)*.02;
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
  const employeeNet2026 = (salary,pension,band=44000,extraCredits=0,reducedUsc=false) => {
    const employeeCredit=Math.min(2000,Math.max(0,salary)*.20);
    const credits=2000+employeeCredit+Math.max(0,extraCredits);
    const tax=incomeTax2026(Math.max(0,salary-pension),band,credits).net;
    const usc=usc2026(salary,reducedUsc), prsi=annualClassA2026(salary).annual;
    return {tax,usc,prsi,credits,net:salary-pension-tax-usc-prsi};
  };
  const selfEmployedNet2026 = (profit,pension=0) => {
    const x=Math.max(0,profit), earnedCredit=Math.min(2000,x*.20), credits=2000+earnedCredit;
    const tax=incomeTax2026(Math.max(0,x-pension),44000,credits).net;
    const usc=usc2026(x)+Math.max(0,x-100000)*.03;
    const prsi=x<5000?0:Math.max(650,x*.042375);
    return {tax,usc,prsi,credits,net:x-pension-tax-usc-prsi};
  };
  const stampDutyResidential = price => Math.min(price,1000000)*.01 + Math.max(0,Math.min(price,1500000)-1000000)*.02 + Math.max(0,price-1500000)*.06;
  const projectMonthly = (initial,monthly,annualRate,years) => {
    const r=Math.pow(Math.max(.000001,1+annualRate/100),1/12)-1, points=[Math.max(0,initial)]; let bal=Math.max(0,initial);
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
  const mortgageOverpaymentProjection = v => {
    const months=Math.max(1,Math.round(v.years*12));
    const base=monthlyPayment(v.balance,v.rate,months), r=v.rate/100/12;
    const advanced=Boolean(v.__advanced);
    const startAfter=advanced?Math.max(0,Math.round(v.overpayment_start_month||0)):0;
    const lumpSum=advanced?Math.max(0,v.lump_sum||0):0;
    const lumpMonth=advanced?Math.max(1,Math.round(v.lump_sum_month||1)):0;
    let bal=Math.max(0,v.balance), interest=0, month=0;
    const labels=['Start'], values=[bal];
    while(bal>0.005 && month<months){
      month++;
      const monthlyInterest=bal*r;
      interest+=monthlyInterest;
      const regularExtra=month>startAfter?Math.max(0,v.overpayment):0;
      const due=bal+monthlyInterest;
      bal=Math.max(0,due-Math.min(due,base+regularExtra));
      if(lumpSum>0 && month===lumpMonth && bal>0) bal=Math.max(0,bal-Math.min(bal,lumpSum));
      if(month%12===0 || bal<=0.005 || month===months){
        labels.push(month%12===0?'Year '+(month/12):'Month '+month);
        values.push(bal);
      }
    }
    const standardInterest=Math.max(0,base*months-v.balance);
    return {months,base,startAfter,lumpSum,lumpMonth,pay:base+Math.max(0,v.overpayment),scenarioMonths:month,interest,standardInterest,labels,values};
  };
  const mortgageSnapshot = (principal,annual,totalMonths,payment,horizonMonths) => {
    const r=annual/100/12;
    let balance=Math.max(0,principal), interest=0, paid=0;
    const months=Math.min(Math.max(0,Math.round(horizonMonths)),Math.max(0,Math.round(totalMonths)));
    for(let month=0;month<months && balance>0.005;month++){
      const monthlyInterest=balance*r, due=balance+monthlyInterest, actual=Math.min(due,payment);
      interest+=monthlyInterest; paid+=actual; balance=Math.max(0,due-actual);
    }
    return {balance,interest,paid};
  };
  const fallbackChart = (name,v) => {
    switch(name){
      case 'mortgage': {
        const months=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,months), s=amortisationSeries(v.amount,v.rate,months,p);
        return {type:'line',title:'Mortgage balance over time',caption:'Scheduled balance if the entered rate stayed unchanged for the full term.',labels:s.labels,series:[{label:'Mortgage balance',values:s.values}]};
      }
      case 'mortgage_overpayment': {
        const p=mortgageOverpaymentProjection(v), standard=amortisationSeries(v.balance,v.rate,p.months,p.base);
        const labels=standard.labels, scenario=[], byLabel=new Map(p.labels.map((label,i)=>[label,p.values[i]]));
        let last=v.balance;
        labels.forEach((label,i)=>{
          const targetMonth=label==='Start'?0:(label.startsWith('Year ')?Number(label.slice(5))*12:(label.startsWith('Month ')?Number(label.slice(6)):i*12));
          if(targetMonth>=p.scenarioMonths) last=0;
          else if(byLabel.has(label)) last=byLabel.get(label);
          scenario.push(last);
        });
        return {type:'line',title:'How the balance falls',caption:'Standard repayment versus your overpayment timing and any lump sum entered.',labels,series:[{label:'Standard',values:standard.values},{label:'Overpayment plan',values:scenario}]};
      }
      case 'mortgage_borrowing': {
        const multiple=v.buyer_type==='ftb'?4:3.5, deposit=Math.max(0,v.deposit), byIncome=Math.max(0,v.income)*multiple+deposit, byDeposit=deposit/.10;
        const labels=['Income-supported price','Deposit-supported price','Indicative maximum'], values=[byIncome,byDeposit,Math.min(byIncome,byDeposit)];
        if(v.__advanced){labels.push('Target price');values.push(Math.max(0,v.target_price||0));}
        return {type:'bar',title:'What sets the purchase-price ceiling?',caption:'Compares standard LTI capacity plus your deposit with the 90% LTV deposit constraint. Lender affordability is separate.',labels,series:[{label:'Purchase price',values}]};
      }
      case 'house_deposit': {
        const rate=v.buyer_type==='btl'?.30:.10, price=Math.max(0,v.price), minimum=price*rate;
        if(v.__advanced){
          const available=Math.min(price,Math.max(0,v.deposit_available||0));
          return {type:'bar',title:'Minimum deposit versus your cash position',caption:'Compares the standard LTV minimum with the deposit cash entered. Purchase costs are not included.',labels:['Minimum deposit','Available deposit','Mortgage needed'],series:[{label:'Amount',values:[minimum,available,Math.max(0,price-available)]}]};
        }
        return {type:'bar',title:'How the purchase is funded',caption:'Deposit and mortgage amounts implied by the selected LTV assumption.',labels:['Deposit','Mortgage'],series:[{label:'Amount',values:[minimum,price-minimum]}]};
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
        const months=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,months), series=amortisationSeries(v.amount,v.rate,months,p);
        return {type:'line',title:'Baseline loan balance over time',caption:Boolean(v.__advanced)&&((v.extra_monthly||0)>0||(v.lump_sum||0)>0)?'Shows the original scheduled balance before the optional overpayment scenario, so you can compare it with the shorter payoff result above.':'Scheduled balance under the entered fixed-rate assumptions.',labels:series.labels,series:[{label:'Loan balance',values:series.values}]};
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
        const gain=Math.max(0,v.sale)-Math.max(0,v.purchase)-Math.max(0,v.costs), lossesUsed=Math.min(Math.max(0,v.losses),Math.max(0,gain));
        const exemptionRemaining=Math.max(0,1270-(Boolean(v.__advanced)?Math.max(0,Math.min(1270,v.exemption_used||0)):0));
        const taxable=Math.max(0,Math.max(0,gain-lossesUsed)-exemptionRemaining), tax=taxable*.33;
        return {type:'bar',title:'From gain to estimated CGT',caption:'Uses entered losses and the remaining annual exemption under this scenario.',labels:['Gain','Taxable gain','CGT'],series:[{label:'Amount',values:[Math.max(0,gain),taxable,tax]}]};
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
        const battery=v.distance*v.efficiency/100, wall=battery/Math.max(.01,1-v.loss/100);
        return {type:'bar',currency:false,title:'Battery energy versus grid energy',caption:'Charging losses mean the grid supplies more energy than reaches the battery. Advanced charging-location assumptions change cost, not the kWh needed for this distance.',labels:['Battery','From grid'],series:[{label:'kWh',values:[battery,wall]}]};
      }
      case 'electricity': {
        const advanced=Boolean(v.__advanced), duty=advanced?Math.max(0,Math.min(100,v.duty_cycle))/100:1, offpeak=advanced?Math.max(0,Math.min(100,v.offpeak_share))/100:0;
        const blended=Math.max(0,v.price)*(1-offpeak)+(advanced?Math.max(0,v.offpeak_rate):Math.max(0,v.price))*offpeak;
        const monthly=Math.max(0,v.watts)/1000*Math.max(0,v.hours)*Math.max(0,v.days)*duty*blended, labels=Array.from({length:12},(_,i)=>'M'+(i+1)), vals=labels.map((_,i)=>monthly*(i+1));
        return {type:'line',title:'Cumulative running cost over a year',caption:'Assumes the same monthly usage pattern, duty cycle and tariff split continue for 12 months.',labels,series:[{label:'Cumulative cost',values:vals}]};
      }
      case 'salary_hourly': {
        const base=Math.max(1,v.hours), hours=[Math.max(20,base-5),base,base+5], vals=hours.map(h=>v.salary/(Math.max(1,v.weeks)*h));
        return {type:'bar',title:'Hourly equivalent versus weekly hours',caption:'Same annual salary spread across fewer or more paid working hours.',labels:hours.map(h=>h+' hrs/wk'),series:[{label:'Gross hourly equivalent',values:vals}]};
      }
      case 'fuel': {
        const distance=v.distance*v.trips, litres=distance*v.consumption/100, prices=[v.price*.8,v.price,v.price*1.2], vals=prices.map(p=>litres*p);
        return {type:'bar',title:'Fuel-price sensitivity',caption:'Trip cost if the entered fuel price were 20% lower, unchanged or 20% higher.',labels:['-20%','Current','+20%'],series:[{label:'Fuel cost',values:vals}]};
      }
      case 'prsi_2026': {
        const p=annualClassA2026(v.salary);
        return {type:'bar',title:'Weekly employee PRSI before and after the 2026 rate change',caption:'Class A estimate using the same weekly-equivalent salary.',labels:['Before change','After change'],series:[{label:'Weekly PRSI',values:[p.before,p.after]}]};
      }
      case 'usc_2026': {
        const x=Math.max(0,v.income); if(x<=13000) return null;
        const reduced=Boolean(v.__advanced)&&v.reduced_rate==='yes'&&x<=60000;
        if(reduced){
          const vals=[Math.min(x,12012)*.005,Math.max(0,x-12012)*.02];
          return {type:'bar',title:'USC by reduced rate band',caption:'2026 reduced USC rates apply only when the qualifying conditions are met and aggregate income is €60,000 or less.',labels:['0.5%','2%'],series:[{label:'USC',values:vals}]};
        }
        let left=x; const vals=[]; for(const [size,rate] of [[12012,.005],[16688,.02],[41344,.03],[Infinity,.08]]){const slice=Math.min(left,size);vals.push(Math.max(0,slice*rate));left-=slice;if(left<=0){while(vals.length<4)vals.push(0);break;}}
        return {type:'bar',title:'USC by rate band',caption:'Each rate applies only to income within that standard USC band.',labels:['0.5%','2%','3%','8%'],series:[{label:'USC',values:vals}]};
      }
      case 'cat': {
        const thresholds={A:400000,B:40000,C:20000}, threshold=thresholds[v.group]||0, prior=Math.max(0,v.prior), remaining=Math.max(0,threshold-prior);
        const used=Boolean(v.__advanced)&&v.benefit_type==='gift'?Math.max(0,Math.min(3000,v.small_gift_used||0)):0, available=v.benefit_type==='gift'?Math.max(0,3000-used):0;
        const current=Math.max(0,Math.max(0,v.benefit)-Math.min(available,Math.max(0,v.benefit))), afterTax=Math.max(0,prior+current-threshold)*.33, beforeTax=Math.max(0,prior-threshold)*.33;
        return {type:'bar',title:'Benefit versus remaining CAT threshold',caption:'Uses the selected relationship group, prior aggregated benefits and the remaining small-gift exemption entered.',labels:['Current taxable value','Threshold remaining','Estimated CAT'],series:[{label:'Amount',values:[current,remaining,Math.max(0,afterTax-beforeTax)]}]};
      }
      case 'rent_credit': {
        const rentBased=v.rent*.20, cap=v.joint==='yes'?2000:1000, credit=Math.min(rentBased,cap,v.income_tax_liability);
        return {type:'bar',title:'What limits the Rent Tax Credit?',caption:'The claim is constrained by rent-based calculation, statutory cap and available Income Tax liability.',labels:['Rent-based','Statutory cap','Usable credit'],series:[{label:'Amount',values:[rentBased,cap,Math.max(0,credit)]}]};
      }
      case 'help_to_buy': {
        const affordable=v.__advanced?Math.max(0,v.la_affordable_contribution||0):0;
        const qualifyingFinance=Math.max(0,v.mortgage)+affordable, valueCap=v.property_value*.10;
        const ltv=v.property_value>0?qualifyingFinance/v.property_value*100:0, basic=v.property_value<=500000&&ltv>=70;
        const claim=basic?Math.min(30000,valueCap,v.tax_paid):0;
        return {type:'bar',title:'Help to Buy refund constraints',caption:'The refund is the lowest applicable amount after the property-value and qualifying-finance screens are met.',labels:['€30k cap','10% value cap','Tax paid','Estimated claim'],series:[{label:'Amount',values:[30000,valueCap,v.tax_paid,claim]}]};
      }
      case 'first_home_scheme': {
        const htb=v.htb==='yes'?Math.min(v.htb_amount,v.property_value):0;
        const depositFunds=Math.max(0,v.deposit)+htb, gap=Math.max(0,v.property_value-v.mortgage-depositFunds);
        const max=v.property_value*(v.htb==='yes'?.20:.30), ceiling=fhsPriceCeiling(v.authority,v.property_type);
        return {type:'bar',title:'First Home Scheme funding stack',caption:'Compares the mortgage, deposit/HTB, funding gap and maximum percentage-based FHS contribution. Local price-ceiling eligibility is checked separately.',labels:['Mortgage','Deposit + HTB','Funding gap','Maximum FHS'],series:[{label:'Amount',values:[v.mortgage,depositFunds,gap,max]}]};
      }
      case 'dirt': {
        const tax=v.interest*.33, net=v.interest-tax;
        return {type:'bar',title:'Gross interest after DIRT',caption:'Shows the entered gross deposit interest, DIRT and amount retained.',labels:['Gross interest','DIRT','Net interest'],series:[{label:'Amount',values:[v.interest,tax,net]}]};
      }
      default: return null;
    }
  };
  const buildInsights = (name,v) => {
    const items=[];
    switch(name){
      case 'mortgage': {
        const n=v.years*12, p=monthlyPayment(v.amount,v.rate,n), pUp=monthlyPayment(v.amount,v.rate+.5,n);
        items.push('At this rate and term, every €100,000 borrowed costs about '+money(p/v.amount*100000)+' per month.');
        if(Number.isFinite(pUp)) items.push('If the rate were 0.5 percentage points higher, the monthly repayment would rise by about '+money(pUp-p)+'.');
        break;
      }
      case 'mortgage_overpayment': {
        const p=mortgageOverpaymentProjection(v);
        items.push('Your regular overpayment is '+pct(p.base>0?v.overpayment/p.base*100:0)+' of the scheduled monthly repayment.');
        if(v.__advanced&&p.startAfter>0) items.push('The regular overpayment begins after month '+p.startAfter+', so the early-interest saving is lower than if the same amount started immediately.');
        if(v.__advanced&&p.lumpSum>0) items.push('The '+money(p.lumpSum)+' lump sum is modelled after the scheduled payment in month '+p.lumpMonth+'.');
        if(items.length<3) items.push('Earlier principal reduction usually saves more interest because less balance remains for later months.');
        break;
      }
      case 'mortgage_borrowing': {
        const multiple=v.buyer_type==='ftb'?4:3.5, deposit=Math.max(0,v.deposit), byIncome=Math.max(0,v.income)*multiple+deposit, byDeposit=deposit/.10, maxPrice=Math.min(byIncome,byDeposit);
        const binding=Math.abs(byIncome-byDeposit)<1?'Income and deposit are equally binding':(byIncome<byDeposit?'Income is the tighter standard constraint':'Deposit is the tighter standard constraint');
        items.push(binding+' before lender affordability checks.');
        if(v.__advanced){
          const target=Math.max(0,v.target_price||0), gap=Math.max(0,target-maxPrice);
          items.push(gap>0?'The target price is '+money(gap)+' above the standard LTI/LTV arithmetic shown here.':'The target price sits within the standard LTI/LTV arithmetic shown here, before lender underwriting.');
        }
        items.push('The Central Bank multiple is a ceiling for most lending, not a mortgage approval.');
        break;
      }
      case 'house_deposit': {
        const rate=v.buyer_type==='btl'?.30:.10, minimum=Math.max(0,v.price)*rate;
        items.push('The standard LTV assumption here is a '+pct(rate*100)+' minimum deposit and '+pct((1-rate)*100)+' maximum loan-to-value.');
        if(v.__advanced){
          const available=Math.max(0,v.deposit_available||0), difference=available-minimum;
          items.push(difference>=0?'Your entered deposit is '+money(difference)+' above the standard minimum.':'Your entered deposit is '+money(Math.abs(difference))+' below the standard minimum.');
        }
        items.push('Keep purchase costs and an emergency reserve separate from the deposit where possible.');
        break;
      }
      case 'stamp_duty': {
        const p=Math.max(0,v.price), a=Math.min(p,1000000)*.01, b=Math.max(0,Math.min(p,1500000)-1000000)*.02, d=Math.max(0,p-1500000)*.06, duty=a+b+d;
        items.push(p<=1000000?'The full entered price sits inside the 1% standard residential band.':p<=1500000?'Only the slice above €1 million is charged at 2%.':'The 6% rate applies only to the slice above €1.5 million.');
        if(p>0) items.push('The effective Stamp Duty rate across the full price is '+pct(duty/p*100)+', which is lower than the highest marginal band that may apply.');
        break;
      }
      case 'lpt': {
        const factor=lptAdjust[v.authority]??0;
        items.push(factor===0?'The selected authority applies no local adjustment in the assumptions currently encoded.':'The selected local adjustment changes the basic LPT estimate by '+pct(Math.abs(factor)*100)+(factor>0?' upward.':' downward.'));
        items.push(v.value<=2100000?'The ordinary 2026–2030 LPT bands create step changes at band boundaries.':'Properties above €2.1 million use Revenue’s actual-value percentage formula rather than a fixed band charge.');
        break;
      }
      case 'loan': {
        const n=Math.round(v.years*12), p=monthlyPayment(v.amount,v.rate,n), total=p*n;
        items.push('Modelled scheduled interest is about '+pct(v.amount>0?(total-v.amount)/v.amount*100:0)+' of the amount borrowed over the full term.');
        if(Boolean(v.__advanced)&&((v.extra_monthly||0)>0||(v.lump_sum||0)>0)) items.push('The Advanced overpayment scenario assumes the lender allows those extra repayments on the timing entered; check the agreement for charges or limits.');
        else items.push('A longer term normally lowers the monthly payment but increases total interest.');
        break;
      }
      case 'savings_goal':
        items.push(v.monthly>0?'Each additional €100 per month adds €1,200 a year of direct contributions before growth.':'With no monthly contribution, the goal depends entirely on the starting balance and assumed return.');
        items.push('For short-term goals, test a lower return as well as the central assumption.');
        break;
      case 'net_worth': {
        const assets=Math.max(0,v.cash)+Math.max(0,v.investments)+Math.max(0,v.pensions)+Math.max(0,v.home_value)+(v.__advanced?Math.max(0,v.other_property)+Math.max(0,v.vehicles)+Math.max(0,v.business_value)+Math.max(0,v.other_assets):0);
        const debt=Math.max(0,v.mortgage)+Math.max(0,v.loans)+Math.max(0,v.credit_cards)+Math.max(0,v.other_debt)+(v.__advanced?Math.max(0,v.other_property_mortgage)+Math.max(0,v.tax_liabilities):0);
        if(assets>0) items.push('Liabilities are about '+pct(debt/assets*100)+' of the assets entered.');
        items.push('Track the same valuation method over time; the trend is usually more useful than comparing yourself with another household.');
        break;
      }
      case 'regular_savings': {
        const months=Math.round(v.years*12), r=Math.pow(Math.max(.000001,1+v.rate/100),1/12)-1; let bal=v.current; for(let i=0;i<months;i++){bal*=1+r;bal+=v.monthly;}
        const contrib=v.current+v.monthly*months, growth=bal-contrib;
        items.push('Under this smooth-return model, growth provides about '+pct(bal>0?growth/bal*100:0)+' of the ending balance.');
        break;
      }
      case 'pension_relief': {
        const limit=Math.min(v.earnings,115000)*pensionPct(v.age), eligible=Math.min(v.contribution,limit);
        items.push('The entered contribution uses about '+pct(limit>0?eligible/limit*100:0)+' of the age-related tax-relief limit in this illustration.');
        items.push('Tax relief reduces the effective cash cost; it does not guarantee any investment return.');
        break;
      }
      case 'cgt': {
        const gain=Math.max(0,v.sale)-Math.max(0,v.purchase)-Math.max(0,v.costs), used=Boolean(v.__advanced)?Math.max(0,Math.min(1270,v.exemption_used||0)):0;
        const remaining=Math.max(0,1270-used), taxable=Math.max(0,Math.max(0,gain-Math.max(0,v.losses))-remaining);
        items.push(taxable>0?'After entered losses and the remaining annual exemption, '+money(taxable)+' remains taxable in this simplified scenario.':'The entered gain is fully absorbed by losses/the remaining annual exemption in this simplified scenario.');
        if(Boolean(v.__advanced)&&used>0) items.push(money(used)+' of the €1,270 annual exemption is assumed to have been used elsewhere in the tax year.');
        break;
      }
      case 'vat': {
        const rate=Number(v.rate)/100; const gross=v.direction==='gross'?v.amount:v.amount*(1+rate), vat=v.direction==='gross'?(rate===0?0:v.amount-v.amount/(1+rate)):v.amount*rate;
        if(gross>0) items.push('VAT represents about '+pct(vat/gross*100)+' of the VAT-inclusive price at this rate.');
        break;
      }
      case 'inflation': {
        const factor=Math.pow(1+v.rate/100,v.years);
        items.push('Over '+v.years+' years, the modelled price level changes by about '+pct((factor-1)*100)+'.');
        items.push('A future nominal amount should be judged against its purchasing power, not just its euro value.');
        break;
      }
      case 'emergency': {
        const target=v.expenses*Number(v.months), gap=Math.max(0,target-v.current);
        items.push(gap===0?'The entered reserve already meets the target.':'The remaining gap equals about '+number.format(v.expenses>0?gap/v.expenses:0)+' months of the essential spending entered.');
        break;
      }
      case 'salary_hourly':
        items.push('The hourly equivalent depends on '+v.hours+' paid hours a week across '+v.weeks+' paid weeks.');
        items.push('Compare contractor rates only after allowing for unpaid leave, downtime, pension and other employment benefits.');
        break;
      case 'fuel': {
        const distance=v.distance*v.trips, cost=distance*v.consumption/100*v.price;
        if(distance>0) items.push('Fuel alone costs about '+money(cost/distance)+' per kilometre under these assumptions.');
        if(Boolean(v.__advanced)&&v.annual_distance>0) items.push('The annual-distance scenario uses the same consumption and pump price as the trip calculation.');
        items.push('Depreciation, finance, insurance, tax and servicing are outside this fuel-only comparison.');
        break;
      }
      case 'ev': {
        const battery=v.distance*v.efficiency/100, wall=battery/Math.max(.01,1-v.loss/100);
        items.push('Charging losses add about '+num(Math.max(0,wall-battery))+' kWh of grid demand over the entered distance.');
        if(Boolean(v.__advanced)) items.push('Advanced mode weights the home and public charging prices by the charging-location split you entered.');
        else items.push('Use Advanced mode if some charging happens on more expensive public chargers.');
        break;
      }
      case 'electricity': {
        const duty=Boolean(v.__advanced)?Math.max(0,Math.min(100,v.duty_cycle))/100:1, kwh=v.watts/1000*v.hours*v.days*duty;
        items.push('The entered usage works out at about '+num(kwh/Math.max(1,v.days))+' kWh on each day of use.');
        if(Boolean(v.__advanced)&&v.duty_cycle<100) items.push('The Advanced duty-cycle assumption reduces nameplate power to reflect time spent cycling off or running below full load.');
        else items.push('Cycling appliances can consume less than their nameplate wattage suggests.');
        break;
      }
      case 'take_home_2026': {
        const pension=Math.max(0,v.salary*v.pension_pct/100), reduced=Boolean(v.__advanced)&&v.usc_reduced==='yes', net=employeeNet2026(v.salary,pension,v.band,v.other_credits,reduced);
        if(v.salary>0) items.push('Estimated take-home after the deductions modelled is about '+pct(net.net/v.salary*100)+' of gross salary.');
        if(reduced && v.salary<=60000) items.push('The advanced scenario is using the 2026 reduced USC bands. Revenue eligibility conditions still need to be satisfied.');
        else if(reduced && v.salary>60000) items.push('Reduced USC cannot apply above €60,000 aggregate income, so standard USC rates are used.');
        items.push('Your marginal deduction rate on the next euro can be much higher than your average deduction rate.');
        break;
      }
      case 'income_tax_2026': {
        const t=incomeTax2026(Math.max(0,v.income-v.pension),v.band,v.credits);
        if(v.income>0) items.push('Estimated Income Tax alone is about '+pct(t.net/v.income*100)+' of the gross income entered after the selected pension deduction.');
        break;
      }
      case 'usc_2026': {
        const reduced=Boolean(v.__advanced)&&v.reduced_rate==='yes'&&v.income<=60000, u=usc2026(v.income,reduced);
        if(v.income>0) items.push('The effective USC rate in this scenario is '+pct(u/v.income*100)+', lower than the highest marginal band because USC is progressive.');
        if(Boolean(v.__advanced)&&v.reduced_rate==='yes'&&v.income>60000) items.push('The reduced-rate option is not applied because Revenue limits it to qualifying people with aggregate income of €60,000 or less.');
        else if(reduced) items.push('This scenario uses the reduced 2026 USC rates: 0.5% on the first €12,012 and 2% on the balance.');
        break;
      }
      case 'prsi_2026': {
        const p=annualClassA2026(v.salary); if(v.salary>0) items.push('Estimated employee PRSI is about '+pct(p.annual/v.salary*100)+' of annual salary under these Class A assumptions.');
        break;
      }
      case 'cat': {
        const thresholds={A:400000,B:40000,C:20000}, threshold=thresholds[v.group]||0, prior=Math.max(0,v.prior), used=Boolean(v.__advanced)&&v.benefit_type==='gift'?Math.max(0,Math.min(3000,v.small_gift_used||0)):0;
        const small=v.benefit_type==='gift'?Math.max(0,3000-used):0, current=Math.max(0,Math.max(0,v.benefit)-Math.min(small,Math.max(0,v.benefit))), aggregate=prior+current;
        items.push('Before this benefit, about '+money(Math.max(0,threshold-prior))+' of the selected group threshold remains under the amounts entered.');
        if(v.benefit_type==='gift') items.push('This scenario has '+money(small)+' of the €3,000 annual small-gift exemption still available from this disponer before the current gift.');
        if(aggregate>=threshold*.8) items.push('The aggregate reaches the general 80% numerical IT38 filing marker; other filing triggers can also apply.');
        else items.push('Relevant prior gifts and inheritances in the same group are part of the calculation.');
        break;
      }
      case 'rent_credit': {
        const rentBased=v.rent*.20, cap=v.joint==='yes'?2000:1000, vals=[['rent-based amount',rentBased],['statutory cap',cap],['Income Tax liability',v.income_tax_liability]].sort((a,b)=>a[1]-b[1]);
        items.push('The '+vals[0][0]+' is the binding limit in this simplified scenario.');
        break;
      }
      case 'help_to_buy': {
        const affordable=v.__advanced?Math.max(0,v.la_affordable_contribution||0):0;
        const qualifyingFinance=Math.max(0,v.mortgage)+affordable, ltv=v.property_value>0?qualifyingFinance/v.property_value*100:0;
        items.push(v.property_value<=500000&&ltv>=70?'The inputs pass the calculator’s basic property-value and 70% qualifying-finance screen.':'The inputs fail at least one basic property-value/qualifying-finance screen.');
        if(affordable>0) items.push('Advanced mode counts '+money(affordable)+' of Local Authority affordable dwelling contribution with the mortgage for the 70% test. First Home Scheme equity is excluded.');
        else items.push('Revenue approval and qualifying Income Tax/DIRT still determine the actual refund.');
        break;
      }
      case 'first_home_scheme': {
        const htb=v.htb==='yes'?Math.min(v.htb_amount,v.property_value):0, depositFunds=Math.max(0,v.deposit)+htb;
        const gap=Math.max(0,v.property_value-v.mortgage-depositFunds), ceiling=fhsPriceCeiling(v.authority,v.property_type);
        if(v.property_value>0) items.push('The modelled funding gap is '+pct(gap/v.property_value*100)+' of the property price; the selected local price ceiling is '+money(ceiling)+'.');
        if(gap>0) items.push('If the full '+money(gap)+' equity share remained outstanding, the year-6 service charge would be about '+money(gap*.0175)+' before any redemption.');
        items.push('Formal eligibility also requires the maximum mortgage available from a participating lender, subject to the scheme rules.');
        break;
      }
      case 'dirt':
        items.push('At the standard 33% DIRT rate, about 67% of the gross deposit interest remains before any exemption/refund considerations.');
        if(Boolean(v.__advanced)) items.push('The Advanced projection assumes interest is credited annually and 33% DIRT is deducted from each year’s interest before the remaining interest compounds.');
        break;
      case 'contractor_vs_salary': {
        const employee=employeeNet2026(v.salary,0,44000,0), revenue=v.day_rate*v.billable_days, profit=Math.max(0,revenue-v.contractor_costs), contractor=selfEmployedNet2026(profit,Math.min(v.contractor_pension,profit));
        const diff=contractor.net-employee.net;
        items.push('The contractor scenario is '+(diff>=0?'ahead by ':'behind by ')+money(Math.abs(diff))+' in estimated annual net cash before valuing employment benefits.');
        items.push(v.billable_days+' billable days are doing significant work in the contractor annualisation.');
        break;
      }
      case 'investment_fees':
        items.push('The fee assumptions differ by '+pct(Math.abs(v.fee_high-v.fee_low))+' percentage points a year over '+v.years+' years.');
        items.push('Fee drag compounds because money paid in fees also loses future growth.');
        break;
      case 'fire_number':
        const realAnnual=(1+v.return_rate/100)/(1+v.inflation_rate/100)-1;
        items.push('A '+pct(v.withdrawal_rate)+' withdrawal assumption implies a target equal to about '+number.format(100/v.withdrawal_rate)+' times annual spending.');
        items.push('The entered '+pct(v.return_rate)+' nominal return and '+pct(v.inflation_rate)+' inflation imply about '+pct(realAnnual*100)+' annual real return in this model.');
        break;
      case 'retirement_income':
        items.push('The first-year portfolio withdrawal is '+pct(v.withdrawal_rate)+' of the starting pot before tax.');
        if(v.state_pension+v.other_income>0) items.push('Non-portfolio income supplies '+pct((v.state_pension+v.other_income)/(v.pot*v.withdrawal_rate/100+v.state_pension+v.other_income)*100)+' of the modelled first-year gross income.');
        items.push('The sustainability path assumes a smooth '+pct(v.return_rate)+' annual return and withdrawals rising '+pct(v.inflation_rate)+' a year; real markets will be uneven.');
        break;
      case 'pension_projection':
        const netAnnual=(1+v.return_rate/100)*(1-v.annual_fee/100)-1;
        items.push('The modelled annual return after the entered fee is about '+pct(netAnnual*100)+'.');
        items.push('At '+pct(v.inflation_rate)+' inflation, the today’s-money result can be materially lower than the future nominal pot.');
        break;
      case 'rent_vs_buy': {
        items.push('The model assumes house-price growth of '+pct(v.house_growth)+' and renter investment returns of '+pct(v.renter_return)+'. Small changes to either can move a long-term result materially.');
        if(v.__advanced) items.push('Treat the renter return as a net return after the fees and tax treatment that would apply to your actual investment rather than a headline market return.');
        if(v.years>v.mortgage_years) items.push('The comparison continues beyond the entered mortgage term, so the buyer stops making mortgage payments after the modelled balance reaches zero.');
        else items.push('A robust decision should survive more than one plausible assumption set.');
        break;
      }
      case 'mortgage_affordability': {
        const multiple=v.buyer_type==='ftb'?4:3.5, income=Math.max(0,v.income), debt=Math.max(0,v.other_debt);
        const lti=income*multiple, grossLimit=Math.max(0,income/12*v.max_payment_pct/100-debt);
        const useNet=Boolean(v.__advanced)&&Math.max(0,v.net_income_monthly)>0;
        const netLimit=useNet?Math.max(0,v.net_income_monthly-Math.max(0,v.essential_spend_monthly)-debt-Math.max(0,v.buffer_monthly)):Infinity;
        const capacity=Math.min(grossLimit,netLimit), r=v.rate/100/12,n=v.term*12;
        const paymentBased=r===0?capacity*n:capacity*(1-Math.pow(1+r,-n))/r,depositBased=Math.max(0,v.deposit)*9;
        const constraints=[['The LTI ceiling',lti],['Your payment budget',paymentBased],['Your deposit at 90% LTV',depositBased]].sort((a,b)=>a[1]-b[1]);
        items.push(constraints[0][0]+' is the tightest mortgage constraint in this scenario.');
        if(useNet) items.push('The optional net-income budget lowers the monthly mortgage capacity to '+money(capacity)+' after the spending, debt and buffer entered.');
        else items.push('The '+pct(v.max_payment_pct)+' gross-income payment share is your modelling choice, not an official affordability rule.');
        break;
      }
      case 'house_buying_costs': {
        const advanced=Boolean(v.__advanced), deposit=v.price*v.deposit_pct/100, professional=v.legal+v.survey+v.valuation;
        const setup=v.moving+v.other+(advanced?v.insurance_setup+v.furnishing+v.immediate_works:0);
        const total=deposit+stampDutyResidential(v.price)+professional+setup;
        if(v.price>0) items.push('The upfront cash budget is about '+pct(total/v.price*100)+' of the purchase price under the costs entered.');
        if(advanced){
          const target=total+Math.max(0,v.reserve), position=Math.max(0,v.cash_available)-target;
          items.push(position>=0?'Your cash input leaves about '+money(position)+' above the entered purchase-plus-reserve target.':'Your cash input is about '+money(Math.abs(position))+' short of the entered purchase-plus-reserve target.');
        }
        break;
      }
      case 'solar_payback':
        items.push('Directly used solar is valued against avoided imports, while exports are valued at the separate export rate.');
        if(v.has_ev) items.push('EV solar charging is valued against the '+money(v.ev_alternative_rate)+'/kWh rate you say the car would otherwise use.');
        break;
      case 'ber_energy':
        if(v.current_kwh_m2>0) items.push('The target energy-use assumption is '+pct((1-v.target_kwh_m2/v.current_kwh_m2)*100)+' lower than the current assumption.');
        items.push('BER performance and actual metered bills are related but not identical.');
        break;
      case 'solar_optimizer':
        items.push('The day-versus-night tariff spread entered is '+money(Math.max(0,v.day_rate-v.night_rate))+'/kWh before battery losses.');
        items.push('Maximum self-consumption is not automatically maximum financial value when export and EV rates differ.');
        break;
      case 'retrofit_planner': {
        items.push('The entered energy-saving assumption is '+pct(v.saving_pct)+' of the current annual energy bill.');
        if(Boolean(v.__advanced)&&v.heat_pump&&(v.central_heating_upgrade||v.renewable_heat_bonus)) items.push('Advanced mode is including only the conditional 2026 heat-pump grants you explicitly selected; final SEAI eligibility still needs to be confirmed.');
        items.push('Simple payback does not capture comfort, ventilation, building durability or financing.');
        break;
      }
      case 'myfuturefund':
        items.push('The statutory employee contribution rate starts lower and phases upward over time, so future take-home impact will not stay at the 2026 level.');
        items.push('Employer and State contributions are part of the retirement value even though they are not employee take-home deductions.');
        break;
      case 'childcare_return':
        items.push('This is an immediate cash-flow comparison; employer pension value and future career earnings are not included in the headline household gain.');
        items.push('Using your actual NCS award and provider fee matters more than relying on national averages.');
        break;
      case 'mortgage_switch': {
        const p1=monthlyPayment(v.balance,v.current_rate,Math.round(v.current_years*12)), p2=monthlyPayment(v.balance,v.new_rate,Math.round(v.new_years*12)), saving=p1-p2;
        const horizon=v.__advanced?Math.max(1,Math.round(v.comparison_years||5)):5;
        items.push(saving>0?'The alternative reduces the modelled monthly repayment by '+money(saving)+'.':'The alternative does not reduce the modelled monthly repayment.');
        items.push('The short-term comparison uses a '+horizon+'-year horizon; keep it within the period for which the entered rates are a reasonable assumption.');
        if(v.current_years!==v.new_years) items.push('The terms differ, so compare the remaining balances as well as the monthly payments.');
        break;
      }
      case 'lifetime_cost':
        items.push('The scenario spans '+Math.max(0,Math.floor(v.end_age-v.current_age))+' years, so the '+pct(v.inflation)+' inflation assumption has a large effect on nominal totals.');
        items.push('Use today’s-money spending to separate lifestyle scale from inflation.');
        break;
      case 'car_finance':
        items.push('PCP monthly payments are reduced by deferring part of the financed amount into the final balloon/GMFV.');
        items.push('Compare total paid and end-of-term ownership, not monthly payment alone.');
        break;
      case 'nutrition_needs':
        items.push('Maintenance energy is a prediction from resting energy × the selected activity factor, not a direct measurement.');
        items.push('The protein setting is '+(v.protein_context==='resistance'?'1.6 g/kg/day for the resistance-training illustration.':'0.83 g/kg/day for the general adult reference illustration.'));
        break;
      case 'pregnancy_timeline':
        items.push(v.assigned_due_date?'The assigned due date takes priority over the LMP-derived estimate in this scenario.':'The due date is estimated as 280 days from the LMP entered.');
        items.push('Clinical dating from an early ultrasound can supersede a menstrual-date estimate.');
        break;
      case 'alcohol_ireland':
        items.push('Ireland defines one standard drink as 10 g of pure alcohol; drink size and ABV both matter.');
        items.push('The calorie figure covers ethanol itself and can understate total drink calories where sugar or mixers add energy.');
        break;
    }
    return items.slice(0,3);
  };

  const validateRelationships = (name,v) => {
    if(name==='pension_projection' && v.retirement_age<=v.age) return 'Target retirement age must be later than your current age.';
    if(name==='lifetime_cost' && v.end_age<=v.current_age) return 'The projection end age must be later than your current age.';
    if(name==='car_finance' && v.deposit>v.car_price) return 'The car-finance deposit cannot exceed the car price.';
    if(name==='rent_vs_buy' && v.deposit>v.house_price) return 'The deposit cannot exceed the home purchase price in this comparison.';
    if(name==='mortgage_switch' && v.balance===0) return 'Enter a current mortgage balance above €0 to compare switching.';
    if(name==='mortgage_overpayment' && v.balance===0) return 'Enter a current mortgage balance above €0.';
    if(name==='mortgage_overpayment' && v.__advanced && v.lump_sum>0 && v.lump_sum_month>v.years*12) return 'The lump-sum month must fall within the remaining mortgage term.';
    if(name==='mortgage_overpayment' && v.__advanced && v.overpayment_start_month>=v.years*12 && v.overpayment>0) return 'The regular overpayment must start before the remaining mortgage term ends.';
    if(name==='first_home_scheme' && v.property_value===0) return 'Enter a property value above €0.';
    if(name==='help_to_buy' && v.property_value===0) return 'Enter a property value above €0.';
    return '';
  };

  const renderInsights = (root,items) => {
    const panel=root.querySelector('[data-tool-insights]'), list=root.querySelector('[data-tool-insight-list]');
    if(!panel||!list) return;
    list.innerHTML='';
    (items||[]).forEach(text=>{const li=document.createElement('li');li.textContent=text;list.appendChild(li);});
    panel.hidden=!(items&&items.length);
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
      const amount=Math.max(0,v.amount),n=Math.max(1,Math.round(v.years*12)),p=monthlyPayment(amount,v.rate,n),total=p*n;
      const firstYear=mortgageSnapshot(amount,v.rate,n,p,Math.min(12,n));
      const fiveYears=mortgageSnapshot(amount,v.rate,n,p,Math.min(60,n));
      const firstYearPrincipal=Math.max(0,amount-firstYear.balance);
      const stress1=monthlyPayment(amount,Math.max(0,v.rate)+1,n),stress2=monthlyPayment(amount,Math.max(0,v.rate)+2,n);
      return {
        monthly:money(p),interest:money(Math.max(0,total-amount)),total:money(total),annual_repayment:money(p*12),
        first_year_interest:money(firstYear.interest),first_year_principal:money(firstYearPrincipal),
        balance_5y:money(fiveYears.balance),stress_1pp:money(stress1),stress_2pp:money(stress2),
        payment_per_100k:money(amount>0?p/amount*100000:0)
      };
    },
    mortgage_overpayment(v){
      const p=mortgageOverpaymentProjection(v);
      return {
        payment:money(p.base),
        new_payment:money(p.pay),
        new_term:duration(p.scenarioMonths),
        time_saved:duration(Math.max(0,p.months-p.scenarioMonths)),
        standard_interest:money(p.standardInterest),
        overpayment_interest:money(p.interest),
        interest_saved:money(Math.max(0,p.standardInterest-p.interest)),
        __chart:fallbackChart('mortgage_overpayment',v)
      };
    },
    mortgage_borrowing(v){
      const multiple=v.buyer_type==='ftb'?4:3.5, income=Math.max(0,v.income), deposit=Math.max(0,v.deposit);
      const lti=income*multiple, byIncome=lti+deposit, depPrice=deposit/.10, maxPrice=Math.max(0,Math.min(byIncome,depPrice));
      const binding=Math.abs(byIncome-depPrice)<1?'Income and deposit':(byIncome<depPrice?'Income':'Deposit');
      const target=Math.max(0,v.target_price||0), targetMortgage=Math.max(0,target-deposit), targetIncome=multiple>0?targetMortgage/multiple:0;
      const targetMinDeposit=target*.10, targetGap=Math.max(0,target-maxPrice);
      return {
        lti_multiple:number.format(multiple)+'× gross income',
        lti_limit:money(lti),
        deposit_limit:money(depPrice),
        purchase_price:money(maxPrice),
        binding_constraint:binding,
        target_mortgage:money(targetMortgage),
        target_income:money(targetIncome),
        target_min_deposit:money(targetMinDeposit),
        target_gap:targetGap>0?money(targetGap):'No standard-rule gap',
        __chart:fallbackChart('mortgage_borrowing',v)
      };
    },
    house_deposit(v){
      const price=Math.max(0,v.price), rate=v.buyer_type==='btl'?.30:.10, dep=price*rate, maxMortgage=Math.max(0,price-dep);
      const available=Math.min(price,Math.max(0,v.deposit_available||0)), difference=available-dep, needed=Math.max(0,price-available);
      const resultingLtv=price>0?needed/price*100:0;
      return {
        deposit_rate:pct(rate*100),
        deposit:money(dep),
        mortgage:money(maxMortgage),
        ltv:pct((1-rate)*100),
        deposit_position:(difference>=0?'+':'-')+money(Math.abs(difference))+(difference>=0?' above minimum':' below minimum'),
        resulting_ltv:pct(resultingLtv),
        mortgage_with_available:money(needed),
        __chart:fallbackChart('house_deposit',v)
      };
    },
    stamp_duty(v){
      const p=Math.max(0,v.price);
      const band1=Math.min(p,1000000)*.01, band2=Math.max(0,Math.min(p,1500000)-1000000)*.02, band6=Math.max(0,p-1500000)*.06;
      const duty=band1+band2+band6;
      return {duty:money(duty),band_1_duty:money(band1),band_2_duty:money(band2),band_6_duty:money(band6),effective_rate:pct(p?duty/p*100:0),total_cost:money(p+duty)};
    },
    lpt(v){
      const value=Math.max(0,v.value);
      let base=0, bandLabel='';
      if(value<=2100000){
        const idx=lptBands.findIndex(b=>value<=b[0]), band=idx>=0?lptBands[idx]:null;
        base=band?band[1]:0;
        const lower=idx<=0?1:lptBands[idx-1][0]+1, upper=band?band[0]:2100000;
        bandLabel='€'+Math.round(lower).toLocaleString('en-IE')+'–€'+Math.round(upper).toLocaleString('en-IE');
      } else {
        base=1260000*.000906 + (2100000-1260000)*.0025 + (value-2100000)*.003;
        bandLabel='Over €2.1m — actual-value formula';
      }
      const factor=lptAdjust[v.authority]??0, adj=base*factor, total=base+adj;
      return {
        valuation_band:bandLabel,
        base_lpt:money(base),
        local_factor:(factor>0?'+':'')+pct(factor*100),
        adjustment:(factor>=0?'+':'-')+money(Math.abs(adj)),
        lpt:money(total),
        monthly_lpt:money(total/12),
        effective_rate:pct(value?total/value*100:0)
      };
    },
    loan(v){
      const advanced=Boolean(v.__advanced), amount=Math.max(0,v.amount), n=Math.max(1,Math.round(v.years*12)), p=monthlyPayment(amount,v.rate,n), total=p*n, standardInterest=Math.max(0,total-amount);
      const fee=advanced?Math.max(0,v.upfront_fee):0, extra=advanced?Math.max(0,v.extra_monthly):0;
      const extraStart=advanced?Math.max(1,Math.round(v.extra_start_month)):Infinity;
      const lump=advanced?Math.max(0,v.lump_sum):0, lumpMonth=advanced?Math.max(1,Math.round(v.lump_sum_month)):Infinity;
      const r=Math.max(0,v.rate)/100/12;
      let bal=amount, scenarioInterest=0, scenarioPaid=0, months=0;
      while(bal>0.005 && months<1200){
        months++;
        const interest=bal*r; scenarioInterest+=interest; bal+=interest;
        let due=p+(months>=extraStart?extra:0)+(months===lumpMonth?lump:0);
        if(!Number.isFinite(due)||due<=0) break;
        const payment=Math.min(bal,due); bal=Math.max(0,bal-payment); scenarioPaid+=payment;
      }
      const saved=Math.max(0,standardInterest-scenarioInterest);
      return {
        monthly:money(p),interest:money(standardInterest),total:money(total),
        payoff_time:advanced?duration(months):duration(n),
        scenario_interest:money(scenarioInterest),
        interest_saved:money(saved),
        scenario_total:money(scenarioPaid+fee)
      };
    },
    savings_goal(v){
      const advanced=Boolean(v.__advanced), start=Math.max(0,v.current), initialTarget=Math.max(0,v.target);
      const r=Math.pow(Math.max(.000001,1+v.rate/100),1/12)-1;
      const targetR=advanced?Math.pow(Math.max(.000001,1+v.target_growth/100),1/12)-1:0;
      const contributionGrowth=advanced?Math.max(-.99,v.annual_contribution_growth/100):0, annualLump=advanced?Math.max(0,v.annual_lump):0;
      let bal=start, target=initialTarget, monthly=Math.max(0,v.monthly), months=0, contributed=0;
      const labels=['Start'], balances=[bal], targets=[target];
      if(bal>=target) return {
        time:'Already reached',contributions:money(0),growth:money(0),ending_balance:money(bal),ending_target:money(target),monthly_at_target:money(monthly),
        __chart:{type:'line',title:'Path to the savings goal',caption:'The current balance already meets or exceeds the target entered.',labels,series:[{label:'Projected balance',values:balances},{label:'Target',values:targets}]}
      };
      while(bal<target && months<1200){
        bal*=1+r;
        bal+=monthly; contributed+=monthly; months++;
        target*=1+targetR;
        if(months%12===0){
          if(annualLump>0){bal+=annualLump;contributed+=annualLump;}
          if(bal<target) monthly*=1+contributionGrowth;
        }
        if(months%12===0 || bal>=target){
          labels.push(months%12===0?'Year '+(months/12):duration(months));
          balances.push(bal);targets.push(target);
        }
      }
      const reached=bal>=target, growth=bal-start-contributed;
      return {
        time:reached?duration(months):'Not reached within 100 years',
        contributions:money(contributed),
        growth:money(growth),
        ending_balance:money(bal),
        ending_target:money(target),
        monthly_at_target:money(monthly),
        __chart:{type:'line',title:'Path to the savings goal',caption:advanced?'Balance and target both follow the assumptions entered. Monthly saving can rise annually and any annual lump sum is added at each 12-month point.':'Modelled balance against the fixed target using the net annual return and monthly contribution entered.',labels,series:[{label:'Projected balance',values:balances},{label:'Target',values:targets}]}
      };
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
      const advanced=Boolean(v.__advanced), months=Math.max(0,Math.round(v.years*12));
      const contributionGrowth=advanced?Math.max(-.99,v.annual_contribution_growth/100):0, fee=advanced?Math.max(0,v.annual_fee):0;
      const simulate=feePct=>{
        const netAnnual=(1+v.rate/100)*(1-feePct/100)-1, r=Math.pow(Math.max(.000001,1+netAnnual),1/12)-1;
        let bal=Math.max(0,v.current), contributed=bal, monthly=Math.max(0,v.monthly);
        const labels=['Start'], balances=[bal], contributions=[contributed];
        for(let m=1;m<=months;m++){
          bal=bal*(1+r)+monthly; contributed+=monthly;
          if(m%12===0 && m<months) monthly*=1+contributionGrowth;
          if(m%12===0 || m===months){labels.push(m%12===0?'Year '+(m/12):duration(m));balances.push(bal);contributions.push(contributed);}
        }
        return {bal,contributed,monthly,labels,balances,contributions,netAnnual};
      };
      const main=simulate(fee), noFee=simulate(0);
      const inflation=advanced?Math.max(-.99,v.inflation_rate/100):0, years=months/12;
      const real=main.bal/Math.pow(1+inflation,years), feeDrag=Math.max(0,noFee.bal-main.bal);
      return {
        final:money(main.bal),
        contributed:money(main.contributed),
        growth:money(main.bal-main.contributed),
        net_return:pct(main.netAnnual*100),
        real_balance:money(real),
        ending_monthly:money(main.monthly),
        fee_drag:money(feeDrag),
        __chart:{type:'line',title:'Contributions versus projected balance',caption:advanced?'The projected balance uses the entered return, annual percentage fee and contribution-growth assumption. Contributions show money actually added.':'Shows how much comes from money added versus modelled growth at the entered constant annual return.',labels:main.labels,series:[{label:'Projected balance',values:main.balances},{label:'Money contributed',values:main.contributions}]}
      };
    },
    pension_relief(v){
      const pctLimit=pensionPct(v.age), earnings=Math.min(Math.max(0,v.earnings),115000), limit=earnings*pctLimit;
      const existing=v.__advanced?Math.max(0,v.existing_contributions):0, remaining=Math.max(0,limit-existing), contribution=Math.max(0,v.contribution);
      const eligible=Math.min(contribution,remaining), excess=Math.max(0,contribution-eligible), relief=eligible*(Number(v.tax_rate)/100);
      return {
        age_percentage:pct(pctLimit*100),
        earnings_used:money(earnings),
        limit:money(limit),
        remaining_limit:money(remaining),
        eligible:money(eligible),
        excess:money(excess),
        relief:money(relief),
        net_cost:money(contribution-relief),
        __chart:{type:'bar',title:'New contribution inside and outside the relief limit',caption:'The age-related limit is applied to earnings up to €115,000, then any employee/personal contributions already entered are deducted before assessing the new contribution.',labels:['New contribution','Potentially eligible','Above remaining limit','Illustrative Income Tax relief'],series:[{label:'Amount',values:[contribution,eligible,excess,relief]}]}
      };
    },
    cgt(v){
      const advanced=Boolean(v.__advanced), gain=Math.max(0,v.sale)-Math.max(0,v.purchase)-Math.max(0,v.costs);
      const losses=Math.max(0,v.losses), lossesUsed=Math.min(losses,Math.max(0,gain)), afterLoss=Math.max(0,gain-lossesUsed);
      const exemptionUsed=advanced?Math.max(0,Math.min(1270,v.exemption_used||0)):0, exemptionRemaining=Math.max(0,1270-exemptionUsed);
      const exemptionApplied=Math.min(afterLoss,exemptionRemaining), taxable=Math.max(0,afterLoss-exemptionApplied), tax=taxable*.33;
      const lossGenerated=Math.max(0,-gain), unusedLosses=Math.max(0,losses-lossesUsed);
      return {
        gain:money(gain),taxable:money(taxable),tax:money(tax),
        exemption_remaining:money(exemptionRemaining),losses_used:money(lossesUsed),
        unused_losses:money(unusedLosses),loss_generated:money(lossGenerated)
      };
    },
    vat(v){
      const amount=Math.max(0,v.amount),r=Math.max(0,Number(v.rate))/100; let net,vat,gross;
      if(v.direction==='gross'){ gross=amount; net=r===0?gross:gross/(1+r); vat=gross-net; }
      else { net=amount; vat=net*r; gross=net+vat; }
      return {
        net:money(net),vat:money(vat),gross:money(gross),
        vat_share_gross:pct(gross?vat/gross*100:0),
        multiplier:r===0?'1.000×':number.format(1+r)+'×'
      };
    },
    inflation(v){
      const amount=Math.max(0,v.amount), years=Math.max(0,v.years), inflation=Math.max(-.99,v.rate/100), factor=Math.pow(1+inflation,years);
      const future=amount*factor, power=factor===0?0:amount/factor;
      const nominal=v.__advanced?Math.max(-.99,v.nominal_return/100):0, real=(1+nominal)/(1+inflation)-1;
      const grown=amount*Math.pow(1+nominal,years), grownReal=factor===0?0:grown/factor;
      const chartYears=Math.round(years), labels=Array.from({length:chartYears+1},(_,i)=>i===0?'Today':'Year '+i);
      const futureSeries=labels.map((_,i)=>amount*Math.pow(1+inflation,i)), powerSeries=labels.map((_,i)=>amount/Math.pow(1+inflation,i));
      return {
        future_cost:money(future),
        purchasing_power:money(power),
        lost_power:money(amount-power),
        price_multiplier:number.format(factor)+'×',
        real_return:pct(real*100),
        nominal_growth_value:money(grown),
        real_growth_value:money(grownReal),
        __chart:{type:'line',title:'Inflation compounds in both directions',caption:'Future cost of today’s amount versus the purchasing power of holding the same nominal euro amount.',labels,series:[{label:'Future cost',values:futureSeries},{label:'Purchasing power',values:powerSeries}]}
      };
    },
    emergency(v){
      const advanced=Boolean(v.__advanced), recurring=Math.max(0,v.expenses)+(advanced?Math.max(0,v.annual_essentials)/12:0);
      const target=recurring*Number(v.months)+(advanced?Math.max(0,v.extra_buffer):0), current=Math.max(0,v.current), gap=Math.max(0,target-current);
      const annualRate=advanced?Math.max(-.99,v.interest_rate/100):0, r=Math.pow(1+annualRate,1/12)-1, monthly=Math.max(0,v.monthly);
      let bal=current, months=0, contributed=0;
      const labels=['Start'], balances=[bal], targets=[target];
      while(bal<target && months<1200){
        bal=bal*(1+r)+monthly; contributed+=monthly; months++;
        if(months%12===0 || bal>=target){labels.push(months%12===0?'Year '+(months/12):duration(months));balances.push(bal);targets.push(target);}
        if(monthly<=0 && r<=0) break;
      }
      const reached=bal>=target, deadline=advanced?Math.max(1,Math.round(v.deadline_months)):24;
      const futureCurrent=current*Math.pow(1+r,deadline);
      let needed=0;
      if(futureCurrent<target){
        const annuity=Math.abs(r)<1e-12?deadline:(Math.pow(1+r,deadline)-1)/r;
        needed=annuity>0?(target-futureCurrent)/annuity:Infinity;
      }
      return {
        target:money(target),
        gap:money(gap),
        time:gap===0?'Already reached':(reached?duration(months):'Not reached within 100 years'),
        coverage_now:recurring>0?number.format(current/recurring)+' months':'No recurring essentials entered',
        monthly_needed:Number.isFinite(needed)?money(Math.max(0,needed)):'Not calculable',
        interest_growth:money(reached?bal-current-contributed:bal-current-contributed),
        __chart:{type:'line',title:'Emergency-fund path',caption:advanced?'Includes irregular essential bills, the extra buffer and the net savings-interest assumption entered.':'Current savings grow only from the monthly amount entered; no interest is assumed in Basic mode.',labels,series:[{label:'Projected emergency fund',values:balances},{label:'Target',values:targets}]}
      };
    },
    salary_hourly(v){
      const salary=Math.max(0,v.salary),hours=Math.max(0,v.hours),weeks=Math.max(0,v.weeks),days=Math.max(0,v.days);
      const annualHours=hours*weeks,weekly=weeks?salary/weeks:0,monthly=salary/12,daily=days?weekly/days:0,hourly=annualHours?salary/annualHours:0;
      const workdayHours=days?hours/days:0,weeklyShare=hours/168*100;
      return {
        monthly:money(monthly),weekly:money(weekly),daily:money(daily),hourly:money(hourly),annual_hours:num(annualHours)+' hours',
        fortnightly:money(weekly*2),workday_hours:num(workdayHours)+' hours',weekly_hours_share:pct(weeklyShare)
      };
    },
    fuel(v){
      const distance=Math.max(0,v.distance)*Math.max(0,v.trips), consumption=Math.max(0,v.consumption), price=Math.max(0,v.price);
      const litres=distance*consumption/100, cost=litres*price, per100=consumption*price;
      const annualDistance=Boolean(v.__advanced)?Math.max(0,v.annual_distance):0;
      const annualLitres=annualDistance*consumption/100, annualCost=annualLitres*price;
      return {
        litres:num(litres)+' L',cost:money(cost),per100:money(per100),cost_per_km:money(distance>0?cost/distance:0),
        annual_litres:num(annualLitres)+' L',annual_cost:money(annualCost)
      };
    },
    ev(v){
      const advanced=Boolean(v.__advanced), distance=Math.max(0,v.distance), efficiency=Math.max(0,v.efficiency);
      const chargeEff=Math.max(.01,1-Math.max(0,Math.min(50,v.loss))/100);
      const homeRate=Math.max(0,v.price), homeShare=advanced?Math.max(0,Math.min(100,v.home_share))/100:1;
      const publicRate=advanced?Math.max(0,v.public_price):homeRate, blended=homeRate*homeShare+publicRate*(1-homeShare);
      const battery=distance*efficiency/100, wall=battery/chargeEff, cost=wall*blended, per100=efficiency/chargeEff*blended;
      const annualDistance=advanced?Math.max(0,v.annual_distance):0, annualBattery=annualDistance*efficiency/100, annualWall=annualBattery/chargeEff, annualCost=annualWall*blended;
      const iceCost=advanced?annualDistance*Math.max(0,v.ice_consumption)/100*Math.max(0,v.fuel_price):0, saving=iceCost-annualCost;
      return {
        battery_kwh:num(battery)+' kWh',wall_kwh:num(wall)+' kWh',cost:money(cost),per100:money(per100),
        blended_rate:money(blended)+'/kWh',annual_wall_kwh:num(annualWall)+' kWh',annual_cost:money(annualCost),
        ice_annual_cost:money(iceCost),annual_saving_vs_ice:(saving>=0?'+':'-')+money(Math.abs(saving))
      };
    },
    electricity(v){
      const advanced=Boolean(v.__advanced), duty=advanced?Math.max(0,Math.min(100,v.duty_cycle))/100:1;
      const kwh=Math.max(0,v.watts)/1000*Math.max(0,v.hours)*Math.max(0,v.days)*duty;
      const offpeak=advanced?Math.max(0,Math.min(100,v.offpeak_share))/100:0;
      const dayRate=Math.max(0,v.price), nightRate=advanced?Math.max(0,v.offpeak_rate):dayRate, blended=dayRate*(1-offpeak)+nightRate*offpeak;
      const monthly=kwh*blended;
      return {
        kwh:num(kwh)+' kWh',monthly:money(monthly),annual:money(monthly*12),
        annual_kwh:num(kwh*12)+' kWh',blended_rate:money(blended)+'/kWh'
      };
    },
    take_home_2026(v){
      const reduced=Boolean(v.__advanced)&&v.usc_reduced==='yes', pension=Math.max(0,v.salary*v.pension_pct/100), net=employeeNet2026(v.salary,pension,v.band,v.other_credits,reduced);
      const salaryPlus=Math.max(0,v.salary)+1000, pensionPlus=Math.max(0,salaryPlus*v.pension_pct/100), netPlus=employeeNet2026(salaryPlus,pensionPlus,v.band,v.other_credits,reduced);
      const deductions=net.tax+net.usc+net.prsi+pension;
      return {
        annual_net:money(net.net),monthly_net:money(net.net/12),paye:money(net.tax),usc:money(net.usc),prsi:money(net.prsi),pension:money(pension),
        deductions:money(deductions),effective_deductions:pct(v.salary?deductions/v.salary*100:0),next_1000_net:money(netPlus.net-net.net),
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
      const requested=Boolean(v.__advanced)&&v.reduced_rate==='yes', reduced=requested&&v.income<=60000, u=usc2026(v.income,reduced);
      return {usc:money(u),effective:pct(v.income?u/v.income*100:0),monthly:money(u/12),rate_basis:reduced?'Reduced 2026 rates':'Standard 2026 rates'};
    },
    prsi_2026(v){
      const salary=Math.max(0,v.salary),p=annualClassA2026(salary),octoberEffect=Math.max(0,(p.after-p.before)*13);
      const oldAnnual=p.before*52,newAnnual=p.after*52;
      return {
        weekly_equivalent:money(p.weekly),weekly_before:money(p.before),weekly_after:money(p.after),annual:money(p.annual),
        effective:pct(salary?p.annual/salary*100:0),october_increase:money(octoberEffect),
        annual_if_old_rate:money(oldAnnual),annual_if_new_rate:money(newAnnual),monthly_equivalent:money(p.annual/12)
      };
    },
    cat(v){
      const advanced=Boolean(v.__advanced), thresholds={A:400000,B:40000,C:20000}, threshold=thresholds[v.group]||0;
      const benefit=Math.max(0,v.benefit), prior=Math.max(0,v.prior);
      const smallAlreadyUsed=advanced&&v.benefit_type==='gift'?Math.max(0,Math.min(3000,v.small_gift_used||0)):0;
      const smallAvailable=v.benefit_type==='gift'?Math.max(0,3000-smallAlreadyUsed):0;
      const smallApplied=Math.min(smallAvailable,benefit), current=Math.max(0,benefit-smallApplied);
      const beforeTax=Math.max(0,prior-threshold)*.33, aggregate=prior+current, afterTax=Math.max(0,aggregate-threshold)*.33, cat=Math.max(0,afterTax-beforeTax);
      const filingMarker=threshold>0&&aggregate>=threshold*.80?'80% filing marker reached':'Below 80% numerical filing marker';
      return {
        threshold:money(threshold),current_taxable_value:money(current),threshold_remaining:money(Math.max(0,threshold-prior)),cat:money(cat),
        small_gift_applied:money(smallApplied),aggregate_after_current:money(aggregate),threshold_remaining_after:money(Math.max(0,threshold-aggregate)),it38_marker:filingMarker
      };
    },
    rent_credit(v){
      const rent=Math.max(0,v.rent),liability=Math.max(0,v.income_tax_liability),rentBased=rent*.20,cap=v.joint==='yes'?2000:1000;
      const credit=Math.min(rentBased,cap,liability),usable=Math.max(0,credit);
      const limits=[['20% of qualifying rent',rentBased],['2026 statutory cap',cap],['available Income Tax liability',liability]].sort((a,b)=>a[1]-b[1]);
      return {
        rent_based:money(rentBased),statutory_cap:money(cap),credit:money(usable),rent_for_max:money(cap/.20),
        unused_cap:money(Math.max(0,cap-usable)),binding_limit:limits[0][0],
        effective_rent_relief:pct(rent?usable/rent*100:0)
      };
    },
    help_to_buy(v){
      const propertyValue=Math.max(0,v.property_value), taxPaid=Math.max(0,v.tax_paid), affordable=v.__advanced?Math.max(0,v.la_affordable_contribution||0):0;
      const qualifyingFinance=Math.max(0,v.mortgage)+affordable, minimumFinance=propertyValue*.70;
      const ltv=propertyValue>0?qualifyingFinance/propertyValue*100:0, valueCap=propertyValue*.10;
      const valueOk=propertyValue<=500000, financeOk=ltv>=70, basic=valueOk&&financeOk;
      const constraints=[['€30,000 scheme cap',30000],['10% property-value cap',valueCap],['four-year Income Tax + DIRT paid',taxPaid]].sort((a,b)=>a[1]-b[1]);
      const claim=basic?Math.max(0,constraints[0][1]):0;
      let eligibility='Passes basic value/finance check';
      if(!valueOk) eligibility='Property value exceeds €500,000';
      else if(!financeOk) eligibility='Qualifying finance is below 70%';
      return {
        ltv:pct(ltv),qualifying_finance:money(qualifyingFinance),minimum_finance:money(minimumFinance),value_cap:money(valueCap),claim:money(claim),eligibility,
        binding_limit:basic?constraints[0][0]:'Basic value/finance screen not passed',
        finance_shortfall:money(Math.max(0,minimumFinance-qualifyingFinance))
      };
    },
    first_home_scheme(v){
      const propertyValue=Math.max(0,v.property_value), htb=v.htb==='yes'?Math.min(Math.max(0,v.htb_amount),propertyValue):0;
      const depositFunds=Math.max(0,v.deposit)+htb, gap=Math.max(0,propertyValue-Math.max(0,v.mortgage)-depositFunds);
      const maxShare=v.htb==='yes'?.20:.30, maxFhs=propertyValue*maxShare, minFhs=Math.max(propertyValue*.025,10000);
      const share=propertyValue?gap/propertyValue*100:0, ceiling=fhsPriceCeiling(v.authority,v.property_type);
      const priceOk=propertyValue<=ceiling, depositOk=depositFunds>=propertyValue*.10;
      const fundingOk=gap>=minFhs&&gap<=maxFhs, serviceBase=(priceOk&&depositOk&&fundingOk)?gap:0;
      const rateForYear=y=>y<=5?0:y<=15?.0175:y<=29?.0215:.0285;
      const horizon=Boolean(v.__advanced)?Math.max(5,Math.min(40,Math.round(v.service_charge_horizon||10))):10;
      let cumulative=0; for(let y=1;y<=horizon;y++) cumulative+=serviceBase*rateForYear(y);
      let check='Within calculator’s basic scheme range';
      if(gap===0) check='No funding gap';
      else if(!priceOk) check='Above local property price ceiling';
      else if(!depositOk) check='Deposit / HTB is below 10%';
      else if(gap<minFhs) check='Gap is below the FHS minimum';
      else if(gap>maxFhs) check='Gap exceeds the percentage maximum';
      return {
        price_ceiling:money(ceiling),gap:money(gap),share:pct(share),max_fhs:money(maxFhs),
        year6_charge:serviceBase>0?money(serviceBase*.0175):'—',
        charges_to_year10:serviceBase>0?money(serviceBase*.0175*5):'—',
        year16_charge:serviceBase>0?money(serviceBase*.0215):'—',
        year30_charge:serviceBase>0?money(serviceBase*.0285):'—',
        charges_to_horizon:serviceBase>0?money(cumulative):'—',
        check
      };
    },
    dirt(v){
      const interest=Math.max(0,v.interest), tax=interest*.33, net=interest-tax, advanced=Boolean(v.__advanced);
      const deposit=advanced?Math.max(0,v.deposit||0):0, grossRate=advanced?Math.max(0,v.gross_rate||0)/100:0, years=advanced?Math.max(0,Math.round(v.years||0)):0;
      let balance=deposit, projectedTax=0;
      for(let y=0;y<years;y++){const grossInterest=balance*grossRate, yearTax=grossInterest*.33; projectedTax+=yearTax; balance+=grossInterest-yearTax;}
      return {
        dirt:money(tax),net:money(net),retained:pct(interest?net/interest*100:0),
        after_dirt_rate:pct(grossRate*(1-.33)*100),projected_balance:money(balance),projected_dirt:money(projectedTax),projected_net_growth:money(Math.max(0,balance-deposit))
      };
    },
    contractor_vs_salary(v){
      const employee=employeeNet2026(v.salary,0,44000,0), revenue=v.day_rate*v.billable_days, profit=Math.max(0,revenue-v.contractor_costs), pension=Math.min(v.contractor_pension,profit), contractor=selfEmployedNet2026(profit,pension), diff=contractor.net-employee.net;
      let breakEven=null;
      if(v.billable_days>0){
        let lo=0, hi=Math.max(1000,v.day_rate*3,1);
        const netAt=rate=>{const p=Math.max(0,rate*v.billable_days-v.contractor_costs), pen=Math.min(v.contractor_pension,p);return selfEmployedNet2026(p,pen).net;};
        while(netAt(hi)<employee.net && hi<1000000) hi*=2;
        if(netAt(hi)>=employee.net){
          for(let i=0;i<60;i++){const mid=(lo+hi)/2;if(netAt(mid)>=employee.net)hi=mid;else lo=mid;}
          breakEven=hi;
        }
      }
      return {
        employee_net:money(employee.net),contractor_revenue:money(revenue),contractor_profit:money(profit),contractor_net:money(contractor.net),net_difference:(diff>=0?'+':'')+money(diff),break_even_day_rate:breakEven===null?'—':money(breakEven)+'/day',
        __chart:{type:'bar',title:'Gross and estimated net comparison',caption:'The contractor side excludes the value of employment benefits and uses the stated self-employed assumptions.',labels:['Employee','Contractor'],series:[{label:'Gross / profit',values:[v.salary,profit]},{label:'Estimated take-home',values:[employee.net,contractor.net]}]}
      };
    },
    investment_fees(v){
      const advanced=Boolean(v.__advanced), gross=Math.max(-.99,v.gross_return/100);
      const simulate=(feePct,fixedAnnual,contributionChargePct)=>{
        const pctFee=Math.max(0,feePct)/100, fixed=advanced?Math.max(0,fixedAnnual):0, contributionCharge=advanced?Math.max(0,contributionChargePct)/100:0;
        const grossMonthly=Math.pow(1+gross,1/12)-1, feeMonthFactor=Math.pow(Math.max(.000001,1-pctFee),1/12);
        const months=Math.max(0,Math.round(v.years*12)), monthly=Math.max(0,v.monthly);
        let bal=Math.max(0,v.initial), fees=0;
        const labels=['Start'], balances=[bal];
        for(let m=1;m<=months;m++){
          const beforeFee=bal*(1+grossMonthly);
          const afterPct=beforeFee*feeMonthFactor;
          const pctCharge=Math.max(0,beforeFee-afterPct);
          const fixedCharge=Math.min(afterPct,fixed/12);
          const contributionFee=monthly*contributionCharge;
          bal=Math.max(0,afterPct-fixedCharge)+Math.max(0,monthly-contributionFee);
          fees+=pctCharge+fixedCharge+contributionFee;
          if(m%12===0 || m===months){labels.push(m%12===0?'Year '+(m/12):duration(m));balances.push(bal);}
        }
        return {bal,fees,labels,balances};
      };
      const low=simulate(v.fee_low,v.fixed_low,v.contribution_charge_low), high=simulate(v.fee_high,v.fixed_high,v.contribution_charge_high);
      const cleanRate=x=>Math.round(x*1e10)/1e10;
      const lowNet=cleanRate(((1+gross)*(1-Math.max(0,v.fee_low)/100)-1)*100), highNet=cleanRate(((1+gross)*(1-Math.max(0,v.fee_high)/100)-1)*100);
      const gap=low.bal-high.bal, inflation=advanced?Math.max(-.99,v.inflation_rate/100):0, realGap=gap/Math.pow(1+inflation,Math.max(0,v.years));
      return {
        low_net_return:pct(lowNet),high_net_return:pct(highNet),low_balance:money(low.bal),high_balance:money(high.bal),fee_gap:(gap>=0?'+':'-')+money(Math.abs(gap)),
        low_fees_paid:money(low.fees),high_fees_paid:money(high.fees),real_fee_gap:(realGap>=0?'+':'-')+money(Math.abs(realGap)),
        __chart:{type:'line',title:'Fee drag over time',caption:advanced?'Both options use the same before-fee return and gross contribution plan. Percentage fees, fixed charges and contribution charges are applied separately so the compounding effect is visible.':'Both options use the same before-fee return and contribution plan; only the annual percentage fee changes.',labels:low.labels,series:[{label:'Lower-fee option',values:low.balances},{label:'Higher-fee option',values:high.balances}]}
      };
    },
    fire_number(v){
      const advanced=Boolean(v.__advanced), withdrawalRate=Math.max(.000001,v.withdrawal_rate/100);
      const otherIncome=advanced?Math.max(0,v.ongoing_income):0, reserve=advanced?Math.max(0,v.extra_reserve):0;
      const portfolioSpend=Math.max(0,Math.max(0,v.annual_spend)-otherIncome);
      const baseTarget=portfolioSpend/withdrawalRate, target=baseTarget+reserve;
      const fee=advanced?Math.max(0,v.annual_fee/100):0;
      const nominalNet=(1+Math.max(-.99,v.return_rate/100))*(1-fee)-1;
      const inflation=Math.max(-.99,(advanced?v.inflation_rate:2)/100), realAnnual=(1+nominalNet)/(1+inflation)-1;
      const r=Math.pow(Math.max(.000001,1+realAnnual),1/12)-1;
      let annualContribution=Math.max(0,v.annual_contribution), monthly=annualContribution/12, bal=Math.max(0,v.current), months=0, contributed=0;
      const contributionGrowth=advanced?Math.max(-.99,v.contribution_growth/100):0;
      const labels=['Now'], vals=[bal], targets=[target], contributions=[bal];
      while(bal<target&&months<1200){
        bal=bal*(1+r)+monthly; contributed+=monthly; months++;
        if(months%12===0 && bal<target){annualContribution*=1+contributionGrowth;monthly=annualContribution/12;}
        if(months%12===0 || bal>=target){labels.push(months%12===0?'Year '+(months/12):duration(months));vals.push(bal);targets.push(target);contributions.push(Math.max(0,v.current)+contributed);}
      }
      const reached=bal>=target, sensitivity=r=>portfolioSpend/(r/100)+reserve;
      return {
        portfolio_spending:money(portfolioSpend),target:money(target),gap:money(Math.max(0,target-Math.max(0,v.current))),progress:pct(target>0?Math.min(100,Math.max(0,v.current)/target*100):100),
        real_return:pct(realAnnual*100),years:reached?duration(months):'Not reached within 100 years',
        contributions_to_target:money(contributed),growth_to_target:money(bal-Math.max(0,v.current)-contributed),
        target_3:money(sensitivity(3)),target_35:money(sensitivity(3.5)),target_4:money(sensitivity(4)),
        __chart:{type:'line',title:'Today’s-money path towards the financial-independence target',caption:advanced?'The path uses the entered return after the annual fee, adjusts it for inflation, and can grow the annual contribution in real terms. Ongoing income reduces the portfolio-funded spending only if you choose to include it.':'Spending, portfolio value and annual contributions are treated in today’s money using the default 2% inflation assumption.',labels,series:[{label:'Projected portfolio — today’s money',values:vals},{label:'Target — today’s money',values:targets},{label:'Starting capital + contributions',values:contributions}]}
      };
    },
    retirement_income(v){
      const advanced=Boolean(v.__advanced), pot=Math.max(0,v.pot), portfolio=pot*Math.max(0,v.withdrawal_rate)/100;
      const state=Math.max(0,v.state_pension), other=Math.max(0,v.other_income), total=portfolio+state+other;
      const years=Math.max(1,Math.round(advanced?v.retirement_years:30)), inflation=Math.max(-.99,(advanced?v.inflation_rate:2)/100);
      const fee=advanced?Math.max(0,v.annual_fee/100):0, baselineReturn=advanced?v.return_rate:4, stressReturn=advanced?v.stress_return_rate:2;
      const simulate=annualReturn=>{
        let bal=pot, withdrawal=portfolio, depletedYear=null, fees=0, withdrawn=0;
        const labels=['Start'], balances=[bal];
        for(let year=1;year<=years;year++){
          const afterGrowth=bal*(1+Math.max(-.99,annualReturn/100));
          const charge=Math.max(0,afterGrowth*fee);
          fees+=charge;
          bal=Math.max(0,afterGrowth-charge-withdrawal);
          withdrawn+=Math.min(withdrawal,Math.max(0,afterGrowth-charge));
          if(bal<=0.005&&depletedYear===null) depletedYear=year;
          labels.push('Year '+year);balances.push(bal);
          withdrawal*=1+inflation;
        }
        return {bal,depletedYear,fees,withdrawn,labels,balances};
      };
      const base=simulate(baselineReturn), stress=simulate(stressReturn);
      const targetIncome=advanced?Math.max(0,v.target_income):0, requiredDraw=Math.max(0,targetIncome-state-other);
      const requiredRate=pot>0?requiredDraw/pot*100:(requiredDraw>0?Infinity:0);
      const realEnding=base.bal/Math.pow(1+inflation,years);
      const depletionText=x=>x===null?'Not depleted in '+years+' years':'Depleted in year '+x;
      return {
        portfolio_income:money(portfolio),annual_income:money(total),monthly_income:money(total/12),ending_pot:money(base.bal),depletion:depletionText(base.depletedYear),
        target_gap:targetIncome>0?(total>=targetIncome?'+':'-')+money(Math.abs(total-targetIncome)):'Not set',
        required_portfolio_income:targetIncome>0?money(requiredDraw):'Not set',
        required_withdrawal_rate:targetIncome>0?(Number.isFinite(requiredRate)?pct(requiredRate):'Not calculable'):'Not set',
        real_ending_pot:money(realEnding),fees_paid:money(base.fees),stress_ending_pot:money(stress.bal),stress_depletion:depletionText(stress.depletedYear),
        __chart:{type:'line',title:'Retirement-pot sustainability scenarios',caption:advanced?'Baseline and stress paths use the same inflation-linked withdrawals and annual fee, but different constant return assumptions. This still does not model volatile year-by-year market returns.':'Basic mode shows a 30-year deterministic path using 4% annual return and 2% annual withdrawal increases.',labels:base.labels,series:[{label:'Baseline portfolio',values:base.balances},{label:'Stress-return portfolio',values:stress.balances}]}
      };
    },
    pension_projection(v){
      const advanced=Boolean(v.__advanced), years=Math.max(0,Math.floor(v.retirement_age-v.age));
      const contributionGrowth=advanced?Math.max(-.99,v.contribution_growth/100):0, annualAvc=advanced?Math.max(0,v.annual_avc):0;
      const fee=advanced?Math.max(0,v.annual_fee/100):.0075, baseReturn=advanced?v.return_rate:6, stressReturn=advanced?v.stress_return_rate:3;
      const simulate=(annualReturn,feeRate)=>{
        const netAnnual=(1+Math.max(-.99,annualReturn/100))*(1-feeRate)-1, r=Math.pow(Math.max(.000001,1+netAnnual),1/12)-1;
        let bal=Math.max(0,v.current), employeeMonthly=Math.max(0,v.monthly_employee), employerMonthly=Math.max(0,v.monthly_employer);
        let employeeTotal=0, employerTotal=0, avcTotal=0;
        const labels=['Age '+v.age], pots=[bal], contribs=[bal];
        for(let y=1;y<=years;y++){
          for(let m=0;m<12;m++){
            bal=bal*(1+r)+employeeMonthly+employerMonthly;
            employeeTotal+=employeeMonthly;employerTotal+=employerMonthly;
          }
          if(annualAvc>0){bal+=annualAvc;avcTotal+=annualAvc;}
          labels.push('Age '+(v.age+y));pots.push(bal);contribs.push(Math.max(0,v.current)+employeeTotal+employerTotal+avcTotal);
          if(y<years){employeeMonthly*=1+contributionGrowth;employerMonthly*=1+contributionGrowth;}
        }
        return {bal,employeeMonthly,employerMonthly,employeeTotal,employerTotal,avcTotal,labels,pots,contribs,netAnnual};
      };
      const base=simulate(baseReturn,fee), noFee=simulate(baseReturn,0), stress=simulate(stressReturn,fee);
      const contributed=Math.max(0,v.current)+base.employeeTotal+base.employerTotal+base.avcTotal;
      const inflation=Math.max(-.99,(advanced?v.inflation_rate:2)/100), real=base.bal/Math.pow(1+inflation,years);
      return {
        years:years+' years',projected:money(base.bal),projected_real:money(real),contributed:money(contributed),growth:money(base.bal-contributed),
        employee_contributions:money(base.employeeTotal+base.avcTotal),employer_contributions:money(base.employerTotal),
        ending_employee_monthly:money(base.employeeMonthly),ending_employer_monthly:money(base.employerMonthly),
        fee_drag:money(Math.max(0,noFee.bal-base.bal)),stress_projected:money(stress.bal),
        __chart:{type:'line',title:'Pension projection to retirement',caption:advanced?'Baseline and lower-return stress paths use the same contribution-growth, AVC and fee assumptions. Cumulative contributions are shown separately from investment outcomes.':'Basic mode uses 6% gross return, a 0.75% annual fee, level monthly contributions and 2% inflation.',labels:base.labels,series:[{label:'Baseline pension',values:base.pots},{label:'Lower-return stress',values:stress.pots},{label:'Starting pot + contributions',values:base.contribs}]}
      };
    },
    rent_vs_buy(v){
      const price=Math.max(0,v.house_price), deposit=Math.min(price,Math.max(0,v.deposit)), mortgage=Math.max(0,price-deposit);
      const n=Math.max(1,Math.round(v.mortgage_years*12)), payment=monthlyPayment(mortgage,v.mortgage_rate,n), mr=v.mortgage_rate/100/12;
      const hr=Math.pow(Math.max(.000001,1+v.house_growth/100),1/12)-1;
      const rr=Math.pow(Math.max(.000001,1+v.annual_rent_growth/100),1/12)-1;
      const ir=Math.pow(Math.max(.000001,1+v.renter_return/100),1/12)-1;
      const stamp=stampDutyResidential(price), upfrontCosts=stamp+Math.max(0,v.buying_costs), sellPct=Math.max(0,v.selling_cost_pct)/100;
      let house=price, balance=mortgage, rent=Math.max(0,v.monthly_rent), renter=deposit+upfrontCosts, ownerInvest=0, firstCrossover=null;
      const saleEquity=()=>Math.max(0,house*(1-sellPct))-balance;
      const ownerNet=()=>saleEquity()+ownerInvest;
      const labels=['Now'], ownerVals=[ownerNet()], renterVals=[renter];
      const totalMonths=Math.max(1,Math.round(v.years*12));
      for(let month=1;month<=totalMonths;month++){
        house*=1+hr; rent*=1+rr; renter*=1+ir; ownerInvest*=1+ir;
        let mortgageOutflow=0;
        if(balance>0.005){
          const interest=balance*mr, due=balance+interest;
          mortgageOutflow=Math.min(payment,due);
          balance=Math.max(0,due-mortgageOutflow);
        }
        const maintenance=house*(Math.max(0,v.maintenance_pct)/100)/12;
        const ownerCost=mortgageOutflow+maintenance+Math.max(0,v.owner_fixed_annual)/12;
        if(ownerCost>rent) renter+=ownerCost-rent;
        else ownerInvest+=rent-ownerCost;
        if(month%12===0 || month===totalMonths){
          const label=month%12===0?'Year '+(month/12):'Month '+month;
          const ownerNow=ownerNet();
          labels.push(label); ownerVals.push(ownerNow); renterVals.push(renter);
          if(firstCrossover===null && ownerNow>=renter) firstCrossover=month;
        }
      }
      const owner=ownerVals[ownerVals.length-1], renterEnd=renterVals[renterVals.length-1], diff=owner-renterEnd;
      return {
        mortgage_payment:money(payment),
        upfront_buying_costs:money(upfrontCosts),
        owner_equity:money(owner),
        renter_portfolio:money(renterEnd),
        difference:(diff>=0?'+':'')+money(diff),
        first_crossover:firstCrossover===null?'Not reached in '+number.format(v.years)+' years':duration(firstCrossover),
        ending_home_value:money(house),
        remaining_mortgage:money(balance),
        buyer_sale_equity:money(saleEquity()),
        ending_monthly_rent:money(rent),
        __chart:{type:'line',title:'Illustrative liquidated net-wealth paths',caption:'The renter starts with the buyer deposit plus Stamp Duty and other buying costs invested. Buyer value assumes the home is sold at the comparison point and the entered selling-cost percentage is deducted. The mortgage rate, growth rates and investment return are held constant.',labels,series:[{label:'Buy scenario',values:ownerVals},{label:'Rent scenario',values:renterVals}]}
      };
    },
    mortgage_affordability(v){
      const multiple=v.buyer_type==='ftb'?4:3.5, income=Math.max(0,v.income), deposit=Math.max(0,v.deposit), debt=Math.max(0,v.other_debt);
      const lti=income*multiple;
      const grossLimit=Math.max(0,income/12*Math.max(0,v.max_payment_pct)/100-debt);
      const useNet=Boolean(v.__advanced)&&Math.max(0,v.net_income_monthly)>0;
      const netLimit=useNet?Math.max(0,v.net_income_monthly-Math.max(0,v.essential_spend_monthly)-debt-Math.max(0,v.buffer_monthly)):Infinity;
      const capacity=Math.min(grossLimit,netLimit);
      const r=Math.max(0,v.rate)/100/12, n=Math.max(1,Math.round(v.term*12));
      const paymentBased=r===0?capacity*n:capacity*(1-Math.pow(1+r,-n))/r;
      const depositBased=deposit*9;
      const options=[['Income (LTI)',lti],['Payment budget',paymentBased],['Deposit (LTV)',depositBased]].sort((a,b)=>a[1]-b[1]);
      const mortgage=Math.max(0,options[0][1]), price=mortgage+deposit, stressRate=Math.max(0,v.rate)+(v.__advanced?Math.max(0,v.stress_rate_add):1);
      const stressPayment=monthlyPayment(mortgage,stressRate,n);
      return {
        lti_mortgage:money(lti),
        payment_capacity:money(capacity),
        payment_based_mortgage:money(paymentBased),
        deposit_based_mortgage:money(depositBased),
        indicative_mortgage:money(mortgage),
        indicative_price:money(price),
        binding_constraint:options[0][0],
        gross_payment_limit:money(grossLimit),
        net_budget_limit:useNet?money(netLimit):'Not used',
        stress_rate:pct(stressRate),
        stress_payment:money(stressPayment),
        __chart:{type:'bar',title:'Which mortgage constraint is binding?',caption:'Compares the standard LTI ceiling, your payment-budget mortgage and the 90% LTV deposit constraint. The payment budget can optionally use the lower of your gross-income percentage and entered net-income household budget.',labels:['LTI ceiling','Payment budget','Deposit/LTV','Indicative'],series:[{label:'Mortgage amount',values:[lti,paymentBased,depositBased,mortgage]}]}
      };
    },
    house_buying_costs(v){
      const advanced=Boolean(v.__advanced), price=Math.max(0,v.price), deposit=price*Math.max(0,v.deposit_pct)/100, stamp=stampDutyResidential(price);
      const professional=Math.max(0,v.legal)+Math.max(0,v.survey)+Math.max(0,v.valuation);
      const setup=Math.max(0,v.moving)+Math.max(0,v.other)+(advanced?Math.max(0,v.insurance_setup)+Math.max(0,v.furnishing)+Math.max(0,v.immediate_works):0);
      const other=professional+setup, total=deposit+stamp+other, mortgage=Math.max(0,price-deposit);
      const reserve=advanced?Math.max(0,v.reserve):0, target=total+reserve, cash=advanced?Math.max(0,v.cash_available):0, position=cash-target;
      const labels=advanced?['Deposit','Stamp duty','Professional','Moving/setup','Retained reserve']:['Deposit','Stamp duty','Legal','Survey','Valuation','Moving','Other'];
      const values=advanced?[deposit,stamp,professional,setup,reserve]:[deposit,stamp,v.legal,v.survey,v.valuation,v.moving,v.other];
      return {
        deposit:money(deposit),
        stamp:money(stamp),
        other_costs:money(other),
        total_upfront:money(total),
        mortgage_required:money(mortgage),
        professional_costs:money(professional),
        moving_setup_costs:money(setup),
        cash_target:money(target),
        cash_position:(position>=0?'+':'-')+money(Math.abs(position))+(position>=0?' surplus':' shortfall'),
        __chart:{type:'bar',title:advanced?'Cash target for purchase and retained reserve':'Upfront cash budget',caption:advanced?'Purchase costs plus the cash reserve you chose to keep after closing. The reserve is not a transaction cost.':'Deposit plus Stamp Duty and the editable professional/moving costs entered above.',labels,series:[{label:'Cash amount',values}]}
      };
    },
    solar_payback(v){
      const advanced=Boolean(v.__advanced), size=Math.max(0,v.kwp);
      const generation=size*Math.max(0,v.generation_per_kwp);
      const rawGrant=Math.min(1800,Math.min(size,2)*700+Math.max(0,Math.min(size-2,2))*200);
      const grant=v.grant_eligible?rawGrant:0;
      const hasEv=advanced&&Boolean(v.has_ev),hasBattery=advanced&&Boolean(v.has_battery);

      const homeDemand=Math.max(0,v.annual_home_kwh);
      const directHome=Math.min(generation*Math.max(0,Math.min(100,v.direct_solar_pct))/100,homeDemand);
      let remainingSolar=Math.max(0,generation-directHome);

      let evHomeDemand=0,directEv=0;
      if(hasEv){
        const chargeEfficiency=Math.max(.01,1-Math.max(0,Math.min(40,v.ev_loss_pct))/100);
        const vehicleEnergy=Math.max(0,v.annual_ev_km)*Math.max(0,v.ev_efficiency)/100;
        evHomeDemand=vehicleEnergy/chargeEfficiency*Math.max(0,Math.min(100,v.ev_home_charge_pct))/100;
        directEv=Math.min(remainingSolar,evHomeDemand*Math.max(0,Math.min(100,v.ev_solar_share_pct))/100);
        remainingSolar=Math.max(0,remainingSolar-directEv);
      }

      const totalDemand=homeDemand+evHomeDemand;
      const efficiency=hasBattery?Math.max(.01,Math.min(1,v.battery_efficiency/100)):1;
      const batteryCapacity=hasBattery?Math.max(0,v.battery_kwh):0;
      const annualBatteryInputCapacity=batteryCapacity*365;
      const remainingDemandBeforeBattery=Math.max(0,totalDemand-directHome-directEv);

      let solarBatteryInput=0,solarBatteryDelivered=0;
      if(hasBattery&&batteryCapacity>0){
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

      let nightInput=0,nightDelivered=0,arbitrage=0;
      if(hasBattery&&v.night_charge&&batteryCapacity>0){
        const remainingAnnualBatteryInput=Math.max(0,annualBatteryInputCapacity-solarBatteryInput);
        const requestedNightInput=Math.max(0,v.night_battery_kwh_day)*365;
        const remainingGridDemand=Math.max(0,totalDemand-directHome-directEv-solarBatteryDelivered);
        nightInput=Math.min(requestedNightInput,remainingAnnualBatteryInput,remainingGridDemand/efficiency);
        nightDelivered=nightInput*efficiency;
        arbitrage=nightDelivered*Math.max(0,v.import_rate)-nightInput*Math.max(0,v.night_rate);
      }

      const batteryCost=hasBattery?Math.max(0,v.battery_cost):0;
      const solarOnlyNet=Math.max(0,Math.max(0,v.system_cost)-grant);
      const net=Math.max(0,solarOnlyNet+batteryCost);
      const annual=solarValue+arbitrage;
      const payback=annual>0?net/annual:Infinity;

      const solarOnlyExport=Math.max(0,generation-directHome-directEv);
      const solarOnlyAnnual=directHomeValue+directEvValue+solarOnlyExport*Math.max(0,v.export_rate);
      const batteryIncremental=hasBattery?annual-solarOnlyAnnual:0;
      const batteryPayback=hasBattery&&batteryIncremental>0?batteryCost/batteryIncremental:Infinity;
      const solarDelivered=directHome+directEv+solarBatteryDelivered;
      const selfConsumption=generation>0?(generation-exported)/generation*100:0;
      const selfSufficiency=totalDemand>0?solarDelivered/totalDemand*100:0;
      const twentyYear=annual*20-net;

      const labels=['Install'],full=[-net],withoutBattery=[-solarOnlyNet];
      for(let year=1;year<=20;year++){
        labels.push('Year '+year);
        full.push(-net+annual*year);
        withoutBattery.push(-solarOnlyNet+solarOnlyAnnual*year);
      }
      const fullLabel=hasBattery?(hasEv?'Solar + EV + battery':'Solar + battery'):(hasEv?'Solar + EV':'Solar');
      const series=hasBattery
        ? [{label:fullLabel,values:full},{label:hasEv?'Solar + EV, no battery':'Solar only',values:withoutBattery}]
        : [{label:fullLabel,values:full}];

      return {
        grant:money(grant),net_cost:money(net),annual_generation:num(generation)+' kWh',total_demand:num(totalDemand)+' kWh',
        solar_used:num(solarDelivered)+' kWh',exported:num(exported)+' kWh',solar_value:money(solarValue),
        self_consumption:pct(selfConsumption),self_sufficiency:pct(selfSufficiency),
        battery_arbitrage:(arbitrage>=0?'+':'-')+money(Math.abs(arbitrage)),
        battery_incremental_value:hasBattery?(batteryIncremental>=0?'+':'-')+money(Math.abs(batteryIncremental)):'Not included',
        battery_incremental_payback:hasBattery?(Number.isFinite(batteryPayback)?number.format(batteryPayback)+' years':'Not reached'):'Not included',
        annual_value:money(annual),payback:Number.isFinite(payback)?number.format(payback)+' years':'Not reached',
        twenty_year_net:(twentyYear>=0?'+':'-')+money(Math.abs(twentyYear)),
        __chart:{type:'line',title:'Cumulative value under your assumptions',caption:hasBattery?'The battery scenario is compared with the same solar/EV setup without a battery. Constant annual values are assumed; degradation and tariff changes are not modelled.':'Constant annual savings and export value are assumed; degradation and tariff changes are not modelled.',labels,series}
      };
    },
    ber_energy(v){
      const area=Math.max(0,v.area),currentRate=Math.max(0,v.current_kwh_m2),targetRate=Math.max(0,v.target_kwh_m2),price=Math.max(0,v.energy_price);
      const current=area*currentRate,target=area*targetRate,currentCost=current*price,targetCost=target*price,saving=currentCost-targetCost;
      const energyReduction=current>0?(current-target)/current*100:0,costReduction=currentCost>0?saving/currentCost*100:0;
      return {
        current_use:num(current)+' kWh',target_use:num(target)+' kWh',current_cost:money(currentCost),target_cost:money(targetCost),saving:(saving>=0?'+':'-')+money(Math.abs(saving)),
        monthly_saving:(saving>=0?'+':'-')+money(Math.abs(saving/12)),energy_reduction:pct(energyReduction),cost_reduction:pct(costReduction),
        ten_year_saving:(saving>=0?'+':'-')+money(Math.abs(saving*10)),
        __chart:{type:'bar',title:'Current versus target energy-cost illustration',caption:'Uses the same blended energy-price assumption for both scenarios.',labels:['Current','Target'],series:[{label:'Annual energy cost',values:[currentCost,targetCost]}]}
      };
    },
    solar_optimizer(v){
      const advanced=Boolean(v.__advanced),size=Math.max(0,v.kwp);
      const generation=size*Math.max(0,v.generation_per_kwp);
      const grant=v.grant_eligible?Math.min(1800,Math.min(size,2)*700+Math.max(0,Math.min(size-2,2))*200):0;
      const solarNet=Math.max(0,Math.max(0,v.solar_cost)-grant);
      const directHomePct=advanced?Math.max(0,Math.min(100,v.direct_home_pct)):35;
      const directHome=Math.min(generation*directHomePct/100,Math.max(0,v.home_kwh));
      const surplus0=Math.max(0,generation-directHome);
      const hasEv=Boolean(v.has_ev);
      const evEfficiency=advanced?Math.max(0,v.ev_efficiency):18;
      const evLossPct=advanced?Math.max(0,Math.min(40,v.ev_loss_pct)):10;
      const evHomePct=advanced?Math.max(0,Math.min(100,v.ev_home_pct)):80;
      const evSolarPct=advanced?Math.max(0,Math.min(100,v.ev_solar_pct)):35;
      const smartEvCost=advanced&&hasEv?Math.max(0,v.smart_ev_cost||0):0;

      let evDemand=0,directEv=0;
      if(hasEv){
        const chargeEff=Math.max(.01,1-evLossPct/100);
        evDemand=Math.max(0,v.ev_km)*evEfficiency/100/chargeEff*evHomePct/100;
        directEv=Math.min(surplus0,evDemand*evSolarPct/100);
      }
      const dayRate=Math.max(0,v.day_rate),exportRate=Math.max(0,v.export_rate),evGridRate=Math.max(0,v.ev_grid_rate);
      const solarOnlyAnnual=directHome*dayRate+surplus0*exportRate;
      const evSurplus=Math.max(0,surplus0-directEv);
      const evAnnual=directHome*dayRate+directEv*evGridRate+evSurplus*exportRate;

      const batteryEff=advanced?Math.max(.01,Math.min(1,v.battery_efficiency/100)):.90;
      const solarCapturePct=advanced?Math.max(0,Math.min(100,v.solar_capture_pct)):60;
      const annualInputCap=Math.max(0,v.battery_kwh)*365;
      const homeRemaining=Math.max(0,v.home_kwh-directHome);
      const batteryInput=Math.min(surplus0*solarCapturePct/100,annualInputCap,homeRemaining/batteryEff);
      const batteryDelivered=batteryInput*batteryEff;
      const batteryExport=Math.max(0,surplus0-batteryInput);
      const remainingCap=Math.max(0,annualInputCap-batteryInput);
      const remainingHome=Math.max(0,homeRemaining-batteryDelivered);
      const nightKwhDay=advanced?Math.max(0,v.night_kwh_day):3;
      const nightInput=v.use_night_charge?Math.min(nightKwhDay*365,remainingCap,remainingHome/batteryEff):0;
      const nightDelivered=nightInput*batteryEff;
      const nightValue=nightDelivered*dayRate-nightInput*Math.max(0,v.night_rate);
      const batteryAnnual=directHome*dayRate+batteryDelivered*dayRate+batteryExport*exportRate+nightValue;

      const combinedHomeRemaining=Math.max(0,v.home_kwh-directHome);
      const combinedSurplus=Math.max(0,surplus0-directEv);
      const combinedBatteryInput=Math.min(combinedSurplus*solarCapturePct/100,annualInputCap,combinedHomeRemaining/batteryEff);
      const combinedDelivered=combinedBatteryInput*batteryEff;
      const combinedExport=Math.max(0,combinedSurplus-combinedBatteryInput);
      const combinedCap=Math.max(0,annualInputCap-combinedBatteryInput);
      const combinedHomeGrid=Math.max(0,combinedHomeRemaining-combinedDelivered);
      const combinedNightInput=v.use_night_charge?Math.min(nightKwhDay*365,combinedCap,combinedHomeGrid/batteryEff):0;
      const combinedNightDelivered=combinedNightInput*batteryEff;
      const combinedNightValue=combinedNightDelivered*dayRate-combinedNightInput*Math.max(0,v.night_rate);
      const combinedAnnual=directHome*dayRate+directEv*evGridRate+combinedDelivered*dayRate+combinedExport*exportRate+combinedNightValue;

      const batteryCost=Math.max(0,v.battery_cost),batteryNet=solarNet+batteryCost,evNet=solarNet+smartEvCost,combinedNet=batteryNet+smartEvCost;
      const payback=(cost,annual)=>annual>0?cost/annual:Infinity;
      const solarBenefit=solarOnlyAnnual*20-solarNet;
      const evBenefit=hasEv?evAnnual*20-evNet:null;
      const batteryBenefit=batteryAnnual*20-batteryNet;
      const combinedBenefit=hasEv?combinedAnnual*20-combinedNet:null;
      const benefits=[
        {name:'Solar only',value:solarBenefit},
        ...(hasEv?[{name:'Solar + smart EV',value:evBenefit}]:[]),
        {name:'Solar + battery',value:batteryBenefit},
        ...(hasEv?[{name:'Solar + EV + battery',value:combinedBenefit}]:[])
      ];
      const best=benefits.reduce((a,b)=>b.value>a.value?b:a,benefits[0]);
      const bestMargin=Math.max(0,best.value-solarBenefit);
      const fmtPayback=(cost,annual,enabled=true)=>enabled?(Number.isFinite(payback(cost,annual))?number.format(payback(cost,annual))+' years':'Not reached'):'EV not included';
      const fmtBenefit=(value,enabled=true)=>enabled?((value>=0?'+':'-')+money(Math.abs(value))):'EV not included';

      return {
        generation:num(generation)+' kWh',ev_demand:num(evDemand)+' kWh',best_scenario:best.name,
        solar_payback:fmtPayback(solarNet,solarOnlyAnnual),
        ev_payback:fmtPayback(evNet,evAnnual,hasEv),
        battery_payback:fmtPayback(batteryNet,batteryAnnual),
        combined_payback:fmtPayback(combinedNet,combinedAnnual,hasEv),
        solar_benefit:fmtBenefit(solarBenefit),ev_benefit:fmtBenefit(evBenefit,hasEv),
        battery_benefit:fmtBenefit(batteryBenefit),combined_benefit:fmtBenefit(combinedBenefit,hasEv),
        best_margin:'+'+money(bestMargin),
        solar_annual:money(solarOnlyAnnual),ev_annual:hasEv?money(evAnnual):'EV not included',
        battery_annual:money(batteryAnnual),combined_annual:hasEv?money(combinedAnnual):'EV not included',
        __chart:{type:'bar',title:'20-year net benefit by configuration',caption:'Annual values are held constant and the relevant upfront solar, smart-EV and battery costs are deducted. EV scenarios are omitted if no home-charged EV is selected.',labels:benefits.map(x=>x.name),series:[{label:'20-year net benefit',values:benefits.map(x=>x.value)}]}
      };
    },
    retrofit_planner(v){
      const advanced=Boolean(v.__advanced);
      const costs={
        attic:v.attic?v.attic_cost:0,wall:v.external_wall?v.wall_cost:0,windows:v.windows?v.windows_cost:0,
        heat:v.heat_pump?v.heat_pump_cost:0,solar:v.solar?v.solar_cost:0,doors:v.doors?v.doors_cost:0,
        ventilation:v.ventilation?v.ventilation_cost:0,airtight:v.airtightness?v.airtightness_cost:0,other:v.other_cost
      };
      const gross=Object.values(costs).reduce((a,b)=>a+Math.max(0,b),0);
      let baseGrants=0, conditionalHeatGrants=0, serviceGrants=0;
      if(v.oss_eligible){
        const type=v.home_type;
        const atticStandard={detached:2000,semi:1500,mid:1400,apartment:1100};
        const atticFtb={detached:2500,semi:1900,mid:1800,apartment:1400};
        const wallGrant={detached:8000,semi:6000,mid:3500,apartment:3000};
        const windowGrant={detached:4000,semi:3000,mid:1800,apartment:1500};
        const pmGrant={detached:2000,semi:1600,mid:1200,apartment:800};
        if(v.attic) baseGrants+=Math.min(Math.max(0,v.attic_cost),(v.first_time_buyer?atticFtb:atticStandard)[type]||0);
        if(v.external_wall) baseGrants+=Math.min(Math.max(0,v.wall_cost),wallGrant[type]||0);
        if(v.windows) baseGrants+=Math.min(Math.max(0,v.windows_cost),windowGrant[type]||0);
        if(v.heat_pump){
          const heatCost=Math.max(0,v.heat_pump_cost), baseHeat=Math.min(heatCost,type==='apartment'?4500:6500);
          baseGrants+=baseHeat;
          const central=advanced&&v.central_heating_upgrade?(type==='apartment'?1000:2000):0;
          const bonus=advanced&&v.renewable_heat_bonus?4000:0;
          conditionalHeatGrants=Math.min(Math.max(0,heatCost-baseHeat),central+bonus);
        }
        if(v.solar) baseGrants+=Math.min(Math.max(0,v.solar_cost),Math.min(1800,Math.min(Math.max(0,v.solar_kwp),2)*700+Math.max(0,Math.min(v.solar_kwp-2,2))*200));
        if(v.doors) baseGrants+=Math.min(Math.max(0,v.doors_cost),Math.min(2,Math.max(0,v.door_count))*800);
        if(v.ventilation) baseGrants+=Math.min(Math.max(0,v.ventilation_cost),1500);
        if(v.airtightness) baseGrants+=Math.min(Math.max(0,v.airtightness_cost),1000);
        if(advanced&&v.include_oss_services){
          const available=350+(pmGrant[type]||0);
          serviceGrants=Math.min(Math.max(0,v.other_cost),available);
        }
      }
      const grants=Math.min(gross,baseGrants+conditionalHeatGrants+serviceGrants);
      const net=Math.max(0,gross-grants), annual=Math.max(0,v.annual_energy_bill)*Math.max(0,Math.min(100,v.saving_pct))/100, payback=annual>0?net/annual:Infinity;
      const labels=['Start'],vals=[-net];for(let y=1;y<=20;y++){labels.push('Year '+y);vals.push(-net+annual*y);}
      return {
        gross_cost:money(gross),grants:money(grants),net_cost:money(net),annual_saving:money(annual),payback:Number.isFinite(payback)?number.format(payback)+' years':'Not reached',
        base_grants:money(baseGrants),conditional_heat_grants:money(conditionalHeatGrants),oss_service_grants:money(serviceGrants),
        __chart:{type:'line',title:'Simple retrofit cash payback',caption:'Uses the energy-saving percentage entered and holds annual savings constant. Grant amounts are capped by the entered cost of the relevant measures.',labels,series:[{label:'Cumulative cash position',values:vals}]}
      };
    },
    myfuturefund(v){
      const advanced=Boolean(v.__advanced), employee=v.employment_status==='employee', age=Math.max(0,v.age), salary=Math.max(0,v.salary);
      const autoEligible=employee&&!v.workplace_pension&&age>=23&&age<60&&salary>=20000;
      const optInEligible=employee&&!v.workplace_pension&&age>=18&&age<66&&!autoEligible;
      const participating=autoEligible||(advanced&&optInEligible&&Boolean(v.assume_opt_in));
      let status;
      if(!employee) status='Self-employed only — not currently eligible';
      else if(v.workplace_pension) status='Employment normally exempt';
      else if(autoEligible) status='Likely auto-enrolled';
      else if(optInEligible&&advanced&&v.assume_opt_in) status='Opt-in scenario selected';
      else if(optInEligible) status='Eligible to opt in';
      else status='Outside current participation age';
      const rateForYear=year=>year<=2028?.015:year<=2031?.03:year<=2034?.045:.06;
      const stateRateForYear=year=>rateForYear(year)/3;
      const baseEarnings=Math.min(salary,80000), er2026=participating?baseEarnings*rateForYear(2026):0, sr2026=participating?baseEarnings*stateRateForYear(2026):0;
      let fund=advanced?Math.max(0,v.current_fund):0, projectedSalary=salary, employeeTotal=0, employerTotal=0, stateTotal=0;
      const startingFund=fund, labels=['Age '+age], funds=[fund], contributionCum=[fund];
      const years=Math.max(0,Math.floor(v.retirement_age-age)), salaryGrowth=advanced?v.salary_growth/100:0, investmentReturn=advanced?v.return_rate/100:.05;
      for(let i=0;i<years;i++){
        const year=2026+i, currentAge=age+i;
        fund*=1+investmentReturn;
        if(participating&&currentAge<66){
          const earnings=Math.min(Math.max(0,projectedSalary),80000), emp=earnings*rateForYear(year), employer=emp, state=earnings*stateRateForYear(year);
          fund+=emp+employer+state; employeeTotal+=emp; employerTotal+=employer; stateTotal+=state;
        }
        projectedSalary*=1+salaryGrowth;
        labels.push('Age '+(age+i+1));funds.push(fund);contributionCum.push(startingFund+employeeTotal+employerTotal+stateTotal);
      }
      const inflation=advanced?Math.max(-.99,v.inflation_rate/100):.02, projectedReal=fund/Math.pow(1+inflation,years);
      const investmentGrowth=fund-startingFund-employeeTotal-employerTotal-stateTotal;
      return {
        status,employee_2026:money(er2026),employer_2026:money(er2026),state_2026:money(sr2026),total_2026:money(er2026*2+sr2026),external_2026:money(er2026+sr2026),
        projected:money(fund),employee_total:money(employeeTotal),employer_total:money(employerTotal),state_total:money(stateTotal),projected_real:money(projectedReal),investment_growth:money(investmentGrowth),
        __chart:{type:'line',title:'Projected MyFutureFund balance',caption:'The projection applies the statutory calendar-year contribution phases to the annual pay assumption, subject to the €80,000 annual modelling cap. Actual eligibility and payroll collection use NAERSA rules including pay-period assessment.',labels,series:[{label:'Projected fund',values:funds},{label:'Starting fund + all contributions',values:contributionCum}]}
      };
    },
    childcare_return(v){
      const advanced=Boolean(v.__advanced);
      const salary=Math.max(0,v.salary);
      const pension=advanced?salary*Math.max(0,v.pension_pct||0)/100:0;
      const band=advanced?Math.max(0,v.standard_rate_band||44000):44000;
      const extraCredits=advanced?Math.max(0,v.extra_tax_credits||0):0;
      const reduced=advanced&&v.reduced_usc==='yes'&&salary<=60000;
      const net=employeeNet2026(salary,pension,band,extraCredits,reduced);
      const weeks=advanced?Math.max(1,v.childcare_weeks||48):48;
      const gross=Math.max(0,v.children)*Math.max(0,v.childcare_hours)*Math.max(0,v.childcare_fee)*weeks;
      const subsidisedHours=Math.min(45,Math.max(0,v.childcare_hours));
      const ncs=Math.max(0,v.children)*subsidisedHours*Math.min(Math.max(0,v.childcare_fee),Math.max(0,v.ncs_rate))*weeks;
      const childcare=Math.max(0,gross-ncs);
      const workCosts=advanced?((Math.max(0,v.commute_weekly||0)+Math.max(0,v.work_cost_weekly||0))*weeks+Math.max(0,v.other_annual||0)):0;
      const gain=net.net-childcare-workCosts;
      const workHours=(advanced?Math.max(0,v.work_hours||0):37.5)*weeks;
      const hourly=workHours>0?gain/workHours:0;
      const retained=salary>0?gain/salary*100:0;
      const fixedCosts=childcare+workCosts;
      const netAtGross=grossSalary=>{
        const p=advanced?grossSalary*Math.max(0,v.pension_pct||0)/100:0;
        return employeeNet2026(grossSalary,p,band,extraCredits,advanced&&v.reduced_usc==='yes'&&grossSalary<=60000).net;
      };
      let lo=0,hi=Math.max(100000,salary*2,fixedCosts*3);
      while(netAtGross(hi)<fixedCosts&&hi<1000000) hi*=2;
      for(let i=0;i<60;i++){const mid=(lo+hi)/2;if(netAtGross(mid)>=fixedCosts)hi=mid;else lo=mid;}
      return {
        take_home:money(net.net),childcare_gross:money(gross),ncs_support:money(ncs),childcare_net:money(childcare),work_costs:money(workCosts),
        household_gain:(gain>=0?'+':'-')+money(Math.abs(gain)),monthly_gain:(gain>=0?'+':'-')+money(Math.abs(gain/12)),
        effective_hourly:(hourly>=0?'+':'-')+money(Math.abs(hourly))+'/hour',retained_pct:pct(retained),breakeven_salary:money(hi),
        __chart:{type:'bar',title:'What remains after returning-to-work costs',caption:'Estimated annual take-home pay compared with net childcare, employment-related costs and the resulting household cash gain.',labels:['Take-home','Net childcare','Work costs','Financial gain'],series:[{label:'Annual amount',values:[net.net,childcare,workCosts,gain]}]}
      };
    },
    mortgage_switch(v){
      const n1=Math.round(v.current_years*12),n2=Math.round(v.new_years*12),p1=monthlyPayment(v.balance,v.current_rate,n1),p2=monthlyPayment(v.balance,v.new_rate,n2);
      const total1=p1*n1,total2=p2*n2,netCost=v.switching_costs+v.break_fee-v.cashback,monthlySaving=p1-p2;
      const breakEven=monthlySaving>0?(netCost<=0?'Immediate':duration(netCost/monthlySaving)):'No monthly saving';
      const diff=total1-(total2+netCost);
      const horizonYears=v.__advanced?Math.max(1,Math.round(v.comparison_years||5)):5, horizonMonths=horizonYears*12;
      const currentHorizon=mortgageSnapshot(v.balance,v.current_rate,n1,p1,horizonMonths);
      const newHorizon=mortgageSnapshot(v.balance,v.new_rate,n2,p2,horizonMonths);
      const horizonNewCost=newHorizon.interest+netCost, horizonSaving=currentHorizon.interest-horizonNewCost;
      const horizonBalanceAdvantage=currentHorizon.balance-newHorizon.balance;
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
        current_payment:money(p1),new_payment:money(p2),monthly_change:(monthlySaving>=0?'-':'+')+money(Math.abs(monthlySaving)),
        net_switch_cost:(netCost>=0?'':'-')+money(Math.abs(netCost)),break_even:breakEven,
        horizon_interest_current:money(currentHorizon.interest),horizon_interest_new:money(horizonNewCost),
        horizon_saving:(horizonSaving>=0?'+':'-')+money(Math.abs(horizonSaving)),
        horizon_balance_difference:(horizonBalanceAdvantage>=0?'+':'-')+money(Math.abs(horizonBalanceAdvantage)),
        lifetime_difference:(diff>=0?'+':'-')+money(Math.abs(diff)),
        __chart:{type:'line',title:'Scheduled mortgage balance',caption:'Current mortgage versus the alternative rate/term entered. The full chart assumes the entered rates continue unchanged.',labels,series:[{label:'Current mortgage',values:a},{label:'Alternative mortgage',values:b}]}
      };
    },
    lifetime_cost(v){
      const advanced=Boolean(v.__advanced),years=Math.max(0,Math.floor(v.end_age-v.current_age)),inflation=v.inflation/100;
      const otherMonthly=advanced?Math.max(0,v.other_monthly||0):0;
      const monthlyBase=Math.max(0,v.food_monthly)+Math.max(0,v.utilities_monthly)+Math.max(0,v.transport_monthly)+Math.max(0,v.leisure_monthly)+otherMonthly;
      const baseAnnual=monthlyBase*12+Math.max(0,v.travel_annual)+Math.max(0,v.insurance_health_annual);
      const housingUntil=advanced?Math.max(v.current_age,Math.min(v.end_age,v.housing_until)):v.end_age;
      const childcareYears=advanced?Math.max(0,v.childcare_years||0):0;
      const childcareAnnual=advanced?Math.max(0,v.childcare_annual||0):0;
      const majorInterval=advanced?Math.max(1,Math.round(v.major_interval||1)):0;
      const majorPurchase=advanced?Math.max(0,v.major_purchase||0):0;
      const todayAnnual=baseAnnual+(v.current_age<housingUntil?Math.max(0,v.housing_monthly)*12:0)+(childcareYears>0?childcareAnnual:0)+(majorInterval>0?majorPurchase/majorInterval:0);
      let nominal=0,todayMoney=0,housingTotal=0,majorTotal=0,cumulative=0,lastAnnual=0;
      const labels=['Age '+v.current_age],vals=[0];
      for(let y=0;y<years;y++){
        const factor=Math.pow(1+inflation,y),age=v.current_age+y;
        let annual=baseAnnual*factor,annualToday=baseAnnual;
        if(age<housingUntil){annual+=Math.max(0,v.housing_monthly)*12*factor;annualToday+=Math.max(0,v.housing_monthly)*12;housingTotal+=Math.max(0,v.housing_monthly)*12*factor;}
        if(y<childcareYears){annual+=childcareAnnual*factor;annualToday+=childcareAnnual;}
        if(majorInterval>0&&(y+1)%majorInterval===0){const mp=majorPurchase*factor;annual+=mp;annualToday+=majorPurchase;majorTotal+=mp;}
        nominal+=annual;todayMoney+=annualToday;cumulative+=annual;lastAnnual=annual;
        labels.push('Age '+(age+1));vals.push(cumulative);
      }
      return {
        years:years+' years',today_annual:money(todayAnnual),lifetime_nominal:money(nominal),lifetime_today_money:money(todayMoney),
        inflation_uplift:money(Math.max(0,nominal-todayMoney)),average_annual:money(years?nominal/years:0),end_year_spend:money(lastAnnual),
        housing_total:money(housingTotal),major_total:money(majorTotal),
        __chart:{type:'line',title:'Cumulative projected lifetime spending',caption:'Future cash spending rises with the inflation assumption and follows the time limits entered for housing, childcare and recurring major purchases.',labels,series:[{label:'Cumulative spending',values:vals}]}
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
      const advanced=Boolean(v.__advanced),sexConst=v.sex==='female'?-161:5;
      const resting=10*Math.max(0,v.weight)+6.25*Math.max(0,v.height)-5*Math.max(0,v.age)+sexConst;
      const pal=Number(v.activity)||1.4,maintenance=resting*pal;
      const scenario=advanced?v.energy_scenario:'maintain';
      const factor=scenario==='lower10'?.90:scenario==='higher10'?1.10:1;
      const target=maintenance*factor;
      const resistance=advanced&&v.protein_context==='resistance';
      const proteinRate=resistance?1.6:.83,proteinG=Math.max(0,v.weight)*proteinRate;
      const fatG=Math.max(0,target*.30/9),carbG=Math.max(0,(target-proteinG*4-fatG*9)/4);
      const delta=target-maintenance;
      return {
        resting:num(Math.round(resting))+' kcal/day',maintenance:num(Math.round(maintenance))+' kcal/day',
        target:num(Math.round(target))+' kcal/day',energy_delta:(delta>=0?'+':'-')+num(Math.abs(Math.round(delta)))+' kcal/day',
        protein:num(proteinG)+' g/day',protein_per_kg:num(proteinRate)+' g/kg/day',fat:num(fatG)+' g/day',carbs:num(carbG)+' g/day',fibre:'At least 25 g/day',
        __chart:advanced?{type:'bar',currency:false,title:'Illustrative macro amounts',caption:'Protein uses the selected evidence/reference context; fat is set at 30% of energy and carbohydrate is the mathematical remainder.',labels:['Protein','Fat','Carbohydrate'],series:[{label:'g/day',values:[proteinG,fatG,carbG]}]}:{type:'bar',currency:false,title:'Resting and estimated maintenance energy',caption:'Resting energy is predicted from Mifflin–St Jeor and maintenance multiplies that estimate by the selected physical activity level.',labels:['Resting','Maintenance'],series:[{label:'kcal/day',values:[resting,maintenance]}]}
      };
    },
    pregnancy_timeline(v){
      const lmp=parseDateOnly(v.lmp),assigned=parseDateOnly(v.assigned_due_date);
      if(!lmp&&!assigned) return {due_date:'Enter a date above',gestational_age:'—',pregnancy_progress:'—',days_to_due:'—',trimester:'—',conception_estimate:'—',week12:'—',anatomy_window:'—',week37:'—',week42:'—'};
      const cycleAdjust=(!assigned&&v.__advanced)?Math.round((Number(v.cycle_length)||28)-28):0;
      const due=assigned||addDaysUTC(lmp,280+cycleAdjust);
      const baseLmp=(assigned||cycleAdjust)?addDaysUTC(due,-280):lmp;
      const todayLocal=new Date();
      const today=new Date(Date.UTC(todayLocal.getFullYear(),todayLocal.getMonth(),todayLocal.getDate()));
      const gestDays=Math.floor((today-baseLmp)/86400000);
      let gestational='Not yet at LMP date',trimester='Not yet in pregnancy timeline';
      if(gestDays>=0){
        const weeks=Math.floor(gestDays/7),days=gestDays%7;
        gestational=weeks+' week'+(weeks===1?'':'s')+' '+days+' day'+(days===1?'':'s');
        trimester=gestDays<98?'First trimester':gestDays<196?'Second trimester':'Third trimester';
      }
      const daysToDue=Math.round((due-today)/86400000);
      const progress=Math.max(0,Math.min(100,gestDays/280*100));
      const conception=addDaysUTC(due,-266);
      const source=assigned?'assigned date used':cycleAdjust?'LMP estimate adjusted '+(cycleAdjust>0?'+':'')+cycleAdjust+' day'+(Math.abs(cycleAdjust)===1?'':'s')+' for cycle length':'LMP estimate';
      const completedWeeks=Math.max(0,Math.min(40,gestDays/7)),remainingWeeks=Math.max(0,40-completedWeeks);
      return {
        due_date:formatDateIE(due)+' ('+source+')',gestational_age:gestational,pregnancy_progress:pct(progress),
        days_to_due:daysToDue>0?daysToDue+' day'+(daysToDue===1?'':'s'):daysToDue===0?'Estimated due date is today':Math.abs(daysToDue)+' day'+(Math.abs(daysToDue)===1?'':'s')+' past estimated due date',
        trimester,conception_estimate:formatDateIE(conception),week12:formatDateIE(addDaysUTC(baseLmp,84)),
        anatomy_window:formatDateIE(addDaysUTC(baseLmp,126))+' – '+formatDateIE(addDaysUTC(baseLmp,154)),
        week37:formatDateIE(addDaysUTC(baseLmp,259)),week42:formatDateIE(addDaysUTC(baseLmp,294)),
        __chart:{type:'bar',currency:false,title:'Progress to the 40-week estimate',caption:'This is calendar progress only, not a clinical assessment of pregnancy or fetal development.',labels:['Completed','Remaining to 40 weeks'],series:[{label:'Weeks',values:[completedWeeks,remainingWeeks]}]}
      };
    },
    alcohol_ireland(v){
      const advanced=Boolean(v.__advanced);
      const grams=(ml,abv,count)=>Math.max(0,ml)*Math.max(0,abv)/100*.789*Math.max(0,count);
      const beerAbv=advanced?Math.max(0,v.beer_abv):4.5;
      const wineMl=advanced?Math.max(0,v.wine_ml):175,wineAbv=advanced?Math.max(0,v.wine_abv):12.5;
      const spiritMl=advanced?Math.max(0,v.spirit_ml):35.5,spiritAbv=advanced?Math.max(0,v.spirit_abv):40;
      const canMl=advanced?Math.max(0,v.can_ml):500,canAbv=advanced?Math.max(0,v.can_abv):4.3;
      const total=grams(568,beerAbv,v.beer_pints)+grams(wineMl,wineAbv,v.wine_glasses)+grams(spiritMl,spiritAbv,v.spirits)+grams(canMl,canAbv,v.cans);
      const drinks=total/10,weeklyKcal=total*7,annualKcal=weeklyKcal*52;
      const weeklySpend=advanced?Math.max(0,v.weekly_spend||0):0,annualSpend=weeklySpend*52;
      const reduction=advanced?Math.max(0,Math.min(100,v.reduction_pct||0))/100:0;
      let guideline='Not compared',limit=null;
      if(v.guideline_group==='woman'){limit=11;guideline=drinks<=limit?'Within current HSE weekly low-risk limit':'Above current HSE weekly low-risk limit';}
      if(v.guideline_group==='man'){limit=17;guideline=drinks<=limit?'Within current HSE weekly low-risk limit':'Above current HSE weekly low-risk limit';}
      const difference=limit===null?'Choose a guideline group':drinks===limit?'At selected weekly limit':drinks<limit?num(limit-drinks)+' below selected weekly limit':num(drinks-limit)+' above selected weekly limit';
      return {
        standard_drinks:num(drinks),grams:num(total)+' g/week',guideline,guideline_difference:difference,weekly_kcal:num(Math.round(weeklyKcal))+' kcal/week',
        annual_kcal:num(Math.round(annualKcal))+' kcal/year',annual_spend:money(annualSpend),reduced_drinks:num(drinks*(1-reduction)),annual_saving:money(annualSpend*reduction),
        __chart:{type:'bar',currency:false,title:advanced?'Current intake and modelled reduction':'Estimated weekly alcohol intake',caption:advanced?'Irish standard drinks are based on 10 g of pure alcohol. The reduced scenario applies the percentage you entered to the same weekly pattern.':'Basic mode uses typical drink sizes and strengths; switch to Advanced to enter the exact ABV and serving sizes.',labels:advanced?['Current','After reduction']:['Current'],series:[{label:'Standard drinks/week',values:advanced?[drinks,drinks*(1-reduction)]:[drinks]}]}
      };
    },
    redundancy_ireland(v){
      const years=Math.max(0,Math.floor(v.years||0)), weekly=Math.min(600,Math.max(0,v.weekly_pay||0));
      const eligible=years>=2, statutory=eligible?weekly*(2*years+1):0;
      const advanced=Boolean(v.__advanced), ex=Math.max(0,v.ex_gratia||0), pension=Math.max(0,v.pension_lump_sum||0);
      const basic=10160+765*years;
      const increasedAdd=advanced&&v.increased_eligible?Math.max(0,10000-pension):0;
      const increased=basic+increasedAdd;
      const avg=Math.max(0,v.avg_annual_pay||0), scsb=Math.max(0,(avg/15)*years-pension);
      const best=Math.max(basic,increased,scsb);
      const remainingLifetime=Math.max(0,200000-Math.max(0,v.prior_exempt||0));
      const taxFree=Math.min(ex,best,remainingLifetime), taxable=Math.max(0,ex-taxFree);
      return {
        statutory:money(statutory),
        capped_weekly:money(weekly),
        statutory_status:eligible?'Meets 2-year service test':'Under 2 years — no statutory amount modelled',
        basic_exemption:money(basic),
        increased_exemption:money(increased),
        scsb:money(scsb),
        best_exemption:money(best),
        tax_free_ex_gratia:money(taxFree),
        taxable_ex_gratia:money(taxable),
        total_package:money(statutory+ex),
        __chart:{type:'bar',title:advanced?'Redundancy package breakdown':'Statutory redundancy estimate',caption:advanced?'Statutory redundancy is shown separately from the modelled tax-free and taxable portions of the ex-gratia payment.':'Uses the €600 statutory weekly-pay ceiling and complete years of service.',labels:advanced?['Statutory','Tax-free ex-gratia','Taxable ex-gratia']:['Statutory redundancy'],series:[{label:'Amount',values:advanced?[statutory,taxFree,taxable]:[statutory]}]}
      };
    },
    self_employed_tax_ireland(v){
      const gross=Math.max(0,v.gross_income||0), expenses=Math.min(gross,Math.max(0,v.expenses||0)), profit=Math.max(0,gross-expenses);
      const advanced=Boolean(v.__advanced), age=Math.max(18,Math.min(100,v.age||35));
      const maxPension=advanced?Math.min(profit,115000)*pensionPct(age):0;
      const pension=advanced?Math.min(Math.max(0,v.pension||0),maxPension):0;
      const base=selfEmployedNet2026(profit,0), withPension=selfEmployedNet2026(profit,pension);
      const total=withPension.tax+withPension.usc+withPension.prsi, effective=profit>0?total/profit*100:0;
      const pensionSaving=Math.max(0,base.tax-withPension.tax);
      return {
        profit:money(profit),
        income_tax:money(withPension.tax),
        usc:money(withPension.usc),
        prsi:money(withPension.prsi),
        total_tax:money(total),
        net_income:money(profit-total),
        effective_rate:pct(effective),
        monthly_reserve:money(total/12),
        pension_relief_used:money(pension),
        pension_tax_saving:money(pensionSaving),
        net_after_pension:money(profit-total-pension),
        __chart:{type:'bar',title:'Where the annual profit goes',caption:'Estimated 2026 personal taxes on the business profit entered. Pension contributions are shown separately in Advanced mode.',labels:advanced?['Income Tax','USC','PRSI','Pension','Cash after tax & pension']:['Income Tax','USC','PRSI','Cash after tax'],series:[{label:'Annual amount',values:advanced?[withPension.tax,withPension.usc,withPension.prsi,pension,Math.max(0,profit-total-pension)]:[withPension.tax,withPension.usc,withPension.prsi,Math.max(0,profit-total)]}]}
      };
    },
    pension_lump_sum_ireland(v){
      const advanced=Boolean(v.__advanced), fund=Math.max(0,v.fund||0), previous=Math.max(0,v.previous_lump_sums||0);
      const calculated=fund*.25, custom=advanced?Math.max(0,v.custom_lump_sum||0):0, lump=custom>0?custom:calculated;
      const before=previous, after=previous+lump;
      const overlap=(lo,hi)=>Math.max(0,Math.min(after,hi)-Math.max(before,lo));
      const taxFree=overlap(0,200000), at20=overlap(200000,500000), above500=Math.max(0,after-Math.max(before,500000));
      const rate=advanced?Math.max(0,Math.min(60,v.marginal_rate||40))/100:.40;
      const tax20=at20*.20, marginalTax=above500*rate, totalTax=tax20+marginalTax;
      return {
        gross_lump:money(lump),
        remaining_tax_free:money(Math.max(0,200000-previous)),
        tax_free_current:money(taxFree),
        at_20:money(at20),
        tax_20:money(tax20),
        above_500:money(above500),
        marginal_tax:money(marginalTax),
        total_tax:money(totalTax),
        net_lump:money(Math.max(0,lump-totalTax)),
        lifetime_after:money(after),
        __chart:{type:'bar',title:'Tax treatment of this retirement lump sum',caption:'Slices the current payment according to your cumulative retirement lump sums. The above-€500,000 slice uses the marginal PAYE rate assumption in Advanced mode.',labels:['Tax-free','Taxed at 20%','Above €500k threshold'],series:[{label:'Current lump sum',values:[taxFree,at20,above500]}]}
      };

  };

  if(typeof globalThis!=='undefined'){
    globalThis.CompoundToolsTest={calculators,monthlyPayment,incomeTax2026,usc2026,annualClassA2026,selfEmployedNet2026,stampDutyResidential,lptBands,lptAdjust,fhsPriceCeilings,fhsPriceCeiling,mortgageOverpaymentProjection,mortgageSnapshot};
  }
  if(typeof document==='undefined') return;

  document.querySelectorAll('[data-calculator]').forEach(root => {
    const form=root.querySelector('[data-tool-form]'), error=root.querySelector('[data-tool-error]');
    const run=(showErrors=true)=>{
      const values={}; let invalid=false, invalidField=null, invalidMessage='';
      root.querySelectorAll('[data-field]').forEach(el=>el.removeAttribute('aria-invalid'));
      root.querySelectorAll('[data-field]').forEach(el=>{
        const raw=el.value;
        if(el.type==='checkbox'){ values[el.dataset.field]=el.checked; return; }
        if(el.type==='date'){
          if(!raw&&el.dataset.optional==='true'){values[el.dataset.field]='';return;}
          if(!/^\d{4}-\d{2}-\d{2}$/.test(raw)){invalid=true;invalidField=invalidField||el;invalidMessage=invalidMessage||'Enter a valid date.';return;}
          values[el.dataset.field]=raw; return;
        }
        if(el.tagName==='SELECT'){ values[el.dataset.field]=raw; return; }
        const n=Number(raw);
        const min=el.min!==''?Number(el.min):null, max=el.max!==''?Number(el.max):null;
        if(!raw || !Number.isFinite(n) || (min!==null&&n<min) || (max!==null&&n>max)){
          invalid=true; invalidField=invalidField||el;
          const field=el.closest('.tool-field'), label=field?.querySelector('label')?.textContent?.trim()||'This field';
          if(min!==null&&max!==null) invalidMessage=invalidMessage||label+' must be between '+num(min)+' and '+num(max)+'.';
          else if(min!==null) invalidMessage=invalidMessage||label+' must be at least '+num(min)+'.';
          else if(max!==null) invalidMessage=invalidMessage||label+' must be no more than '+num(max)+'.';
          else invalidMessage=invalidMessage||'Check the value entered for '+label+'.';
          return;
        }
        values[el.dataset.field]=n;
      });
      values.__advanced=root.dataset.advancedMode==='true';
      if(invalid){
        if(invalidField) invalidField.setAttribute('aria-invalid','true');
        if(showErrors) error.textContent=invalidMessage||'Check the numbers entered and try again.';
        return;
      }
      const relationshipError=validateRelationships(root.dataset.calculator,values);
      if(relationshipError){ if(showErrors) error.textContent=relationshipError; return; }
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
        renderInsights(root,buildInsights(root.dataset.calculator,values));
        renderScenarioSummary(values);
        renderSavedComparison();
        if(window.gtag) window.gtag('event','tool_calculate',{tool_name:root.dataset.toolName});
      }catch(e){ if(showErrors) error.textContent='This combination could not be calculated. Check the values and try again.'; }
    };
    const decodeScenario = () => {
      if(!window.location.hash.startsWith('#scenario=')) return null;
      try{
        let raw=window.location.hash.slice(10).replace(/-/g,'+').replace(/_/g,'/');
        while(raw.length%4) raw+='=';
        const bytes=Uint8Array.from(atob(raw),ch=>ch.charCodeAt(0));
        return JSON.parse(new TextDecoder().decode(bytes));
      }catch(e){ return null; }
    };
    const sharedScenario=decodeScenario();
    const legacyParams=new URLSearchParams(window.location.search);
    root.dataset.advancedMode=(sharedScenario?.advanced===true||legacyParams.get('advanced')==='1')?'true':'false';
    root.querySelectorAll('[data-field]').forEach(el=>{
      const key=el.dataset.field;
      let has=false,val='';
      if(sharedScenario&&sharedScenario.values&&Object.prototype.hasOwnProperty.call(sharedScenario.values,key)){has=true;val=sharedScenario.values[key];}
      else if(legacyParams.has(key)){has=true;val=legacyParams.get(key);}
      if(!has) return;
      if(el.type==='checkbox') el.checked=val===true||val==='1'||val==='true';
      else el.value=String(val);
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
      root.querySelectorAll('[data-advanced-result]').forEach(card=>{card.hidden=root.dataset.advancedMode!=='true';});
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
        const fieldId=wrapper.querySelector('[data-field]')?.dataset.field;
        if(fieldId){
          const section=root.querySelector('[data-section-for="'+fieldId+'"]');
          if(section) section.hidden=!show;
        }
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
    const saveScenarioButton=root.querySelector('[data-tool-save-scenario]');
    const clearScenarioButton=root.querySelector('[data-tool-clear-scenario]');
    const comparePanel=root.querySelector('[data-tool-compare-panel]');
    const compareTable=root.querySelector('[data-tool-compare-table]');
    let savedScenario=null;

    const snapshotResults=()=>[...root.querySelectorAll('.tool-result')].filter(card=>!card.hidden).map(card=>({
      label:card.querySelector('span')?.textContent?.trim()||'Result',
      value:card.querySelector('strong')?.textContent?.trim()||'—'
    }));

    const renderSavedComparison=()=>{
      if(!comparePanel||!compareTable) return;
      if(!savedScenario){comparePanel.hidden=true;compareTable.innerHTML='';return;}
      const current=snapshotResults();
      const byLabel=new Map(current.map(item=>[item.label,item.value]));
      compareTable.innerHTML='';
      const head=document.createElement('div'); head.className='tool-compare-row tool-compare-row-head';
      ['Metric','Saved','Current'].forEach(label=>{const el=document.createElement('strong');el.textContent=label;head.appendChild(el);});
      compareTable.appendChild(head);
      savedScenario.results.forEach(item=>{
        const row=document.createElement('div');row.className='tool-compare-row';
        const metric=document.createElement('span');metric.textContent=item.label;
        const saved=document.createElement('span');saved.textContent=item.value;
        const currentValue=document.createElement('span');currentValue.textContent=byLabel.get(item.label)||'—';
        row.append(metric,saved,currentValue);compareTable.appendChild(row);
      });
      comparePanel.hidden=false;
    };

    if(saveScenarioButton) saveScenarioButton.addEventListener('click',()=>{
      savedScenario={results:snapshotResults()};
      saveScenarioButton.textContent='Replace saved scenario';
      renderSavedComparison();
      if(actionStatus) actionStatus.textContent='Scenario saved on this page for comparison.';
      if(window.gtag) window.gtag('event','tool_save_comparison',{tool_name:root.dataset.toolName});
    });
    if(clearScenarioButton) clearScenarioButton.addEventListener('click',()=>{
      savedScenario=null;
      if(saveScenarioButton) saveScenarioButton.textContent='Save for comparison';
      renderSavedComparison();
      if(actionStatus) actionStatus.textContent='Saved comparison cleared.';
    });

    const shareButton=root.querySelector('[data-tool-share]'), copyResultsButton=root.querySelector('[data-tool-copy-results]'), printButton=root.querySelector('[data-tool-print]'), actionStatus=root.querySelector('[data-tool-action-status]');
    if(shareButton) shareButton.addEventListener('click',async()=>{
      const url=new URL(window.location.href); url.search=''; url.hash='';
      const values={};
      root.querySelectorAll('[data-field]').forEach(el=>{
        values[el.dataset.field]=el.type==='checkbox'?el.checked:el.value;
      });
      const json=JSON.stringify({advanced:root.dataset.advancedMode==='true',values});
      const bytes=new TextEncoder().encode(json);
      let binary=''; bytes.forEach(byte=>binary+=String.fromCharCode(byte));
      const encoded=btoa(binary).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
      url.hash='scenario='+encoded;
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
    if(copyResultsButton) copyResultsButton.addEventListener('click',async()=>{
      const lines=[root.querySelector('h1')?.textContent?.trim()||'Compound calculator'];
      root.querySelectorAll('.tool-result').forEach(card=>{
        const label=card.querySelector('span')?.textContent?.trim();
        const value=card.querySelector('strong')?.textContent?.trim();
        if(label&&value&&value!=='—') lines.push(label+': '+value);
      });
      const textValue=lines.join('\n');
      let copied=false;
      try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(textValue);copied=true;}}catch(e){}
      if(!copied){
        const ta=document.createElement('textarea');ta.value=textValue;ta.setAttribute('readonly','');ta.style.position='absolute';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();
        try{copied=document.execCommand('copy');}catch(e){} ta.remove();
      }
      if(actionStatus) actionStatus.textContent=copied?'Results copied.':'Could not copy automatically.';
      if(window.gtag) window.gtag('event','tool_copy_results',{tool_name:root.dataset.toolName});
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
