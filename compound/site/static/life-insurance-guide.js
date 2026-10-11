/* Life-cover funding-gap model. No personal inputs leave this browser. */
(function(){
"use strict";
var root=document.getElementById("li26-calc");
if(!root)return;
var ids=["monthly","years","debt","family","savings","employer","existing"];
var el={};ids.forEach(function(id){el[id]=root.querySelector("#li26-"+id)});
var out={
needed:root.querySelector("#li26-needed"),gross:root.querySelector("#li26-gross"),
annual:root.querySelector("#li26-annual"),support:root.querySelector("#li26-support"),
debts:root.querySelector("#li26-debts"),resources:root.querySelector("#li26-resources"),
barGross:root.querySelector("#li26-gross-bar"),barResources:root.querySelector("#li26-resources-bar"),
note:root.querySelector("#li26-note")};
var euro=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
function val(id,max){var v=Number(el[id].value);return Number.isFinite(v)?Math.min(max,Math.max(0,v)):0;}
function run(){
 var monthly=val("monthly",100000),years=val("years",70),debt=val("debt",10000000),
 family=val("family",10000000),savings=val("savings",10000000),
 employer=val("employer",10000000),existing=val("existing",10000000);
 var income=monthly*12*years, gross=income+debt+family,res=savings+employer+existing;
 var gap=Math.max(0,gross-res);
 out.needed.textContent=euro.format(Math.round(gap));
 out.gross.textContent=euro.format(Math.round(gross));
 out.annual.textContent=euro.format(Math.round(monthly*12));
 out.support.textContent=euro.format(Math.round(income));
 out.debts.textContent=euro.format(Math.round(debt+family));
 out.resources.textContent=euro.format(Math.round(res));
 var scale=Math.max(1,gross,res);
 out.barGross.style.width=(gross/scale*100).toFixed(2)+"%";
 out.barResources.style.width=(res/scale*100).toFixed(2)+"%";
 out.note.textContent=gap>0?"Illustrative additional cover to investigate with a regulated adviser.":"On these simplified assumptions, available resources meet the stated funding target; review whether they are genuinely accessible to beneficiaries.";
}
ids.forEach(function(id){el[id].addEventListener("input",run);el[id].addEventListener("change",run)});
run();
})();