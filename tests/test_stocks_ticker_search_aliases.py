"""Regression checks for company/ticker search punctuation and accessible result status.

The source directory uses BRK-B / BF-B, while readers may enter BRK.B or
BRK B. The same filter code is shared with the earnings directory.
"""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_stocks_directory_search_feedback_and_cache_version():
    template = (ROOT / "compound/site/templates/stocks_hub.html").read_text(encoding="utf-8")
    assert 'aria-describedby="stocks-search-count"' in template
    assert 'id="stocks-search-count"' in template
    assert 'data-earnings-count role="status" aria-live="polite" aria-atomic="true"' in template
    assert "/static/earnings-directory.js?v=20261123-ticker-aliases" in template
    assert 'href="{{ site_url }}/stocks/"' in template  # Canonical unchanged.
    assert 'data-earnings-sector' in template


NODE_HARNESS = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
const records = [
  {name:'Berkshire Hathaway',symbols:'BRK-B',sector:'Financials'},
  {name:'Brown–Forman',symbols:'BF-B',sector:'Consumer Staples'},
  {name:'A. O. Smith',symbols:'AOS',sector:'Industrials'},
  {name:'Apple Inc.',symbols:'AAPL',sector:'Information Technology'}
];
const rows = records.map(({name,symbols,sector}) => ({
  dataset:{name,symbols,sector},hidden:false
}));
const search = {value:'', listeners:{},addEventListener(k,fn){this.listeners[k]=fn;}};
const sector = {value:'', listeners:{},addEventListener(k,fn){this.listeners[k]=fn;}};
const count = {textContent:''};
const empty = {hidden:true};
const chips = ['', 'Financials'].map(stockSector => ({
  dataset:{stockSector},attributes:{},
  addEventListener(k,fn){this[k]=fn;},
  setAttribute(k,v){this.attributes[k]=v;}
}));
const single = {
  '[data-earnings-search]':search,
  '[data-earnings-sector]':sector,
  '[data-earnings-count]':count,
  '[data-earnings-empty]':empty
};
const document = {
  querySelector: key => single[key]||null,
  querySelectorAll: key => ({
    '[data-earnings-row]':rows, '[data-stock-sector]':chips
  })[key]||[]
};
vm.runInNewContext(code, {document}, {timeout:1500});
function match(query, shown) {
  search.value=query;search.listeners.input();
  assert.deepEqual(rows.map(r=>!r.hidden),shown,query);
}
match('BRK.B',[true,false,false,false]);
assert.equal(count.textContent,'Showing 1 of 4 companies');
match('brk-b',[true,false,false,false]);
match('BRK B',[true,false,false,false]);
match('BRK/B',[true,false,false,false]);
match('BF.B',[false,true,false,false]);
match('brown-forman',[false,true,false,false]);
match('A O Smith',[false,false,true,false]);
sector.value='Financials';sector.listeners.change();
match('BRK.B',[true,false,false,false]);
assert.equal(chips[1].attributes['aria-pressed'],'true');
sector.value='Industrials';sector.listeners.change();
assert.equal(empty.hidden,false);
assert.equal(count.textContent,'Showing 0 of 4 companies');
let prevented=false;
search.listeners.keydown({key:'Escape',preventDefault(){prevented=true;}});
assert.equal(prevented,true);
assert.equal(search.value,'');
assert.deepEqual(rows.map(r=>!r.hidden),[false,false,true,false]);
assert.equal(count.textContent,'Showing 1 of 4 companies');
"""


def test_actual_search_js_matches_share_class_aliases_and_preserves_filters():
    result = subprocess.run(
        ["node", "-e", NODE_HARNESS, str(ROOT / "compound/site/static/earnings-directory.js")],
        capture_output=True, text=True, check=False, timeout=15
    )
    assert result.returncode == 0, result.stderr
