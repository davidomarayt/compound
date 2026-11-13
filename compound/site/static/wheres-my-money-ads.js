/* Where's My Money: reserve three desktop / two mobile interstitial-free display placements.
 * The existing Compound AdSense loader + CMP remain authoritative.
 * Never read or transmit calculator inputs from ad code.
 */
(function () {
  'use strict';
  if (typeof document === 'undefined' || typeof window === 'undefined') return;
  var placements = Array.prototype.slice.call(document.querySelectorAll('.wmm-ad[data-wmm-ad-slot]'));
  if (!placements.length) return;

  var media = window.matchMedia('(min-width: 761px)');
  var observer = null;

  function eligible(element) {
    return !element.classList.contains('wmm-ad-desktop-only') || media.matches;
  }

  function nearViewport(element) {
    var rect = element.getBoundingClientRect();
    return rect.top <= window.innerHeight + 500 && rect.bottom >= -500;
  }

  function fill(element) {
    if (element.dataset.wmmAdLoaded === 'true' || !eligible(element)) return;
    if (!nearViewport(element)) return;
    var host = element.querySelector('.wmm-ad-container');
    if (!host || host.getBoundingClientRect().width < 220) return;
    var slot = element.getAttribute('data-wmm-ad-slot');
    var client = element.getAttribute('data-wmm-ad-client');
    if (!/^\d+$/.test(slot || '') || !/^ca-pub-\d+$/.test(client || '')) return;

    var unit = document.createElement('ins');
    unit.className = 'adsbygoogle';
    unit.style.display = 'block';
    unit.setAttribute('data-ad-client', client);
    unit.setAttribute('data-ad-slot', slot);
    unit.setAttribute('data-ad-format', 'auto');
    unit.setAttribute('data-full-width-responsive', 'true');
    host.appendChild(unit);
    element.dataset.wmmAdLoaded = 'true';
    if (observer) observer.unobserve(element);
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (_) {
      // Ad blockers and ad delivery may prevent fill. Calculator remains unaffected.
    }
  }

  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) fill(entry.target);
      });
    }, {rootMargin:'500px 0px', threshold:0});
    placements.forEach(function (element) {observer.observe(element);});
  } else {
    placements.forEach(fill);
    window.addEventListener('scroll', function () {placements.forEach(fill);}, {passive:true});
  }
  function onBreakpointChange() {
    placements.forEach(function (element) {
      if (eligible(element) && nearViewport(element)) fill(element);
    });
  }
  if (media.addEventListener) media.addEventListener('change', onBreakpointChange);
  else if (media.addListener) media.addListener(onBreakpointChange);
  // The first two slots are identical across devices; the final one is desktop-only.
})();
