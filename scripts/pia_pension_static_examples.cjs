"use strict";
/* Canonical static examples for /pia/vs-pension/ are derived from the exact browser calculator. */
const {calculate}=require("../compound/site/static/pia-pension.js");
const fmt=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
const eur=x=>fmt.format(x);
const assumptions=Object.freeze({
  years:30,current_age:35,relief_headroom:23000,return_rate:6,
  pia_fee:0.25,pension_fee:0.75,tax_free_lump_pct:25,
  tax_free_cap:200000,retirement_tax_rate:20
});
function renderTable(){
  const lines=[
    "| Take-home budget | Pension relief | Extra employer contribution | PIA after PIA charge | Pension before retirement tax | Pension after illustrative retirement deductions |",
    "| --- | ---: | ---: | ---: | ---: | ---: |"
  ];
  for(const budget of [250,500,1000]){
    for(const relief of [20,40]){
      for(const employer of [0,100]){
        const r=calculate({...assumptions,monthly_net:budget,relief_rate:relief,extra_employer:employer});
        lines.push("| "+eur(budget)+"/month | "+relief+"% | "+eur(employer)+"/month | "+
          eur(r.pia)+" | "+eur(r.pension)+" | "+eur(r.illustrativeNetPension)+" |");
      }
    }
  }
  return lines.join("\n");
}
if(require.main===module)process.stdout.write(renderTable()+"\n");
module.exports={renderTable,assumptions};
