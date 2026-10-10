"""No live network required: S&P reference parser, membership identity and scanner tests."""
import importlib.util
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

registry = load_module('sp500_registry', HERE/'scripts'/'sp500_registry.py')
earnings = load_module('earnings', HERE/'scripts'/'earnings.py')
SECTORS = sorted(registry.SECTORS)


def fake_html(rows):
    table = '<table id="constituents"><thead><tr><th>Symbol</th><th>Security</th><th>GICS Sector</th><th>GICS Sub-Industry</th><th>Headquarters Location</th><th>Date added</th><th>CIK</th><th>Founded</th></tr></thead><tbody>'
    for symbol, cik, sector in rows:
        table += (f'<tr><td><a href="/x">{symbol}</a></td><td><b>Company {symbol}</b></td><td>{sector}</td>'
                  f'<td>Example</td><td>US</td><td>2000</td><td>{cik:010d}</td><td>2000</td></tr>')
    return table + '</tbody></table>'


def test_strict_scrape_and_multiple_share_classes(tmp_path):
    rows = [(f'X{i:03d}', 100000 + i, SECTORS[i%11]) for i in range(501)]
    rows.extend([('GOOG', 999999, 'Communication Services'), ('GOOGL', 999999, 'Communication Services')])
    source = fake_html(rows)
    securities = registry.parse_constituents(source)
    assert len(securities) == 503
    p = tmp_path/'snapshot.json'
    assert registry.refresh(p, fetch=lambda url: source, now='2026-10-10')
    result = registry.load_registry(p)
    assert result['security_count'] == 503 and result['company_count'] == 502
    alphabet = next(x for x in result['members'] if x['cik'] == 999999)
    assert alphabet['symbol'] == 'GOOGL' and alphabet['symbols'] == ['GOOG','GOOGL']
    assert not registry.refresh(p, fetch=lambda url: source, now='2026-10-10')
    before = p.read_text()
    try:
        registry.refresh(p, fetch=lambda url: fake_html(rows[:25]), now='2026-10-11')
        assert False, 'should reject truncated source'
    except ValueError:
        assert p.read_text() == before
    # Dropped companies are retained in the snapshot but no longer active.
    new = rows[1:] + [('NEW', 500000, 'Information Technology')]
    registry.refresh(p, fetch=lambda url: fake_html(new), now='2026-10-12')
    old = next(x for x in registry.load_registry(p)['members'] if x['cik'] == 100000)
    assert not old['active']


def test_fails_closed_on_missing_table_and_duplicate_ticker():
    import pytest
    with pytest.raises(ValueError):
        registry.parse_constituents('<html>No table</html>')
    with pytest.raises(ValueError, match='Duplicate security'):
        registry.parse_constituents(fake_html([('AAPL', 1, 'Information Technology'),('AAPL',2,'Financials')]), strict=False)


def test_sharded_scan_uses_one_request_per_cik(tmp_path):
    members = [{'symbol': f'X{i:03d}', 'symbols':[f'X{i:03d}'], 'name':f'Company {i}', 'cik': 100000+i,
                'sector': SECTORS[i%11], 'active':True} for i in range(500)]
    path=tmp_path/'registry.json'
    path.write_text(json.dumps({'checked':'2026-10-10','company_count':500,'security_count':500,'members':members}))
    watch=tmp_path/'trial.yml'
    watch.write_text('tickers: [AAPL]\n')
    class Client:
        def __init__(self): self.calls=[]
        def get_json(self,url):
            self.calls.append(url)
            return {'filings':{'recent':{k:[] for k in ('accessionNumber','form','filingDate','reportDate','primaryDocument')}}}
    client=Client()
    out=earnings.run(watch,tmp_path/'content',client=client,now=date(2026,10,10),lookback=10,
                     max_new=8,dry_run=True,registry_path=path,shard_count=4,shard_index=2)
    assert not out
    assert len(client.calls)==125
    assert all('/submissions/' in x for x in client.calls)


def test_current_constituent_csv_parser():
    import pytest
    csv = ('Symbol,Security,GICS Sector,CIK\n'
           'AAPL,Apple Inc.,Information Technology,320193\n'
           'BRK.B,Berkshire Hathaway,Financials,1067983\n')
    result=registry.parse_dataset_csv(csv,strict=False)
    assert result[0]['cik']==320193
    assert result[1]['symbol']=='BRK-B'
    with pytest.raises(ValueError):
        registry.parse_dataset_csv(csv.replace('AAPL,Apple Inc.', 'AAPL,Apple Inc.').replace('BRK.B,Berkshire Hathaway', 'AAPL,Berkshire Hathaway'),strict=False)