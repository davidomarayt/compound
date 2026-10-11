/*
  Small dependency-free DOM simulation for the income interruption widget.
  Used by GitHub Actions after deployment and can be run locally with Node.
*/
"use strict";
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");

const script = fs.readFileSync(process.argv[2] || "/tmp/insurance-hub.js", "utf8");
const values = {spending:"3200",other:"1200",months:"12",sick:"2",savings:"6500"};
const listeners = {};
const fields = Object.fromEntries(Object.entries(values).map(([id,val]) => [id, {
  value:val,
  addEventListener(event,cb){listeners[id+":"+event]=cb;}
}]));
const out={};
for (const key of ["gap","monthly","months","gross","savings"]) out[key]={textContent:""};
const meter={style:{width:""}};
const summary={textContent:""};
const root={
  querySelector(selector){
    const field=selector.match(/^\[data-ins-field="(.+)"\]$/);
    if(field)return fields[field[1]];
    const result=selector.match(/^\[data-ins-result=(.+)\]$/);
    if(result)return out[result[1]];
    if(selector==="[data-ins-meter]")return meter;
    if(selector==="[data-ins-summary]")return summary;
    throw new Error("Unexpected selector "+selector);
  }
};
const document={querySelector(s){assert.equal(s,"[data-ins-gap]");return root;}};
vm.runInNewContext(script,{document,Intl,Number,Math}, {filename:"insurance-hub.js",timeout:1000});
assert.equal(out.gap.textContent,"€13,500","default gap");
assert.equal(out.monthly.textContent,"€2,000","monthly gap");
assert.equal(out.gross.textContent,"€20,000","gross gap");
assert.equal(out.months.textContent,"10","employer paid months");
assert.equal(meter.style.width,"32.5%","savings meter");

function set(id,value){ fields[id].value=String(value);listeners[id+":input"](); }
set("savings",50000);
assert.equal(out.gap.textContent,"€0","savings greater than gross need");
set("savings",0);
set("sick",24);
assert.equal(out.gap.textContent,"€0","sick pay months capped by interruption duration");
set("sick",0);
assert.equal(out.gap.textContent,"€24,000","12 uncovered months");
set("spending",1000);
assert.equal(out.gap.textContent,"€0","continuing income exceeding spending");
set("spending",-500);
assert.equal(out.gap.textContent,"€0","negative input clamped to zero");
console.log("Insurance income-gap calculator: 7 behavioural checks passed");
