/* Compound Solar roof-direction explorer. Fast illustrative model, optional official PVGIS.
   No geolocation, accounts or inputs transmitted to Compound. */
(function(){
  'use strict';
  var root=document.querySelector('[data-solar-orientation]');
  if(!root)return;
  var places={
    dublin:{lat:53.35,lon:-6.26,yield:930,label:'Dublin'},
    navan:{lat:53.65,lon:-6.68,yield:930,label:'Navan / Meath'},
    cork:{lat:51.90,lon:-8.47,yield:960,label:'Cork'},
    wexford:{lat:52.34,lon:-6.46,yield:985,label:'Wexford'},
    galway:{lat:53.27,lon:-9.06,yield:880,label:'Galway'},
    limerick:{lat:52.67,lon:-8.63,yield:920,label:'Limerick'},
    sligo:{lat:54.27,lon:-8.48,yield:855,label:'Sligo'},
    donegal:{lat:54.95,lon:-7.73,yield:835,label:'Letterkenny / Donegal'},
    kilkenny:{lat:52.65,lon:-7.25,yield:960,label:'Kilkenny'}
  };
  var months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var southMonthly=[.02,.04,.07,.10,.13,.14,.14,.12,.10,.07,.04,.03];
  var representativeDays=[15,46,74,105,135,166,196,227,258,288,319,349];
  var angle=180, official=null, busy=false, controller=null;
  function q(k){return root.querySelector('[data-or="'+k+'"]');}
  function val(k){return Number(q(k).value);}
  function normal(a){return ((Math.round(a)%360)+360)%360;}
  function clamp(n,min,max){return Math.max(min,Math.min(max,n));}
  function fmt(n){return Math.round(n).toLocaleString('en-IE');}
  function direction(a){var arr=['North','North-east','East','South-east','South','South-west','West','North-west'];return arr[Math.round(a/45)%8];}
  function at(lat,az,tilt){
    lat=lat*Math.PI/180;tilt=tilt*Math.PI/180;az=az*Math.PI/180;
    return representativeDays.map(function(day){
      var dec=(23.44*Math.sin(2*Math.PI*(284+day)/365))*Math.PI/180,sum=0;
      for(var h=4.5;h<=19;h+=.5){
        var ha=(15*(h-12))*Math.PI/180;
        var sinEl=Math.sin(lat)*Math.sin(dec)+Math.cos(lat)*Math.cos(dec)*Math.cos(ha);
        if(sinEl<=0)continue;
        var el=Math.asin(sinEl),sunAz=Math.atan2(Math.sin(ha),Math.cos(ha)*Math.sin(lat)-Math.tan(dec)*Math.cos(lat))+Math.PI;
        var incidence=Math.sin(el)*Math.cos(tilt)+Math.cos(el)*Math.sin(tilt)*Math.cos(sunAz-az);
        sum+=.39*Math.max(0,incidence)*Math.pow(sinEl,.4)+
             .58*(1+Math.cos(tilt))/2*Math.pow(sinEl,1.2)+
             .03*(1-Math.cos(tilt))/2*Math.pow(sinEl,1.2);
      }
      return sum;
    });
  }
  var chart= q('chart');
  months.forEach(function(m){
    var cell=document.createElement('div');cell.className='sor-month';
    var bar=document.createElement('div');bar.className='sor-month-track';
    var fill=document.createElement('div');fill.className='sor-month-fill';fill.setAttribute('data-or-bar',m);bar.appendChild(fill);
    var label=document.createElement('span');label.textContent=m;cell.appendChild(bar);cell.appendChild(label);chart.appendChild(cell);
  });
  var fills=Array.prototype.slice.call(root.querySelectorAll('.sor-month-fill'));
  function estimate(){
    var place=places[q('place').value]||places.dublin;
    var size=clamp(val('size')||0,0,30),pitch=clamp(val('pitch'),0,90),shade=clamp(val('shade'),0,50);
    var reference=at(place.lat,180,35),current=at(place.lat,angle,pitch),comparison=at(place.lat,180,pitch);
    var profile=current.map(function(v,i){return place.yield*size*southMonthly[i]*(reference[i]>0?v/reference[i]:0)*(1-shade/100);});
    var south=comparison.reduce(function(acc,v,i){return acc+place.yield*size*southMonthly[i]*(reference[i]>0?v/reference[i]:0)*(1-shade/100);},0);
    var sum=profile.reduce(function(a,b){return a+b;},0);
    return {annual:sum,south:south,months:profile,perKwp:size>0?sum/size:0};
  }
  function render(){
    var size=val('size'),pitch=val('pitch'),shade=val('shade');
    var valid=Number.isFinite(size)&&size>0&&size<=30&&Number.isFinite(pitch)&&pitch>=0&&pitch<=90&&Number.isFinite(shade)&&shade>=0&&shade<=50;
    q('angle').textContent=angle+'°';q('heading').textContent=direction(angle);
    q('needle').style.transform='rotate('+angle+'deg)';
    q('slider').value=String(angle);q('slider-value').textContent=angle+'°';
    root.querySelectorAll('[data-or-preset]').forEach(function(b){b.setAttribute('aria-pressed',String(Number(b.getAttribute('data-or-preset'))===angle));});
    q('error').hidden=valid;
    q('results').hidden=!valid;
    q('request').disabled=!valid||busy;
    if(!valid)return;
    var r=estimate();
    if(official){r=official;}
    q('total').textContent=fmt(r.annual);
    q('unit').textContent=fmt(r.perKwp);
    var pct=r.south>0?r.annual/r.south*100:0;
    q('percent').textContent=Math.round(pct)+'%';
    q('relative').textContent=Math.abs(pct-100)<.5?'Comparable to a south-facing roof':pct<100?'About '+Math.round(100-pct)+'% below south-facing at the same pitch':'About '+Math.round(pct-100)+'% above south-facing at the same pitch';
    q('source').textContent=official?'PVGIS 5.3 modelled generation for the selected representative location.':'Illustrative geometry-based estimate; regional Irish yields are approximate, not PVGIS output.';
    q('accuracy').textContent=official?'PVGIS result (typical year, assumed 14% system loss)':'Indicative estimate (assumed normal system losses; shading adjustment selected above)';
    q('copy').disabled=false;
    q('grade').style.width=clamp(pct,0,110)+'%';
    var max=Math.max.apply(null,r.months.concat([1]));
    fills.forEach(function(bar,i){
      bar.style.height=(r.months[i]/max*100).toFixed(2)+'%';
      bar.parentNode.title=months[i]+': '+fmt(r.months[i])+' kWh';
      bar.parentNode.setAttribute('aria-label',months[i]+': '+fmt(r.months[i])+' kWh');
    });
  }
  function changeAngle(n,track){
    angle=normal(n);official=null; q('status').textContent='';render();
    if(track)trackUse();
  }
  function trackUse(){try{if(localStorage.getItem('compound_analytics_consent')==='granted'&&window.gtag&&!root.dataset.sorTracked){root.dataset.sorTracked='1';window.gtag('event','solar_orientation_explorer_used');}}catch(_){ }}
  var dial=q('dial');
  function compassEvent(ev){
    var rect=dial.getBoundingClientRect(),x=ev.clientX-(rect.left+rect.width/2),y=ev.clientY-(rect.top+rect.height/2);
    if(Math.hypot(x,y)<16)return;
    changeAngle(Math.atan2(x,-y)*180/Math.PI,true);
  }
  dial.addEventListener('pointerdown',function(ev){if(ev.button!==0)return;dial.setPointerCapture(ev.pointerId);compassEvent(ev);});
  dial.addEventListener('pointermove',function(ev){if(dial.hasPointerCapture(ev.pointerId))compassEvent(ev);});
  dial.addEventListener('keydown',function(ev){var d={'ArrowRight':1,'ArrowUp':1,'ArrowLeft':-1,'ArrowDown':-1,'PageUp':10,'PageDown':-10};if(Object.prototype.hasOwnProperty.call(d,ev.key)){ev.preventDefault();changeAngle(angle+d[ev.key],true);}else if(ev.key==='Home'||ev.key==='End'){ev.preventDefault();changeAngle(ev.key==='Home'?0:359,true);}});
  q('slider').addEventListener('input',function(){changeAngle(Number(this.value),true);});
  root.querySelectorAll('[data-or-preset]').forEach(function(b){b.addEventListener('click',function(){changeAngle(Number(b.getAttribute('data-or-preset')),true);});});
  ['place','size','pitch','shade'].forEach(function(key){
    q(key).addEventListener('input',function(){official=null;q('status').textContent='';render();trackUse();});
    q(key).addEventListener('change',function(){official=null;q('status').textContent='';render();});
  });
  function pvgisUrl(az){
    var place=places[q('place').value],p=new URLSearchParams({
      lat:String(place.lat),lon:String(place.lon),peakpower:String(val('size')),
      loss:'14',angle:String(val('pitch')),aspect:String(az-180),outputformat:'json',
      pvtechchoice:'crystSi',mountingplace:'building'
    });
    return 'https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?'+p.toString();
  }
  function parsePV(data,shade){
    var monthly=data&&data.outputs&&data.outputs.monthly&&data.outputs.monthly.fixed;
    if(!Array.isArray(monthly)||monthly.length!==12)throw new Error('Unexpected PVGIS result');
    var arr=monthly.map(function(row){if(!Number.isFinite(Number(row.E_m)))throw new Error('Invalid PVGIS response');return Number(row.E_m)*(1-shade/100);});
    return {monthly:arr,annual:arr.reduce(function(a,b){return a+b;},0)};
  }
  q('request').addEventListener('click',async function(){
    if(busy)return;
    busy=true;official=null;render();q('request').textContent='Checking PVGIS…';
    q('status').textContent='Requesting modelled generation from the European Commission.';
    var original=[angle,val('pitch'),val('shade'),val('size'),q('place').value].join('|');
    controller=new AbortController();
    try{
      var urls=[pvgisUrl(angle),pvgisUrl(180)],responses=await Promise.all(urls.map(function(u){return fetch(u,{signal:controller.signal}).then(function(r){if(!r.ok)throw new Error('PVGIS '+r.status);return r.json();});}));
      if(original!==[angle,val('pitch'),val('shade'),val('size'),q('place').value].join('|'))return;
      var a=parsePV(responses[0],val('shade')),b=parsePV(responses[1],val('shade'));
      official={annual:a.annual,south:b.annual,months:a.monthly,perKwp:a.annual/val('size')};
      q('status').textContent='PVGIS calculation loaded for '+places[q('place').value].label+'. This is not a site survey.';
      trackUse();
    }catch(e){if(e.name!=='AbortError')q('status').textContent='PVGIS could not be reached from this browser. The indicative estimate is still shown. Try again or use the official PVGIS website.';}
    finally{busy=false;q('request').textContent='Refine with PVGIS';render();}
  });
  q('copy').addEventListener('click',function(){
    var r=official||estimate(),output=String(Math.round(r.perKwp));
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(output).then(function(){q('status').textContent='Copied '+output+' kWh per kWp. Paste this into the solar payback calculator.';},function(){q('status').textContent='Annual yield per kWp: '+output+' kWh.';});}
    else q('status').textContent='Annual yield per kWp: '+output+' kWh. Enter this in the payback calculator.';
    trackUse();
  });
  render();
})();