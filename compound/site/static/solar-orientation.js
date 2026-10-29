/* Compound Solar roof-direction explorer. Fast illustrative model, no external navigation.
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
  var angle=180, official=null;
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
  var chart=q('chart'),profile=null,selectedMonth=5;
  // Render with native HTML columns instead of Canvas. Some mobile browsers
  // suppress or lose the 2D drawing surface after viewport/dark-mode changes.
  // Bar elements also exist in the HTML before JavaScript runs.
  function drawChart(values){
    if(!values||values.length!==12)return;
    var max=Math.max.apply(null,values.concat([1]));
    var bars=chart.querySelectorAll('[data-sor-month]');
    bars.forEach(function(bar,i){
      var amount=Math.max(0,Number(values[i])||0);
      var fill=bar.querySelector('.sor-canvas-fill');
      if(fill)fill.style.height=Math.max(3,Math.round(amount/max*100))+'%';
      bar.setAttribute('aria-pressed',String(selectedMonth===i));
      bar.setAttribute('aria-label',months[i]+': '+fmt(amount)+' kWh of estimated solar production');
      bar.title=months[i]+': '+fmt(amount)+' kWh';
    });
    chart.setAttribute('aria-label','Estimated monthly electricity generation from January to December. Use arrow keys to select a month.');
    q('chart-amount').textContent=months[selectedMonth]+': '+fmt(values[selectedMonth])+' kWh';
    var peak=Math.max.apply(null,values),peakAt=values.indexOf(peak);
    q('chart-peak').textContent='Peak production: '+months[peakAt]+' · '+fmt(peak)+' kWh';
  }
  chart.addEventListener('click',function(ev){
    if(!profile)return;
    var button=ev.target.closest('[data-sor-month]');
    if(!button)return;
    var i=Number(button.getAttribute('data-sor-month'));
    if(!Number.isInteger(i)||i<0||i>11)return;
    selectedMonth=i;
    drawChart(profile);
  });
  chart.addEventListener('keydown',function(ev){
    if(!profile)return;
    if(ev.key==='ArrowRight'||ev.key==='ArrowLeft'){
      ev.preventDefault();
      selectedMonth=clamp(selectedMonth+(ev.key==='ArrowRight'?1:-1),0,11);
      drawChart(profile);
      var selected=chart.querySelector('[data-sor-month="'+selectedMonth+'"]');
      if(selected)selected.focus({preventScroll:true});
    }
  });
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
    profile=r.months;
    drawChart(profile);
  }
  function emitToProject(source){
    if(!root.hasAttribute('data-orientation-embedded'))return;
    var result=estimate();
    root.dispatchEvent(new CustomEvent('compound:solar:orientation',{bubbles:true,detail:{
      azimuth:angle,pitch:val('pitch'),size:val('size'),shade:val('shade'),
      annual:result.annual,source:source||'direction'
    }}));
  }
  // The project dashboard can swap roof faces without navigating away.
  root.addEventListener('compound:solar:load',function(event){
    if(!root.hasAttribute('data-orientation-embedded'))return;
    var data=event.detail||{};
    if(Number.isFinite(data.azimuth))angle=normal(data.azimuth);
    if(Number.isFinite(data.pitch)&&data.pitch>=0&&data.pitch<=90)q('pitch').value=String(data.pitch);
    if(Number.isFinite(data.size)&&data.size>0&&data.size<=30)q('size').value=String(data.size);
    official=null;q('status').textContent='';render();
  });
  function changeAngle(n,track){
    angle=normal(n);official=null; q('status').textContent='';render();
    emitToProject('direction');
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
    q(key).addEventListener('input',function(){official=null;q('status').textContent='';render();emitToProject(key);trackUse();});
    q(key).addEventListener('change',function(){official=null;q('status').textContent='';render();emitToProject(key);});
  });
  q('copy').addEventListener('click',function(){
    var r=official||estimate(),output=String(Math.round(r.perKwp));
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(output).then(function(){q('status').textContent='Copied '+output+' kWh per kWp. Paste this into the solar payback calculator.';},function(){q('status').textContent='Annual yield per kWp: '+output+' kWh.';});}
    else q('status').textContent='Annual yield per kWp: '+output+' kWh. Enter this in the payback calculator.';
    trackUse();
  });
  render();
})();