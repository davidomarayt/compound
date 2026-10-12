/* Browser-independent checks for all historical and future solar links. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = fs.readFileSync(path.join(__dirname, '../compound/site/static/solar-funnel.js'), 'utf8');
const storage = new Map();

function harness(page, consent = 'granted', extra = {}) {
  const logs = [];
  let listener;
  const base = 'https://compound.ie';
  const loc = new URL(page, base);
  const ctx = {
    URL,
    Date,
    window: {
      location: {href: loc.href, hostname: loc.hostname, pathname: loc.pathname, origin:loc.origin},
      ...(extra.withoutGtag ? {} : {gtag: (...args) => logs.push(args)})
    },
    document: {addEventListener(event, fn) { if (event === 'click') listener = fn; }},
    localStorage: {getItem(key) { return key === 'compound_analytics_consent' ? consent : null; }},
    sessionStorage: {
      getItem(key) { return storage.get(key) || null; },
      setItem(key, value) { storage.set(key, value); },
      removeItem(key) { storage.delete(key); }
    }
  };
  vm.runInNewContext(script, ctx, {filename:'solar-funnel.js'});
  assert.equal(typeof listener, 'function');
  return {
    logs,
    click(href, opts = {}) {
      const anchor = {
        getAttribute() { return href; },
        hasAttribute(name) { return name === 'download' && Boolean(opts.download); },
        closest(selector) {
          if (selector.includes('article-prose')) return opts.area === 'article';
          if (selector.includes('footer.site-footer')) return opts.area === 'footer';
          if (selector.includes('header.site-header')) return opts.area === 'navigation';
          if (selector.includes('.sol-shell')) return opts.area === 'solar';
          return false;
        }
      };
      listener({target: {closest(selector) { return selector === 'a[href]' ? anchor : null; }}});
      return logs.at(-1);
    }
  };
}
function expectOne(page, href, step, consent='granted') {
  storage.clear();
  const h=harness(page,consent);
  const output=h.click(href, {area:'article'});
  assert.equal(h.logs.length,consent==='granted'?1:0,page+' => '+href);
  if(consent==='granted') {
    assert.equal(output[0], 'event');
    assert.equal(output[1], 'solar_journey_click');
    assert.equal(output[2].destination_step,step);
    assert.equal(output[2].source_path,page);
    assert.equal(output[2].journey_origin,page);
    assert.equal(output[2].link_area,'article_body');
    assert.ok(!Object.keys(output[2]).some(x=>/email|input|visitor|query/.test(x)));
  }
}
const news='/news/budget-2027-energy-credit/';
[
  ['/solar/', 'hub'],
  ['/solar/grants/', 'grants'],
  ['/solar/costs/', 'installation_costs'],
  ['/solar/batteries/', 'battery_guide'],
  ['/solar/export-rates/', 'export_rates'],
  ['/solar/equipment/', 'equipment_guide'],
  ['/solar/installers/', 'installer_directory'],
  ['/solar/get-quotes/', 'quote_brief'],
  ['/solar/compare-quotes/', 'quote_comparison'],
  ['/solar-payback-calculator/', 'payback_calculator'],
  ['/solar-ev-battery-optimiser/', 'solar_ev_battery_calculator'],
  ['/wealth/solar-panels-ireland/', 'solar_article'],
  ['/news/new-solar-panels-news-2027/', 'solar_article'],
  ['/solar/future-roof-tool/', 'solar_hub_subpage'],
  ['/solar/for-installers/', 'installer_partnership'],
].forEach(([dest,step])=>expectOne(news,dest,step));

storage.clear();
const entry=harness('/news/budget-2027-energy-credit/');
entry.click('/solar/',{area:'article'});
assert.equal(entry.logs[0][2].audience,'homeowner_research');
assert.equal(entry.logs[0][2].source_type,'news');
const next=harness('/solar/');
next.click('/solar-payback-calculator/',{area:'solar'});
assert.equal(next.logs.length,1);
assert.equal(next.logs[0][2].source_path,'/solar/');
assert.equal(next.logs[0][2].journey_origin,'/news/budget-2027-energy-credit/');
const after=harness('/solar-payback-calculator/');
after.click('/solar/get-quotes/');
assert.equal(after.logs[0][2].journey_origin,'/news/budget-2027-energy-credit/');
assert.equal(after.logs[0][2].destination_step,'quote_brief');

// A business sponsor link never masquerades as a qualified household enquiry.
storage.clear();
const business=harness('/solar/');
business.click('/solar/for-installers/');
assert.equal(business.logs[0][2].audience, 'installer_business');

expectOne('/wealth/older-electricity-tariffs/', '/solar/', 'hub');
expectOne(news, '/solar/', 'hub', 'denied');
storage.clear();
const denied=harness(news,'denied');
denied.click('/solar/');
assert.equal(storage.size,0);
const without=harness(news,'granted',{withoutGtag:true});
without.click('/solar/');
assert.equal(without.logs.length,0);

// Exclusions: external links, same-page anchors, downloadable files, generic non-solar links.
const exclusions=harness('/solar/');
for(const href of ['#solar-tools','/solar/#solar-tools','https://other.example/solar/',
                    '/insurance/','/electricity-cost-calculator/','javascript:alert(1)']) exclusions.click(href);
exclusions.click('/solar/grants/',{download:true});
assert.equal(exclusions.logs.length,0);

// Canonical www alias should still be recognised and never include URL query strings.
storage.clear();
const alias=harness('/wealth/smart-meter-news/');
alias.click('https://www.compound.ie/solar/?campaign=test@example.com');
assert.equal(alias.logs.length,1);
assert.equal(alias.logs[0][2].destination_path,'/solar/');
assert.ok(!JSON.stringify(alias.logs[0]).includes('test@example.com'));
console.log('PASS: sitewide solar attribution, source journeys, one event per click, privacy and exclusions');
