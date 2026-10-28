"""Loopback-only review UI; SSH forwarding is the supported remote access path."""
import base64
import hmac
import json
import secrets
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from compound.freshness.core import Store, ROOT


def render(store, csrf):
    def e(value):
        return escape(str(value), quote=True)

    jobs = store.rows("SELECT j.*,s.url,s.fetched,s.source FROM jobs j JOIN snapshots s ON s.id=j.snapshot ORDER BY j.id DESC")
    checks = store.rows("SELECT * FROM checks ORDER BY source")
    cards = []
    for job in jobs:
        result = json.loads(job["result"] or "{}")
        edits = "".join(f'<div class="comparison"><section><h4>Before</h4><pre>{e(edit["before"])}</pre></section><section><h4>Proposed</h4><pre>{e(edit["after"])}</pre></section></div><blockquote>{e(edit["quote"])}</blockquote><p>{e(edit["reason"])}</p>' for edit in result.get("edits", []))
        patch_link = f'<p><a href="/patch/{job["id"]}">Download proposed patch</a></p>' if job['status'] in {'review', 'approved'} and result.get('edits') else ''
        actions = ""
        if job["status"] == "review":
            actions = '<button name="action" value="approved">Approve proposal</button><button class="secondary" name="action" value="dismissed">Dismiss</button>'
        elif job["status"] in {"failed", "held"}:
            actions = '<button name="action" value="retry">Retry on next run</button>'
        form = f'<form method="post" action="/decision"><input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="id" value="{job["id"]}"><label>Editorial feedback (optional)<textarea name="note" maxlength="2000" placeholder="What should future reviews do differently?"></textarea></label>{actions}</form>' if actions else ""
        cards.append(f'''<article><div class="eyebrow">#{job['id']} · {e(job['source'])} · <b>{e(job['status'])}</b></div>
        <h2>{e(job['path'].split('/')[-1].removesuffix('.md').replace('-', ' '))}</h2>
        <p>{e(result.get('summary', 'Source captured. Waiting for AI review.' if job['status']=='queued' else job['error'] or ''))}</p>
        <p class="meta"><a href="{e(job['url'])}" target="_blank" rel="noopener noreferrer">Source evidence ↗</a> · Retrieved {e(job['fetched'][:16])} UTC · Attempt {job['attempts']}</p>
        <p>Effective date: {e(result.get('effective_date','Not assessed'))}</p>{edits}
        {''.join('<p class="warning">'+e(x)+'</p>' for x in result.get('uncertainties', []))}
        {('<p class="warning">'+e(job['error'])+'</p>') if job['error'] else ''}
        <details><summary>Saved page and source evidence</summary><h4>Page at check time</h4><pre>{e(job['content'])}</pre><h4>Source snapshot</h4><pre>{e(store.rows('SELECT text FROM snapshots WHERE id=?',(job['snapshot'],))[0]['text'])}</pre></details>{patch_link}{form}</article>''')
    memories = []
    for rule in store.rows("SELECT * FROM memories ORDER BY id DESC"):
        controls = f'<form action="/memory" method="post"><input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="id" value="{rule["id"]}"><button name="action" value="approved">Use rule</button><button class="secondary" name="action" value="dismissed">Dismiss</button></form>' if rule['status']=='proposed' else ''
        memories.append(f'<p>{e(rule["rule"])} <small>({e(rule["status"])})</small></p>{controls}')
    events = store.rows("SELECT * FROM events ORDER BY id DESC LIMIT 30")
    count = sum(j['status']=='review' for j in jobs)
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Compound · Review queue</title>
    <style>*{box-sizing:border-box}body{margin:0;background:#f5f5ef;color:#183b32;font:16px/1.6 system-ui,sans-serif}header{border-bottom:1px solid #ccd5cc;background:#fff;padding:20px max(24px,calc((100vw - 1100px)/2));display:flex;justify-content:space-between;align-items:center}.logo{font-size:27px;font-weight:800;letter-spacing:-1px}.private{font-size:12px;text-transform:uppercase;letter-spacing:2px}main{max-width:1100px;margin:auto;padding:44px 24px}h1{font-size:clamp(32px,5vw,54px);letter-spacing:-2px;line-height:1.1;margin:12px 0 20px}h2{font-size:23px;line-height:1.3;text-transform:capitalize}p{max-width:82ch}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:1.5px}.intro{color:#52655d}.stats{display:flex;gap:16px;flex-wrap:wrap;margin:30px 0}.stat{flex:1;background:#e4eddd;padding:20px;min-width:180px;border-radius:12px}.stat strong{display:block;font-size:32px}article{background:white;border:1px solid #d7ded4;border-radius:14px;padding:28px;margin:22px 0}.meta,small{color:#64736b;font-size:13px}a{color:#21634a}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.65 ui-monospace,monospace;background:#f5f6f2;padding:16px;max-height:400px;overflow:auto}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:18px}.comparison section{min-width:0}.comparison h4{margin-bottom:0}blockquote{border-left:3px solid #90a86d;margin:18px 0;padding:6px 18px;color:#496349}textarea{display:block;width:100%;min-height:76px;border:1px solid #b8c6b8;padding:12px;font:inherit;margin:8px 0 14px;border-radius:6px}button{border:0;background:#214f3b;color:white;padding:12px 18px;border-radius:6px;font:600 14px system-ui;cursor:pointer;margin:4px 8px 4px 0}.secondary{background:#edf0e8;color:#214f3b}.warning{background:#fff3d5;padding:12px;border-radius:6px}summary{cursor:pointer;padding:12px 0}form{margin-top:20px}footer{padding:24px 0;color:#64736b;font-size:13px}@media(max-width:650px){.comparison{grid-template-columns:1fr}article{padding:18px}header{gap:20px}.private{font-size:10px}}</style>
    <header><span class="logo">Compound.</span><span class="private">Private editorial workspace</span></header><main><p class="eyebrow">Electricity & solar · Pilot</p><h1>Keep useful content current.</h1><p class="intro">Review the evidence, refine the proposed edit, and decide what deserves an update. Approval records your decision; publishing remains a separate editorial step.</p>'''
    html += f'<div class="stats"><div class="stat"><strong>{count}</strong>Awaiting your review</div><div class="stat"><strong>{len(set(j["path"] for j in jobs))}</strong>Pages with saved checks</div><div class="stat"><strong>{sum(bool(c["error"]) for c in checks)}</strong>Source fetch problems</div></div>'
    html += '<details><summary>Source health & usage</summary>' + ''.join(f'<p><b>{e(c["source"])}</b> · {e(c["checked"])} · {e(c["error"] or "Fetched successfully")}</p>' for c in checks)
    html += ''.join(f'<p>{e(b["day"])}: {b["reserved"]:,} tokens reserved (includes failed attempts).</p>' for b in store.rows('SELECT * FROM budgets ORDER BY day DESC LIMIT 7')) + '</details>'
    html += ''.join(cards) or '<article><h2>Ready for the first check</h2><p>No sources have been checked yet. Run the freshness worker to populate this queue.</p></article>'
    html += '<article><h2>Editorial memory</h2><p>Repeated review feedback becomes a proposed rule. Only rules you approve are used in future drafts.</p>' + (''.join(memories) or '<p>No proposed rules yet.</p>') + '</article>'
    html += '<details><summary>Recent activity</summary>' + ''.join(f'<p>{e(v["at"])} · #{v["job"]} · {e(v["action"])} · {e(v["note"])}</p>' for v in events) + '</details><footer>Evidence quotes are checked for exact matches. Their interpretation still needs editorial review. Calculator code is never changed by this worker.</footer></main></html>'
    return html


def handler(db_path, token, root=ROOT):
    csrf = secrets.token_urlsafe(32)
    expected = 'Basic ' + base64.b64encode(('owner:' + token).encode()).decode()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def authorised(self):
            if not hmac.compare_digest(self.headers.get('Authorization', ''), expected):
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Compound Review"')
                self.end_headers()
                return False
            return True

        def respond(self, status, text):
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(text.encode())

        def do_GET(self):
            if not self.authorised():
                return
            if self.path.startswith('/patch/'):
                store = Store(db_path)
                try:
                    patch = store.proposal_patch(int(self.path.removeprefix('/patch/')), root)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.send_header('Content-Disposition', 'attachment; filename="compound-proposal.diff"')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.end_headers()
                    self.wfile.write(patch.encode())
                except ValueError as exc:
                    self.respond(400, escape(str(exc)))
                finally:
                    store.close()
                return
            if self.path != '/':
                return self.respond(404, 'Not found')
            store = Store(db_path)
            try:
                self.respond(200, render(store, csrf))
            finally:
                store.close()

        def do_POST(self):
            if not self.authorised():
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 12000:
                    raise ValueError('Invalid request size')
                data = {k: v[0] for k, v in parse_qs(self.rfile.read(size).decode()).items()}
                if not hmac.compare_digest(data.get('csrf', ''), csrf):
                    return self.respond(403, 'Refresh the queue and try again.')
                store = Store(db_path)
                try:
                    if self.path == '/decision':
                        store.decide(int(data['id']), data['action'], data.get('note', ''), root)
                        store.propose_memories()
                    elif self.path == '/memory' and data['action'] in {'approved', 'dismissed'}:
                        with store.db:
                            store.db.execute("UPDATE memories SET status=? WHERE id=? AND status='proposed'", (data['action'], int(data['id'])))
                    else:
                        raise ValueError('Unknown action')
                finally:
                    store.close()
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            except (ValueError, KeyError) as exc:
                self.respond(400, escape(str(exc)))
    return Handler


def serve(db_path, port=8765):
    token = secrets.token_urlsafe(24)
    print(f'Review queue: http://127.0.0.1:{port}\nUsername: owner\nPassword: {token}', flush=True)
    HTTPServer(('127.0.0.1', port), handler(db_path, token)).serve_forever()
