(function(){'use strict';
  const search=document.querySelector('[data-earnings-search]');
  const sector=document.querySelector('[data-earnings-sector]');
  const rows=Array.from(document.querySelectorAll('[data-earnings-row]'));
  if(!search||!sector||!rows.length)return;
  const count=document.querySelector('[data-earnings-count]');
  const empty=document.querySelector('[data-earnings-empty]');
  const chips=Array.from(document.querySelectorAll('[data-stock-sector]'));
  const normalise=value=>String(value||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('en-IE').trim();
  function update(){
    const q=normalise(search.value);let visible=0;
    for(const row of rows){
      const match=(!q||normalise(row.dataset.name).includes(q)||normalise(row.dataset.symbols).includes(q))
        &&(!sector.value||row.dataset.sector===sector.value);
      row.hidden=!match;if(match)visible++;
    }
    if(count)count.textContent='Showing '+visible+' of '+rows.length+' companies';
    if(empty)empty.hidden=visible!==0;
    for(const chip of chips)chip.setAttribute('aria-pressed',String(chip.dataset.stockSector===sector.value));
  }
  search.addEventListener('input',update);
  search.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&search.value){search.value='';update();event.preventDefault();}
  });
  sector.addEventListener('change',update);
  for(const chip of chips)chip.addEventListener('click',()=>{
    sector.value=chip.dataset.stockSector;
    update();
  });
  update();
})();