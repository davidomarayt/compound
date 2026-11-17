// The original, MIT-licensed Caffeine Day chart is served locally alongside this page.
import { mount } from '/static/caffeine-day.js';
const root = document.querySelector('[data-caffeine-chart]');
if (root) {
  try { mount(root, { hash: true, widget: false }); }
  catch (error) {
    root.innerHTML = '<p style="padding:24px;color:#eee">The interactive chart is temporarily unavailable. The guidance and sources below are still accessible.</p>';
    console.error('Caffeine chart could not start', error);
  }
}
