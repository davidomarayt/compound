(() => {
  'use strict';
  const root = document.querySelector('[data-calculator="mortgage"]');
  if (!root) return;

  const euro = new Intl.NumberFormat('en-IE', {style:'currency', currency:'EUR', maximumFractionDigits:2});
  const money = value => euro.format(Number.isFinite(value) ? value : 0);
  const fields = {
    amount: root.querySelector('[data-field="amount"]'),
    rate: root.querySelector('[data-field="rate"]'),
    years: root.querySelector('[data-field="years"]')
  };
  const error = root.querySelector('[data-tool-error]');
  const actionStatus = root.querySelector('[data-tool-action-status]');
  let savedScenario = null;
  let lastRaw = null;

  const monthlyPayment = (principal, annual, months) => {
    const r = annual / 100 / 12;
    return r === 0 ? principal / months : principal * r / (1 - Math.pow(1 + r, -months));
  };

  const snapshot = (principal, annual, totalMonths, payment, horizonMonths) => {
    const r = annual / 100 / 12;
    let balance = principal, interest = 0;
    const months = Math.min(horizonMonths, totalMonths);
    for (let month = 0; month < months && balance > 0.005; month++) {
      const monthlyInterest = balance * r;
      const actual = Math.min(balance + monthlyInterest, payment);
      interest += monthlyInterest;
      balance = Math.max(0, balance + monthlyInterest - actual);
    }
    return {balance, interest};
  };

  const readValues = showErrors => {
    let invalid = false, message = '';
    const values = {};
    for (const [key, el] of Object.entries(fields)) {
      el.removeAttribute('aria-invalid');
      const n = Number(el.value);
      const min = el.min !== '' ? Number(el.min) : null;
      const max = el.max !== '' ? Number(el.max) : null;
      if (!el.value || !Number.isFinite(n) || (min !== null && n < min) || (max !== null && n > max)) {
        invalid = true;
        el.setAttribute('aria-invalid', 'true');
        if (!message) {
          const label = el.closest('.tool-field')?.querySelector('label')?.textContent?.trim() || 'This field';
          message = min !== null && max !== null ? `${label} must be between ${min} and ${max}.` :
                    min !== null ? `${label} must be at least ${min}.` :
                    max !== null ? `${label} must be no more than ${max}.` : `Check ${label}.`;
        }
      }
      values[key] = n;
    }
    if (invalid) {
      if (showErrors && error) error.textContent = message;
      return null;
    }
    if (error) error.textContent = '';
    return values;
  };

  const calculate = values => {
    const amount = Math.max(0, values.amount);
    const months = Math.max(1, Math.round(values.years * 12));
    const payment = monthlyPayment(amount, values.rate, months);
    const total = payment * months;
    const firstYear = snapshot(amount, values.rate, months, payment, Math.min(12, months));
    const fiveYears = snapshot(amount, values.rate, months, payment, Math.min(60, months));
    return {
      monthly: payment,
      interest: Math.max(0, total - amount),
      total,
      annual_repayment: payment * 12,
      first_year_interest: firstYear.interest,
      first_year_principal: Math.max(0, amount - firstYear.balance),
      balance_5y: fiveYears.balance,
      stress_1pp: monthlyPayment(amount, values.rate + 1, months),
      stress_2pp: monthlyPayment(amount, values.rate + 2, months),
      payment_per_100k: amount > 0 ? payment / amount * 100000 : 0,
      months
    };
  };

  const setResult = (id, value) => {
    const el = root.querySelector('[data-result="' + id + '"]');
    if (el) el.textContent = money(value);
  };

  const renderChart = (values, result) => {
    const panel = root.querySelector('[data-tool-chart]');
    const canvas = root.querySelector('[data-chart-canvas]');
    if (!panel || !canvas) return;
    const labels = ['Start'], balances = [values.amount];
    const r = values.rate / 100 / 12;
    let balance = values.amount;
    for (let month = 1; month <= result.months && balance > 0.005; month++) {
      const interest = balance * r;
      balance = Math.max(0, balance + interest - Math.min(balance + interest, result.monthly));
      if (month % 12 === 0 || month === result.months) {
        labels.push('Year ' + Math.round(month / 12));
        balances.push(balance);
      }
    }
    const W=760,H=300,L=64,R=24,T=18,B=54,plotW=W-L-R,plotH=H-T-B;
    const max = Math.max(...balances, 1);
    const y = v => T + (max - v) / max * plotH;
    let svg = '<svg class="tool-chart-svg" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Mortgage balance over time">';
    for (let i=0;i<=4;i++) {
      const val=max*i/4, yy=y(val);
      svg += '<line class="tool-chart-grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+yy.toFixed(1)+'" y2="'+yy.toFixed(1)+'"/>';
      svg += '<text class="tool-chart-axis" x="'+(L-8)+'" y="'+(yy+4).toFixed(1)+'" text-anchor="end">€'+Math.round(val).toLocaleString('en-IE')+'</text>';
    }
    const n=Math.max(1,balances.length-1);
    const points=balances.map((v,i)=>(L+plotW*(i/n)).toFixed(1)+','+y(v).toFixed(1)).join(' ');
    svg += '<polyline class="tool-chart-line tool-chart-series-0" points="'+points+'"/>';
    [0,Math.round(n*.25),Math.round(n*.5),Math.round(n*.75),n].filter((v,i,a)=>a.indexOf(v)===i).forEach(i=>{
      const x=L+plotW*(i/n);
      svg += '<text class="tool-chart-axis" x="'+x.toFixed(1)+'" y="'+(H-18)+'" text-anchor="middle">'+labels[i]+'</text>';
    });
    svg += '</svg>';
    canvas.innerHTML = svg;
    const title=panel.querySelector('[data-chart-title]'), caption=panel.querySelector('[data-chart-caption]');
    if(title) title.textContent='Mortgage balance over time';
    if(caption) caption.textContent='Scheduled balance if the entered rate stayed unchanged for the full term.';
    const legend=panel.querySelector('[data-chart-legend]');
    if(legend) legend.innerHTML='<span><i class="series-0"></i>Mortgage balance</span>';
    panel.hidden=false;
  };

  const renderInsights = (values, result) => {
    const panel=root.querySelector('[data-tool-insights]'), list=root.querySelector('[data-tool-insight-list]');
    if(!panel || !list) return;
    const higherHalf=monthlyPayment(values.amount, values.rate + .5, result.months);
    const items=[
      'At this rate and term, every €100,000 borrowed costs about '+money(result.payment_per_100k)+' per month.',
      'If the rate were 0.5 percentage points higher, the monthly repayment would rise by about '+money(higherHalf-result.monthly)+'.'
    ];
    list.innerHTML='';
    items.forEach(text=>{const li=document.createElement('li');li.textContent=text;list.appendChild(li);});
    panel.hidden=false;
  };

  const renderScenario = values => {
    const wrap=root.querySelector('[data-tool-scenario-summary]'), chips=root.querySelector('[data-tool-scenario-chips]');
    if(!wrap || !chips) return;
    chips.innerHTML='';
    [
      'Mortgage amount: €'+values.amount.toLocaleString('en-IE'),
      'Interest rate: '+values.rate+'%',
      'Mortgage term: '+values.years+' years'
    ].forEach(text=>{const span=document.createElement('span');span.className='tool-scenario-chip';span.textContent=text;chips.appendChild(span);});
    wrap.hidden=false;
  };

  const currentResults = () => [...root.querySelectorAll('.tool-result')].filter(card=>!card.hidden).map(card=>({
    label: card.querySelector('span')?.textContent?.trim() || 'Result',
    value: card.querySelector('strong')?.textContent?.trim() || '—'
  }));

  const renderSaved = () => {
    const panel=root.querySelector('[data-tool-compare-panel]'), table=root.querySelector('[data-tool-compare-table]');
    if(!panel || !table) return;
    if(!savedScenario){panel.hidden=true;table.innerHTML='';return;}
    const current=currentResults(), byLabel=new Map(current.map(x=>[x.label,x.value]));
    table.innerHTML='';
    const head=document.createElement('div');head.className='tool-compare-row tool-compare-row-head';
    ['Metric','Saved','Current'].forEach(label=>{const el=document.createElement('strong');el.textContent=label;head.appendChild(el);});
    table.appendChild(head);
    savedScenario.forEach(item=>{
      const row=document.createElement('div');row.className='tool-compare-row';
      [item.label,item.value,byLabel.get(item.label)||'—'].forEach((text,index)=>{
        const el=document.createElement(index===0?'span':'span');el.textContent=text;row.appendChild(el);
      });
      table.appendChild(row);
    });
    panel.hidden=false;
  };

  const run = (showErrors=false) => {
    const values=readValues(showErrors);
    if(!values) return;
    const result=calculate(values);
    lastRaw={values,result};
    ['monthly','interest','total','annual_repayment','first_year_interest','first_year_principal','balance_5y','stress_1pp','stress_2pp','payment_per_100k'].forEach(id=>setResult(id,result[id]));
    renderInsights(values,result);
    renderScenario(values);
    renderSaved();
    renderChart(values,result);
    if(window.gtag) window.gtag('event','tool_calculate',{tool_name:root.dataset.toolName});
  };

  const form=root.querySelector('[data-tool-form]');
  if(form){
    let timer=null;
    form.addEventListener('submit',event=>{event.preventDefault();run(true);});
    form.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>run(false),160);});
    form.addEventListener('change',()=>run(false));
    form.addEventListener('reset',()=>setTimeout(()=>run(false),0));
  }

  const save=root.querySelector('[data-tool-save-scenario]');
  const clear=root.querySelector('[data-tool-clear-scenario]');
  if(save) save.addEventListener('click',()=>{
    savedScenario=currentResults();
    save.textContent='Replace saved scenario';
    renderSaved();
    if(actionStatus) actionStatus.textContent='Scenario saved on this page for comparison.';
  });
  if(clear) clear.addEventListener('click',()=>{
    savedScenario=null;
    if(save) save.textContent='Save for comparison';
    renderSaved();
    if(actionStatus) actionStatus.textContent='Saved comparison cleared.';
  });

  const share=root.querySelector('[data-tool-share]');
  if(share) share.addEventListener('click',async()=>{
    if(!lastRaw) run(false);
    const url=new URL(location.href); url.search=''; url.hash='';
    const values={amount:fields.amount.value,rate:fields.rate.value,years:fields.years.value};
    const json=JSON.stringify({advanced:false,values});
    const bytes=new TextEncoder().encode(json);let binary='';bytes.forEach(byte=>binary+=String.fromCharCode(byte));
    url.hash='scenario='+btoa(binary).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
    let copied=false;
    try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(url.toString());copied=true;}}catch(_){}
    if(actionStatus) actionStatus.textContent=copied?'Scenario link copied.':'Copy the current page URL to share this scenario.';
  });

  const copy=root.querySelector('[data-tool-copy-results]');
  if(copy) copy.addEventListener('click',async()=>{
    const lines=['Mortgage Calculator Ireland',...currentResults().map(x=>x.label+': '+x.value)];
    let copied=false;try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(lines.join('\n'));copied=true;}}catch(_){}
    if(actionStatus) actionStatus.textContent=copied?'Results copied.':'Could not copy automatically.';
  });
  root.querySelector('[data-tool-print]')?.addEventListener('click',()=>window.print());

  if(location.hash.startsWith('#scenario=')){
    try{
      let raw=location.hash.slice(10).replace(/-/g,'+').replace(/_/g,'/');
      while(raw.length%4) raw+='=';
      const data=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(raw),c=>c.charCodeAt(0))));
      for(const key of ['amount','rate','years']) if(data.values?.[key]!==undefined) fields[key].value=String(data.values[key]);
    }catch(_){}
  }

  run(false);
})();