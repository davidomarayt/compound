from copy import deepcopy
from datetime import date
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('earnings_review', Path(__file__).parents[1] / 'scripts/earnings_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
TODAY = date(2026, 10, 28)


def profile():
    period = {'fy': 2026, 'fp': 'Q3', 'period_end': '2026-09-30', 'filed': '2026-10-20',
              'form': '8-K', 'accession': '0000000001-26-000001',
              'source': 'https://www.sec.gov/Archives/edgar/data/1/000000000126000001/results.htm',
              'metrics': {k: {'current': 10, 'prior_year': None, 'tag': 'Reported GAAP',
                             'unit': 'USD/shares' if k == 'diluted_eps' else 'USD'}
                          for k in ['revenue', 'net_income', 'diluted_eps']}}
    return {'ticker': 'ABC', 'company': 'Example', 'cik': 1, 'latest': period,
            'periods': [deepcopy(period)], 'updated': '2026-10-20'}


@pytest.fixture
def repo(tmp_path):
    (tmp_path / 'content/earnings-profiles').mkdir(parents=True)
    (tmp_path / 'content/wealth').mkdir()
    review.atomic_json(tmp_path / 'content/earnings-sp500.json', {'members': [
        {'symbol': 'ABC', 'symbols': ['ABC', 'ABC.B'], 'cik': 1, 'active': True}]})
    review.atomic_json(tmp_path / 'content/company-watchlist.json', {'listed': []})
    review.atomic_json(tmp_path / 'content/earnings-profiles/abc.json', profile())
    (tmp_path / 'content/wealth/example.md').write_text('''---
title: Example company
canonical_path: /wealth/example/
reviewed: '2026-10-01'
tags: [company-research, abc]
---
An existing company article. [Peer](/stocks/other/).
''')
    return tmp_path


def state():
    return {'version': 1, 'jobs': {}, 'history': [], 'rules': []}


def test_accepts_furnished_earnings_release_and_missing_comparisons():
    assert review.profile_errors(profile(), TODAY) == []


@pytest.mark.parametrize('mutate,expected', [
    (lambda p: p['latest'].update(filed='2027-01-01'), 'dates'),
    (lambda p: p['latest'].update(fp='Q4'), 'Unsupported fiscal period'),
    (lambda p: p['latest'].update(source='https://evil.example/results'), 'Source URL'),
    (lambda p: p['latest'].update(form='10-K'), 'Annual/quarterly'),
    (lambda p: p['latest']['metrics']['revenue'].update(current=float('nan')), 'non-finite'),
    (lambda p: p['latest']['metrics']['diluted_eps'].update(unit='USD'), 'unit'),
])
def test_rejects_bad_financial_metadata(mutate, expected):
    p = profile()
    mutate(p)
    p['periods'] = [deepcopy(p['latest'])]
    assert expected in ' '.join(review.profile_errors(p, TODAY))


def test_latest_must_match_actual_saved_period():
    p = profile()
    p['latest']['metrics']['revenue']['current'] = 12
    assert 'Latest result does not match' in ' '.join(review.profile_errors(p, TODAY))


def test_duplicate_period_is_flagged():
    p = profile()
    p['periods'].append(deepcopy(p['periods'][0]))
    assert 'Duplicate fiscal' in ' '.join(review.profile_errors(p, TODAY))


def test_article_mapping_and_newer_report(repo):
    jobs, counts = review.scan(repo, TODAY)
    assert counts['profiles_scanned'] == 1
    assert len(jobs) == 1
    assert jobs[0]['kind'] == 'article_review'
    assert jobs[0]['severity'] == 'medium'
    assert jobs[0]['paths'][0] == 'content/wealth/example.md'


def test_recorded_decisions_survive_retry_but_new_content_reopens(repo):
    jobs, counts = review.scan(repo, TODAY)
    first = review.reconcile(state(), jobs, TODAY, counts)
    key = jobs[0]['id']
    review.decide(first, key, 'reviewed', 'Checked the filing; historical framing remains accurate.', TODAY)
    again = review.reconcile(first, jobs, TODAY, counts)
    assert again['jobs'][key]['status'] == 'reviewed'
    path = repo / 'content/wealth/example.md'
    path.write_text(path.read_text() + '\nNew paragraph.\n')
    jobs, counts = review.scan(repo, TODAY)
    changed = review.reconcile(again, jobs, TODAY, counts)
    assert changed['jobs'][jobs[0]['id']]['status'] == 'pending'
    assert changed['history'][0]['status'] == 'reviewed'


def test_requires_real_pr_link_for_drafted_state(repo):
    jobs, counts = review.scan(repo, TODAY)
    current = review.reconcile(state(), jobs, TODAY, counts)
    with pytest.raises(ValueError, match='actual Compound'):
        review.decide(current, jobs[0]['id'], 'drafted', 'Prepared draft', TODAY)
    review.decide(current, jobs[0]['id'], 'drafted', 'Prepared draft', TODAY,
                  'https://github.com/davidomarayt/compound/pull/99')
    assert current['jobs'][jobs[0]['id']]['status'] == 'drafted'


def test_invalid_checkpoint_not_silently_reset(tmp_path):
    path = tmp_path / 'state.json'
    review.atomic_json(path, {'version': 999, 'jobs': {}})
    with pytest.raises(ValueError):
        review.load_state(path)


def test_missing_profile_is_review_item_not_invented_result(repo):
    (repo / 'content/earnings-profiles/abc.json').unlink()
    jobs, _ = review.scan(repo, TODAY)
    assert any(j['kind'] == 'coverage_check' for j in jobs)
    assert not (repo / 'content/earnings-profiles/abc.json').exists()


def test_bad_profile_does_not_abort_other_reviews(repo):
    (repo / 'content/earnings-profiles/abc.json').write_text('{bad json')
    jobs, _ = review.scan(repo, TODAY)
    assert any(j['kind'] == 'profile_integrity' for j in jobs)
    assert any(j['kind'] == 'article_review' for j in jobs)


def test_updated_timestamp_alone_does_not_reopen_article(repo):
    original, _ = review.scan(repo, TODAY)
    p = profile()
    p['updated'] = '2026-10-28'
    review.atomic_json(repo / 'content/earnings-profiles/abc.json', p)
    changed, _ = review.scan(repo, TODAY)
    assert original[0]['id'] == changed[0]['id']


def test_scan_never_changes_publishing_files(repo):
    before = {str(p): p.read_bytes() for p in (repo / 'content').rglob('*') if p.is_file()}
    jobs, counts = review.scan(repo, TODAY)
    review.report(review.reconcile(state(), jobs, TODAY, counts))
    assert before == {str(p): p.read_bytes() for p in (repo / 'content').rglob('*') if p.is_file()}


def test_accepts_explicit_earnings_exhibit_form_label():
    p = profile()
    p['latest']['form'] = '8-K Exhibit 99.1'
    p['periods'] = [deepcopy(p['latest'])]
    assert review.profile_errors(p, TODAY) == []
