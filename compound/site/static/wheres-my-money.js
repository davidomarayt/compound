(function () {
  'use strict';
  var moneyFmt = new Intl.NumberFormat('en-IE', {style:'currency', currency:'EUR', maximumFractionDigits:0});
  var money = function (value) { return moneyFmt.format(Number.isFinite(value) ? value : 0); };
  var clamp = function (v) { return Math.max(0, Number.isFinite(v) ? v : 0); };

  function incomeTax2026(taxable, band, credits) {
    var x = clamp(taxable);
    var gross = Math.min(x, band) * .20 + Math.max(0, x - band) * .40;
    return Math.max(0, gross - clamp(credits));
  }
  function usc2026(salary) {
    var x = clamp(salary);
    if (x <= 13000) return 0;
    return Math.min(x,12012)*.005
      + Math.min(Math.max(x-12012,0),16688)*.02
      + Math.min(Math.max(x-28700,0),41344)*.03
      + Math.max(x-70044,0)*.08;
  }
  function prsi2026(salary) {
    var weekly = clamp(salary)/52;
    if (weekly <= 352) return 0;
    var credit = (weekly > 352 && weekly <= 424)
      ? Math.max(0,12-(weekly-352.01)/6) : 0;
    return Math.max(0,weekly*.042-credit)*39 + Math.max(0,weekly*.0435-credit)*13;
  }
  function calcHousehold(values) {
    var status = values.status === 'joint_one' || values.status === 'joint_two' ? values.status : 'single';
    var salary = clamp(values.salary);
    var second = status === 'joint_two' ? clamp(values.second) : 0;
    var p1 = Math.min(salary, clamp(values.pension));
    var p2 = status === 'joint_two' ? Math.min(second, clamp(values.pensionSecond)) : 0;
    var gross = salary + second;
    var pension = p1 + p2;
    var band = status === 'single' ? 44000 : 53000 + (status === 'joint_two' ? Math.min(35000, salary, second) : 0);
    var personalCredits = status === 'single' ? 2000 : 4000;
    var payeCredits = Math.min(2000,salary*.20) + (status === 'joint_two' ? Math.min(2000,second*.20) : 0);
    var tax = incomeTax2026(gross-pension, band, personalCredits+payeCredits);
    var usc = usc2026(salary) + usc2026(second);
    var prsi = prsi2026(salary) + prsi2026(second);
    var payroll = tax + usc + prsi;
    var vat = clamp(values.vatSpend)*12*(23/123);
    return {gross:gross, tax:tax, usc:usc, prsi:prsi, payroll:payroll,
      net:gross-payroll-pension, pension:pension, vat:vat, band:band,
      rate:gross>0?payroll/gross:0};
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {incomeTax2026:incomeTax2026,usc2026:usc2026,prsi2026:prsi2026,calcHousehold:calcHousehold};
  }
  if (typeof document === 'undefined') return;
  var app = document.querySelector('[data-wmm]');
  if (!app) return;

  var data;
  try { data = JSON.parse(document.getElementById('wmm-spending-data').textContent); }
  catch (error) { return; }
  if (!data || !Array.isArray(data.categories) || !data.categories.length) return;
  var sectorSum = data.categories.reduce(function (sum,c) { return sum + c.billion; }, 0);
  if (Math.abs(sectorSum-data.total_billion) > .051) {
    var notice = document.getElementById('wmm-spending-list');
    notice.textContent = 'Public spending totals cannot be reconciled. Please check the official source.';
    return;
  }
  var q = function (selector) { return app.querySelector(selector); };
  var status = q('#wmm-status'), salary = q('#wmm-salary'), second = q('#wmm-second');
  var pension = q('#wmm-pension'), pensionSecond = q('#wmm-pension-second'), vatSpend = q('#wmm-vat-spend');
  var error = q('#wmm-error');
  var result = null;
  var activeSector = 'health';
  function values() {
    return {status:status.value,salary:Number(salary.value),second:Number(second.value),
      pension:Number(pension.value),pensionSecond:Number(pensionSecond.value),vatSpend:Number(vatSpend.value)};
  }
  function validate(v) {
    var fields = [salary,pension,vatSpend];
    if (v.status === 'joint_two') fields.push(second,pensionSecond);
    for (var i=0;i<fields.length;i++) {
      if (!fields[i].value.trim() || !Number.isFinite(Number(fields[i].value))
          || Number(fields[i].value) < 0 || Number(fields[i].value) > 10000000) {
        return 'Enter a valid non-negative number in every visible field.';
      }
    }
    if (v.pension > v.salary || (v.status === 'joint_two' && v.pensionSecond > v.second)) {
      return 'Pension contributions cannot exceed the corresponding salary.';
    }
    return '';
  }
  function showText(selector,text) { q(selector).textContent = text; }
  function renderReceipt() {
    var v = values(), issue = validate(v);
    error.hidden = !issue;
    error.textContent = issue;
    if (issue) return;
    result = calcHousehold(v);
    showText('#wmm-total',money(result.payroll));
    showText('#wmm-percent',(result.rate*100).toFixed(1)+'% of gross pay');
    showText('#wmm-net',money(result.net)+' take-home');
    q('#wmm-meter-fill').style.width = Math.max(0,Math.min(100,result.rate*100))+'%';
    showText('#wmm-income-tax',money(result.tax));
    showText('#wmm-usc',money(result.usc));
    showText('#wmm-prsi',money(result.prsi));
    q('[data-wmm-pension-row]').hidden = !(result.pension>0);
    showText('#wmm-pension-total',money(result.pension));
    q('[data-wmm-vat-row]').hidden = !(result.vat>0);
    showText('#wmm-vat',money(result.vat));
    drawSectors();
    drawWhatIf();
  }
  function drawSectors() {
    if (!result) return;
    var list = q('#wmm-spending-list');
    list.replaceChildren();
    data.categories.forEach(function (category) {
      var share = category.billion/data.total_billion;
      var button = document.createElement('button');
      button.type='button';
      button.className='wmm-spend-row'+(activeSector===category.id?' is-current':'');
      button.setAttribute('aria-pressed',String(activeSector===category.id));
      var head=document.createElement('span'); head.className='wmm-spend-row-head';
      var name=document.createElement('strong'); name.textContent=category.name;
      var amount=document.createElement('strong'); amount.textContent=money(result.payroll*share);
      head.append(name,amount);
      var bar=document.createElement('span');bar.className='wmm-spend-row-track';
      var fill=document.createElement('span'); fill.style.width=(100*share)+'%'; bar.append(fill);
      var foot=document.createElement('span'); foot.className='wmm-spend-row-foot';
      foot.textContent='€'+category.billion.toFixed(1)+'bn national · '+(share*100).toFixed(1)+'% of expenditure';
      button.append(head,bar,foot);
      button.addEventListener('click',function(){activeSector=category.id;drawSectors();drawSectorDetail();});
      list.append(button);
    });
    drawSectorDetail();
  }
  function drawSectorDetail() {
    var c = data.categories.find(function (item) { return item.id===activeSector; }) || data.categories[0];
    showText('#wmm-sector-name',c.name);
    showText('#wmm-sector-national','€'+c.billion.toFixed(1)+'bn');
    showText('#wmm-sector-personal',result ? money(result.payroll*c.billion/data.total_billion) : '—');
    showText('#wmm-sector-summary',c.summary);
    var themes=q('#wmm-sector-themes'); themes.replaceChildren();
    c.themes.forEach(function (item) {var li=document.createElement('li');li.textContent=item;themes.append(li);});
    q('#wmm-sector-source').href=c.source;
  }
  function drawWhatIf() {
    if (!result) return;
    var raise=Number(q('#wmm-raise').value);
    showText('#wmm-raise-label',money(raise));
    var v=values();v.salary+=raise;
    var projected=calcHousehold(v);
    showText('#wmm-extra-net',money(projected.net-result.net));
    showText('#wmm-extra-tax',money(projected.payroll-result.payroll));
    showText('#wmm-extra-month',money((projected.net-result.net)/12));
  }
  function initBudget() {
    var from=q('#wmm-from'),to=q('#wmm-to');
    data.categories.forEach(function (c) {
      [from,to].forEach(function (node) {
        var option=document.createElement('option');option.value=c.id;option.textContent=c.name;node.append(option);
      });
    });
    from.value='debt';to.value='health';
    function render() {
      var source=data.categories.find(function(c){return c.id===from.value;});
      var target=data.categories.find(function(c){return c.id===to.value;});
      var transfer=Number(q('#wmm-transfer').value);
      var issue = !Number.isFinite(transfer)||transfer<=0||transfer>source.billion
        ? 'Choose a positive transfer no greater than the source sector budget.'
        : source.id===target.id ? 'Choose two different sectors.' : '';
      q('#wmm-budget-error').hidden=!issue;
      q('#wmm-budget-error').textContent=issue;
      var output=q('#wmm-budget-result');output.replaceChildren();
      if(issue)return;
      [[source,-transfer],[target,transfer]].forEach(function (item){
        var row=document.createElement('div');row.className='wmm-budget-row';
        var title=document.createElement('span');title.textContent=item[0].name;
        var value=document.createElement('strong');value.textContent='€'+(item[0].billion+item[1]).toFixed(1)+'bn';
        var change=document.createElement('small'); change.textContent=(item[1]>0?'+':'−')+'€'+Math.abs(item[1]).toFixed(1)+'bn from published estimate';
        row.append(title,value,change);output.append(row);
      });
      var total=document.createElement('p');
      total.className='wmm-budget-total';
      total.textContent='Total government spending remains €'+data.total_billion.toFixed(1)+'bn. This models allocation only.';
      output.append(total);
    }
    [from,to,q('#wmm-transfer')].forEach(function(input){input.addEventListener('input',render);});
    render();
  }
  function initReliefs() {
    var reliefs = {
      health:{name:'Health expenses',info:'Check what qualifies, receipts and whether expenses were reimbursed.',url:'https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/health-and-age/health-expenses/how-do-you-claim-health-expenses.aspx'},
      rent:{name:'Rent Tax Credit',info:'Check the 2026 credit, eligible tenancies and whether you have already claimed.',url:'https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx?year=2026'},
      remote:{name:'Remote Working Relief',info:'Check eligible working days, utility bills and employer contributions.',url:'https://www.revenue.ie/en/jobs-and-pensions/eworking/calculate-allowable-remote-working-costs.aspx'},
      pension:{name:'Pension contribution relief',info:'Check eligibility, age-related contribution limits and payroll relief already received.',url:'https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx?year=2026'}
    };
    var boxes=Array.from(app.querySelectorAll('[data-wmm-relief]'));
    function render() {
      var parent=q('#wmm-relief-results'); parent.replaceChildren();
      var checked=boxes.filter(function(input){return input.checked;});
      if(!checked.length){var p=document.createElement('p');p.textContent='Select an item to see the relevant official information.';parent.append(p);return;}
      checked.forEach(function(input){
        var item=reliefs[input.dataset.wmmRelief];
        var article=document.createElement('article'); article.className='wmm-relief-item';
        var head=document.createElement('strong');head.textContent=item.name;
        var p=document.createElement('p');p.textContent=item.info;
        var link=document.createElement('a');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='Read Revenue guidance ↗';
        article.append(head,p,link);parent.append(article);
      });
    }
    boxes.forEach(function(input){input.addEventListener('change',render);});render();
  }
  q('#wmm-tax-form').addEventListener('submit',function(e){e.preventDefault();});
  status.addEventListener('change',function(){
    app.querySelectorAll('[data-wmm-second]').forEach(function(el){el.hidden=status.value!=='joint_two';});
    renderReceipt();
  });
  [salary,second,pension,pensionSecond,vatSpend].forEach(function(input){input.addEventListener('input',renderReceipt);});
  q('#wmm-raise').addEventListener('input',drawWhatIf);
  q('#wmm-share').addEventListener('click',function() {
    if (!result) return;
    var text='Where\'s My Money? My illustrative 2026 Irish payroll taxes and PRSI: '+money(result.payroll)+
      ' on '+money(result.gross)+' gross PAYE pay. This is an estimate, not money traced to services. https://compound.ie/wheres-my-money/';
    var feedback=q('#wmm-share-status');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function(){feedback.textContent='Anonymous receipt copied.';})
        .catch(function(){feedback.textContent='Unable to copy on this device.';});
    } else { feedback.textContent='Copying is unavailable in this browser.'; }
  });
  initBudget();initReliefs();renderReceipt();
})();
