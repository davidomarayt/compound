(function () {
  'use strict';
  const starts = [0, 5, 10];
  function project(monthly, annual, start, age) {
    const months = Math.max(0, (age - start) * 12);
    const rate = Math.pow(1 + annual / 100, 1 / 12) - 1;
    const paid = monthly * months;
    const balance = Math.abs(rate) < 1e-12 ? paid : monthly * Math.expm1(months * Math.log1p(rate)) / rate;
    return { paid, balance, growth: balance - paid };
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { project };
  if (typeof document === 'undefined') return;
  const root = document.getElementById('child-savings-tool');
  if (!root) return;
  const byId = id => document.getElementById(id);
  const inputs = ['cs-monthly', 'cs-return', 'cs-inflation'].map(byId);
  const error = byId('cs-error');
  const output = byId('cs-output');
  const slider = byId('cs-age');
  const chart = byId('cs-chart');
  const money = value => new Intl.NumberFormat('en-IE', {style:'currency', currency:'EUR', maximumFractionDigits:0}).format(value);
  const ns = 'http://www.w3.org/2000/svg';
  function svg(tag, attrs, text) {
    const el = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
    if (text !== undefined) el.textContent = text;
    return el;
  }
  function render() {
    const values = inputs.map(el => el.value.trim() === '' ? NaN : Number(el.value));
    const [monthly, annual, inflation] = values;
    const limits = [[0,10000],[-20,20],[0,15]];
    const labels = ['Enter a monthly amount from €0 to €10,000.', 'Enter an assumed return from −20% to 20%.', 'Enter assumed inflation from 0% to 15%.'];
    let invalid = -1;
    values.forEach((v,i) => {
      const bad = !Number.isFinite(v) || v < limits[i][0] || v > limits[i][1];
      inputs[i].setAttribute('aria-invalid', String(bad));
      if (bad && invalid < 0) invalid = i;
    });
    if (invalid >= 0) {error.textContent = labels[invalid]; output.hidden = true; return;}
    error.textContent = ''; output.hidden = false;
    const age = Number(slider.value);
    const finals = starts.map(s => project(monthly, annual, s, 18));
    const inflationFactor = Math.pow(1 + inflation/100, 18);
    byId('cs-balance').textContent = money(finals[0].balance);
    byId('cs-real').textContent = money(finals[0].balance / inflationFactor);
    byId('cs-summary').textContent = `${money(monthly)} a month from birth to 18: ${money(finals[0].paid)} paid in and ${money(finals[0].growth)} modelled growth, before tax and fees.`;
    byId('cs-age-label').textContent = `Explore age ${age}`;
    slider.setAttribute('aria-valuetext', `${age} years old`);
    byId('cs-inspect').textContent = starts.map((s,i) => `${i===0 ? 'From birth' : `From age ${s}`}: ${money(project(monthly, annual, s, age).balance)}`).join(' · ');
    const tbody = byId('cs-table-body');
    tbody.replaceChildren();
    finals.forEach((r,i) => {
      const row = document.createElement('tr');
      [i===0?'Birth':`Age ${starts[i]}`,money(r.paid),money(r.growth),money(r.balance)].forEach((value,j) => {
        const cell=document.createElement(j===0?'th':'td');
        if(j===0)cell.scope='row';
        cell.textContent=value;row.appendChild(cell);
      });
      tbody.appendChild(row);
    });
    chart.removeAttribute('hidden');
    const w=Math.max(240,chart.clientWidth || 720),h=w<500?280:340,left=60,right=18,top=24,bottom=44;
    chart.setAttribute('viewBox', `0 0 ${w} ${h}`);
    const max=Math.max(...finals.map(r=>r.balance),1)*1.08;
    const x = a => left+(w-left-right)*a/18;
    const y = v => h-bottom-(h-top-bottom)*v/max;
    chart.replaceChildren();
    chart.appendChild(svg('title',{},'Illustrative savings balances from birth, age five and age ten to age eighteen'));
    chart.appendChild(svg('desc',{},`Monthly saving ${money(monthly)}, assumed annual return ${annual}%. Before tax and fees. Exact age-18 values are in the table below. Use the age slider for intermediate values.`));
    for(let i=0;i<5;i++) {
      const value=max*i/4;
      chart.appendChild(svg('line',{x1:left,x2:w-right,y1:y(value),y2:y(value),class:'cs-grid'}));
      chart.appendChild(svg('text',{x:left-10,y:y(value)+5,'text-anchor':'end',class:'cs-axis'},value>=1000?`€${(value/1000).toFixed(value>=10000?0:1)}k`:money(value)));
    }
    [0,5,10,15,18].forEach(a=>chart.appendChild(svg('text',{x:x(a),y:h-14,'text-anchor':'middle',class:'cs-axis'},a===0?'Birth':`${a}`)));
    starts.forEach((s,i)=>{
      const points=Array.from({length:217},(_,m)=>`${x(m/12)},${y(project(monthly,annual,s,m/12).balance)}`).join(' ');
      chart.appendChild(svg('polyline',{points,fill:'none',class:`cs-line cs-line-${i}`}));
    });
    chart.appendChild(svg('line',{x1:x(age),x2:x(age),y1:top,y2:h-bottom,class:'cs-cursor'}));
    starts.forEach((s,i)=>chart.appendChild(svg('circle',{cx:x(age),cy:y(project(monthly,annual,s,age).balance),r:5,class:`cs-point cs-point-${i}`})));
    root.querySelectorAll('[data-cs-monthly]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.csMonthly)===monthly)));
  }
  inputs.forEach(el=>el.addEventListener('input',render));
  slider.addEventListener('input',render);
  root.querySelectorAll('[data-cs-monthly]').forEach(b=>b.addEventListener('click',()=>{inputs[0].value=b.dataset.csMonthly;render();}));
  root.querySelector('.cs-controls').hidden=false;
  byId('cs-explore').hidden=false;
  render();
  let lastWidth=root.clientWidth;
  if(typeof ResizeObserver !== 'undefined') new ResizeObserver(()=>{if(root.clientWidth!==lastWidth){lastWidth=root.clientWidth;render();}}).observe(root);
}());
