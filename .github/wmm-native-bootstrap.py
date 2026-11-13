"""One-time reviewed import of the captured public chart evidence.
Runs only on the isolated feature branch; it cannot publish production.
The resulting JSON, page metadata and primary-source captures are committed
as ordinary, inspectable repository files. Remove this bootstrap after import.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import unicodedata

R=Path(__file__).resolve().parents[1]
E=Path(os.environ['WMM_EVIDENCE_DIR']).resolve()
assert hashlib.sha256((E/'manifest.json').read_bytes()).hexdigest()=='3515ad2139ac55c13a62ede2fdd407d2767e35b18a4ee45435273cde630413a5'
B='/wheres-my-money/spending/'
META={
'socialprotection':('social-protection','Social protection','Income supports, pensions and family payments','Explore pensions, working-age income supports, children’s payments and disability and carer supports. This is the public cost of the programmes, not a calculation of your household’s entitlements.','The source separates “Pensions” (the non-contributory State Pension) from “Pension” (contributory and related payments). Both are retained below; they are different categories, not duplicates.',[('State Pension guide','/wealth/state-pension-ireland/'),('PRSI calculator','/prsi-calculator/'),('Pension planning tools','/tools/')]),
'health':('health','Health','Healthcare funding, capital services and HSE regions','Follow the published health allocation through capital services, national programmes and the six HSE regional health areas. The figures describe funding categories; they are not hospital waiting-time or quality scores.','The six regional health area lines are accounting groupings, not six extra budgets to add to total health spending. They do not give a reliable county-by-county split or separate prices for every clinical service.',[('Health insurance comparison','/health-insurance-cost-comparison-calculator/'),('Health guides','/health/'),('Your tax receipt','/wheres-my-money/#your-receipt')]),
'housing':('housing','Housing and local government','Housing, water, planning and local services','Explore the housing sector’s published allocation, including the housing department, Uisce Éireann, Tailte Éireann and the Electoral Commission. The sector is wider than building or subsidising homes.','Uisce Éireann appears as a separate 2026 line. A zero in an earlier source category is not evidence that water services had no funding then. Departmental transfers can change the shape of the series.',[('Buying a home guide','/wealth/buying-a-home-in-ireland/'),('Mortgage calculator','/mortgage-calculator/'),('Local Property Tax calculator','/local-property-tax-calculator/')]),
'education':('education','Education','School salaries, supports, pensions and buildings','See how the first, second and early-years education allocation divides between teaching salaries, special needs assistants, school transport, grants and infrastructure. Higher education sits in a separate sector grouping.','The source has one top-level school programme, so this page opens its detailed lines directly rather than making you visit a duplicate page. School meals are in Social Protection; further and higher education is under Additional Departments.',[('Childcare cost calculator','/childcare-return-to-work-calculator/'),('Saving for your child','/wealth/saving-for-your-child-ireland/'),('Family planning tools','/tools/')]),
'transport':('transport','Transport','Public transport, roads, active travel and safety','Explore public transport, road networks, active travel, aviation and maritime spending. Programme detail distinguishes published operating, administrative and investment lines where the source provides them.','An annual allocation is not the lifetime cost of a railway, road or other capital project. Construction schedules, delivery outputs and multi-year contracts require separate evidence.',[('EV and motoring tools','/tools/'),('Car finance calculator','/car-finance-calculator/'),('Your tax receipt','/wheres-my-money/#your-receipt')]),
'justice':('justice','Justice and migration','Policing, prisons, courts and justice programmes','Compare the allocations for An Garda Síochána, prisons, courts, justice and migration, and oversight bodies. The source’s broad migration programme is shown as published, without inventing a more detailed accommodation or nationality split.','For several bodies the official drill-down repeats the full body total as one line. Those are shown as single allocations, not artificially split into staffing, vehicles or individual services.',[('Your tax receipt','/wheres-my-money/#your-receipt'),('Income tax calculator','/income-tax-calculator/'),('Finance guides','/wealth/')]),
'debt':('debt-and-eu','Debt, EU and other non-voted spending','Debt service, EU contributions and other central items','Separate the service of national debt, the EU Budget contribution and other non-voted expenditure. The sector total is not a measure of the size of Ireland’s national debt.','These are annual spending flows, not the outstanding debt stock. Other non-voted expenditure is a separate source category and must not all be described as debt interest. Non-voted spending is not assigned a current/capital split in this source.',[('Debt repayment calculator','/debt-repayment-calculator/'),('Compound interest calculator','/compound-interest-calculator/'),('Public spending methodology','/wheres-my-money/methodology/')]),
'other':('other-departments','Additional departments','Agriculture, disability, enterprise, defence and more','Open the departments grouped outside the seven other headline sectors. This includes children and disability, further and higher education, agriculture, defence, climate, culture and public administration.','“Additional departments” is a grouping, not a separate administrative agency or a measure of overhead. Each department below has its own published programme breakdown.',[('Pensions guide','/wealth/pensions-in-ireland/'),('Solar and home energy','/solar/'),('Finance tools','/tools/')])
}
FRIENDLY={
'Pensions':('non-contributory-state-pension','Non-contributory State Pension','The source calls this “Pensions” and identifies the State Pension (Non-contributory) as its single component. It is separate from the contributory pension group.'),
'Pension':('contributory-and-related-pensions','Contributory and related pensions','This source group contains the State Pension (Contributory), bereaved partner contributory pension and the widow’s death benefit. It is not the non-contributory State Pension line.'),
'Children':('children-and-family-payments','Children and family payments','Child Benefit, Working Family Payment and school meals appear here. The programme total is larger than the displayed component lines; the unexplained balance is shown rather than assigned to an invented scheme.'),
'Auto-enrolment':('pension-auto-enrolment','Pension auto-enrolment','Separate the State contribution from the allocation for the National Automatic Enrolment Retirement Savings Authority. These are public allocations, not the employee’s pension deduction.'),
'Illness, Disability And Carers':('illness-disability-and-carers','Illness, disability and carers','This group covers income-support programmes. It is distinct from disability services within the Children, Disability and Equality department. The displayed component list does not account for the whole programme total.'),
'Working Age - Income Supports':('working-age-income-supports','Working-age income supports','Explore the published income-support payment lines. An allocation describes scheme expenditure, not the amount any particular claimant receives. The source’s component coverage is incomplete.'),
'Working Age - Employment Supports':('employment-supports','Employment supports','Compare the published employment-support scheme lines within this programme. Funding totals alone do not show how many people entered or retained employment.'),
'Supplementary Payments, Agencies And Miscellaneous Services':('supplementary-payments-and-agencies','Supplementary payments and agencies','This is a source-defined grouping of supplementary payments, agencies and miscellaneous services. Its displayed line items leave a balance that cannot be assigned to individual schemes from this source alone.'),
'Administration':('social-protection-administration','Social Protection administration','The published administration lines distinguish operating costs within Social Protection. Do not treat the entire administration allocation as avoidable savings.'),
'Health (Admin)':('department-of-health-administration','Department of Health administration','This is the Department of Health administration grouping. HSE corporate administration is a separate published programme; the two labels should not be substituted for each other.'),
'Capital Services':('health-capital-services','Health capital services','Compare the capital service lines published within the health allocation. This annual capital provision is not the completed value or lifetime cost of a named hospital project.'),
'Grants':('health-grants','Health grants','These are the grant lines explicitly itemised in the health source. They are a subset of the wider health budget, not all grants or purchased services across the HSE.'),
'Other Services':('other-health-services','Other health services','Explore the services placed in this specific source grouping. It is distinct from the separate “Other HSE Services” programme and should not be merged simply because the labels sound similar.'),
'Other Hse Services':('other-hse-services','Other HSE services','These are the itemised lines in the source’s Other HSE Services programme. The source also contains a different Other Services grouping; each keeps its own total here.'),
'Care Programme':('care-programme','Care programme','Open the three published care-programme lines. These categories do not establish how spending is distributed across individual patients, hospitals or counties.'),
'Housing, Local Government and Heritage (Gross)':('housing-local-government-and-heritage','Housing, Local Government and Heritage','This department’s programmes include housing, planning, heritage, local government, water and marine services, and Met Éireann. Its total is not exclusively expenditure on housing delivery.'),
'Justice, Home Affairs And Migration (Gross)':('justice-home-affairs-and-migration','Justice, Home Affairs and Migration','The department’s source breakdown separates criminal justice, civil justice and migration. These are programme totals; no unsupported subdivision of migration spending is inferred.'),
'Further and Higher Education, Research, Innovation and Science':('further-higher-education-and-research','Further and higher education and research','Explore higher education, skills, research and the remaining published expenditure heading. One source line uses an accounting code; its original label is retained rather than guessed.'),
'Children, Disability And Equality':('children-disability-and-equality','Children, disability and equality','Explore the department’s five published programmes. These are service and agency allocations; disability income payments and Child Benefit appear separately in Social Protection.'),
'Public Expenditure, Infrastructure, Public Service Reform And Digitalisation':('public-expenditure-and-reform','Public expenditure and reform','This department group includes several offices and public-service functions. Repeated source labels are retained as separate numbered rows so their amounts are not silently lost or counted twice.'),
'Defence':('defence','Defence','The source separates Defence Forces pensions from the Defence allocation. Adding the parent total to either component would double-count the same funding.'),
'Agriculture, Food And The Marine':('agriculture-food-and-marine','Agriculture, food and marine','Compare the four published agriculture, food, seafood and policy programmes. These State expenditure figures are not a total measure of farm incomes or all European agricultural support.'),
'Climate, Energy And The Environment':('climate-energy-and-environment','Climate, energy and environment','The source separates climate, energy and the circular economy. Climate-related expenditure may also appear in other departments, so this is not a complete cross-government climate-spending total.'),
'Enterprise, Tourism And Employment':('enterprise-tourism-and-employment','Enterprise, tourism and employment','Explore jobs and enterprise development, innovation, regulation and tourism within this department group. Spending does not by itself establish the number of jobs created.'),
'Culture, Communications And Sport':('culture-communications-and-sport','Culture, communications and sport','The four programmes cover culture, communications, media and sport. Their different remits are kept visible rather than presented as a single cultural subsidy.'),
'Foreign Affairs And Trade':('foreign-affairs-and-trade','Foreign affairs and trade','Explore the published international, development and other departmental programme lines. The full department total should not automatically be described as overseas aid.'),
'Rural And Community Development And The Gaeltacht':('rural-community-and-gaeltacht','Rural, community and Gaeltacht','The source separates rural development, community development and the Gaeltacht. These allocations describe programme funding, not an estimate of spending in each county.'),
'Finance':('finance','Finance','Explore the Finance group’s published office and service allocations. Expenditure on the Revenue Commissioners is not the same thing as the taxes Revenue collects.'),
'Taoiseach':('taoiseach','Taoiseach’s department group','This source group includes several offices and bodies as well as the Department of the Taoiseach. It is not simply the cost of the Taoiseach’s personal office.')
}
def slug(text):
    text=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    return re.sub('[^a-z0-9]+','-',text).strip('-')
def clean(text):
    return text.replace('Hse','HSE').replace('Rha','RHA').replace('Etb','ETB').replace('Snas','SNAs').replace(' Of ',' of ').replace(' And ',' and ').replace(' The ',' the ').replace(' (Gross)','')
def friendly(label,key):
    if label in FRIENDLY:return FRIENDLY[label]
    name=clean(label)
    if key=='transport':
        name={'Information Technology, Engagement And Research Delivery':'IT, engagement and research','Sustainable Mobility - Public Transport':'Public transport','Road Networks And Road Safety':'Road networks and road safety','Civil Aviation':'Civil aviation','Sustainable Mobility - Active Travel And Greenways':'Active travel and greenways','Maritime Transport And Safety':'Maritime transport and safety'}[label]
        return slug(name),name,f'This page opens the published {name.lower()} allocation into its component lines. Administrative and delivery expenditure are kept as the source reports them; the total is not a promise of a particular service level.'
    return slug(name),name,''
raw={key:json.loads((E/(key+'.json')).read_text(encoding='utf-8')) for key in ['national']+list(META)}
D={'year':2026,'updated':'2026-11-13','source_updated':'October 2026','years':list(range(2016,2027)),'comparison_years':[2024,2025,2026], 'total':raw['national']['charts'][0]['series'][0]['data'][10],'history':raw['national']['charts'][0]['series'][0]['data'][:11],'source':raw['national']['url'],'method_source':'https://www.whereyourmoneygoes.gov.ie/en/about/','source_hashes':{key:hashlib.sha256((E/(key+'.json')).read_bytes()).hexdigest() for key in raw},'sectors':[]}
for key,meta in META.items():
    source=raw[key];s_slug,s_name,tagline,intro,note,related=meta
    trend=source['charts'][0]; chart=source['charts'][1];comparison=source['charts'][2]
    types={x['name']:x['y'] for x in source['charts'][3]['series'][0]['data']}
    years=trend['xAxes'][0]['categories'];values=trend['series'][0]['data']
    s={'key':key,'slug':s_slug,'name':s_name,'tagline':tagline,'intro':intro,'note':note,'url':B+s_slug+'/','source':source['url'],'total':values[years.index(2026)],'years':[y for y in years if y<=2026],'history':[v for y,v in zip(years,values) if y<=2026],'current':types.get('Current',0),'capital':types.get('Capital',0),'related':[{'name':a,'url':b} for a,b in related],'programmes':[]}
    detail={x['id']:x['data'] for x in chart['drilldown']}
    for item in chart['series'][0]['data']:
        original=item['name'];p_slug,p_name,p_note=friendly(original,key)
        lines=detail[item['drilldown']];idx=comparison['xAxes'][0]['categories'].index(original)
        history=[v['data'][idx] for v in comparison['series']]
        has_detail=len(lines)>1 and key!='education'
        p={'slug':p_slug,'name':p_name,'original':original,'total':item['y'],'history':history,'detail':has_detail,'url':s['url']+p_slug+'/' if has_detail else s['url']+'#'+p_slug,'note':p_note,'lines':[[clean(a),int(b)] for a,b in lines]}
        p['gap']=p['total']-sum(v for _,v in p['lines'])
        s['programmes'].append(p)
    s['gap']=s['total']-sum(p['total'] for p in s['programmes']);D['sectors'].append(s)
D['sector_gap']=D['total']-sum(s['total'] for s in D['sectors'])
D['current']=sum(s['current'] for s in D['sectors']);D['capital']=sum(s['capital'] for s in D['sectors'])
assert D['total']==132996715000 and D['sector_gap']==0
assert sum(len(s['programmes']) for s in D['sectors'])==57
assert sum(len(p['lines']) for s in D['sectors'] for p in s['programmes'])==228
(R/'content/public-spending-detail-2026.json').write_text(json.dumps(D,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
dest=R/'content/public-spending-sources/2026';dest.mkdir(parents=True,exist_ok=True)
for key in raw:shutil.copyfile(E/(key+'.json'),dest/(key+'.json'))
(dest/'provenance.json').write_text(json.dumps({'captured_at':'2026-11-13T07:53:20.567443+00:00','source_vintage':'October 2026','capture_run':43388890985,'source':D['source'],'methodology_url':D['method_source'],'scope':'Gross voted and non-voted expenditure. Voted data excludes centrally held unallocated funding.','basis':{'2016-2024':'Voted actual expenditure returns / latest non-voted outturn.','2025':'Voted provisional outturn estimates / latest non-voted Exchequer outturn.','2026':'Revised Estimates for voted expenditure / fiscal forecast projections for non-voted.','2027':'Present in source capture but not used in published 2026 library.'},'note':'Raw public chart series preserved for provenance. Website styling and scripts are not reused.'},indent=2)+'\n',encoding='utf-8')
subprocess.run(['python','scripts/sync_wmm_views.py'],cwd=R,check=True)

def replace(path,before,after):
    file=R/path;text=file.read_text(encoding='utf-8')
    assert before in text,'Missing integration anchor: '+path
    file.write_text(text.replace(before,after,1),encoding='utf-8')
# Existing page pipeline provides sitemap and search entries automatically.
p='compound/site/templates/page.html'
replace(p,'{% extends "base.html" %}','{% extends "base.html" %}\n{% set is_wmm = page.slug.startswith("wmm-") %}\n{% if is_wmm %}{% set wmm_page = true %}{% endif %}')
replace(p,'{% block meta %}\n','{% block meta %}\n{% if is_wmm %}<meta name="description" content="{{ page.meta_description }}">{% else %}\n')
replace(p,'{% endblock %}\n{% block head %}','{% endif %}\n{% endblock %}\n{% block head %}')
replace(p,'<link rel="canonical" href="{{ site_url }}{{ page.url }}">','<link rel="canonical" href="{{ site_url }}{{ page.url }}">\n{% if is_wmm %}{% include "_wmm_explorer_head.html" %}{% endif %}')
replace(p,'{% block post_styles %}','{% block post_styles %}\n{% if is_wmm %}<link rel="stylesheet" href="/static/wheres-my-money.css?v=20261113-ads1"><link rel="stylesheet" href="/static/wmm-explorer.css?v=20261113-native1"><script defer src="/static/wmm-explorer.js?v=20261113-native1"></script><script defer src="/static/wheres-my-money-ads.js?v=20261113-1"></script>{% endif %}')
replace(p,'{% block content %}\n','{% block content %}\n{% if is_wmm %}{% include "_wmm_explorer.html" %}{% else %}\n')
f=R/p;s=f.read_text(encoding='utf-8');s=s.rsplit('{% endblock %}',1)[0]+'{% endif %}\n{% endblock %}\n';f.write_text(s,encoding='utf-8')
p='compound/site/static/wheres-my-money.js'
replace(p,'var share = category.billion/data.total_billion;','var share = category.exact_eur && data.exact_total_eur ? category.exact_eur/data.exact_total_eur : category.billion/data.total_billion;')
replace(p,'money(result.payroll*c.billion/data.total_billion)','money(result.payroll*(c.exact_eur && data.exact_total_eur ? c.exact_eur/data.exact_total_eur : c.billion/data.total_billion))')
replace(p,"    c.themes.forEach(function (item) {var li=document.createElement('li');li.textContent=item;themes.append(li);});\n    q('#wmm-sector-source').href=c.source;", """    (c.detail_links || c.themes).forEach(function (item) {
      var li=document.createElement('li');
      if (typeof item === 'object' && item.url && item.url.indexOf('/wheres-my-money/')===0) {
        var link=document.createElement('a');link.href=item.url;link.textContent=item.name;li.append(link);
      } else {li.textContent=typeof item==='string'?item:item.name;}
      themes.append(li);
    });
    q('#wmm-sector-source').href=c.url || '/wheres-my-money/spending/';""")
p='compound/site/templates/wheres_my_money.html'
changes=[('/static/wheres-my-money.js?v=20261113-1','/static/wheres-my-money.js?v=20261113-native1'),('<a href="{{ spending.source }}" target="_blank" rel="noopener noreferrer">View the source data ↗</a>','<a href="/wheres-my-money/spending/">Explore the full spending library →</a>'),('<span>Official source linked</span>','<span>Native programme detail</span>'),('<a href="#spending">Spending explorer</a>','<a href="#spending">Spending explorer</a><a href="/wheres-my-money/spending/">Spending library</a>'),('<a href="{{ c.source }}">Source ↗</a>',"<a href=\"{{ c.url or '/wheres-my-money/spending/' }}\">Explore the breakdown →</a>"),('<p class="wmm-detail-label">Services you can investigate</p>','<p class="wmm-detail-label">Published programmes · open the detail</p>'),('These are navigation themes, not independently priced subcategories. Deeper amounts will appear only when validated official programme data is available.','Open a programme to explore its published allocations, history and source notes on Compound. Not every service has a separately published budget.'),('<a id="wmm-sector-source" href="{{ spending.source }}" target="_blank" rel="noopener noreferrer">Read official sector figures ↗</a>','<a id="wmm-sector-source" href="/wheres-my-money/spending/health/">Explore this sector on Compound →</a>'),("Sector totals are the government's 2026 published estimates, rounded to €0.1bn. Personal sector amounts are illustrative: your payroll taxes × sector spending ÷ total spending.",'Headline sector totals are rounded to €0.1bn. Personal shares use the underlying published euro amounts: your payroll taxes × sector spending ÷ total spending. <a href="/wheres-my-money/methodology/">Read the full methodology</a>.')]
for before,after in changes:replace(p,before,after)
replace('compound/site/templates/finance.html','<p>{{ catalogue.guidance }}</p>','<section aria-labelledby="finance-public-money"><h2 id="finance-public-money">Where’s My Money? — Public spending</h2><p>Explore <a href="/wheres-my-money/spending/">Ireland’s public spending breakdown</a>, from eight sectors to programme-level charts. Or <a href="/wheres-my-money/">create your personal tax receipt</a>.</p></section>\n<p>{{ catalogue.guidance }}</p>')
replace('compound/site/templates/tools.html','    <p class="tools-insurance-hub-link">','    <p class="tools-insurance-hub-link"><a href="/wheres-my-money/spending/">Explore Irish public spending: native sector and programme charts →</a></p>\n    <p class="tools-insurance-hub-link">')
# Remove the temporary source-code archive feature from future evidence captures.
f=R/'scripts/capture_public_spending.py';s=f.read_text(encoding='utf-8').replace('import subprocess\n','').replace('import tarfile\n','')
a=s.index('    # Public committed application files only.');b=s.index("\nif __name__ == '__main__':")
f.write_text(s[:a]+s[b:],encoding='utf-8')
print('Imported 8 sectors, 57 programme groups, 228 component lines and 44 native pages.')
