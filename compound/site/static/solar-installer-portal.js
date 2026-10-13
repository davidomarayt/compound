/* Compound Solar installer portal. No homeowner data is embedded in static files. */
(() => {
  'use strict';
  const root = document.querySelector('[data-installer-portal]');
  if (!root) return;
  const find = key => root.querySelector('[data-ip-' + key + ']');
  const read = (name) => root.dataset[name] || '';
  const serverUrl = read('supabaseUrl').trim();
  const publishableKey = read('supabasePublishableKey').trim();
  const checkoutApiUrl = read('checkoutApiUrl').trim();
  const ready = /^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/i.test(serverUrl) && publishableKey.startsWith('sb_publishable_');
  const demo = new URLSearchParams(window.location.search).get('preview') === '1';
  let supabase = null;
  let currentUser = null;
  let installer = null;
  let available = [];
  let purchases = [];
  let activeTab = 'available';
  let selectedCounty = '';
  let requestedEmail = '';

  function status(node, message, kind) {
    if (!node) return;
    node.textContent = message;
    node.dataset.state = kind || '';
  }
  function element(tag, className, value) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined && value !== null) el.textContent = String(value);
    return el;
  }
  function setScreen(name) {
    root.querySelectorAll('[data-ip-screen]').forEach(node => { node.hidden = node.dataset.ipScreen !== name; });
    find('application').hidden = name === 'dashboard';
  }
  function setText(key, value) {
    const node = find(key);
    if (node) node.textContent = value === undefined || value === null ? '—' : String(value);
  }
  const euro = cents => new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR',maximumFractionDigits:0}).format(Number(cents || 0) / 100);
  const txt = v => (v === null || v === undefined || v === '') ? 'Not specified' : String(v);
  const stock = p => Math.max(0, Number(p.max_introductions) - Number(p.sold_count || 0) - Number(p.reserved_count || 0));

  function switchTab(tab) {
    activeTab = tab;
    root.querySelectorAll('[data-ip-tab]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.ipTab === tab)));
    root.querySelectorAll('[data-ip-tab-panel]').forEach(p => { p.hidden = p.dataset.ipTabPanel !== tab; });
  }

  function projectCard(p, owned) {
    const card = element('article', 'sip-card');
    const top = element('div','sip-card-top');
    const left = element('div');
    left.append(element('p','sip-card-tag',owned?'PURCHASED INTRODUCTION':'QUALIFIED SOLAR OPPORTUNITY'));
    left.append(element('h3','',p.sku));
    left.append(element('p','sip-card-location', [p.county, p.area_general].filter(Boolean).join(' · ')));
    const price = element('div','sip-card-price');
    price.append(element('strong','',euro(owned ? (p.amount_cents || p.price_cents || 6500) : p.price_cents)));
    price.append(element('small','',owned?'Purchased':'Per introduction'));
    top.append(left,price);
    card.append(top);
    const facts = element('div','sip-project-facts');
    [
      ['Property',p.property_type],['System',p.system_kwp ? p.system_kwp+' kWp':'Installer to advise'],
      ['Roof',p.roof_orientation],['Battery',p.battery_preference],['Timing',p.installation_timeframe]
    ].forEach(([key,value]) => {
      const box = element('span');
      box.append(element('small','',key),element('b','',txt(value)));
      facts.append(box);
    });
    card.append(facts);
    const bottom = element('div','sip-card-bottom');
    const label = owned ? 'Access granted to your business' : (stock(p) + ' of '+p.max_introductions+' introduction slots available');
    bottom.append(element('span','sip-slot-count',label));
    const button = element('button','sip-button sip-button-primary',owned ? 'View secure brief ↗':'Purchase introduction ↗');
    button.type = 'button';
    if (demo) {
      button.disabled = true;
      button.textContent = 'Preview only — not for sale';
    } else if (!owned && !checkoutApiUrl) {
      button.disabled = true;
      button.textContent = 'Purchasing opens soon';
    } else if (!owned && stock(p) === 0) {
      button.disabled = true;
      button.textContent = 'Sold out';
    } else {
      if (owned) button.addEventListener('click', () => openBrief(p,card,button));
      else button.addEventListener('click', () => purchase(p,button));
    }
    bottom.append(button);
    card.append(bottom);
    return card;
  }

  function render() {
    const purchasedProjects = purchases.map(order => ({
      ...(order.solar_lead_teasers || {}),
      project_id:order.project_id,
      order_id:order.id,
      amount_cents:order.amount_cents
    })).filter(item => item.sku);
    const purchasedIds = new Set(purchases.map(x => x.project_id));
    const visible = available.filter(p => !purchasedIds.has(p.id) && (!selectedCounty || p.county === selectedCounty) && stock(p) > 0);
    const list = find('available-list');
    const bought = find('purchased-list');
    list.replaceChildren(...visible.map(p => projectCard(p,false)));
    bought.replaceChildren(...purchasedProjects.map(p => projectCard(p,true)));
    find('available-empty').hidden = visible.length !== 0;
    find('purchased-empty').hidden = purchasedProjects.length !== 0;
    setText('total',available.filter(p => !purchasedIds.has(p.id) && stock(p) > 0).length);
    setText('purchased-total',purchasedProjects.length);
    setText('tab-available',available.filter(p => !purchasedIds.has(p.id) && stock(p) > 0).length);
    setText('tab-purchased',purchasedProjects.length);
    const counties = [...new Set(available.map(p => p.county))].filter(Boolean).sort();
    const select = find('county-filter');
    const original = select.value;
    select.replaceChildren(new Option('All service counties',''),...counties.map(x => new Option(x,x)));
    select.value = counties.includes(original) ? original : '';
    selectedCounty = select.value;
  }

  async function purchase(p, button) {
    if (demo || !ready || !checkoutApiUrl || !installer) return;
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Preparing secure checkout…';
    try {
      const {data:{session}, error:sessionError} = await supabase.auth.getSession();
      if (sessionError || !session) throw new Error('Sign in again to continue.');
      const response = await fetch(checkoutApiUrl, {
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer '+session.access_token},
        body:JSON.stringify({project_id:p.id})
      });
      const result = await response.json();
      if (!response.ok || !result.url || new URL(result.url).hostname !== 'checkout.stripe.com') throw new Error(result.message || 'Checkout is unavailable.');
      window.location.assign(result.url);
    } catch (error) {
      status(find('dashboard-status'),error.message || 'Unable to begin checkout.','error');
      button.disabled = false;
      button.textContent = original;
    }
  }

  async function openBrief(p,card,button) {
    if (demo || !ready || !installer) return;
    button.disabled = true;
    button.textContent = 'Opening secure brief…';
    try {
      // RLS grants access only to this installer’s paid, access_granted project.
      const {data,error} = await supabase.from('solar_lead_details')
        .select('project_id,homeowner_name,homeowner_email,homeowner_phone,eircode,brief')
        .eq('project_id',p.project_id).maybeSingle();
      if (error || !data) throw new Error('This brief is not available to your account.');
      const previous = card.querySelector('.sip-private-brief');
      if (previous) { previous.remove();button.disabled=false;button.textContent='View secure brief ↗';return; }
      const section = element('section','sip-private-brief');
      section.append(element('h4','', 'Secure project brief · '+p.sku));
      const details = element('dl');
      [
        ['Homeowner',data.homeowner_name],['Email',data.homeowner_email],['Phone',data.homeowner_phone],
        ['Eircode',data.eircode],
        ...Object.entries(data.brief || {}).filter(([k,v]) => v !== null && typeof v !== 'object').map(([k,v]) => [k.replace(/_/g,' '),String(v)])
      ].forEach(([key,value])=>{
        const pair=element('div');pair.append(element('dt','',key),element('dd','',txt(value)));details.append(pair);
      });
      section.append(details);
      section.append(element('p','', 'Use these details only for the quotation requested by the homeowner. Do not share or use them for unrelated marketing.'));
      card.append(section);
      button.textContent='Hide secure brief ↑';
      button.disabled=false;
    } catch (error) {
      status(find('dashboard-status'),error.message || 'Unable to show this brief.','error');
      button.disabled=false;button.textContent='View secure brief ↗';
    }
  }

  function showDashboard() {
    setScreen('dashboard');
    setText('company',installer.company_name);
    setText('account-name',installer.company_name);
    setText('account-email',currentUser?.email || '—');
    setText('account-registration',installer.seai_registration || 'Awaiting verification');
    setText('account-counties',Array.isArray(installer.service_counties) ? installer.service_counties.join(', ') : '—');
    setText('account-verification',installer.verification_status || '—');
    find('demo-warning').hidden = !demo;
    setText('mode',demo?'EXAMPLE DASHBOARD':'APPROVED ACCOUNT');
    render();
    switchTab(activeTab);
  }

  async function loadDashboard() {
    if (!currentUser || !supabase) return;
    status(find('message'),'Checking installer approval…');
    const {data:profile,error:profileError} = await supabase.from('solar_installer_accounts')
      .select('id,company_name,seai_registration,service_counties,verification_status')
      .eq('owner_user_id',currentUser.id).maybeSingle();
    if (profileError) {status(find('message'),'Could not check your installer account. Please retry.','error');return;}
    if (!profile || profile.verification_status !== 'approved') {
      setScreen('signin');
      status(find('message'),'This email is not yet linked to an approved installer account. Apply for access or contact Compound Solar.','error');
      return;
    }
    installer=profile;
    const [leads,orders]=await Promise.all([
      supabase.from('solar_lead_teasers').select('id,sku,county,area_general,property_type,system_kwp,roof_orientation,battery_preference,installation_timeframe,price_cents,max_introductions,sold_count,reserved_count,status').eq('status','active').order('created_at',{ascending:false}).limit(100),
      supabase.from('solar_lead_purchases').select('id,project_id,amount_cents,status,purchased_at,solar_lead_teasers(sku,county,area_general,property_type,system_kwp,roof_orientation,battery_preference,installation_timeframe)').eq('installer_id',profile.id).eq('status','access_granted').order('purchased_at',{ascending:false}).limit(100)
    ]);
    if (leads.error || orders.error) {
      status(find('message'),'Could not load projects. Please try signing in again.','error');
      return;
    }
    available=leads.data||[];
    purchases=orders.data||[];
    showDashboard();
  }

  async function startAuth() {
    if (!ready || demo) return;
    try {
      // External client code is only loaded after configuration; no credentials in repository.
      const module = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.58.0/+esm');
      supabase = module.createClient(serverUrl,publishableKey,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
      supabase.auth.onAuthStateChange((_event,session) => {
        const newUser=session?.user || null;
        if (!newUser) {currentUser=null;installer=null;setScreen('signin');return;}
        if (!currentUser || currentUser.id !== newUser.id) { currentUser=newUser;void loadDashboard(); }
      });
      const {data,error}=await supabase.auth.getUser();
      if (!error && data?.user) {currentUser=data.user;await loadDashboard();}
      find('prelaunch').hidden=true;
      find('send').disabled=false;
    } catch (error) {
      status(find('message'),'Installer sign-in is temporarily unavailable. Please contact Compound Solar.','error');
    }
  }

  find('email-form').addEventListener('submit',async e=>{
    e.preventDefault();
    if (!ready || !supabase) {status(find('message'),'Installer login is not open yet. You can apply for the pilot below.');return;}
    const email=find('email-form').elements.email.value.trim().toLowerCase();
    if (!/^\S+@\S+\.\S+$/.test(email)) {status(find('message'),'Enter a valid company email address.','error');return;}
    find('send').disabled=true;
    requestedEmail=email;
    const {error}=await supabase.auth.signInWithOtp({email,options:{shouldCreateUser:false}});
    find('send').disabled=false;
    if (error) {status(find('message'),'Could not send a code. Please try again or contact Compound Solar.','error');return;}
    find('email-form').hidden=true;
    find('code-form').hidden=false;
    find('code').focus();
    status(find('message'),'If this email has an approved account, a login code is on its way.','success');
  });
  find('code-form').addEventListener('submit',async e=>{
    e.preventDefault();
    if (!ready || !supabase) return;
    const code=find('code').value.trim();
    if (!/^\d{6}$/.test(code)) {status(find('message'),'Enter the six-digit code from your email.','error');return;}
    const {data,error}=await supabase.auth.verifyOtp({email:requestedEmail,token:code,type:'email'});
    if (error || !data?.user) {status(find('message'),'The code was invalid or expired. Request a new one.','error');return;}
    currentUser=data.user;
    status(find('message'),'Signed in. Loading your account…','success');
    await loadDashboard();
  });
  find('code-back').addEventListener('click',()=>{
    find('code-form').hidden=true;find('email-form').hidden=false;find('code').value='';
    status(find('message'),'');
  });
  find('application-form').addEventListener('submit',e=>{
    e.preventDefault();
    const form=e.currentTarget;
    if (!form.reportValidity()) return;
    const fields=Object.fromEntries(new FormData(form));
    const body=['Compound Solar installer portal application','','Company: '+fields.company,'Email: '+fields.email,
      'SEAI registration: '+fields.registration,'Counties served: '+fields.counties,'','Please review my company for installer portal access.'].join('\n');
    const link='mailto:david@compound.ie?subject='+encodeURIComponent('Compound Solar — installer access application')+'&body='+encodeURIComponent(body);
    window.location.href=link;
    status(find('application-status'),'Your email application has been prepared. Please send it from your email app.','success');
  });
  root.querySelectorAll('[data-ip-tab]').forEach(button=>button.addEventListener('click',()=>switchTab(button.dataset.ipTab)));
  find('county-filter').addEventListener('change',e=>{selectedCounty=e.target.value;render();});
  find('signout').addEventListener('click',async()=>{
    if (demo) {const clean=new URL(window.location);clean.searchParams.delete('preview');window.location.assign(clean.toString());return;}
    if (supabase) await supabase.auth.signOut();
    currentUser=null;installer=null;available=[];purchases=[];setScreen('signin');
  });

  if (demo) {
    installer={company_name:'Example Solar Installer',seai_registration:'Preview account',service_counties:['Meath','Dublin','Kildare'],verification_status:'Demonstration'};
    currentUser={email:'preview@example.invalid'};
    available=[
      {id:'demo-1',sku:'SOL-MH-DEMO-00421',county:'Meath',area_general:'Mid-Meath',property_type:'Detached house',system_kwp:6,roof_orientation:'South-west',battery_preference:'Compare both options',installation_timeframe:'Within 3 months',max_introductions:3,sold_count:0,reserved_count:0,price_cents:6500},
      {id:'demo-2',sku:'SOL-D-DEMO-00422',county:'Dublin',area_general:'South Dublin',property_type:'Semi-detached house',system_kwp:4.5,roof_orientation:'East / west',battery_preference:'Solar PV only',installation_timeframe:'3–6 months',max_introductions:2,sold_count:1,reserved_count:0,price_cents:6500},
      {id:'demo-3',sku:'SOL-KE-DEMO-00423',county:'Kildare',area_general:'North Kildare',property_type:'Bungalow',system_kwp:8,roof_orientation:'South',battery_preference:'Battery requested',installation_timeframe:'As soon as practical',max_introductions:3,sold_count:2,reserved_count:0,price_cents:6500}
    ];
    purchases=[];
    showDashboard();
  } else {
    find('send').disabled=!ready;
    if (ready) void startAuth();
    else status(find('message'),'Pilot access is not open yet. Installer applications can be prepared below.');
  }
})();
