(async()=>{
  const {el,setup}=explorer;
  const euro=n=>n==null?'Withheld':new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
  let update=()=>{}, moving=false;
  const moveButton=el('place-pin');
  function moveMode(active){
    moving=active;
    moveButton.textContent=active?'Tap map to place pin · Cancel':'Move workplace pin';
    moveButton.setAttribute('aria-pressed',String(active));
    el('explorer-map').classList.toggle('placing',active);
  }
  moveButton.onclick=()=>moveMode(!moving);
  const {map,pin}=setup(()=>{moveMode(false);update();},9,()=>moving,false);
  pin.bindTooltip('Workplace',{permanent:true,direction:'bottom',className:'pin-caption',offset:[0,6]});
  try {
    async function read(url){const response=await fetch(url);if(!response.ok)throw Error(url);return response.json();}
    const [[points,edges],areas]=await Promise.all([read('/static/irish-explorers/roads.json'),read('/static/rent-map/areas.json')]);
    const graph=points.map(()=>[]),districts=new Map(areas.features.map(f=>[f.id,f.properties]));
    for(const [a,b,length] of edges){graph[a].push([b,length]);graph[b].push([a,length]);}
    L.geoJSON(areas,{interactive:false,style:{color:'#ced7c9',weight:.8,fillColor:'#f5f4e9',fillOpacity:1}}).addTo(map);
    map.attributionControl.addAttribution('Boundaries © Tailte Éireann');
    const districtsLayer=L.layerGroup().addTo(map), prices=L.layerGroup().addTo(map);
    let records=[], selected=null;
    function details(record){
      const {area,minutes,price,loc}=record;
      const body=document.createElement('div');
      body.className='rent-detail';
      const name=document.createElement('strong'), value=document.createElement('b'), time=document.createElement('span');
      name.textContent=area.name+' · '+area.county;
      value.textContent=euro(price)+(price==null?'':' / month');
      time.textContent=minutes+' min to the closest sampled road';
      body.append(name,value,time);
      selected=record;
      refreshDistricts();
      L.popup({maxWidth:225,autoPanPadding:[20,20]}).setLatLng(loc).setContent(body).openOn(map);
    }
    function refreshDistricts(){
      for(const record of records){
        record.polygon.setStyle({weight:record===selected?2.2:1,color:record===selected?'#174f48':'#5c8d84',fillColor:'#529785',fillOpacity:record===selected?.30:.13});
      }
    }
    function labels(){
      prices.clearLayers();
      const size=map.getSize(), used=[], workplace=map.latLngToContainerPoint(pin.getLatLng());
      used.push(workplace);
      for(const record of records){
        const pos=map.latLngToContainerPoint(record.loc);
        if(pos.x<47||pos.y<22||pos.x>size.x-47||pos.y>size.y-22)continue;
        if(pos.y<72 && (pos.x>size.x-210 || pos.x<76))continue;
        if(used.some(p=>Math.abs(p.x-pos.x)<98 && Math.abs(p.y-pos.y)<54))continue;
        used.push(pos);
        const tag=document.createElement('div'),name=document.createElement('span'),price=document.createElement('b');
        name.textContent=record.area.name;price.textContent=euro(record.price);tag.append(name,price);
        const icon=L.divIcon({className:'rent-tag',html:tag,iconSize:[88,39],iconAnchor:[44,20]});
        const marker=L.marker(record.loc,{icon,title:record.area.name,alt:record.area.name+' '+euro(record.price),bubblingMouseEvents:true}).addTo(prices);
        marker.on('click',()=>{if(!moving)details(record);});
      }
    }
    map.on('zoomend moveend resize',labels);
    map.on('popupclose',()=>{selected=null;refreshDistricts();});
    update=()=>{
      const origin=pin.getLatLng(),duration=Number(el('minutes').value),speed=Number(el('speed').value)*1000/60,mode=el('tenancy').value;
      let nearest=0,distance=Infinity;
      points.forEach(([lon,lat],i)=>{const d=map.distance(origin,[lat/10000,lon/10000]);if(d<distance){distance=d;nearest=i;}});
      const ceiling=el('budget').value==='' ? Infinity : Math.max(0,Number(el('budget').value));
      const withinBudget=area=>ceiling===Infinity || (area[mode]!=null && area[mode]<=ceiling);
      const limit=(duration-distance/1000*3)*speed,dist=new Float64Array(points.length).fill(Infinity),queue=[nearest];
      const found=new Map();dist[nearest]=0;
      for(let i=0;i<queue.length;i++){const a=queue[i];for(const [b,w] of graph[a]){const next=dist[a]+w;if(next<=limit && next<dist[b]){dist[b]=next;queue.push(b);}}}
      map.closePopup();districtsLayer.clearLayers();prices.clearLayers();selected=null;records=[];
      if(limit>=0 && distance<=10000){
        dist.forEach((d,i)=>{
          const id=points[i][2];
          if(d>limit||!districts.has(id)||!withinBudget(districts.get(id)))return;
          let entry=found.get(id);
          if(!entry){entry={nearest:i,members:[],x:0,y:0};found.set(id,entry);}
          if(d<dist[entry.nearest])entry.nearest=i;
          entry.members.push(i);entry.x+=points[i][0];entry.y+=points[i][1];
        });
      }
      for(const feature of areas.features){
        const entry=found.get(feature.id);
        if(!entry)continue;
        const area=feature.properties, cx=entry.x/entry.members.length, cy=entry.y/entry.members.length;
        const offset=i=>((points[i][0]-cx)*.6)**2+(points[i][1]-cy)**2;
        const anchor=entry.members.reduce((best,i)=>offset(i)<offset(best)?i:best);
        const loc=[points[anchor][1]/10000,points[anchor][0]/10000];
        const polygon=L.geoJSON(feature,{bubblingMouseEvents:true}).addTo(districtsLayer);
        const record={area,loc,polygon,price:area[mode],minutes:Math.ceil(distance/1000*3+dist[entry.nearest]/speed)};
        polygon.on('click',()=>{if(!moving)details(record);});
        records.push(record);
      }
      records.sort((a,b)=>(a.price??Infinity)-(b.price??Infinity)||a.area.name.localeCompare(b.area.name));
      refreshDistricts();labels();
      el('summary').textContent=records.length?records.length+' areas · Lowest monthly rent first':'No areas match. Try a higher budget or a longer drive.';
      const list=el('rents');list.replaceChildren();
      for(const record of records){
        const button=document.createElement('button'),text=document.createElement('span'),place=document.createElement('strong'),info=document.createElement('small'),price=document.createElement('b');
        place.textContent=record.area.name;info.textContent=record.area.county+' · '+record.minutes+' min';text.append(place,info);
        price.textContent=euro(record.price);button.append(text,price);
        button.onclick=()=>{el('explorer-map').scrollIntoView({block:'nearest'});details(record);};
        list.append(button);
      }
    };
    el('budget').oninput=()=>{map.closePopup();update();};
    for(const key of ['tenancy','minutes','speed'])el(key).onchange=()=>{map.closePopup();update();};
    update();
  }catch{el('summary').textContent='Road data could not load. Refresh to try again.';}
})();
