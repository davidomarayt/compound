(async()=>{
  const {el,setup}=explorer;
  const palette=['#f2d99e','#e4ac6f','#d08255','#b25852','#91405a','#5e3159'];
  const labels=['< €1,000','€1,000–1,249','€1,250–1,499','€1,500–1,749','€1,750–1,999','€2,000+','Withheld'];
  const color=v=>v==null?'#9ea9a7':palette[[1000,1250,1500,1750,2000].filter(n=>v>=n).length];
  const euro=n=>n==null?'Withheld':new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
  labels.forEach((label,i)=>{const span=document.createElement('span'),chip=document.createElement('i');chip.style.background=palette[i]||color(null);span.append(chip,label);el('scale').append(span);});
  let update=()=>{};
  const {map,pin}=setup(()=>update(),10);
  try {
    async function read(url){const response=await fetch(url);if(!response.ok)throw Error(url);return response.json();}
    const [[points,edges],areas]=await Promise.all([read('/static/irish-explorers/roads.json'),read('/static/rent-map/areas.json')]);
    const graph=points.map(()=>[]),districts=new Map(areas.features.map(f=>[f.id,f.properties]));
    for(const [a,b,length] of edges){graph[a].push([b,length]);graph[b].push([a,length]);}
    const renderer=L.svg().addTo(map);
    const layer=L.geoJSON(areas,{renderer,interactive:false,style:f=>({stroke:false,fillColor:color(f.properties[el('tenancy').value]),fillOpacity:.82})}).addTo(map);
    const ns='http://www.w3.org/2000/svg';
    const first=layer.getLayers()[0].getElement(),svg=first.ownerSVGElement;
    const defs=document.createElementNS(ns,'defs'),clip=document.createElementNS(ns,'clipPath'),shape=document.createElementNS(ns,'path');
    clip.id='reachable-roads';clip.append(shape);defs.append(clip);svg.prepend(defs);
    for(const part of layer.getLayers())part.getElement().setAttribute('clip-path','url(#reachable-roads)');
    let segments=[];
    function paint(){
      const path=[],radius=Math.max(2,Math.min(42,Math.abs(map.latLngToLayerPoint([53,-6]).x-map.latLngToLayerPoint([53,-6.01]).x)*.65));
      for(const [a,b,fraction] of segments){
        const p=map.latLngToLayerPoint([points[a][1]/10000,points[a][0]/10000]),end=map.latLngToLayerPoint([points[b][1]/10000,points[b][0]/10000]);
        const dx=(end.x-p.x)*fraction,dy=(end.y-p.y)*fraction,length=Math.hypot(dx,dy)||1;
        const x=radius*dy/length,y=-radius*dx/length;
        path.push('M'+[p.x+x,p.y+y]+'l'+[dx,dy]+' '+[-2*x,-2*y]+' '+[-dx,-dy]+'Z');
      }
      shape.setAttribute('d',path.join(''));
    }
    map.on('zoomend moveend',paint);
    update=()=>{
      const origin=pin.getLatLng(),duration=Number(el('minutes').value),speed=Number(el('speed').value)*1000/60,mode=el('tenancy').value;
      let nearest=0,distance=Infinity;
      points.forEach(([lon,lat],i)=>{const d=map.distance(origin,[lat/10000,lon/10000]);if(d<distance){distance=d;nearest=i;}});
      const ceiling=el('budget').value==='' ? Infinity : Math.max(0,Number(el('budget').value));
      const withinBudget=area=>ceiling===Infinity || (area[mode]!=null && area[mode]<=ceiling);
      const limit=(duration-distance/1000*3)*speed,dist=new Float64Array(points.length).fill(Infinity),queue=[nearest];
      const found=new Map();dist[nearest]=0;
      for(let i=0;i<queue.length;i++){const a=queue[i];for(const [b,w] of graph[a]){const next=dist[a]+w;if(next<=limit && next<dist[b]){dist[b]=next;queue.push(b);}}}
      segments=[];
      if(limit>=0 && distance<=10000){
        for(let [a,b,w] of edges){
          if(dist[b]<dist[a])[a,b]=[b,a];
          if(dist[a]>=limit)continue;
          segments.push([a,b,Math.min(1,(limit-dist[a])/w)]);
        }
        dist.forEach((d,i)=>{const id=points[i][2];if(d<=limit && districts.has(id) && withinBudget(districts.get(id)) && (!found.has(id)||d<dist[found.get(id)]))found.set(id,i);});
      }
      layer.setStyle(f=>({fillColor:color(f.properties[mode]),fillOpacity:withinBudget(f.properties)?.82:0}));paint();
      el('summary').textContent=found.size?found.size+' electoral areas along reachable roads. Select one for details.':'No matching areas. Try a higher budget, a longer drive or a pin closer to a town.';
      const list=el('rents');list.replaceChildren();
      for(const [id,i] of [...found].sort(([a],[b])=>(districts.get(a)[mode]??Infinity)-(districts.get(b)[mode]??Infinity))){
        const area=districts.get(id),button=document.createElement('button'),price=document.createElement('b');
        price.textContent=euro(area[mode]);button.append(area.name+' · '+area.county,price);
        button.onclick=()=>{
          const loc=[points[i][1]/10000,points[i][0]/10000],body=document.createElement('div'),name=document.createElement('b');name.textContent=area.name+' · '+area.county;
          body.append(name,document.createElement('br'),euro(area[mode])+' monthly · '+Math.ceil(distance/1000*3+dist[i]/speed)+' min to closest sampled road.');
          L.popup().setLatLng(loc).setContent(body).openOn(map);
        };list.append(button);
      }
    };
    el('budget').oninput=()=>{map.closePopup();update();};
    for(const key of ['tenancy','minutes','speed'])el(key).onchange=()=>{map.closePopup();update();};
    update();
  }catch{el('summary').textContent='Road data could not load. Refresh to try again.';}
})();
