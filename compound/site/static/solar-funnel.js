/* Sitewide solar journey attribution. One GA4 event per qualifying internal link click.
   Automatic for published older and future articles; no data-* attributes required.
   Analytics consent is required and no calculator input, contact details or URL query is sent. */
(function () {
  'use strict';

  var ORIGIN_KEY = 'compound_solar_origin_v1';
  var ORIGIN_TTL = 30 * 60 * 1000;

  function normalise(path) {
    if (!path || path[0] !== '/' || path.length > 250) return '';
    return path === '/' ? '/' : path.replace(/\/+$/, '') + '/';
  }

  function destinationStep(path) {
    if (path === '/solar/') return 'hub';
    var routes = {
      '/solar/costs/': 'installation_costs',
      '/solar/grants/': 'grants',
      '/solar/batteries/': 'battery_guide',
      '/solar/export-rates/': 'export_rates',
      '/solar/equipment/': 'equipment_guide',
      '/solar/roof-direction/': 'roof_orientation_explorer',
      '/solar/compare-quotes/': 'quote_comparison',
      '/solar/get-quotes/': 'quote_brief',
      '/solar/installers/': 'installer_directory',
      '/solar/for-installers/': 'installer_partnership',
      '/solar-payback-calculator/': 'payback_calculator',
      '/solar-ev-battery-optimiser/': 'solar_ev_battery_calculator',
      // Upstream energy research is included so an article -> electricity tool
      // -> Solar Hub journey retains the original article. It is not a solar lead.
      '/electricity-cost-calculator/': 'electricity_cost_calculator',
      '/ber-energy-cost-calculator/': 'ber_energy_calculator',
      '/whole-house-retrofit-planner/': 'retrofit_calculator',
      '/ev-charging-cost-calculator/': 'ev_charging_calculator',
      '/wealth/electricity-tariffs-ireland/': 'electricity_tariff_guide',
      '/wealth/average-home-electricity-use-ireland/': 'electricity_usage_guide',
      '/wealth/ceg-vs-sress-ireland/': 'solar_export_guide'
    };
    if (routes[path]) return routes[path];
    // Includes future Solar Hub subpages and solar-related news/evergreen guides.
    if (/^\/solar\/[a-z0-9/-]+\/$/.test(path)) return 'solar_hub_subpage';
    if (/^\/(?:wealth|news|health|life)\/[a-z0-9-]*solar[a-z0-9-]*\/$/.test(path)) return 'solar_article';
    return '';
  }

  function sourceType(path) {
    if (path === '/') return 'homepage';
    if (path.indexOf('/news/') === 0) return 'news';
    if (/^\/(?:wealth|health|life)\//.test(path)) return 'evergreen';
    if (path.indexOf('/solar/') === 0) return 'solar_hub';
    if (path === '/tools/' || /-calculator\/$/.test(path) || path === '/solar-ev-battery-optimiser/') return 'tool';
    return 'other';
  }

  function linkArea(anchor) {
    if (anchor.closest('header.site-header,.pillar-nav,.masthead-note')) return 'site_navigation';
    if (anchor.closest('footer.site-footer')) return 'site_footer';
    if (anchor.closest('.article-prose,.article-body,.article-content')) return 'article_body';
    if (anchor.closest('.tool-more,.related-tools,.related-articles,.related-reading')) return 'related_content';
    if (anchor.closest('.sol-shell')) return 'solar_hub_content';
    return 'page_content';
  }

  function consentGranted() {
    try { return localStorage.getItem('compound_analytics_consent') === 'granted'; }
    catch (_) { return false; }
  }

  function originFor(sourcePath) {
    var now = Date.now(), saved;
    try {
      saved = JSON.parse(sessionStorage.getItem(ORIGIN_KEY) || 'null');
      if (saved && typeof saved.path === 'string' && normalise(saved.path) === saved.path &&
          typeof saved.time === 'number' && now - saved.time >= 0 && now - saved.time < ORIGIN_TTL) {
        // Sliding attribution window: one editorial entry stays linked to later hub/tool steps.
        sessionStorage.setItem(ORIGIN_KEY, JSON.stringify({path:saved.path,time:now}));
        return saved.path;
      }
    } catch (_) { /* Browsers may block sessionStorage. Event still sends source_path. */ }
    try { sessionStorage.setItem(ORIGIN_KEY, JSON.stringify({path:sourcePath,time:now})); } catch (_) {}
    return sourcePath;
  }

  document.addEventListener('click', function (event) {
    if (!consentGranted() || typeof window.gtag !== 'function') return;
    var anchor = event.target && event.target.closest && event.target.closest('a[href]');
    if (!anchor || anchor.hasAttribute('download')) return;

    var url;
    try { url = new URL(anchor.getAttribute('href'), window.location.href); }
    catch (_) { return; }
    // The canonical domain and its www alias are the same publication.
    var siteHost = window.location.hostname.replace(/^www\./, '');
    if (!/^https?:$/.test(url.protocol) || url.hostname.replace(/^www\./, '') !== siteHost) return;

    var destination = normalise(url.pathname);
    var step = destinationStep(destination);
    if (!step) return;

    var sourcePath = normalise(window.location.pathname);
    if (sourcePath === destination) return; // Ignore page fragments and reload links.

    var origin = originFor(sourcePath);
    var audience = step === 'installer_partnership' ? 'installer_business' : 'homeowner_research';

    // Only this event represents a click. Other "calculator_used" events represent actual use.
    // Do not send full hrefs, search queries, referrers, form values or visitor identifiers.
    if (destination === '/solar/get-quotes/' && anchor.hasAttribute('data-solar-cta')) {
      // Distinguish high-intent form starts from clicks on research tools.
      // Only an editorial placement name is included, never form contents.
      window.gtag('event', 'solar_project_cta_click', {
        source_path: sourcePath,
        journey_origin: origin,
        cta_placement: anchor.getAttribute('data-solar-cta') || 'unspecified',
        transport_type: 'beacon'
      });
    }
    window.gtag('event', 'solar_journey_click', {
      source_path: sourcePath,
      destination_path: destination,
      destination_step: step,
      journey_origin: origin,
      source_type: sourceType(sourcePath),
      link_area: linkArea(anchor),
      audience: audience,
      transport_type: 'beacon'
    });
  });
})();
