"""Behavioural regression checks for the filter on the canonical /tools/ directory."""

from pathlib import Path
import subprocess

from compound.site.build import build_site


ROOT = Path(__file__).resolve().parents[1]


def test_tools_hub_exposes_search_count_to_all_readers(settings):
    build_site(settings)
    html = (settings.public_dir / "tools" / "index.html").read_text(encoding="utf-8")
    assert 'id="tool-directory-search"' in html
    assert 'aria-describedby="tool-search-feedback"' in html
    assert 'id="tool-search-feedback"' in html
    assert 'data-tool-search-status' in html
    assert 'role="status" aria-live="polite" aria-atomic="true"' in html
    assert "/static/tools.js?v=20261118-search-feedback" in html
    assert "/static/tools.css?v=20261118-search-feedback" in html
    assert 'data-tool-no-results hidden' in html


NODE_HARNESS = r"""
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(process.argv[1], 'utf8');
const begin=source.lastIndexOf("  const search=document.querySelector('[data-tool-search]');");
const end=source.lastIndexOf('\n})();');
assert.ok(begin>=0 && end>begin, 'filter is a standalone footer block');
const cards=[
  {dataset:{toolText:'mortgage monthly payment ireland'},textContent:'Mortgage',hidden:false},
  {dataset:{toolText:'solar pv home energy'},textContent:'Solar',hidden:false},
  {dataset:{toolText:'salary hourly rate'},textContent:'Salary',hidden:false}
];
const groupA={hidden:false,querySelectorAll:()=>cards.slice(0,2)};
const groupB={hidden:false,querySelectorAll:()=>cards.slice(2)};
const input={value:'',listeners:{},addEventListener(key,fn){this.listeners[key]=fn;}};
const feedback={textContent:''};
const empty={hidden:true};
const lookup={
  '[data-tool-search]':input,
  '[data-tool-search-status]':feedback,
  '[data-tool-no-results]':empty
};
const document={
  querySelector:key=>lookup[key]||null,
  querySelectorAll:key=>{
    if(key==='[data-tool-card]')return cards;
    if(key==='[data-tool-group]')return [groupA,groupB];
    return [];
  }
};
vm.runInNewContext('(function(){\n'+source.slice(begin,end)+'\n})();',{document},{timeout:1500});
assert.equal(feedback.textContent,'Showing all 3 tools.');
assert.equal(empty.hidden,true);
input.value='solar';input.listeners.input();
assert.deepEqual(cards.map(card=>card.hidden),[true,false,true]);
assert.equal(feedback.textContent,'Showing 1 matching tool.');
assert.equal(groupA.hidden,false);
assert.equal(groupB.hidden,true);
input.value='a';input.listeners.input();
assert.equal(feedback.textContent,'Showing 3 matching tools.');
input.value='not a calculator';input.listeners.input();
assert.ok(cards.every(card=>card.hidden));
assert.equal(empty.hidden,false);
assert.equal(feedback.textContent,'No matching tools. Try a broader search.');
let prevented=false;
input.listeners.keydown({key:'Escape',preventDefault(){prevented=true;}});
assert.equal(prevented,true);
assert.equal(input.value,'');
assert.ok(cards.every(card=>!card.hidden));
assert.equal(groupB.hidden,false);
assert.equal(feedback.textContent,'Showing all 3 tools.');
"""


def test_filter_counts_matches_and_escape_restores_all():
    completed = subprocess.run(
        ["node", "-e", NODE_HARNESS, str(ROOT / "compound/site/static/tools.js")],
        capture_output=True, text=True, timeout=15, check=False,
    )
    assert completed.returncode == 0, completed.stderr
