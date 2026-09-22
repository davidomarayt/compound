(() => {
  const chooseTarget = (active, strategy) => {
    const candidates = active.filter(d => d.balance > 0.005);
    if (!candidates.length) return null;
    const sorted = [...candidates].sort((a,b) => {
      if (strategy === 'avalanche') {
        if (b.apr !== a.apr) return b.apr - a.apr;
        if (a.balance !== b.balance) return a.balance - b.balance;
      } else {
        if (a.balance !== b.balance) return a.balance - b.balance;
        if (b.apr !== a.apr) return b.apr - a.apr;
      }
      return a.index - b.index;
    });
    return sorted[0];
  };

  const simulate = (inputDebts, extra, strategy) => {
    const debts = inputDebts.map((d, index) => ({...d, index, paidOff:false}));
    const startingBalance = debts.reduce((sum,d) => sum + d.balance, 0);
    const fixedBudget = debts.reduce((sum,d) => sum + d.minimum, 0) + Math.max(0,extra);
    let totalInterest = 0;
    let totalPaid = 0;
    let month = 0;
    const schedule = [startingBalance];
    const payoffOrder = [];

    if (fixedBudget <= 0 || startingBalance <= 0) {
      return {success:false, months:Infinity, interest:Infinity, paid:Infinity, schedule, payoffOrder, first:null};
    }

    const recordPaid = d => {
      if (!d.paidOff && d.balance <= 0.005) {
        d.balance = 0;
        d.paidOff = true;
        payoffOrder.push({name:d.name, month});
      }
    };

    while (month < 1200) {
      month += 1;

      for (const d of debts) {
        if (d.balance <= 0.005) continue;
        const interest = d.balance * (d.apr / 100 / 12);
        d.balance += interest;
        totalInterest += interest;
      }

      let budgetLeft = fixedBudget;

      for (const d of debts) {
        if (d.balance <= 0.005) continue;
        const payment = Math.min(d.balance, d.minimum, budgetLeft);
        if (payment > 0) {
          d.balance -= payment;
          budgetLeft -= payment;
          totalPaid += payment;
        }
        recordPaid(d);
      }

      let guard = 0;
      while (budgetLeft > 0.005 && guard < debts.length + 4) {
        guard += 1;
        const target = chooseTarget(debts, strategy);
        if (!target) break;
        const payment = Math.min(target.balance, budgetLeft);
        target.balance -= payment;
        budgetLeft -= payment;
        totalPaid += payment;
        recordPaid(target);
      }

      const remaining = debts.reduce((sum,d) => sum + Math.max(0,d.balance), 0);
      schedule.push(remaining);

      if (remaining <= 0.005) {
        return {
          success:true,
          months:month,
          interest:totalInterest,
          paid:totalPaid,
          schedule,
          payoffOrder,
          first:payoffOrder[0] || null
        };
      }

      if (!Number.isFinite(remaining) || remaining > 1e9) break;
    }

    return {
      success:false,
      months:Infinity,
      interest:totalInterest,
      paid:totalPaid,
      schedule,
      payoffOrder,
      first:payoffOrder[0] || null
    };
  };

  if (typeof globalThis !== 'undefined') globalThis.CompoundDebtTest = {chooseTarget, simulate};
  if (typeof document === 'undefined') return;

  const root = document.querySelector('[data-debt-calculator]');
  if (!root) return;

  const euro = new Intl.NumberFormat('en-IE', {style:'currency', currency:'EUR', maximumFractionDigits:2});
  const number = new Intl.NumberFormat('en-IE', {maximumFractionDigits:2});
  const money = v => euro.format(Number.isFinite(v) ? v : 0);
  const fmt = v => number.format(Number.isFinite(v) ? v : 0);
  const rows = root.querySelector('[data-debt-rows]');
  const form = root.querySelector('[data-debt-form]');
  const extraInput = root.querySelector('#debt-extra');
  const error = root.querySelector('[data-debt-error]');
  const addButton = root.querySelector('[data-add-debt]');
  const clearButton = root.querySelector('[data-clear-debts]');
  const resetButton = root.querySelector('[data-reset-example]');
  const chartPanel = root.querySelector('[data-debt-chart]');
  const chartCanvas = root.querySelector('[data-debt-chart-canvas]');
  const sampleNode = document.querySelector('#debt-example-data');
  const maxDebts = 8;
  let rowCounter = 0;
  let sampleDebts = [];

  try {
    sampleDebts = JSON.parse(sampleNode ? sampleNode.textContent : '[]');
  } catch (e) {
    sampleDebts = [];
  }

  const escapeAttr = value => String(value ?? '').replace(/[&<>"']/g, ch => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[ch]));

  const duration = months => {
    if (!Number.isFinite(months)) return 'Not cleared';
    if (months <= 0) return 'Already clear';
    const years = Math.floor(months / 12);
    const rem = months % 12;
    if (!years) return months + ' month' + (months === 1 ? '' : 's');
    if (!rem) return years + ' year' + (years === 1 ? '' : 's');
    return years + ' yr ' + rem + ' mo';
  };

  const payoffDate = months => {
    if (!Number.isFinite(months)) return 'Not reached within model';
    const d = new Date();
    d.setDate(1);
    d.setMonth(d.getMonth() + months);
    return new Intl.DateTimeFormat('en-IE', {month:'long', year:'numeric'}).format(d);
  };

  let comparisonTimer=null;
  const scheduleComparison = () => {
    updateSummaryPreview();
    clearTimeout(comparisonTimer);
    comparisonTimer=setTimeout(()=>{
      const check=readDebts(true), extra=readExtra();
      if(!check.problem && check.debts.length && Number.isFinite(extra)) runComparison();
    },220);
  };

  const addDebtRow = debt => {
    if (rows.children.length >= maxDebts) return;
    rowCounter += 1;
    const id = rowCounter;
    const item = debt || {name:'', balance:'', apr:'', minimum:''};
    const row = document.createElement('div');
    row.className = 'debt-row';
    row.dataset.debtRow = '';
    row.innerHTML = `
      <div class="debt-cell debt-cell-name">
        <label for="debt-name-${id}">Debt name</label>
        <input id="debt-name-${id}" type="text" maxlength="42" autocomplete="off" value="${escapeAttr(item.name || '')}" placeholder="e.g. Credit card">
      </div>
      <div class="debt-cell debt-cell-balance">
        <label for="debt-balance-${id}">Balance</label>
        <span class="debt-input-affix"><span>€</span><input id="debt-balance-${id}" data-debt-balance type="number" inputmode="decimal" min="0.01" step="10" value="${escapeAttr(item.balance ?? '')}"></span>
      </div>
      <div class="debt-cell debt-cell-apr">
        <label for="debt-apr-${id}">APR</label>
        <span class="debt-input-affix debt-input-percent"><input id="debt-apr-${id}" data-debt-apr type="number" inputmode="decimal" min="0" max="100" step="0.1" value="${escapeAttr(item.apr ?? '')}"><span>%</span></span>
      </div>
      <div class="debt-cell debt-cell-payment">
        <label for="debt-min-${id}">Monthly payment</label>
        <span class="debt-input-affix"><span>€</span><input id="debt-min-${id}" data-debt-min type="number" inputmode="decimal" min="0.01" step="5" value="${escapeAttr(item.minimum ?? '')}"></span>
      </div>
      <button class="debt-remove" type="button" aria-label="Remove this debt" title="Remove debt">×</button>
    `;
    row.querySelector('.debt-remove').addEventListener('click', () => {
      row.remove();
      if (!rows.children.length) addDebtRow();
      updateSummaryPreview();
      addButton.disabled = rows.children.length >= maxDebts;
    });
    row.querySelectorAll('input').forEach(input => input.addEventListener('input', scheduleComparison));
    rows.appendChild(row);
    addButton.disabled = rows.children.length >= maxDebts;
  };

  const loadExample = () => {
    rows.innerHTML = '';
    rowCounter = 0;
    (sampleDebts.length ? sampleDebts : [
      {name:'Credit card', balance:4500, apr:19.9, minimum:150},
      {name:'Personal loan', balance:8000, apr:8.5, minimum:220},
      {name:'Car loan', balance:12000, apr:6.9, minimum:280}
    ]).forEach(addDebtRow);
    extraInput.value = root.dataset.extraDefault || extraInput.defaultValue || '200';
    updateSummaryPreview();
    runComparison();
  };

  const clearExample = () => {
    rows.innerHTML = '';
    rowCounter = 0;
    addDebtRow();
    addDebtRow();
    extraInput.value = '0';
    error.textContent = '';
    clearResults();
    updateSummaryPreview();
  };

  const readDebts = (strict = true) => {
    const debts = [];
    let problem = '';
    [...rows.querySelectorAll('[data-debt-row]')].forEach((row, index) => {
      const nameInput = row.querySelector('input[type="text"]');
      const balanceInput = row.querySelector('[data-debt-balance]');
      const aprInput = row.querySelector('[data-debt-apr]');
      const minInput = row.querySelector('[data-debt-min]');
      const rawBalance = balanceInput.value.trim();
      const rawApr = aprInput.value.trim();
      const rawMin = minInput.value.trim();

      if (!rawBalance && !rawApr && !rawMin && !nameInput.value.trim()) return;

      const balance = Number(rawBalance);
      const apr = Number(rawApr);
      const minimum = Number(rawMin);
      const name = nameInput.value.trim() || ('Debt ' + (index + 1));

      if (!Number.isFinite(balance) || balance <= 0) problem = problem || (name + ': enter a balance above €0.');
      if (!Number.isFinite(apr) || apr < 0 || apr > 100) problem = problem || (name + ': enter an APR between 0% and 100%.');
      if (!Number.isFinite(minimum) || minimum <= 0) problem = problem || (name + ': enter a monthly payment above €0.');

      if (!problem || !strict) {
        if (Number.isFinite(balance) && balance > 0 && Number.isFinite(apr) && apr >= 0 && Number.isFinite(minimum) && minimum > 0) {
          debts.push({name, balance, apr, minimum});
        }
      }
    });
    return {debts, problem};
  };

  const readExtra = () => {
    const value = Number(extraInput.value);
    return Number.isFinite(value) && value >= 0 ? value : NaN;
  };

  const scenarioUrl = debts => {
    const url = new URL(window.location.href);
    url.search = ''; url.hash = '';
    const payload={extra:readExtra(),debts:debts.map(d=>({name:d.name,balance:d.balance,apr:d.apr,minimum:d.minimum}))};
    const bytes=new TextEncoder().encode(JSON.stringify(payload));
    let binary=''; bytes.forEach(byte=>binary+=String.fromCharCode(byte));
    const encoded=btoa(binary).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
    url.hash='scenario='+encoded;
    return url.toString();
  };

  const copyText = async value => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
        return true;
      }
    } catch (e) {}
    const ta=document.createElement('textarea');
    ta.value=value; ta.setAttribute('readonly','');
    ta.style.position='absolute'; ta.style.left='-9999px';
    document.body.appendChild(ta); ta.select();
    let copied=false;
    try { copied=document.execCommand('copy'); } catch (e) {}
    ta.remove();
    return copied;
  };

  const loadSharedScenario = () => {
    if(!window.location.hash.startsWith('#scenario=')) return false;
    try {
      let raw=window.location.hash.slice(10).replace(/-/g,'+').replace(/_/g,'/');
      while(raw.length%4) raw+='=';
      const bytes=Uint8Array.from(atob(raw),ch=>ch.charCodeAt(0));
      const payload=JSON.parse(new TextDecoder().decode(bytes));
      const parsed=payload.debts;
      if(!Array.isArray(parsed) || !parsed.length) return false;
      rows.innerHTML=''; rowCounter=0;
      parsed.slice(0,maxDebts).forEach(item=>{
        const debt={
          name:String(item.name||'').slice(0,42),
          balance:Number(item.balance),
          apr:Number(item.apr),
          minimum:Number(item.minimum)
        };
        if(Number.isFinite(debt.balance)&&debt.balance>0&&Number.isFinite(debt.apr)&&debt.apr>=0&&Number.isFinite(debt.minimum)&&debt.minimum>0) addDebtRow(debt);
      });
      if(!rows.children.length) return false;
      const extra=Number(payload.extra);
      extraInput.value=Number.isFinite(extra)&&extra>=0?String(extra):'0';
      updateSummaryPreview();
      runComparison();
      return true;
    } catch(e) {
      return false;
    }
  };

  const updateSummaryPreview = () => {
    const {debts} = readDebts(false);
    const extra = readExtra();
    const totalBalance = debts.reduce((sum, d) => sum + d.balance, 0);
    const minimums = debts.reduce((sum, d) => sum + d.minimum, 0);
    const safeExtra = Number.isFinite(extra) ? extra : 0;
    setText('[data-summary="balance"]', money(totalBalance));
    setText('[data-summary="minimums"]', money(minimums));
    setText('[data-summary="extra"]', money(safeExtra));
    setText('[data-summary="budget"]', money(minimums + safeExtra));

    const weak = debts.filter(d => d.minimum <= d.balance * (d.apr / 100 / 12) + 0.005);
    const warning = root.querySelector('[data-interest-warning]');
    if (weak.length) {
      warning.hidden = false;
      warning.textContent = weak.length === 1
        ? 'One entered monthly payment is no higher than that debt\'s first-month interest. Its balance may grow while another debt is being targeted.'
        : weak.length + ' entered monthly payments are no higher than first-month interest on those debts. Some balances may grow while another debt is being targeted.';
    } else {
      warning.hidden = true;
      warning.textContent = '';
    }
  };


  const setText = (selector, text) => {
    const el = root.querySelector(selector);
    if (el) el.textContent = text;
  };

  const setStrategy = (prefix, result) => {
    const data = prefix === 'avalanche' ? 'data-avalanche' : 'data-snowball';
    root.querySelectorAll('[' + data + ']').forEach(el => {
      const key = el.getAttribute(data);
      if (key === 'duration') el.textContent = result.success ? duration(result.months) : 'Not cleared';
      if (key === 'date') el.textContent = result.success ? ('Estimated ' + payoffDate(result.months)) : 'Review the payment assumptions';
      if (key === 'interest') el.textContent = result.success ? money(result.interest) : '—';
      if (key === 'paid') el.textContent = result.success ? money(result.paid) : '—';
      if (key === 'first') el.textContent = result.first ? result.first.name : '—';
      if (key === 'first_time') el.textContent = result.first ? ('after ' + duration(result.first.month)) : 'No debt cleared in model';
    });

    const list = root.querySelector('[' + (prefix === 'avalanche' ? 'data-avalanche-order' : 'data-snowball-order') + ']');
    if (list) {
      list.innerHTML = '';
      result.payoffOrder.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.name;
        li.title = 'Cleared after ' + duration(item.month);
        list.appendChild(li);
      });
      if (!result.payoffOrder.length) {
        const li = document.createElement('li');
        li.textContent = 'No payoff reached';
        list.appendChild(li);
      }
    }
  };

  const clearResults = () => {
    ['avalanche','snowball'].forEach(prefix => {
      const data = prefix === 'avalanche' ? 'data-avalanche' : 'data-snowball';
      root.querySelectorAll('[' + data + ']').forEach(el => el.textContent = '—');
      const list = root.querySelector('[' + (prefix === 'avalanche' ? 'data-avalanche-order' : 'data-snowball-order') + ']');
      if (list) list.innerHTML = '';
    });
    const callout = root.querySelector('[data-comparison-callout]');
    if (callout) callout.textContent = 'Enter your debts above to compare the two strategies.';
    chartPanel.hidden = true;
    chartCanvas.innerHTML = '';
  };

  const renderCallout = (a, s) => {
    const el = root.querySelector('[data-comparison-callout]');
    if (!el) return;
    if (!a.success || !s.success) {
      el.textContent = 'At least one strategy does not clear all balances within the 100-year modelling limit. Check whether the monthly payments are high enough relative to the balances and APRs entered.';
      return;
    }

    const interestDiff = s.interest - a.interest;
    const monthDiff = s.months - a.months;
    const firstDiff = (s.first && a.first) ? a.first.month - s.first.month : 0;
    let text = '';

    if (Math.abs(interestDiff) < 0.5) {
      text = 'Under these assumptions, the two strategies produce almost the same total interest.';
    } else if (interestDiff > 0) {
      text = 'Under these assumptions, avalanche costs ' + money(interestDiff) + ' less in interest than snowball.';
    } else {
      text = 'Under these assumptions, snowball happens to cost ' + money(Math.abs(interestDiff)) + ' less in interest in this specific model.';
    }

    if (monthDiff > 0) text += ' Avalanche also finishes ' + duration(monthDiff) + ' sooner.';
    else if (monthDiff < 0) text += ' Snowball finishes ' + duration(Math.abs(monthDiff)) + ' sooner.';
    else text += ' Both finish in the same month.';

    if (firstDiff > 0) text += ' Snowball delivers the first cleared debt ' + duration(firstDiff) + ' earlier.';
    else if (firstDiff < 0) text += ' Avalanche delivers the first cleared debt ' + duration(Math.abs(firstDiff)) + ' earlier.';

    el.textContent = text;
  };

  const renderChart = (avalanche, snowball) => {
    if (!avalanche.schedule.length || !snowball.schedule.length) {
      chartPanel.hidden = true;
      return;
    }
    const maxMonths = Math.max(avalanche.schedule.length, snowball.schedule.length) - 1;
    const maxValue = Math.max(avalanche.schedule[0] || 0, snowball.schedule[0] || 0, 1);
    const W = 820, H = 330, L = 70, R = 24, T = 20, B = 54;
    const plotW = W - L - R, plotH = H - T - B;
    const x = m => L + (maxMonths ? (m / maxMonths) * plotW : 0);
    const y = v => T + (1 - Math.max(0, Math.min(maxValue, v)) / maxValue) * plotH;

    const valueAt = (arr, i) => i < arr.length ? arr[i] : 0;
    const step = Math.max(1, Math.ceil(maxMonths / 180));
    const points = arr => {
      const out = [];
      for (let i=0; i<=maxMonths; i+=step) out.push(x(i).toFixed(1) + ',' + y(valueAt(arr,i)).toFixed(1));
      if (maxMonths % step !== 0) out.push(x(maxMonths).toFixed(1) + ',' + y(valueAt(arr,maxMonths)).toFixed(1));
      return out.join(' ');
    };

    let svg = '<svg class="debt-chart-svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Total debt balance over time for avalanche and snowball strategies">';
    for (let i=0;i<=4;i++) {
      const value = maxValue * (1 - i/4);
      const yy = T + plotH * i/4;
      svg += '<line class="debt-chart-grid" x1="' + L + '" x2="' + (W-R) + '" y1="' + yy + '" y2="' + yy + '"/>';
      svg += '<text class="debt-chart-axis" x="' + (L-9) + '" y="' + (yy+4) + '" text-anchor="end">€' + new Intl.NumberFormat('en-IE',{notation:'compact',maximumFractionDigits:1}).format(value) + '</text>';
    }
    const ticks = [0, Math.round(maxMonths*.25), Math.round(maxMonths*.5), Math.round(maxMonths*.75), maxMonths].filter((v,i,a) => a.indexOf(v) === i);
    ticks.forEach(m => {
      const label = m === 0 ? 'Start' : (m < 24 ? m + ' mo' : (m/12).toFixed(m%12===0?0:1) + ' yr');
      svg += '<text class="debt-chart-axis" x="' + x(m).toFixed(1) + '" y="' + (H-18) + '" text-anchor="middle">' + label + '</text>';
    });
    svg += '<polyline class="debt-chart-a" points="' + points(avalanche.schedule) + '"/>';
    svg += '<polyline class="debt-chart-s" points="' + points(snowball.schedule) + '"/>';
    svg += '</svg>';

    chartCanvas.innerHTML = svg;
    chartPanel.hidden = false;
  };

  const runComparison = () => {
    const {debts, problem} = readDebts(true);
    const extra = readExtra();

    if (problem) {
      error.textContent = problem;
      return;
    }
    if (!debts.length) {
      error.textContent = 'Add at least one debt with a balance, APR and monthly payment.';
      return;
    }
    if (!Number.isFinite(extra) || extra < 0) {
      error.textContent = 'Enter an extra monthly payment of €0 or more.';
      return;
    }

    error.textContent = '';
    updateSummaryPreview();

    const avalanche = simulate(debts, extra, 'avalanche');
    const snowball = simulate(debts, extra, 'snowball');
    setStrategy('avalanche', avalanche);
    setStrategy('snowball', snowball);
    renderCallout(avalanche, snowball);
    renderChart(avalanche, snowball);

    if (window.gtag) window.gtag('event','tool_calculate',{tool_name:'debt-repayment-calculator'});
  };

  form.addEventListener('submit', e => {
    e.preventDefault();
    runComparison();
  });
  extraInput.addEventListener('input', scheduleComparison);
  addButton.addEventListener('click', () => addDebtRow());
  clearButton.addEventListener('click', clearExample);
  resetButton.addEventListener('click', loadExample);

  const shareButton=root.querySelector('[data-debt-share]');
  const copyResultsButton=root.querySelector('[data-debt-copy-results]');
  const printButton=root.querySelector('[data-debt-print]');
  const actionStatus=root.querySelector('[data-debt-action-status]');
  if(shareButton) shareButton.addEventListener('click', async()=>{
    const {debts,problem}=readDebts(true);
    if(problem||!debts.length){if(actionStatus)actionStatus.textContent='Complete the debt table before sharing.';return;}
    const copied=await copyText(scenarioUrl(debts));
    if(actionStatus) actionStatus.textContent=copied?'Scenario link copied.':'Copy the current page URL to share this scenario.';
    if(window.gtag) window.gtag('event','tool_share',{tool_name:'debt-repayment-calculator'});
  });
  if(copyResultsButton) copyResultsButton.addEventListener('click',async()=>{
    const lines=['Debt Snowball vs Avalanche Calculator Ireland'];
    const pull=(selector,label)=>{const value=root.querySelector(selector)?.textContent?.trim();if(value&&value!=='—')lines.push(label+': '+value);};
    pull('[data-summary="balance"]','Total debt');
    pull('[data-summary="budget"]','Monthly debt budget');
    pull('[data-avalanche="duration"]','Avalanche payoff time');
    pull('[data-avalanche="interest"]','Avalanche interest');
    pull('[data-snowball="duration"]','Snowball payoff time');
    pull('[data-snowball="interest"]','Snowball interest');
    const copied=await copyText(lines.join('\n'));
    if(actionStatus) actionStatus.textContent=copied?'Results copied.':'Could not copy automatically.';
    if(window.gtag) window.gtag('event','tool_copy_results',{tool_name:'debt-repayment-calculator'});
  });
  if(printButton) printButton.addEventListener('click',()=>window.print());

  if(!loadSharedScenario()) loadExample();
})();
