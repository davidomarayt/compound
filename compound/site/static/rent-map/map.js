(async function () {
  const byId = id => document.getElementById(id);
  const map = L.map('rent-map', {zoomSnap: 0.1, scrollWheelZoom: false, minZoom: 5, maxZoom: 14});
  const country = [[51.38,-10.65],[55.46,-5.43]];
  const resetView = () => map.fitBounds(country, {padding:[8,8]});
  resetView();
  const mode = byId('rent-type'), picker = byId('rent-area');
  const colors = ['#f8eab5','#edc37c','#de965a','#bf6550','#984559','#663557'];
  const cuts = [1000,1250,1500,1750,2000];
  const currency = new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
  const money = value => value == null ? 'Withheld' : currency.format(value);
  const missing = '#b9c4c2';
  const labels = ['Under €1,000','€1,000–1,249','€1,250–1,499','€1,500–1,749','€1,750–1,999','€2,000+','Withheld'];
  labels.forEach((label,i) => {
    const item = document.createElement('span'), chip = document.createElement('i');
    chip.style.background = colors[i] || missing;
    item.append(chip,label); document.querySelector('.rent-key').append(item);
  });
  const national = {name:'Republic of Ireland',new:1839,existing:1513};
  let selected;
  function style(feature) {
    const value = feature.properties[mode.value], index = cuts.filter(cut => value >= cut).length;
    return {color:feature===selected ? '#142e30' : '#fffaf1',weight:feature===selected ? 2.8 : 0.8,fillOpacity:1,fillColor:value==null ? missing : colors[index]};
  }
  try {
    const read = async name => {
      const response = await fetch('/static/rent-map/'+name+'.json');
      if (!response.ok) throw Error(name);
      return response.json();
    };
    const [outline,areas] = await Promise.all([read('ireland'),read('areas')]);
    L.geoJSON(outline,{interactive:false,style:{weight:1,color:'#abbaaf',fillColor:'#eef0e4',fillOpacity:1}}).addTo(map);
    const layers = new Map();
    function select(layer,zoom) {
      selected = layer?.feature;
      const area = selected?.properties || national;
      picker.value = selected ? String(selected.id) : '';
      byId('rent-location').textContent = selected ? area.county.toUpperCase()+' · LOCAL ELECTORAL AREA' : 'NATIONAL AVERAGE';
      byId('rent-name').textContent = area.name;
      for (const type of ['new','existing']) byId('rent-'+type).textContent = money(area[type]);
      byId('rent-context').textContent = selected && area.new!=null ? 'New tenancy rent is '+money(Math.abs(area.new-national.new))+' '+(area.new>=national.new?'above':'below')+' the national monthly average.' : 'Standardised monthly rent for January to March 2026.';
      overlay.setStyle(style);
      if(layer){layer.bringToFront(); if(zoom)map.fitBounds(layer.getBounds(),{padding:[28,28],maxZoom:11});}
      else resetView();
    }
    const overlay = L.geoJSON(areas,{style,onEachFeature(feature,layer){
      const area = feature.properties;
      layers.set(String(feature.id),layer);
      layer.bindTooltip(()=>{const box=document.createElement('div'), name=document.createElement('b'); name.textContent=area.name;box.append(name,money(area[mode.value]));return box;},{sticky:true,className:'rent-tip'});
      layer.on('click',()=>select(layer,true));
    }}).addTo(map);
    [...layers].sort((a,b)=>a[1].feature.properties.name.localeCompare(b[1].feature.properties.name)).forEach(([id,layer])=>{
      const area=layer.feature.properties;picker.add(new Option(area.name+' · '+area.county,id));
    });
    mode.onchange=()=>overlay.setStyle(style);
    picker.onchange=()=>select(layers.get(picker.value),true);
    byId('rent-reset').onclick=()=>select(null,false);
  } catch {byId('rent-context').textContent='The map data could not load. Refresh this page to try again.';}
})();
