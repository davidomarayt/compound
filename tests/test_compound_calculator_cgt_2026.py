"""Protect Compound's direct-share CGT assumptions after Revenue's 7 October 2026 change.

Original sources:
https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx
https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx
"""
from decimal import Decimal
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_cgt_rate_metadata_and_dirt_are_distinct():
    js = source("compound/site/static/compound-calculator.js")
    guide = source("content/compound-calculator-guide.md")
    controls = source("compound/site/templates/_compound_calculator.html")
    page = source("compound/site/templates/calculator.html")

    assert "const standardCgtRate=0.31;" in js
    assert "Math.max(0,balance-paid-v.exempt)*standardCgtRate:0" in js
    assert "Math.max(0,interest)*.33:0" in js  # DIRT unchanged
    assert "31% on positive gains for an ordinary direct-share disposal" in js
    assert "33% on positive capital gains at a single final sale" not in js
    assert "7 October 2026" in js and "6 October 2026" in js
    assert "CGT rate checked 22 November 2026" in controls
    assert "other tax assumptions last checked 22 September 2026" in controls
    assert "31% on a positive gain from an ordinary share sale" in guide
    assert "33% CGT rate for most gains" not in guide
    assert "https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx" in guide
    assert "/capital-gains-tax-calculator/" in guide
    assert "/wealth/capital-gains-tax-ireland/" in guide
    assert "/static/compound-calculator.js?v=20261122-cgt" in page
    assert '"dateModified":"2026-11-22"' in page
    assert "other sources last checked 22 September 2026" in page
    assert Decimal("18730") * Decimal("0.31") == Decimal("5806.30")
    assert Decimal("18730") * Decimal("0.33") == Decimal("6180.90")


def test_actual_project_engine_calculates_current_cgt_and_preserves_dirt():
    """Run the real self-contained projection function in Node, not a Python duplicate."""
    js = source("compound/site/static/compound-calculator.js")
    start = js.index("function project(v)")
    end = js.index("function solve(v)", start)
    assert re.search(r"const standardCgtRate=0\.31;", js)
    engine = js[start:end]
    script = """
const assert=require('node:assert/strict');
const standardCgtRate=0.31;
__PROJECT_FUNCTION__
const input={start:10000,monthly:0,years:1,rate:20,fee:0,increase:0,exempt:1270,events:[]};
const before=project({...input,tax:'none'}).at(-1);
const current=project({...input,tax:'cgt'}).at(-1);
const noExempt=project({...input,tax:'cgt',exempt:0}).at(-1);
const zeroGain=project({...input,tax:'cgt',rate:0}).at(-1);
const deposit=project({...input,tax:'dirt'}).at(-1);
function close(a,b){assert.ok(Math.abs(a-b)<0.00001, a+' != '+b);}
close(before.balance,12000);close(before.tax,0);
close(current.tax,226.30);close(current.net,11773.70);
close(noExempt.tax,620);close(noExempt.net,11380);
close(zeroGain.tax,0);close(zeroGain.net,10000);
assert.ok(deposit.tax>0 && deposit.net<before.net, 'DIRT still applies to interest');
""" .replace("__PROJECT_FUNCTION__", engine)
    subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True, check=True)
