(()=>{
  const {el,setup}=explorer;
  const rad=Math.PI/180;
  const dateFormat=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Dublin',year:'numeric',month:'2-digit',day:'2-digit'});
  const clock=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Dublin',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
  function midnight(day){
    const utc=Date.parse(day+'T00:00:00Z');
    return utc-Number(clock.format(utc).slice(0,2))*3600000;
  }
  const parts=dateFormat.formatToParts(new Date()),part=t=>parts.find(p=>p.type===t).value;
  el('day').value=[part('year'),part('month'),part('day')].join('-');
  const {map,pin}=setup(()=>draw(),12);
  const rays=L.layerGroup().addTo(map);
  function endpoint(point,bearing,metres){
    const angle=bearing*rad;
    return [point.lat+metres*Math.cos(angle)/111320,point.lng+metres*Math.sin(angle)/(111320*Math.cos(point.lat*rad))];
  }
  // Compass projection adapted from Sun Sim (MIT).
  function project(position){
    const bearing=position.azimuth+Math.PI,distance=110*(1-position.altitude/(Math.PI/2));
    return [200+Math.sin(bearing)*distance,155-Math.cos(bearing)*distance];
  }
  function draw(){
    const day=el('day').value;if(!day)return;
    const point=pin.getLatLng(),start=midnight(day);
    const tomorrow=new Date(Date.parse(day+'T12:00:00Z')+86400000).toISOString().slice(0,10);
    const minutes=(midnight(tomorrow)-start)/60000;
    el('hour').max=minutes-5;
    const when=new Date(start+Number(el('hour').value)*60000);
    const position=date=>SunCalc.getPosition(date,point.lat,point.lng),now=position(when);
    const times=SunCalc.getTimes(new Date(start+12*3600000),point.lat,point.lng);
    const bearing=(now.azimuth/rad+540)%360,alt=now.altitude/rad;
    let path='',pen=false;
    for(let m=0;m<=minutes;m+=5){const s=position(start+m*60000);if(s.altitude<0){pen=false;continue;}path+=(pen?'L':'M')+project(s).join(' ');pen=true;}
    const [x,y]=project(now),svg=el('sky');
    svg.innerHTML='<g fill="none" stroke="#779692"><circle cx="200" cy="155" r="110"/><circle cx="200" cy="155" r="73" stroke-dasharray="3 5"/><circle cx="200" cy="155" r="37" stroke-dasharray="3 5"/><path d="M90 155h220M200 45v220" opacity=".55"/></g><g text-anchor="middle" fill="#d8e6dd" font-family="system-ui" font-size="13"><text x="200" y="32">N</text><text x="200" y="288">S</text><text x="72" y="160">W</text><text x="328" y="160">E</text></g><path d="'+path+'" fill="none" stroke="#efb755" stroke-width="3"/>'+(alt>=0?'<path d="M200 155L'+x+' '+y+'" stroke="#e9d5a3" stroke-dasharray="3 4"/><circle cx="'+x+'" cy="'+y+'" r="8" fill="#ffe292"/>':'<text x="200" y="305" text-anchor="middle" fill="white">Sun below the horizon</text>');
    el('clock').textContent=clock.format(when);
    const daylight=Math.round((times.sunset-times.sunrise)/60000);
    const stats={'Sunrise':clock.format(times.sunrise),'Sunset':clock.format(times.sunset),'Daylight':Math.floor(daylight/60)+'h '+daylight%60+'m','Solar elevation':alt.toFixed(1)+'°','Bearing from north':Math.round(bearing)%360+'°','Pin':point.lat.toFixed(3)+'°, '+point.lng.toFixed(3)+'°'};
    const dl=el('solar-stats');dl.replaceChildren();
    for(const [name,value] of Object.entries(stats)){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;dl.append(dt,dd);}
    const height=el('height');
    rays.clearLayers();
    if(alt>0){
      const rayLength=map.distance(map.getBounds().getSouthWest(),map.getBounds().getSouthEast())*.20;
      L.polyline([point,endpoint(point,bearing,rayLength)],{color:'#d88916',weight:3,dashArray:'8 5',interactive:false}).addTo(rays);
      if(height.value && height.validity.valid){
        const shadow=Number(height.value)/Math.tan(now.altitude);
        L.polyline([point,endpoint(point,bearing+180,Math.min(shadow,20000))],{color:'#263a48',weight:6,interactive:false}).addTo(rays);
      }
    }
    el('shadow').textContent=alt<=0?'The sun is below the horizon.':!height.value||!height.validity.valid?'Enter a height from 0.1 to 100 metres.':'Estimated shadow '+(Number(height.value)/Math.tan(now.altitude)).toFixed(1)+' m towards '+Math.round((bearing+180)%360)+'° from north.';
  }
  for(const id of ['hour','height','day'])el(id).oninput=draw;
  for(const [key,suffix] of [['summer','06-21'],['winter','12-21']])el(key).onclick=()=>{el('day').value=(el('day').value||new Date().toISOString()).slice(0,4)+'-'+suffix;draw();};
  map.on('zoomend',draw);
  draw();
})();
