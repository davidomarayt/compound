(function () {
'use strict';
function calculate(balance, annualRate, years, extra) {
  if (![balance, annualRate, years, extra].every(Number.isFinite) || balance < 1 || balance > 10000000 || annualRate < 0 || annualRate > 25 || years < 1 || years > 40 || !Number.isInteger(years) || extra < 0 || extra > 100000) return null;
  const n = years * 12, rate = annualRate / 1200;
  const payment = rate === 0 ? balance / n : balance * rate / -Math.expm1(-n * Math.log1p(rate));
  function schedule(monthly) {
    let outstanding = balance, interest = 0, months = 0;
    while (outstanding > 0.0000001 && months < n + 1) {
      const charge = outstanding * rate;
      const paid = Math.min(monthly, outstanding + charge);
      outstanding = Math.max(0, outstanding + charge - paid);
      interest += charge; months++;
    }
    return {months, interest};
  }
  const base = schedule(payment), over = schedule(payment + extra);
  return {payment, totalPayment:payment + extra, baseInterest:base.interest, overInterest:over.interest, saving:Math.max(0, base.interest-over.interest), months:over.months, monthsSaved:base.months-over.months};
}
if (typeof module !== 'undefined' && module.exports) module.exports = calculate;
if (typeof document === 'undefined') return;
const ids = ['mortgage-balance','mortgage-rate','mortgage-years','mortgage-extra'];
const inputs = ids.map(id=>document.getElementById(id));
if (inputs.some(el=>!el)) return;
const money = new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
const duration = m => `${Math.floor(m/12)} years${m%12 ? ` ${m%12} months` : ''}`;
function update() {
 const values=inputs.map(el=>el.value.trim()===''?NaN:Number(el.value));
 const result=calculate(...values);
 document.getElementById('mortgage-error').textContent=result?'':'Enter a balance from €1 to €10 million, a rate from 0% to 25%, whole years from 1 to 40, and an extra payment from €0 to €100,000.';
 document.getElementById('mortgage-results').hidden=!result;
 if (!result) return;
 const outputs={'mortgage-payment':money.format(result.payment),'mortgage-total':money.format(result.totalPayment),'mortgage-saving':money.format(result.saving),'mortgage-duration':duration(result.months),'mortgage-earlier':result.monthsSaved===0?'No whole months saved':duration(result.monthsSaved)+' earlier'};
 for(const [id,value] of Object.entries(outputs)) document.getElementById(id).textContent=value;
}
inputs.forEach(el=>el.addEventListener('input',update));update();
})();
