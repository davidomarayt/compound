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
      labels.forEach((lab,i)=>{ const cx=L+group*(i+.5); svg+='<text class="tool-chart-axis" x="'+cx.toFixed(1)+'" y="'+(H-18)+'" text-anchor="middle">'+esc(lab)+'</text>'; series.forEach((s,j)=>{const v=Number(s.values[i])||0,x=cx-totalBar/2+j*bw,yy=y(Math.max(0,v)),y0=y(Math.min(0,v)),top=Math.min(yy,y0),h=Math.max(1,Math.abs(y0-yy));svg+='<rect class="tool-chart-bar tool-chart-series-'+(j%3)+'" x="'+x.toFixed(1)+'" y="'+top.toFixed(1)+'" width="'+Math.max(2,bw-3).toFixed(1)+'" height="'+h.toFixed(1)+'"><title>'+esc(s.label)+': '+esc(money(v))+'</title></rect>';});});
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
    }
  };

  document.querySelectorAll('[data-calculator]').forEach(root => {
    const form=root.querySelector('[data-tool-form]'), error=root.querySelector('[data-tool-error]');
    const run=()=>{
      const values={}; let invalid=false;
      root.querySelectorAll('[data-field]').forEach(el=>{
        const raw=el.value;
        if(el.type==='checkbox'){ values[el.dataset.field]=el.checked; return; }
        if(el.tagName==='SELECT'){ values[el.dataset.field]=raw; return; }
        const n=Number(raw); if(!Number.isFinite(n)){invalid=true; return;} values[el.dataset.field]=n;
      });
      if(invalid){ error.textContent='Check the numbers entered and try again.'; return; }
      error.textContent='';
      const fn=calculators[root.dataset.calculator]; if(!fn) return;
      try{
        const results=fn(values);
        Object.entries(results).forEach(([k,v])=>{
          if(k.startsWith('__')) return;
          const el=root.querySelector('[data-result="' + k + '"]');
          if(el) el.textContent=v;
        });
        renderToolChart(root,results.__chart);
        if(window.gtag) window.gtag('event','tool_calculate',{tool_name:root.dataset.toolName});
      }catch(e){ error.textContent='This combination could not be calculated. Check the values and try again.'; }
    };
    const syncVisibility=()=>{
      root.querySelectorAll('[data-show-if]').forEach(wrapper=>{
        const controller=root.querySelector('[data-field="'+wrapper.dataset.showIf+'"]');
        let show=false;
        if(controller){
          if(controller.type==='checkbox') show=controller.checked;
          else show=controller.value!==''&&controller.value!=='no'&&controller.value!=='false'&&controller.value!=='0';
        }
        wrapper.hidden=!show;
      });
    };
    if(form){
      form.addEventListener('submit',e=>{e.preventDefault();run();});
      form.addEventListener('change',()=>{syncVisibility();run();});
      form.addEventListener('reset',()=>setTimeout(()=>{syncVisibility();run();},0));
    }
    syncVisibility();
    run();
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
