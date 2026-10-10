(function(){'use strict';
  const search=document.querySelector('[data-earnings-search]');
  const sector=document.querySelector('[data-earnings-sector]');
  const rows=Array.from(document.querySelectorAll('[data-earnings-row]'));
  if(!search||!sector||!rows.length)return;
  const count=document.querySelector('[data-earnings-count]');
  const empty=document.querySelector('[data-earnings-empty]');
  function update(){
    const q=search.value.trim().toLocaleLowerCase('en-IE');let visible=0;
    for(const row of rows){const match=(!q||row.dataset.name.includes(q)||row.dataset.symbols.includes(q))&&(!sector.value||row.dataset.sector===sector.value);row.hidden=!match;if(match)visible++;}
    count.textContent='Showing '+visible+' of '+rows.length+' companies';empty.hidden=visible!==0;
  }
  search.addEventListener('input',update);sector.addEventListener('change',update);
})();