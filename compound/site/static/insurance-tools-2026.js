/* Compound Ireland Insurance calculators: offline, no storage, no tracking.
   All figures are scenario arithmetic, not quotes or regulated recommendations. */
(function(){
"use strict";
var nfmt=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
function money(n){return nfmt.format(Math.round(n));}
function safe(n){return Number.isFinite(n)?Math.max(0,Math.min(1e12,n)):0;}
function read(root,id){var el=root.querySelector('[data-i-field="'+id+'"]');if(!el)return 0;var n=Number(el.value);return safe(n);}
function calculate(kind,x){
 var z={};
 if(kind==="health"){
   var out=safe(x.outpatient),visits=Math.min(20,x.visits);
   function plan(p,e,reimb,shortfall){
     var reimbursement=Math.min(out,safe(reimb));
     var hospital=visits*(e+shortfall);
     return {total:safe(p)+hospital+Math.max(0,out-reimbursement),hospital:hospital,reimbursement:reimbursement};
   }
   var a=plan(x.ap,x.ae,x.ar,x.as),b=plan(x.bp,x.be,x.br,x.bs);
   z.a=a.total;z.b=b.total;z.diff=Math.abs(a.total-b.total);z.winner=a.total<b.total?"Plan A":b.total<a.total?"Plan B":"Equal estimated cost";
   z.acost=a.hospital;z.bcost=b.hospital;
   z.text="Includes annual premiums, estimated inpatient excesses and shortfalls, and outpatient costs after the reimbursements you entered.";
 }else if(kind==="home"){
   var base=x.area*x.rate, extras=base*Math.min(200,x.extras)/100;
   var total=base+extras+x.demolition+x.outbuildings;
   z.total=total;z.base=base;z.extras=extras;z.gap=Math.max(0,total-x.current);
   z.percent=total>0?x.current/total*100:0;
   z.text=x.rate===0?"Enter a current €/m² rebuilding rate from SCSI or a professional assessment; zero is not a usable insured-value estimate.":x.current>=total?"Current cover meets this simplified scenario; policy terms and any professional valuation still matter.":"Illustrative rebuilding-cover gap, not a confirmed underinsurance finding.";
 }else if(kind==="critical"){
   var gross=x.once+(x.monthly*Math.min(120,x.months))+x.care+x.debt;
   var resources=x.savings+x.existing;
   z.gross=gross;z.resources=resources;z.gap=Math.max(0,gross-resources);
   z.monthly=x.monthly*Math.min(120,x.months);z.text="This is a financial contingency target. A serious illness policy pays only for a qualifying insured diagnosis under its precise terms.";
 }else if(kind==="death"){
   var dis=x.salary*Math.min(20,x.multiple);
   var family=x.monthly*12*Math.min(70,x.years)+x.debt+x.oneoff;
   var existing=dis+x.savings+x.other;
   z.dis=dis;z.target=family;z.existing=existing;z.gap=Math.max(0,family-existing);
   z.text="Only count confirmed employer benefits payable to your intended beneficiaries. Coverage may end when employment ends.";
 }else if(kind==="savings"){
   var cur=x.homecur+x.healthcur+x.carcur+x.lifecur;
   var next=x.homenew+x.healthnew+x.carnew+x.lifenew;
   var annual=cur-next,years=Math.min(50,x.years);
   z.current=cur;z.new=next;z.annual=annual;
   z.horizon=annual*years-x.fees;
   z.breakEven=annual>0?x.fees/annual:0;
   z.text=annual>=0?"Potential nominal premium saving before accounting for any reduction in policy benefits.":"The replacement premiums entered are higher than the existing premiums.";
 }
 return z;
}
window.CompoundInsuranceMath={calculate:calculate}; // no user values are stored or sent
document.querySelectorAll("[data-i-calculator]").forEach(function(root){
 var kind=root.getAttribute("data-i-calculator");
 var fields=Array.from(root.querySelectorAll("[data-i-field]"));
 var outputs=Array.from(root.querySelectorAll("[data-i-result]"));
 var copy=root.querySelector("[data-i-copy]");
 var note=root.querySelector("[data-i-note]");
 var status=root.querySelector("[data-i-status]");
 function recalc(){
  var x={};fields.forEach(function(el){x[el.getAttribute("data-i-field")]=safe(Number(el.value));});
  var result=calculate(kind,x);
  outputs.forEach(function(el){var key=el.getAttribute("data-i-result"),val=result[key]; if(val===undefined)return;
   if(key==="winner" || key==="text"){el.textContent=String(val);}
   else if(key==="percent"){el.textContent=val.toFixed(1)+"%";}
   else if(key==="breakEven"){el.textContent=result.annual>0?val.toFixed(1)+" years":"Not applicable";}
   else el.textContent=money(val);
  });
  if(note)note.textContent=result.text||"Planning estimate only.";
  if(status)status.textContent="Updated estimate";
  if(copy)copy.dataset.text="Compound.ie "+kind+" calculation — "+fields.map(function(el){return el.name+": "+el.value;}).join("; ")+"; "+outputs.map(function(el){return el.getAttribute("data-i-result")+": "+el.textContent;}).join("; ")+". Illustrative only.";
  var bar=root.querySelector("[data-i-progress]");
  if(bar)bar.style.width=(kind==="home"?Math.min(100,result.percent):kind==="health"?(result.a+result.b?100*Math.min(result.a,result.b)/Math.max(result.a,result.b):100):result.gross?Math.min(100,result.resources/result.gross*100):0).toFixed(1)+"%";
 }
 fields.forEach(function(el){el.addEventListener("input",recalc);el.addEventListener("change",recalc);});
 var form=root.querySelector("form");
 if(form)form.addEventListener("submit",function(ev){ev.preventDefault();recalc();});
 if(copy)copy.addEventListener("click",function(){if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(copy.dataset.text||"").then(function(){copy.textContent="Copied summary";},function(){copy.textContent="Copy unavailable";});}else{copy.textContent="Copy unavailable";}});
 recalc();
});
})();