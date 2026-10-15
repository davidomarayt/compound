/* Compound Solar Project Brief — browser-local fields only.
   No account, API submission, transmission of project fields, cookies or persistence of personal data. */
(function(){
  'use strict';
  var root=document.querySelector('[data-solar-project]');if(!root)return;
  var get=function(key){return root.querySelector('[data-sp="'+key+'"]');};
  var fields=Array.prototype.slice.call(root.querySelectorAll('[data-sp]'));
  var show=function(key){var el=get(key);if(!el)return '';return el.type==='checkbox'?(el.checked?'Can provide':'Not available'):el.value.trim();};
  var answer=function(k){return show(k)||'To be confirmed';};
  var number=function(k){var t=show(k),n=Number(t);return t!==''&&Number.isFinite(n)&&n>=0?n.toLocaleString('en-IE',{maximumFractionDigits:2}):'To be confirmed';};
  var mark=function(label,v){return label+': '+v;};
  var snapshot=null;
  try{
    var saved=JSON.parse(sessionStorage.getItem('compound_solar_project_compass_v1')||'null');
    if(saved&&Date.now()-saved.savedAt<30*60*1000&&saved.savedAt<=Date.now()&&
       Number.isFinite(saved.azimuth)&&saved.azimuth>=0&&saved.azimuth<360&&
       Number.isFinite(saved.pitch)&&saved.pitch>=0&&saved.pitch<=90){
      get('azimuth').value=String(saved.azimuth);get('pitch').value=String(saved.pitch);
      if(Number.isFinite(saved.kwp)&&saved.kwp>0&&saved.kwp<=100)get('kwp').value=String(saved.kwp);
      snapshot=saved;
      var note=get('compass');
      root.querySelector('[data-sp-compass]').textContent='Compass values imported for this tab. They are estimates, not an installer survey.';
    }
  }catch(_){ }
  var embedded=root.querySelector('[data-orientation-embedded]');
  var activeFace=1;
  var faceKeys=function(f){return f===2?['azimuth2','pitch2']:['azimuth','pitch'];};
  function faceStatus(){
    var names=faceKeys(activeFace),az=show(names[0]),pitch=show(names[1]);
    var status=root.querySelector('[data-sp-face-status]');
    if(status)status.textContent=az!=='' && pitch!==''?
      'Roof face '+activeFace+' confirmed: '+az+'° direction, '+pitch+'° pitch. These values are now in your quote brief.':
      'Roof face '+activeFace+': compass defaults are examples. Tap a bearing or change pitch to confirm this face.';
    var main=root.querySelector('[data-sp-primary-output]');
    if(main)main.textContent=show('azimuth')!==''&&show('pitch')!==''?show('azimuth')+'° / '+show('pitch')+'° pitch':'Not yet selected';
    var second=root.querySelector('[data-sp-secondary-output]');
    if(second)second.textContent=show('azimuth2')!==''&&show('pitch2')!==''?show('azimuth2')+'° / '+show('pitch2')+'° pitch':'Not yet selected';
  }
  function switchFace(n){
    activeFace=n===2?2:1;
    root.querySelectorAll('[data-sp-face-button]').forEach(function(btn){
      btn.setAttribute('aria-pressed',String(Number(btn.getAttribute('data-sp-face-button'))===activeFace));
    });
    var keys=faceKeys(activeFace),direction=show(keys[0]),pitch=show(keys[1]);
    if(embedded)embedded.dispatchEvent(new CustomEvent('compound:solar:load',{detail:{
      azimuth:direction!==''?Number(direction):180,
      pitch:pitch!==''?Number(pitch):35,
      size:show('kwp')!==''?Number(show('kwp')):6
    }}));
    faceStatus();
  }
  if(embedded){
    embedded.addEventListener('compound:solar:orientation',function(event){
      var data=event.detail||{},keys=faceKeys(activeFace);
      if(!Number.isFinite(data.azimuth)||!Number.isFinite(data.pitch))return;
      get(keys[0]).value=String(Math.round(data.azimuth));
      get(keys[1]).value=String(data.pitch);
      // Array size is an illustrative 6 kWp default. Do not record it as the
      // homeowner's preference unless the size input itself was changed.
      if(data.source==='size'&&Number.isFinite(data.size)&&data.size>0){
        get('kwp').value=String(data.size);
      }
      if(activeFace===1)snapshot={azimuth:Number(get('azimuth').value),pitch:Number(get('pitch').value),annual:Number(data.annual),kwp:Number(data.size)};
      faceStatus();
      update();
    });
    root.querySelectorAll('[data-sp-face-button]').forEach(function(btn){
      btn.addEventListener('click',function(){switchFace(Number(btn.getAttribute('data-sp-face-button')));});
    });
    get('faces').addEventListener('change',function(){
      var two=this.value==='2',selector=root.querySelector('[data-sp-face-switch]');
      if(selector)selector.hidden=!two;
      if(!two||activeFace===2)switchFace(1);
      update();
    });
    get('kwp').addEventListener('change',function(){
      var size=Number(this.value);
      if(Number.isFinite(size)&&size>0&&size<=30)embedded.dispatchEvent(new CustomEvent('compound:solar:load',{detail:{size:size}}));
    });
    root.querySelector('[data-sp-face-switch]').hidden=get('faces').value!=='2';
    switchFace(1);
  }
  function update(){
    var second=get('faces').value==='2';
    root.querySelector('[data-sp-second]').hidden=!second;
    // Readiness is for the essentials, not technical survey answers. The compass,
    // electricity usage and installer extras are genuinely optional.
    var essential=['county','area','role','building','timing','installerCount','name','email'];
    var complete=essential.filter(function(k){return show(k)!==''}).length;
    var total=essential.length,pct=Math.round(100*complete/total);
    root.querySelector('[data-sp-progress]').textContent=pct+'%';
    root.querySelector('[data-sp-progress-bar]').style.width=pct+'%';
    root.querySelector('[data-sp-progress-note]').textContent=pct===100?
      'Key details complete. Your roof and energy answers will make this brief even more useful.':
      (total-complete)+' key detail'+(total-complete===1?'':'s')+' remaining. Technical answers are optional.';
    var tags=[];
    if(show('county'))tags.push(show('county'));
    if(show('building'))tags.push(show('building'));
    if(show('azimuth'))tags.push(show('azimuth')+'° roof bearing');
    if(show('demand'))tags.push(number('demand')+' kWh annual use');
    if(show('bill')&&!show('demand'))tags.push('€'+number('bill')+' monthly electricity bill');
    if(show('kwp'))tags.push(number('kwp')+' kWp proposed');
    if(show('timing'))tags.push(show('timing'));
    var el=root.querySelector('[data-sp-tags]');
    el.replaceChildren();
    (tags.length?tags:['Add your location and solar needs']).forEach(function(t){var span=document.createElement('span');span.textContent=t;el.appendChild(span);});
    var out=[
      'SOLAR INSTALLATION QUOTE REQUEST — COMPOUND PROJECT BRIEF',
      'Prepared by homeowner; all technical details are provisional until surveyed.',
      '',
      'PROPERTY AND TIMING',
      mark('County',answer('county')),
      mark('Nearest town / area',answer('area')),
      mark('Owner / authorised decision-maker',answer('role')),
      mark('Property type',answer('building')),
      mark('Project type',answer('project')),
      mark('Preferred installation timing',answer('timing')),
      mark('Indicative budget',answer('budget'))
    ];
    if(show('protected') && show('protected')!=='Not sure')out.push(mark('Planning restrictions',show('protected')));
    out.push('','ROOF AND INSTALLATION SITE',
      mark('Mounting type',answer('roof')),
      mark('Number of roof faces',get('faces').value==='unknown'?'Not sure':get('faces').value),
      mark('Primary direction (clockwise from north)',show('azimuth')?answer('azimuth')+'°':'Not supplied — installer to survey'),
      mark('Primary roof pitch',show('pitch')?answer('pitch')+'°':'Not supplied — installer to survey'),
      mark('Roof material',answer('material')),
      mark('Visible shading',answer('shade'))
    );
    if(second)out.push(
      mark('Second direction',show('azimuth2')?answer('azimuth2')+'°':'Not supplied'),
      mark('Second pitch',show('pitch2')?answer('pitch2')+'°':'Not supplied'));
    if(show('areaM2'))out.push(mark('Approximate primary roof area',number('areaM2')+' m²'));
    ['obstacles','roofCondition','storeys','access'].forEach(function(k){
      if(show(k)&&show(k)!=='Not sure'){
        var labels={obstacles:'Obstructions',roofCondition:'Roof condition',storeys:'Building height',access:'Access/scaffolding'};
        out.push(mark(labels[k],show(k)));
      }
    });
    out.push('','ELECTRICITY AND HOUSEHOLD LOADS');
    if(show('demand'))out.push(mark('Annual electricity demand',number('demand')+' kWh'));
    if(show('bill'))out.push(mark('Monthly electricity bill','€'+number('bill')));
    if(!show('demand')&&!show('bill'))out.push('Electricity demand: To be confirmed');
    out.push(mark('Use pattern',answer('daytime')),mark('EV plans',answer('ev')),mark('Heat pump',answer('heatPump')));
    if(show('phase')&&show('phase')!=='Not sure')out.push(mark('Electricity supply',show('phase')));
    out.push('','QUOTE REQUIREMENTS',
      mark('Preferred PV size',show('kwp')?number('kwp')+' kWp':'Installer to recommend'),
      mark('Battery',get('battery').options[get('battery').selectedIndex].text),
      mark('Grant status',answer('grant')),
      mark('Previous solar quotations',answer('quotes'))
    );
    if(show('batteryKwh'))out.push(mark('Preferred battery capacity',number('batteryKwh')+' kWh'));
    ['evCharger','diverter','backup','finance'].forEach(function(k){
      if(show(k)&&!['Not sure','Quote separately','Not essential / unsure'].includes(show(k))){
        var labels={evCharger:'EV charger',diverter:'Hot-water diverter',backup:'Backup power',finance:'Funding'};
        out.push(mark(labels[k],show(k)));
      }
    });
    if(show('notes'))out.push(mark('Other requirements',show('notes')));
    if(get('faces').value!=='2' && snapshot && show('azimuth')===String(snapshot.azimuth) && show('pitch')===String(snapshot.pitch)){
      out.push('Indicative compass model (not installer-certified): '+
        (Number.isFinite(snapshot.annual)?Math.round(snapshot.annual).toLocaleString('en-IE')+' kWh/year':'not available')+
        ' at '+snapshot.azimuth+'° and '+snapshot.pitch+'° pitch.');
    }
    if(second)out.push('Two roof faces: installer to model production across both slopes; do not double-count full-array output.');
    out.push('','HOMEOWNER CONTACT / REQUEST PREFERENCES',
      mark('Preferred number of installers',answer('installerCount')),
      mark('Contact method',answer('contactMethod')),
      mark('Name',answer('name')),
      mark('Email',answer('email')),
      mark('Phone',answer('phone')),
      '',
      'REQUEST COMPARABLE WRITTEN PROPOSALS INCLUDING:',
      '• PV panels, inverter, mounting and any battery equipment.',
      '• Estimated annual production with roof and shading assumptions.',
      '• Total installed price, scaffolding, electrical work, VAT, grants and exclusions.',
      '• Workmanship and equipment warranties, monitoring and aftercare.',
      '• Timelines, SEAI registration, grid paperwork and payment terms.',
      '',
      'Homeowner-supplied details are indicative, not an installation survey.',
      'Submission goes to Compound for private review; installer sharing requires separate consent.'
    );
    root.querySelector('[data-sb-output]').value=out.join('\n');
    root.querySelector('[data-sb-copy-status]').textContent='';
  }
  fields.forEach(function(f){f.addEventListener('input',update);f.addEventListener('change',update);});
  // This expanded project form owns its own copy button; legacy template handler is disabled.
  var copy=root.querySelector('[data-sb-copy]');
  if(copy)copy.addEventListener('click',function(){
    var output=root.querySelector('[data-sb-output]'),status=root.querySelector('[data-sb-copy-status]');
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(output.value).then(function(){
        status.textContent='Project brief copied. Review it before sending to your chosen installer.';
      },function(){output.focus();output.select();status.textContent='Select and copy your project brief manually.';});
    }else{output.focus();output.select();status.textContent='Select and copy your project brief manually.';}
  });
  faceStatus();
  update();
})();