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
    }
  };

  document.querySelectorAll('[data-calculator]').forEach(root => {
    const form=root.querySelector('[data-tool-form]'), error=root.querySelector('[data-tool-error]');
    const run=()=>{
      const values={}; let invalid=false;
      root.querySelectorAll('[data-field]').forEach(el=>{
        const raw=el.value;
        if(el.tagName==='SELECT'){ values[el.dataset.field]=raw; return; }
        const n=Number(raw); if(!Number.isFinite(n)){invalid=true; return;} values[el.dataset.field]=n;
      });
      if(invalid){ error.textContent='Check the numbers entered and try again.'; return; }
      error.textContent='';
      const fn=calculators[root.dataset.calculator]; if(!fn) return;
      try{
        const results=fn(values);
        Object.entries(results).forEach(([k,v])=>{
          const el=root.querySelector('[data-result="' + k + '"]');
          if(el) el.textContent=v;
        });
        if(window.gtag) window.gtag('event','tool_calculate',{tool_name:root.dataset.toolName});
      }catch(e){ error.textContent='This combination could not be calculated. Check the values and try again.'; }
    };
    if(form){
      form.addEventListener('submit',e=>{e.preventDefault();run();});
      form.addEventListener('reset',()=>setTimeout(run,0));
    }
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
