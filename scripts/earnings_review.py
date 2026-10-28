"""Offline, resumable review queue for company dashboards and existing articles.

The existing SEC monitor owns ingestion. This layer checks its saved datasets and
queues editorial review; it never invents financial data or publishes content.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = 1
FINAL = {'reviewed', 'dismissed', 'drafted'}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False, encoding='utf-8') as out:
        json.dump(data, out, indent=2, ensure_ascii=False, sort_keys=True)
        out.write('\n')
        temp = Path(out.name)
    temp.replace(path)


@contextmanager
def locked(path):
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def load_state(path):
    if not path.exists():
        return {'version': VERSION, 'jobs': {}, 'history': [], 'rules': []}
    data = read_json(path)
    if data.get('version') != VERSION or not isinstance(data.get('jobs'), dict):
        raise ValueError('Unrecognised review state; preserve it and investigate before continuing')
    for key, job in data['jobs'].items():
        if job.get('id') != key or job.get('status') not in FINAL | {'pending'}:
            raise ValueError('Invalid review job state')
    return data


def period_errors(period, cik, today):
    errors = []
    try:
        end = date.fromisoformat(period['period_end'])
        filed = date.fromisoformat(period['filed'])
        if end > filed or filed > today:
            errors.append('Report/end dates are future-dated or out of order')
    except (ValueError, TypeError, KeyError):
        errors.append('Missing or invalid report/end dates')
    if type(period.get('fy')) is not int or not 1900 <= period['fy'] <= 2100:
        errors.append('Invalid fiscal year')
    if period.get('fp') not in {'Q1', 'Q2', 'Q3', 'FY'}:
        errors.append('Unsupported fiscal period; never infer Q4 from annual totals')
    form = str(period.get('form', '')).split()[0] if period.get('form') else ''
    base_form = form.removesuffix('/A')
    if (base_form == '10-K' and period.get('fp') != 'FY') or (base_form == '10-Q' and period.get('fp') == 'FY'):
        errors.append('Annual/quarterly form and period label disagree')
    if form not in {'10-K', '10-Q', '8-K', '6-K', '10-K/A', '10-Q/A', '8-K/A', '6-K/A'}:
        errors.append('Unsupported filing form in SEC quarterly dataset')
    source = urlparse(str(period.get('source', '')))
    accession = str(period.get('accession', ''))
    expected = f'/Archives/edgar/data/{cik}/{accession.replace("-", "")}/'
    if source.scheme != 'https' or source.hostname != 'www.sec.gov' or source.username or source.port not in (None, 443) or not source.path.startswith(expected) or not re.fullmatch(r'\d{10}-\d{2}-\d{6}', accession):
        errors.append('Source URL does not match the issuer and filing accession')
    metrics = period.get('metrics', {})
    for key in ('revenue', 'net_income', 'diluted_eps'):
        metric = metrics.get(key, {}) if isinstance(metrics, dict) else {}
        if not isinstance(metric, dict):
            metric = {}
        for field in ('current', 'prior_year'):
            value = metric.get(field)
            if field == 'prior_year' and value is None:
                continue  # Missing comparisons are valid; never invent a prior-year number.
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                errors.append(f'{key}: missing/non-finite {field} figure')
        expected_unit = 'USD/shares' if key == 'diluted_eps' else 'USD'
        if metric.get('unit') != expected_unit or not metric.get('tag'):
            errors.append(f'{key}: unsupported unit or missing accounting tag')
    return errors


def profile_errors(data, today):
    if not isinstance(data, dict):
        return ['Profile is not an object']
    cik = data.get('cik')
    errors = []
    if type(cik) is not int or cik <= 0:
        errors.append('Missing SEC issuer CIK')
    periods = data.get('periods')
    if not isinstance(periods, list) or not periods:
        return errors + ['No verified fiscal periods']
    keys = set()
    for period in periods:
        if not isinstance(period, dict):
            errors.append('Invalid fiscal-period object')
            continue
        errors.extend(period_errors(period, cik, today))
        key = (str(period.get('fy')), str(period.get('fp')))
        if key in keys:
            errors.append('Duplicate fiscal year/period; review amendment handling')
        keys.add(key)
    latest = data.get('latest')
    if latest not in periods:
        errors.append('Latest result does not match a saved fiscal period')
    elif all(isinstance(p, dict) for p in periods):
        newest = max(periods, key=lambda p: (str(p.get('period_end', '')), str(p.get('filed', ''))))
        if latest != newest:
            errors.append('Latest result is not the newest saved fiscal period')
    return sorted(set(errors))


def articles(root):
    for path in sorted((root / 'content').glob('*/*.md')):
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            continue
        parts = text.split('---', 2)
        if len(parts) < 3:
            continue
        metadata = yaml.safe_load(parts[1]) or {}
        tags = metadata.get('tags', [])
        if not isinstance(tags, list) or not ({'company-research', 'earnings-analysis'} & set(tags)):
            continue
        if metadata.get('draft') is True or metadata.get('publication_status') in {'draft', 'unpublished'}:
            continue
        yield path, metadata, text


def scan(root, today):
    registry = read_json(root / 'content/earnings-sp500.json')
    members = [r for r in registry['members'] if r.get('active')]
    aliases, issuers = {}, {}
    for member in members:
        primary = member['symbol'].lower()
        issuers[primary] = member
        for symbol in member.get('symbols', []) + [member['symbol']]:
            aliases[symbol.lower()] = primary
    watch = read_json(root / 'content/company-watchlist.json')
    for company in watch.get('listed', []):
        slug = company['slug'].lower()
        aliases[slug] = slug
        aliases[company['ticker'].lower()] = slug
    profiles = {}
    jobs = []

    def add(kind, company, paths, reason, severity, evidence, payload):
        key = fingerprint({'kind': kind, 'company': company, 'paths': paths, 'payload': payload})[:24]
        jobs.append({'id': key, 'kind': kind, 'company': company, 'paths': paths,
                     'reason': reason, 'severity': severity, 'evidence': evidence, 'status': 'pending'})

    for path in sorted((root / 'content/earnings-profiles').glob('*.json')):
        slug = path.stem
        relative = str(path.relative_to(root))
        try:
            data = read_json(path)
            errors = profile_errors(data, today)
            profiles[slug] = data
            expected = issuers.get(slug)
            if expected and data.get('cik') != expected['cik']:
                errors.append('Profile CIK differs from the company registry')
            if str(data.get('ticker', '')).lower() != slug:
                errors.append('Profile ticker differs from its filename')
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            errors = [f'Malformed profile: {type(exc).__name__}']
            data = {'invalid_file_hash': fingerprint(path.read_text())}
        if errors:
            add('profile_integrity', slug, [relative], '; '.join(errors), 'high', {}, data)
        else:
            latest = data['latest']
            threshold = 450 if latest['fp'] == 'FY' else 150
            if (today - date.fromisoformat(latest['filed'])).days > threshold:
                add('coverage_check', slug, [relative], 'Saved filing is old enough to warrant checking the official source; this does not prove newer results exist.', 'medium', latest, data)

    for slug, member in issuers.items():
        if slug not in profiles:
            add('coverage_check', slug, [f'content/earnings-profiles/{slug}.json'], 'No saved profile for an active issuer. Check ingestion and official filings; never fill gaps with estimates.', 'medium', {'cik': member['cik']}, member)

    article_count, matched_count = 0, 0
    for path, metadata, text in articles(root):
        article_count += 1
        tags = [str(t).lower().removeprefix('stock-') for t in metadata.get('tags', [])]
        # Explicit tags and canonical company links only; no fuzzy name/ticker guesses.
        linked = re.findall(r'/stocks/([a-z0-9.-]+)/', text)
        explicit = {aliases[tag] for tag in tags if tag in aliases}
        companies = sorted(explicit or {aliases[tag] for tag in linked if tag in aliases})
        relative = str(path.relative_to(root))
        if not companies:
            add('article_mapping', 'unmapped', [relative], 'Company article has no unambiguous monitored issuer mapping; confirm company identity and primary sources.', 'medium', {'title': metadata.get('title')}, text)
            continue
        matched_count += 1
        for slug in companies:
            data = profiles.get(slug)
            latest = data.get('latest', {}) if isinstance(data, dict) else {}
            reviewed = str(metadata.get('reviewed', metadata.get('date', '')))[:10]
            try:
                newer = bool(latest.get('filed')) and date.fromisoformat(latest['filed']) > date.fromisoformat(reviewed)
            except (ValueError, TypeError):
                newer = False
            reason = 'Newer filing than the article review date; assess whether claims or outlook need updating.' if newer else 'Baseline consistency review of this article against the saved company results and its original sources.'
            # Historical articles are not rewritten as though they were published today.
            evidence = {'latest_saved_result': latest, 'article_reviewed': reviewed,
                        'article_sources': metadata.get('sources', []),
                        'canonical_path': metadata.get('canonical_path', ''),
                        'historical_context': 'Preserve original research/publication dates; distinguish historical claims from current ones.'}
            add('article_review', slug, [relative, f'content/earnings-profiles/{slug}.json'], reason,
                'medium' if newer else 'low', evidence,
                {'article': text, 'profile': {k: v for k, v in (data or {}).items() if k != 'updated'}})
    return jobs, {'profiles_scanned': len(profiles), 'active_issuers': len(issuers),
                  'company_articles': article_count, 'mapped_articles': matched_count}


def reconcile(state, candidates, today, counts):
    previous = state['jobs']
    current = {}
    for candidate in candidates:
        key = candidate['id']
        old = previous.get(key, {})
        current[key] = {**candidate, 'first_seen': old.get('first_seen', today.isoformat()),
                        'last_seen': today.isoformat(), 'status': old.get('status', 'pending')}
        for field in ('decision_note', 'decided', 'pull_request'):
            if field in old:
                current[key][field] = old[field]
    history = list(state.get('history', []))
    for key, old in previous.items():
        if key not in current:
            history.append({**old, 'retired': today.isoformat(), 'retirement_reason': 'Evidence/content changed or condition cleared'})
    # Keep bounded audit history. Do not call a disappeared alert a verified fix.
    return {**state, 'checked': today.isoformat(), 'counts': counts,
            'jobs': current, 'history': history[-250:]}


def decide(state, job_id, status, note, today, pr_url=''):
    if status not in FINAL or not note.strip():
        raise ValueError('A decision and a substantive review note are required')
    job = state['jobs'].get(job_id)
    if not job or job['status'] != 'pending':
        raise ValueError('Unknown or already handled review item')
    if status == 'drafted' and not re.fullmatch(r'https://github\.com/davidomarayt/compound/pull/\d+', pr_url):
        raise ValueError('Drafted items require the actual Compound pull request URL')
    job.update(status=status, decision_note=note[:4000], decided=today.isoformat())
    if pr_url:
        job['pull_request'] = pr_url


def report(state):
    counts = state['counts']
    jobs = list(state['jobs'].values())
    pending = [j for j in jobs if j['status'] == 'pending']
    rank = {'high': 0, 'medium': 1, 'low': 2}
    pending.sort(key=lambda j: (rank[j['severity']], j['kind'], j['company'], j['id']))
    lines = ['# Compound company review queue', '', f"Checked: {state['checked']}", '',
             f"- {counts['profiles_scanned']} saved profiles checked against structural and issuer rules.",
             f"- {counts['company_articles']} existing company articles; {counts['mapped_articles']} mapped to monitored issuers.",
             f"- {len(pending)} pending review items; {len(jobs)-len(pending)} recorded decisions.", '',
             'This is a review queue, not a claim that every figure or source has been independently verified.',
             'The existing SEC monitor updates company datasets. This job never edits or publishes articles.', '',
             '## Pending work', '']
    for job in pending:
        lines.extend([f"### {job['company'].upper()} · {job['kind']} · {job['severity']}", '',
                      f"ID: `{job['id']}`", '', job['reason'], '',
                      'Files: ' + ', '.join(f'`{p}`' for p in job['paths']), ''])
        latest = job['evidence'].get('latest_saved_result', job['evidence'])
        if latest.get('source'):
            lines.append(f"Saved evidence: {latest['source']} · {latest.get('fp')} FY{latest.get('fy')} · period end {latest.get('period_end')} · filed {latest.get('filed')}")
            lines.append('')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--state', type=Path, default=ROOT / 'monitoring/earnings-review-queue.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'monitoring/earnings-review.md')
    parser.add_argument('--today', type=date.fromisoformat, default=date.today())
    parser.add_argument('--resolve')
    parser.add_argument('--decision', choices=sorted(FINAL))
    parser.add_argument('--note', default='')
    parser.add_argument('--pr-url', default='')
    args = parser.parse_args()
    # One writer; each checkpoint is atomically replaced. No external requests or LLM calls.
    with locked(args.state.with_suffix('.lock')):
        state = load_state(args.state)
        candidates, counts = scan(args.root, args.today)
        state = reconcile(state, candidates, args.today, counts)
        if args.resolve:
            decide(state, args.resolve, args.decision, args.note, args.today, args.pr_url)
        atomic_json(args.state, state)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report(state), encoding='utf-8')
        print(json.dumps({**counts, 'pending': sum(j['status'] == 'pending' for j in state['jobs'].values()),
                          'state': str(args.state), 'report': str(args.report)}))


if __name__ == '__main__':
    main()
