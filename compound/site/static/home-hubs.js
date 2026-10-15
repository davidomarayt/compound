/* Homepage hub attribution: category and action only, no PII or form values. */
(function () {
  'use strict';
  var root = document.getElementById('explore-compound');
  if (!root) return;
  var allowed = {solar:1,insurance:1,pia:1,stocks:1};
  var actions = {explore:1,project:1,calculator:1,guide:1,earnings:1};
  root.addEventListener('click',function (event) {
    var source=event.target;
    if (!source || !source.closest) return;
    var link=source.closest('a[data-home-hub][data-home-action]');
    if (!link || !root.contains(link)) return;
    var hub=link.getAttribute('data-home-hub'),action=link.getAttribute('data-home-action');
    if (!allowed[hub] || !actions[action]) return;
    try {
      if (localStorage.getItem('compound_analytics_consent') !== 'granted' || typeof window.gtag !== 'function') return;
      window.gtag('event','homepage_hub_click',{
        hub:hub,action:action,section:'specialist_hubs',transport_type:'beacon'
      });
    } catch (_) { /* Analytics unavailable; navigation still works. */ }
  });
})();
