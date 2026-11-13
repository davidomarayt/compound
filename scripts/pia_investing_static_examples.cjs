"use strict";
// Regenerate static, source-checkable examples from the same exact browser engine.
const {estimate}=require("../compound/site/static/pia-investing.js");
const currency=new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
const common=Object.freeze({monthly:500,years:30,annual_return:6,pia_fee:.25,etf_fee:.25,shares_fee:.25,etf_exit_rate:35,cgt_exemption:1270,dividend_yield:0,dividend_tax:40});
function table(){
  const r=estimate(common);
  const lines=[
    "| Holding period | Contributed to each | PIA after account charge | Outside accumulating ETF after sale tax | Direct shares after CGT |",
    "| --- | ---: | ---: | ---: | ---: |"
  ];
  for(const year of [5,10,20,30]){
    const point=r.rows.find(x=>x.year===year);
    lines.push("| "+year+" years | "+currency.format(common.monthly*12*year)+" | "+
      currency.format(point.pia)+" | "+currency.format(point.etf)+" | "+currency.format(point.shares)+" |");
  }
  return lines.join("\n");
}
if(require.main===module)process.stdout.write(table()+"\n");
module.exports={table,common};