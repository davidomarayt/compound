import importlib.util
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'scripts' / 'earnings.py'
spec = importlib.util.spec_from_file_location('earnings', MODULE)
earnings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(earnings)

FILING = {'form':'10-Q','filingDate':'2026-10-09','reportDate':'2026-09-30',
          'accessionNumber':'0000000001-26-000123','primaryDocument':'q3.htm'}


def rows(tag, value, prior, accn=FILING['accessionNumber']):
    base={'form':'10-Q','filed':'2026-10-09','fy':2026,'fp':'Q3','accn':accn}
    return [{**base,'start':'2026-07-01','end':'2026-09-30','val':value,'frame':'CY2026Q3'},
            {**base,'start':'2025-07-01','end':'2025-09-30','val':prior,'frame':'CY2025Q3'},
            {**base,'start':'2026-01-01','end':'2026-09-30','val':value*3,'frame':'CY2026Q3YTD'}]


def facts():
    return {'facts':{'us-gaap':{
        'RevenueFromContractWithCustomerExcludingAssessedTax': {'units':{'USD': rows('revenue',120_000_000_000,100_000_000_000)}},
        'NetIncomeLoss': {'units':{'USD': rows('net',20_000_000_000,10_000_000_000)}},
        'EarningsPerShareDiluted': {'units':{'USD/shares': rows('eps',2.0,1.5)}},
    }}}


def test_extract_requires_exact_filing_accession_and_standalone_period():
    metrics=earnings.extract_metrics(facts(), FILING)
    assert metrics['revenue']['current'] == 120_000_000_000
    assert metrics['revenue']['prior'] == 100_000_000_000
    assert metrics['diluted_eps']['current'] == 2.0
    bad = facts()
    bad['facts']['us-gaap']['NetIncomeLoss']['units']['USD'][0]['accn'] = '0000000001-26-000124'
    assert earnings.extract_metrics(bad, FILING) is None


def test_rejects_only_year_to_date_quarterly_metrics():
    bad=facts()
    bad['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD'] = [
        {'start':'2026-01-01','end':'2026-09-30','val':300,'form':'10-Q','filed':'2026-10-09', 'accn':FILING['accessionNumber']}]
    assert earnings.extract_metrics(bad, FILING) is None


def test_report_text_has_attribution_yoy_sources_and_no_unverified_claims():
    slug, article=earnings.build_article('AAPL','Apple Inc.',320193,FILING,earnings.extract_metrics(facts(),FILING),date(2026,10,10))
    assert slug=='aapl-earnings-fy2026-q3'
    assert '/wealth/earnings/aapl-earnings-fy2026-q3/' in article
    assert '2026-10-09' in article
    assert '$120.00bn' in article
    assert '+20.0%' in article
    assert 'same financial-statement concept' in article
    assert 'automated-earnings' in article
    assert 'not individually reviewed' in article
    assert '<img' not in article and '<figure' not in article and '<svg' not in article
    assert 'image:' not in article
    assert 'https://www.sec.gov/Archives/edgar/data/320193/000000000126000123/q3.htm' in article
    assert 'investment recommendation' in article
    assert 'related_tools:' not in article
    assert 'Investment Fee Impact Calculator' not in article
    assert 'For wider Irish investing context' not in article



def test_10k_is_annual_not_fourth_quarter():
    annual=dict(FILING,form='10-K')
    annual_facts={}
    for concept in ['RevenueFromContractWithCustomerExcludingAssessedTax','NetIncomeLoss','EarningsPerShareDiluted']:
        unit='USD/shares' if concept=='EarningsPerShareDiluted' else 'USD'
        val=2 if unit=='USD/shares' else 10000
        annual_facts[concept]={'units':{unit:[
            {'accn':annual['accessionNumber'],'form':'10-K','filed':'2026-10-09','fy':2026,'fp':'FY','start':'2025-10-01','end':'2026-09-30','val':val},
            {'accn':annual['accessionNumber'],'form':'10-K','filed':'2026-10-09','fy':2026,'fp':'FY','start':'2024-10-01','end':'2025-09-30','val':val/2},
        ]}}
    m=earnings.extract_metrics({'facts':{'us-gaap':annual_facts}},annual)
    assert m is not None
    slug, report=earnings.build_article('AAPL','Apple Inc.',320193,annual,m,date(2026,10,10))
    assert slug.endswith('fy2026') and 'FY 2026 full-year' in report and 'fourth quarter' not in report


def test_filters_old_filings_future_and_invalid_accessions():
    reports={'filings':{'recent':{k:[FILING[k]] for k in ('accessionNumber','form','filingDate','reportDate','primaryDocument')}}}
    assert len(earnings.recent_filings(reports,date(2026,10,10)))==1
    assert earnings.recent_filings(reports,date(2026,10,20))==[]
    reports['filings']['recent']['accessionNumber'][0]='../bad'
    assert earnings.recent_filings(reports,date(2026,10,10))==[]


class FakeClient:
    def get_json(self, url):
        if url.endswith('company_tickers.json'):
            return {'0':{'ticker':'AAPL','title':'Apple Inc.','cik_str':320193}}
        if '/submissions/' in url:
            return {'filings':{'recent':{k:[FILING[k]] for k in ('accessionNumber','form','filingDate','reportDate','primaryDocument')}}}
        return facts()


def test_run_is_idempotent_and_dry_run_is_safe(tmp_path):
    watchlist=tmp_path/'watchlist.yml'
    watchlist.write_text('tickers: [AAPL]\n')
    content=tmp_path/'content'
    out=earnings.run(watchlist,content,client=FakeClient(),now=date(2026,10,10),lookback=5,max_new=3,dry_run=True)
    assert len(out)==1
    assert not list((content/'wealth').glob('*.md'))
    out=earnings.run(watchlist,content,client=FakeClient(),now=date(2026,10,10),lookback=5,max_new=3,dry_run=False)
    assert len(out)==1
    assert Path(out[0]).exists()
    assert earnings.run(watchlist,content,client=FakeClient(),now=date(2026,10,10),lookback=5,max_new=3,dry_run=False)==[]


def test_reporting_period_misalignment_rejected():
    bad=facts()
    bad['facts']['us-gaap']['NetIncomeLoss']['units']['USD'][0]['start']='2026-07-10'
    assert earnings.extract_metrics(bad, FILING) is None


def test_change_pct_zero_or_negative_comparison():
    assert earnings.change_pct(30,20)==50.0
    assert earnings.change_pct(5,-10) is None
    assert earnings.change_pct(2,0) is None