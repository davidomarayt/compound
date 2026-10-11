/* Compound Solar — offline-first research calculators; no personal data collected. */
(function(){
"use strict";
var euro=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
var nf=new Intl.NumberFormat("en-IE",{maximumFractionDigits:1});
function q(root,key,type){return root.querySelector('[data-'+type+'="'+key+'"]');}
function value(root,key,type,low,high){var e=q(root,key,type);if(!e||e.value.trim()==="")return NaN;var v=Number(e.value);return Number.isFinite(v)&&v>=low&&v<=high?v:NaN;}
function output(root,key,type,str){var e=root.querySelector('[data-'+type+'-out="'+key+'"]');if(e)e.textContent=str;}
function ok(arr){return arr.every(Number.isFinite);}
var bat=document.querySelector("[data-solar-battery]");
if(bat){
function update(){
var price=value(bat,"price","bat",0,100000),capacity=value(bat,"capacity","bat",.1,200),cycles=value(bat,"cycles","bat",0,365);
var solar=value(bat,"solar","bat",0,100000),night=value(bat,"night","bat",0,100000),eff=value(bat,"eff","bat",50,100);
var imp=value(bat,"import","bat",0,150),exp=value(bat,"export","bat",0,150),nightRate=value(bat,"night-rate","bat",0,150),maintenance=value(bat,"maintenance","bat",0,5000);
var grant=q(bat,"grant","bat").value==="600";
if(!ok([price,capacity,cycles,solar,night,eff,imp,exp,nightRate,maintenance])){
["annual","solar","night","net","payback","ten"].forEach(function(k){output(bat,k,"bat","—");});
output(bat,"note","bat","Enter complete values within the indicated ranges.");return;
}
var capacityPerYear=capacity*cycles,solarCharge=Math.min(solar,capacityPerYear),nightCharge=Math.min(night,Math.max(0,capacityPerYear-solarCharge));
var annual=solarCharge*((eff/100)*imp/100-exp/100)+nightCharge*((eff/100)*imp/100-nightRate/100)-maintenance;
var applied=grant&&capacity>=5?600:0,net=Math.max(0,price-applied);
output(bat,"annual","bat",euro.format(annual));
output(bat,"solar","bat",nf.format(solarCharge)+" kWh");
output(bat,"night","bat",nf.format(nightCharge)+" kWh");
output(bat,"net","bat",euro.format(net));
output(bat,"payback","bat",annual>0?(net===0?"Immediate":nf.format(net/annual)+" years"):"Not recovered");
output(bat,"ten","bat",euro.format(annual*10-net));
var note=annual<=0?"No positive annual cash benefit under these assumptions.":"Simplified, undiscounted cash savings; not a forecast.";
if(grant&&capacity<5)note="A battery under 5 kWh is excluded from the grant. "+note;
if(solar+night>capacityPerYear)note+=" Charge energy limited by the entered full cycles.";
output(bat,"note","bat",note);
}
bat.addEventListener("input",update);bat.addEventListener("change",update);update();
}
var ex=document.querySelector("[data-solar-export]");
if(ex){
function update(){
var used=value(ex,"used","ex",0,1000000),exported=value(ex,"exported","ex",0,1000000);
var names=["a","b"].map(function(k){return q(ex,k+"-name","ex").value.trim()||"Tariff "+k.toUpperCase();});
var vals=["a","b"].map(function(k){return [
value(ex,k+"-import","ex",0,150),value(ex,k+"-export","ex",0,150),value(ex,k+"-standing","ex",0,10),value(ex,k+"-fees","ex",-5000,5000)]});
output(ex,"a-label","ex",names[0]+" net bill");output(ex,"b-label","ex",names[1]+" net bill");
if(!ok([used,exported].concat(vals[0],vals[1]))){
["difference","a-bill","b-bill","a-credit","b-credit"].forEach(function(k){output(ex,k,"ex","—");});
output(ex,"winner","ex","Enter complete tariff rates and annual usage.");return;
}
var bills=vals.map(function(v){return used*v[0]/100+365*v[2]+v[3]-exported*v[1]/100;});
var credits=vals.map(function(v){return exported*v[1]/100;});
var gap=Math.abs(bills[0]-bills[1]);
output(ex,"difference","ex",euro.format(gap));
output(ex,"a-bill","ex",euro.format(bills[0]));output(ex,"b-bill","ex",euro.format(bills[1]));
output(ex,"a-credit","ex",euro.format(credits[0]));output(ex,"b-credit","ex",euro.format(credits[1]));
output(ex,"winner","ex",gap<.005?"Both offers are approximately equal.":(bills[0]<bills[1]?names[0]:names[1])+" has the lower annual net bill under your inputs.");
}
ex.addEventListener("input",update);ex.addEventListener("change",update);update();
}
var eq=document.querySelector("[data-solar-equipment]");
if(eq){
function update(){
var panels=value(eq,"panels","eq",1,500),watts=value(eq,"watts","eq",100,1000),inverter=value(eq,"inverter","eq",.1,200);
if(!ok([panels,watts,inverter])||!Number.isInteger(panels)){
["kwp","dc","ratio"].forEach(function(k){output(eq,k,"eq","—");});output(eq,"note","eq","Enter valid panel count, wattage and inverter output.");return;
}
var kwp=panels*watts/1000;
output(eq,"kwp","eq",nf.format(kwp)+" kWp");
output(eq,"dc","eq",panels+" × "+nf.format(watts)+" W");
output(eq,"ratio","eq",nf.format(kwp/inverter)+":1");
output(eq,"note","eq","Nameplate DC/AC sizing only; ask the installer about yield and network limits.");
}
eq.addEventListener("input",update);update();
}
})();