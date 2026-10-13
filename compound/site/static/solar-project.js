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
  function update(){
    var second=get('faces').value==='2';
    root.querySelector('[data-sp-second]').hidden=!second;
    var essential=['county','area','role','building','timing','roof','azimuth','pitch'];
    var complete=essential.filter(function(k){return show(k)!==''}).length;
    var energy=show('demand')!==''||show('bill')!=='';
    if(energy)complete++;
    if(show('battery'))complete++;
    if(show('installerCount'))complete++;
    var total=essential.length+3,pct=Math.round(100*complete/total);
    root.querySelector('[data-sp-progress]').textContent=pct+'%';
    root.querySelector('[data-sp-progress-bar]').style.width=pct+'%';
    root.querySelector('[data-sp-progress-note]').textContent=pct===100?
      'Your preliminary project profile is well described. A site survey is still required.':
      (total-complete)+' key answers remaining. Unknown technical details are fine.';
    var tags=[];
    if(show('county'))tags.push(show('county'));
    if(show('building'))tags.push(show('building'));
    if(show('azimuth'))tags.push(show('azimuth')+'° roof bearing');
    if(show('demand'))tags.push(number('demand')+' kWh annual use');
    if(show('kwp'))tags.push(number('kwp')+' kWp proposed');
    if(show('timing'))tags.push(show('timing'));
    var el=root.querySelector('[data-sp-tags]');
    el.replaceChildren();
    (tags.length?tags:['Add your location and solar needs']).forEach(function(t){var span=document.createElement('span');span.textContent=t;el.appendChild(span);});
    var out=[
      'SOLAR INSTALLATION QUOTE REQUEST — COMPOUND PROJECT BRIEF',
      'Prepared by homeowner. Not a professional solar PV survey.',
      '',
      'PROPERTY',
      mark('County',answer('county')),
      mark('General area',answer('area')),
      mark('Authorisation to proceed',answer('role')),
      mark('Building type',answer('building')),
      mark('Project type',answer('project')),
      mark('Desired installation',answer('timing')),
      mark('Budget indication',answer('budget')),
      mark('Planning considerations',answer('protected')),
      '',
      'ROOF AND INSTALLATION SITE',
      mark('Mounting type',answer('roof')),
      mark('Number of roof faces',get('faces').value==='unknown'?'Not sure':get('faces').value),
      mark('Primary direction (clockwise from north)',show('azimuth')?answer('azimuth')+'°':'To be confirmed'),
      mark('Primary pitch',show('pitch')?answer('pitch')+'°':'To be confirmed'),
      mark('Primary usable area',show('areaM2')?number('areaM2')+' m²':'To be confirmed'),
    ];
    if(second)out.push(
      mark('Second direction',show('azimuth2')?answer('azimuth2')+'°':'To be confirmed'),
      mark('Second pitch',show('pitch2')?answer('pitch2')+'°':'To be confirmed'),
      mark('Second usable area',show('areaM22')?number('areaM22')+' m²':'To be confirmed'));
    out.push(
      mark('Roof material',answer('material')),
      mark('Visible shading',answer('shade')),
      mark('Obstructions',answer('obstacles')),
      mark('Roof condition',answer('roofCondition')),
      mark('Storeys',answer('storeys')),
      mark('Access or scaffolding',answer('access')),
      '',
      'ELECTRICITY AND HOUSEHOLD LOADS',
      mark('Annual electricity demand',show('demand')?number('demand')+' kWh':'Not known'),
      mark('Monthly bill',show('bill')?'€'+number('bill'):'Not known'),
      mark('Use pattern',answer('daytime')),
      mark('Meter',answer('smartMeter')),
      mark('Phase',answer('phase')),
      mark('Distribution board',answer('board')),
      mark('EVs and planned charging',answer('ev')),
      mark('Heat pump',answer('heatPump')),
      mark('Immersion',answer('immersion')),
      mark('Existing PV',answer('existingPV')),
      '',
      'QUOTE REQUIREMENTS',
      mark('Desired PV capacity',show('kwp')?number('kwp')+' kWp':'Request installer recommendation'),
      mark('Battery',get('battery').options[get('battery').selectedIndex].text),
      mark('Preferred usable battery size',show('batteryKwh')?number('batteryKwh')+' kWh':'Installer to advise'),
      mark('EV charger',answer('evCharger')),
      mark('Immersion diverter',answer('diverter')),
      mark('Backup capability',answer('backup')),
      mark('Grant status',answer('grant')),
      mark('Payment plan',answer('finance')),
      mark('Existing quotes',answer('quotes')),
      mark('Inverter / cable route',answer('cable')),
      mark('Other requirements',answer('notes')),
      '',
      'AVAILABLE SUPPORTING IMAGES (SHARE PRIVATELY AFTER CHOOSING INSTALLER)',
      'Roof photographs: '+show('photoRoof'),
      'Chimneys / shade: '+show('photoShade'),
      'Closed electrical board / meter area: '+show('photoBoard'),
      'Proposed equipment location: '+show('photoRoute'),
    );
    if(snapshot && show('azimuth')===String(snapshot.azimuth) && show('pitch')===String(snapshot.pitch)){
      out.push('Indicative compass model (not installer-certified): '+
        (Number.isFinite(snapshot.annual)?Math.round(snapshot.annual).toLocaleString('en-IE')+' kWh/year':'not available')+
        ' at '+snapshot.azimuth+'° and '+snapshot.pitch+'° pitch.');
    }
    out.push('','HOMEOWNER CONTACT / REQUEST PREFERENCES',
      mark('Number of installers requested',answer('installerCount')),
      mark('Contact method',answer('contactMethod')),
      mark('Name',answer('name')),
      mark('Email',answer('email')),
      mark('Phone',answer('phone')),
      mark('Eircode (only share privately with chosen provider)',answer('eircode')),
      '',
      'PLEASE QUOTE ON THE SAME ASSUMPTIONS:',
      '• Panels: proposed quantity, power and model; array size and roof-face layout.',
      '• Inverter: model, capacity and any generation/export limits.',
      '• Roof mounting, scaffolding, wiring, meter/consumer-unit work and exclusions.',
      '• Annual generation projection and assumptions about roof, shade and system loss.',
      '• Solar-only price and solar-plus-battery price separately (where relevant).',
      '• Gross installed price before grants, grants assumed, applicable VAT and net price.',
      '• Warranties, expected maintenance, monitoring, certifications and aftercare.',
      '• SEAI registration, grant/NC6 paperwork, terms, lead time and payment schedule.',
      '',
      'All facts supplied by homeowner. Final quote subject to survey and safety checks.',
      'This brief is copied locally by the homeowner; Compound has not transmitted it.'
    );
    root.querySelector('[data-sb-output]').value=out.join('\n');
    root.querySelector('[data-sb-copy-status]').textContent='';
  }
  fields.forEach(function(f){f.addEventListener('input',update);f.addEventListener('change',update);});
  // Existing solar-hub.js already owns copy button and respects browser clipboard permissions.
  update();
})();