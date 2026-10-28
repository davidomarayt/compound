import argparse
import json
from pathlib import Path
from compound.config import load_settings
from compound.freshness.core import ROOT, Store, config, run, analyse


def main():
    parser = argparse.ArgumentParser(description='Compound private freshness review queue')
    parser.add_argument('--db', type=Path, default=ROOT / 'data/freshness.sqlite3')
    sub = parser.add_subparsers(dest='command', required=True)
    poll = sub.add_parser('check', help='Fetch sources and checkpoint jobs')
    poll.add_argument('--ai', action='store_true', help='Use configured Anthropic API to propose edits')
    web = sub.add_parser('serve', help='Open the private loopback review screen')
    web.add_argument('--port', type=int, default=8765)
    sub.add_parser('status')
    sub.add_parser('reflect', help='Propose editorial rules from repeated human feedback')
    args = parser.parse_args()
    load_settings()  # load existing .env; no credentials copied into queue or logs
    if args.command == 'serve':
        from compound.freshness.web import serve
        serve(args.db, args.port)
        return
    store = Store(args.db)
    try:
        if args.command == 'check':
            if args.ai:
                import os
                if not os.environ.get('FRESHNESS_MODEL') or not os.environ.get('ANTHROPIC_API_KEY'):
                    parser.error('--ai requires FRESHNESS_MODEL and ANTHROPIC_API_KEY')
            run(store, config(), analyser=analyse if args.ai else None)
        elif args.command == 'reflect':
            store.propose_memories()
        print(json.dumps({'jobs': store.rows('SELECT status, COUNT(*) AS count FROM jobs GROUP BY status'),
                          'sources': store.rows('SELECT * FROM checks'),
                          'budgets': store.rows('SELECT * FROM budgets ORDER BY day DESC LIMIT 7')}, indent=2))
    finally:
        store.close()


if __name__ == '__main__':
    main()
