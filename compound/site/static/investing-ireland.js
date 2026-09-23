(()=>{
  const money=new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
  const money2=new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2});

  const route=document.querySelector('[data-investing-route]');
  if(route){
    const horizon=route.querySelector('[data-route-horizon]');
    const buffer=route.querySelector('[data-route-buffer]');
    const debt=route.querySelector('[data-route-debt]');
    const pension=route.querySelector('[data-route-pension]');
    const output=route.querySelector('[data-route-output]');
    const render=()=>{
      const items=[];
      if(!buffer.checked) items.push('Liquidity question: before choosing a market investment, decide how you would cover an unexpected bill or income interruption without having to sell at a bad time.');
      if(debt.checked) items.push('Debt question: compare the guaranteed interest saved by reducing expensive debt with the uncertain return of investing.');
      if(horizon.value==='short') items.push('Time-horizon question: money needed within roughly three years has little time to recover from a market fall, so liquidity and capital stability deserve extra weight.');
      if(horizon.value==='medium') items.push('Time-horizon question: five to seven years can still include a major market decline, so define how much loss you could tolerate before choosing an asset mix.');
      if(horizon.value==='long') items.push('Time-horizon question: a longer horizon gives more time for compounding and recovery, but it does not remove investment risk.');
      if(pension.checked) items.push('Wrapper question: compare any employer contribution, State top-up or pension tax relief with the access restrictions and later tax treatment before using a taxable account.');
      else items.push('Wrapper question: check whether you have access to a workplace pension, PRSA or MyFutureFund before assuming a taxable brokerage account is the only route.');
      output.innerHTML='<ul>'+items.slice(0,4).map(x=>'<li>'+x+'</li>').join('')+'</ul>';
    };
    route.addEventListener('change',render); render();
  }

  const tax=document.querySelector('[data-tax-explorer]');
  if(tax){
    const type=tax.querySelector('[data-tax-type]');
    const amount=tax.querySelector('[data-tax-amount]');
    const used=tax.querySelector('[data-tax-used]');
    const usedWrap=tax.querySelector('[data-tax-used-wrap]');
    const outTax=tax.querySelector('[data-tax-due]');
    const outNet=tax.querySelector('[data-tax-net]');
    const outRate=tax.querySelector('[data-tax-rate]');
    const detail=tax.querySelector('[data-tax-detail]');
    const render=()=>{
      const x=Math.max(0,Number(amount.value)||0);
      let due=0,note='';
      if(type.value==='shares'){
        usedWrap.hidden=false;
        const remaining=Math.max(0,1270-Math.max(0,Number(used.value)||0));
        due=Math.max(0,x-remaining)*.33;
        note='Illustration for a direct-share capital gain using the 33% CGT rate and the remaining part of the €1,270 annual personal exemption. Losses and other gains are not modelled.';
      }else if(type.value==='fund'){
        usedWrap.hidden=true;
        due=x*.38;
        note='Illustration for income/gain within the Irish/equivalent investment-fund regime where the 38% individual rate applies. The exact tax treatment of an ETF or fund depends on its legal form and domicile; deemed disposal is not a second 38% charge on the same gain.';
      }else{
        usedWrap.hidden=true;
        due=x*.33;
        note='Illustration for Irish-resident deposit interest at the current 33% DIRT rate. Exemptions and foreign-account rules are not modelled.';
      }
      outTax.textContent=money2.format(due);
      outNet.textContent=money2.format(Math.max(0,x-due));
      outRate.textContent=(x?due/x*100:0).toFixed(1)+'%';
      detail.textContent=note;
    };
    tax.addEventListener('input',render); tax.addEventListener('change',render); render();
  }

  const host=document.querySelector('[data-saving-chart]');
  if(host){
    const data=[
      ['2023 Q1',14.92],['2023 Q2',16.49],['2023 Q3',16.10],['2023 Q4',15.26],
      ['2024 Q1',19.66],['2024 Q2',17.17],['2024 Q3',19.19],['2024 Q4',22.74],
      ['2025 Q1',20.63],['2025 Q2',19.73],['2025 Q3',20.47],['2025 Q4',18.74],
      ['2026 Q1',19.07],['2026 Q2',19.90]
    ];
    const W=720,H=310,L=48,R=18,T=22,B=44,min=10,max=25;
    const x=i=>L+(W-L-R)*(i/(data.length-1));
    const y=v=>T+(H-T-B)*(1-(v-min)/(max-min));
    const points=data.map((d,i)=>x(i).toFixed(1)+','+y(d[1]).toFixed(1)).join(' ');
    let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-labelledby="saving-chart-title saving-chart-desc"><title id="saving-chart-title">Irish household saving rate, 2023 Q1 to 2026 Q2</title><desc id="saving-chart-desc">The revised seasonally adjusted household saving rate rose from 14.92 percent in 2023 Q1 to 19.9 percent in 2026 Q2, with quarterly variation.</desc>';
    [10,15,20,25].forEach(v=>{const yy=y(v);svg+='<line class="investing-chart-grid" x1="'+L+'" y1="'+yy+'" x2="'+(W-R)+'" y2="'+yy+'"/><text class="investing-chart-axis" x="'+(L-8)+'" y="'+(yy+4)+'" text-anchor="end">'+v+'%</text>';});
    [0,4,8,12,13].forEach(i=>{svg+='<text class="investing-chart-axis" x="'+x(i)+'" y="'+(H-16)+'" text-anchor="'+(i===0?'start':i===13?'end':'middle')+'">'+data[i][0].replace(' ','\u00a0')+'</text>';});
    svg+='<polyline class="investing-chart-line" points="'+points+'"/>';
    data.forEach((d,i)=>{svg+='<circle class="investing-chart-dot" cx="'+x(i)+'" cy="'+y(d[1])+'" r="4"><title>'+d[0]+': '+d[1].toFixed(1)+'%</title></circle>';});
    svg+='</svg>'; host.innerHTML=svg;
  }
})();