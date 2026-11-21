"""Search results should remain usable without rendering hundreds of cards at once."""
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
JS_TEST = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class FakeElement {
  constructor() {
    this.children = [];
    this.listeners = {};
    this.hidden = false;
    this.dataset = {};
    this.value = '';
    this.textContent = '';
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = [...nodes]; }
  setAttribute(name, value) { this[name] = value; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  fire(type) { assert.ok(this.listeners[type], 'missing ' + type + ' listener'); this.listeners[type]({ preventDefault() {} }); }
}
const entries = Array.from({length: 55}, (_, n) => ({
  title: 'Story ' + n,
  summary: 'Source checked article ' + n,
  description: 'A useful summary',
  tags: n === 53 ? ['needle-53'] : ['generic'],
  url: '/wealth/story-' + n + '/',
  pillar: 'Wealth',
  reading_minutes: 3,
  date: '2026-11-17',
  date_label: '17 November 2026',
  image: ''
}));
const elements = {
  'search-data': new FakeElement(),
  'q': new FakeElement(),
  'results': new FakeElement(),
  'search-status': new FakeElement(),
  'search-more': new FakeElement()
};
elements['search-data'].textContent = JSON.stringify(entries);
elements.q.form = new FakeElement();
const document = {
  getElementById: id => elements[id] || null,
  querySelector: () => null,
  querySelectorAll: () => [],
  createElement: () => new FakeElement()
};
vm.runInNewContext(fs.readFileSync('compound/site/static/site.js', 'utf8'), {
  document, localStorage: {getItem: () => null},
  location: {search: ''}, URLSearchParams, window: {}
}, {filename: 'site.js'});

const results = elements.results, more = elements['search-more'];
const status = elements['search-status'], input = elements.q;
assert.equal(results.children.length, 24, 'landing renders only first 24 cards');
assert.equal(more.hidden, false);
assert.equal(status.textContent, 'Showing 24 of 55 stories');
more.fire('click');
assert.equal(results.children.length, 48);
assert.equal(status.textContent, 'Showing 48 of 55 stories');
more.fire('click');
assert.equal(results.children.length, 55);
assert.equal(more.hidden, true);
assert.equal(status.textContent, 'Showing 55 of 55 stories');

input.value = 'needle-53';
input.fire('input');
assert.equal(results.children.length, 1, 'new query discards old cards');
assert.equal(more.hidden, true);
assert.equal(status.textContent, 'Showing 1 of 1 matching stories');

input.value = 'no-such-topic';
input.fire('input');
assert.equal(results.children.length, 1, 'empty-state text is rendered');
assert.equal(results.children[0].className, 'empty');
assert.equal(more.hidden, true);
assert.equal(status.textContent, 'No stories found.');

input.value = '';
input.fire('input');
assert.equal(results.children.length, 24, 'clearing query resets first batch');
assert.equal(more.hidden, false);
"""


def test_search_pagination_behaviour_with_synthetic_dom():
    proc = subprocess.run(
        ["node", "-e", JS_TEST],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_search_template_exposes_keyboard_load_more_and_current_nojs_route():
    template = (ROOT / "compound/site/templates/search.html").read_text(encoding="utf-8")
    assert 'id="search-more" type="button"' in template
    assert 'hidden>Show more results</button>' in template
    assert 'href="/life/">Life</a>' in template
    assert 'href="/happiness/"' not in template
    assert 'role="status"' in template
