import base64
import json
import threading
from http.server import HTTPServer
from pathlib import Path

import httpx
import pytest

from compound.freshness.core import Store, config, digest, run, validate_result, validate_url, worker_lock
from compound.freshness.web import handler, render


@pytest.fixture
def pilot(tmp_path):
    (tmp_path / 'page.md').write_text('The grant is €100. More content.')
    store = Store(tmp_path / 'state.sqlite3')
    cfg = {'sources': {'seai': 'https://www.seai.ie/example'}, 'pages': {'page.md': ['seai']},
           'max_attempts': 3, 'max_jobs_per_run': 4, 'daily_reserved_tokens': 200000}
    yield tmp_path, store, cfg
    store.close()


def result(prompt):
    return {'outcome': 'change', 'summary': 'Grant update', 'effective_date': 'unknown',
            'uncertainties': ['Check eligibility.'], 'edits': [{'before': 'The grant is €100.',
            'after': 'The grant is €200.', 'quote': 'Grant €200', 'reason': 'Source now shows €200.'}]}


def check(pilot, analyser=result, text='Grant €200'):
    root, store, cfg = pilot
    run(store, cfg, root, fetcher=lambda _: text, analyser=analyser)
    return store.rows('SELECT * FROM jobs')


def test_maps_ten_existing_pages():
    cfg = config()
    assert len(cfg['pages']) == 10


def test_dedup_and_new_content(pilot):
    assert len(check(pilot)) == 1
    assert len(check(pilot)) == 1
    root, store, _ = pilot
    (root / 'page.md').write_text('The grant is €100. Changed wording.')
    assert len(check(pilot)) == 2
    assert len(store.rows('SELECT * FROM snapshots')) == 1


def test_change_snapshots_and_failed_fetch_does_not_destroy_evidence(pilot):
    check(pilot)
    root, store, cfg = pilot
    def failure(_):
        raise RuntimeError('Source unavailable')
    run(store, cfg, root, fetcher=failure)
    assert len(store.rows('SELECT * FROM snapshots')) == 1
    assert store.rows('SELECT * FROM checks')[0]['error'] == 'Source unavailable'
    check(pilot, text='Grant €200. New rules.')
    assert len(store.rows('SELECT * FROM snapshots')) == 2


def test_evidence_and_unique_passage_required():
    with pytest.raises(ValueError, match='quote'):
        validate_result(result(''), 'The grant is €100.', 'Unrelated source')
    with pytest.raises(ValueError, match='unique'):
        validate_result(result(''), 'The grant is €100. The grant is €100.', 'Grant €200')


def test_retry_cap_and_crash_recovery(pilot):
    def broken(_):
        raise RuntimeError('Timed out')
    check(pilot, broken)
    root, store, cfg = pilot
    with store.db:
        store.db.execute("UPDATE jobs SET status='running'")
    rows = check(pilot, broken)
    assert rows[0]['attempts'] == 2
    rows = check(pilot, broken)
    assert rows[0]['status'] == 'failed'
    check(pilot)
    assert store.rows('SELECT attempts FROM jobs')[0]['attempts'] == 3
    store.decide(1, 'retry', root=root)
    assert check(pilot)[0]['status'] == 'review'


def test_budget_reserved_before_call_and_not_refunded(pilot):
    root, store, cfg = pilot
    cfg['daily_reserved_tokens'] = 1
    called = []
    check(pilot, lambda p: called.append(p))
    assert not called
    assert store.rows('SELECT status FROM jobs')[0]['status'] == 'held'
    assert store.rows('SELECT reserved FROM budgets')[0]['reserved'] == 0


def test_approval_stale_guard_and_no_publication(pilot):
    check(pilot)
    root, store, _ = pilot
    (root / 'page.md').write_text('New live copy')
    with pytest.raises(ValueError, match='Content changed'):
        store.decide(1, 'approved', root=root)
    assert (root / 'page.md').read_text() == 'New live copy'
    store.decide(1, 'dismissed', 'Always check dates', root=root)
    with pytest.raises(ValueError):
        store.decide(1, 'approved', root=root)


def test_memories_need_repeated_human_feedback_and_approval(pilot):
    root, store, _ = pilot
    check(pilot)
    store.decide(1, 'dismissed', 'Check effective dates', root=root)
    store.propose_memories()
    assert not store.rows('SELECT * FROM memories')
    check(pilot, text='Grant €200. New terms')
    store.decide(2, 'dismissed', 'Check effective dates', root=root)
    store.propose_memories()
    rules = store.rows('SELECT * FROM memories')
    assert rules[0]['status'] == 'proposed'
    assert rules[0]['rule'] == 'Check effective dates'


def test_url_allowlist():
    for url in ['http://www.seai.ie/', 'https://www.seai.ie.evil.com/', 'https://127.0.0.1/',
                'https://www.seai.ie:9000/', 'https://user@www.seai.ie/']:
        with pytest.raises(ValueError):
            validate_url(url)


def test_lock_excludes_second_worker(tmp_path):
    with worker_lock(tmp_path / 'lock'):
        with pytest.raises(RuntimeError):
            with worker_lock(tmp_path / 'lock'):
                pass


def test_ui_escapes_feedback(pilot):
    check(pilot)
    _, store, _ = pilot
    with store.db:
        store.db.execute("INSERT INTO memories(rule,created) VALUES(?,?)", ('<script>alert(1)</script>', 'today'))
    html = render(store, 'csrf')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'Approve proposal' in html


def test_web_auth_csrf_and_decision(pilot):
    root, store, _ = pilot
    check(pilot)
    server = HTTPServer(('127.0.0.1', 0), handler(root / 'state.sqlite3', 'secret', root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(base_url=f'http://127.0.0.1:{server.server_port}', trust_env=False) as client:
            assert client.get('/').status_code == 401
            client.auth = ('owner', 'secret')
            page = client.get('/')
            assert page.status_code == 200
            assert page.headers['Cache-Control'] == 'no-store'
            assert client.post('/decision', data={'id': 1, 'action': 'approved'}).status_code == 403
            import re
            csrf = re.search('name="csrf" value="([^"]+)"', page.text)[1]
            response = client.post('/decision', data={'id': 1, 'action': 'approved', 'csrf': csrf})
            assert response.status_code == 303
            assert store.rows('SELECT status FROM jobs')[0]['status'] == 'approved'
            assert (root / 'page.md').read_text() == 'The grant is €100. More content.'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_patch_export_does_not_apply_changes(pilot):
    root, store, _ = pilot
    check(pilot)
    patch = store.proposal_patch(1, root)
    assert '--- a/page.md' in patch
    assert '+The grant is €200.' in patch
    assert (root / 'page.md').read_text().startswith('The grant is €100.')
    (root / 'page.md').write_text('Updated page')
    with pytest.raises(ValueError, match='Content changed'):
        store.proposal_patch(1, root)


def test_new_evidence_supersedes_pending_draft(pilot):
    check(pilot)
    rows = check(pilot, text='Grant €200. Updated conditions.')
    assert rows[0]['status'] == 'superseded'
    assert rows[1]['status'] == 'review'
    root, store, _ = pilot
    with pytest.raises(ValueError):
        store.decide(1, 'approved', root=root)
