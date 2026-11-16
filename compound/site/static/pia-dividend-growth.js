/* Compound PIA dividend vs growth model. No dependencies or tracking. */
(() => {
'use strict';
const root=document.getElementById('pia-dividend-growth-calculator');
if(!root) return;
const form=document.getElementById('pdg-form'),err=document.getElementById('pdg-error');
const eur=new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
const $=id=>document.getElementById(id);
const get=name=>Number(form.elements.namedItem(name).value);
function model(a,yieldPct,whtPct){
  let balance=a.starting,contrib=a.starting,wht=0,tax=0,fees=0;
  const points=[balance];
  for(let yr=0;yr<a.years;yr++){
    let monthTotal=0;
    for(let m=0;m<12;m++){
      balance+=a.contribution/12;contrib+=a.contribution/12;
      const appreciation=balance*(a.returns-yieldPct)/1200;
      const grossDividend=balance*yieldPct/1200;
      const foreign=grossDividend*whtPct/100;
      wht+=foreign;
      balance+=appreciation+grossDividend-foreign;
      const fee=Math.max(balance,0)*a.fee/1200;
      fees+=fee;balance=Math.max(0,balance-fee);
      monthTotal+=balance;
    }
    const annualIat=Math.max(0,monthTotal/12-50000)*.01;
    tax+=annualIat;balance=Math.max(0,balance-annualIat);
    points.push(balance);
  }
  return {balance,contrib,wht,tax,fees,points};
}
function graph(div,growth){
  const el=$('pdg-chart');const d=div.points,g=growth.points;
  const width=640,height=265,left=64,right=18,top=20,bottom=45;
  const max=Math.max(100,...d,...g)*1.12,plotW=width-left-right,plotH=height-top-bottom;
  const xpos=i=>left+plotW*i/Math.max(1,d.length-1),ypos=v=>top+plotH*(1-v/max);
  const pts=arr=>arr.map((v,i)=>xpos(i).toFixed(1)+','+ypos(v).toFixed(1)).join(' ');
  const grid=[0,.25,.5,.75,1].map(k=>'<line x1="'+left+'" y1="'+ypos(max*k)+'" x2="'+(width-right)+'" y2="'+ypos(max*k)+'" stroke="#e1e8e4"/><text x="'+(left-8)+'" y="'+(ypos(max*k)+4)+'" text-anchor="end" fill="#5b7169" font-size="11">'+eur.format(max*k)+'</text>').join('');
  const ns='http://www.w3.org/2000/svg';const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 '+width+' '+height);svg.setAttribute('role','img');svg.setAttribute('aria-label','Projected balances: dividend and growth portfolios');svg.setAttribute('preserveAspectRatio','xMidYMid meet');
  // The only HTML here is fixed application markup / numeric calculated coordinates.
  svg.innerHTML=grid+'<polyline fill="none" stroke="#bf7d43" stroke-width="3.5" stroke-linejoin="round" points="'+pts(d)+'"/><polyline fill="none" stroke="#1b6757" stroke-width="3.5" stroke-linejoin="round" points="'+pts(g)+'"/><text x="'+left+'" y="'+(height-14)+'" font-size="12" fill="#47645b">Year 0</text><text x="'+(width-right)+'" y="'+(height-14)+'" font-size="12" text-anchor="end" fill="#47645b">Year '+(d.length-1)+'</text>';
  el.replaceChildren(svg);
}
function render(){
  err.hidden=true;
  const a={starting:get('starting'),contribution:get('contribution'),years:get('years'),returns:get('return'),fee:get('fee')},
  dy=get('divyield'),gy=get('growthyield'),dw=get('divwht'),gw=get('growthwht');
  const vals=[...Object.values(a),dy,gy,dw,gw];
  if(vals.some(x=>!Number.isFinite(x))||a.starting<0||a.contribution<0||a.contribution>12000||!Number.isInteger(a.years)||a.years<1||a.years>40||a.returns< -30||a.returns>30||a.fee<0||a.fee>5||dy<0||dy>20||gy<0||gy>20||dw<0||dw>100||gw<0||gw>100){err.textContent='Please enter valid assumptions. Annual contributions cannot exceed the proposed €12,000 limit.';err.hidden=false;return;}
  const div=model(a,dy,dw),growth=model(a,gy,gw),gap=growth.balance-div.balance;
  $('pdg-div-result').textContent=eur.format(div.balance);$('pdg-growth-result').textContent=eur.format(growth.balance);$('pdg-gap-result').textContent=(gap>0?'+':'')+eur.format(gap);
  [['contrib',div.contrib,growth.contrib],['wht',div.wht,growth.wht],['tax',div.tax,growth.tax],['fee',div.fees,growth.fees]].forEach(([n,d,g])=>{$('pdg-'+n+'-div').textContent=eur.format(d);$('pdg-'+n+'-growth').textContent=eur.format(g);});
  const plain= Math.abs(gap)<1?'Both portfolios finish at approximately the same value.': gap>0?'Under these assumptions, the growth portfolio finishes ahead mainly because it has less non-recoverable withholding on dividends.':'Under these assumptions, the dividend portfolio finishes ahead because its dividend withholding drag is lower.';
  $('pdg-explain').textContent=plain+' The assumed gross total return is the same for both; market performance is not forecast. Values are after modelled withholding, fees and PIA charges.';
  graph(div,growth);
}
form.addEventListener('submit',e=>{e.preventDefault();render();});
form.addEventListener('input',render);
$('pdg-reset').addEventListener('click',()=>{form.reset();render();});
render();
})();