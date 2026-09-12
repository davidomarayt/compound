"""Command line entry point: `compound <command>`."""
from __future__ import annotations

import argparse
import secrets
import http.server
import logging
import sys
from functools import partial

from compound.config import load_settings
from compound.db import Database
from compound.llm import build_llm
from compound.pipeline import Pipeline
from compound.poller import poll_all
from compound.site.build import build_site
from compound.sources import build_sources


def make_pipeline() -> Pipeline:
    settings = load_settings()
    return Pipeline(settings=settings, db=Database(settings.db_path), llm=build_llm(settings), sources=build_sources(settings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compound")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db", help="create the SQLite database")
    p_setup = sub.add_parser("setup", help="interactive: write .env, verify the bot token, link your Telegram account")
    p_setup.add_argument("--skip-verify", action="store_true", help="do not contact Telegram (offline)")
    p_poll = sub.add_parser("poll", help="poll sources once and queue new items")
    p_poll.add_argument("--dry-run", action="store_true", help="list what the sources return, store nothing")
    sub.add_parser("run", help="run the Telegram bot with the source poller inside it")
    sub.add_parser("build", help="render the static site into public/")
    p_serve = sub.add_parser("serve", help="serve public/ locally")
    p_serve.add_argument("--port", type=int, default=8080)
    p_sim = sub.add_parser("simulate-item", help="inject a fake item so the loop can be tested without a source")
    p_sim.add_argument("--title", default="Revenue eBrief No. 999/26: Rent Tax Credit increased to €1,000")
    p_sim.add_argument("--pillar", default="wealth")
    p_auto = sub.add_parser("auto-once", help="run one scheduled cycle now: pick a topic, draft, publish if AUTO_PUBLISH allows")
    p_auto.add_argument("--pillar", choices=["health", "wealth", "happiness"], help="override the rotation for this run")
    sub.add_parser("queue", help="list open items and pending drafts")
    p_draft = sub.add_parser("draft", help="draft an item from the CLI (answers taken from the DB)")
    p_draft.add_argument("item_id", type=int)
    p_ans = sub.add_parser("answer", help="record a text answer for an item from the CLI")
    p_ans.add_argument("item_id", type=int)
    p_ans.add_argument("text")
    p_pub = sub.add_parser("publish", help="publish a pending draft (manual approval from the CLI)")
    p_pub.add_argument("draft_id", type=int)
    p_pub.add_argument("--yes", action="store_true", help="confirm you have reviewed the preview")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.cmd == "setup":
        from compound.setup import run_setup

        return run_setup(skip_verify=args.skip_verify)

    if args.cmd == "init-db":
        s = load_settings()
        Database(s.db_path).close()
        print(f"ok: {s.db_path}")
        return 0

    if args.cmd == "build":
        stats = build_site(load_settings())
        print(f"built: {stats}")
        return 0

    if args.cmd == "serve":
        s = load_settings()
        s.public_dir.mkdir(parents=True, exist_ok=True)
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(s.public_dir))
        print(f"serving {s.public_dir} on http://localhost:{args.port}/")
        http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler).serve_forever()
        return 0

    p = make_pipeline()
    if args.cmd == "poll":
        ids = poll_all(p.db, p.sources, p.settings, dry_run=args.dry_run)
        if not args.dry_run:
            print(f"new items: {ids}")
            for item_id in ids:
                if p.needs_triage(item_id):
                    t = p.triage(item_id)
                    if t.score < p.settings.min_relevance:
                        p.skip(item_id)
                        print(f"  #{item_id} skipped ({t.score}/10): {t.reason}")
                        continue
                if not p.settings.interview:
                    print(f"  #{item_id}: queued for drafting (INTERVIEW=0); run: compound draft {item_id}")
                    continue
                p.prepare_questions(item_id)
                for q in p.db.questions_for(item_id):
                    print(f"  #{item_id} Q{q['ordinal']}: {q['text']}")
        return 0

    if args.cmd == "run":
        if not p.settings.telegram_bot_token:
            print("TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
            return 2
        from compound.bot import Bot

        Bot(p.settings, p).run()
        return 0

    if args.cmd == "simulate-item":
        text = (
            f"{args.title}\n\nRevenue has today published guidance confirming the Rent Tax Credit is €1,000 for a "
            "single person and €2,000 for a jointly assessed couple for the 2026 tax year. Claims for 2025 can be "
            "made through myAccount until 31 December 2029."
        )
        item_id = p.db.insert_item(
            source_key="simulated", external_id=f"sim-{secrets.token_hex(4)}",
            pillar=args.pillar, title=args.title, url="https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-9992026.aspx",
            summary=None, published_at=None, status="new", source_text=text,
        )
        print(f"queued item #{item_id} as 'new'. The bot picks it up on its next poll; or run: compound poll")
        return 0

    if args.cmd == "auto-once":
        r = p.run_scheduled(args.pillar)
        print(f"#{r['item_id']} ({r['pillar']}): {r['title']}")
        if r["published"]:
            print(f"published: {r['published']}")
        else:
            d = p.db.get_draft(r["draft_id"])
            print(f"held for review (AUTO_PUBLISH={p.settings.auto_publish}); preview: {p.preview_url(d)}")
            for w in r["warnings"]:
                print(f"  check: {w}")
        return 0

    if args.cmd == "queue":
        for it in p.db.open_items():
            qs = p.db.questions_for(it["id"])
            answered = len(p.db.answered_question_ids(it["id"]))
            print(f"#{it['id']} [{it['status']}] {it['pillar']} {answered}/{len(qs)} — {it['title']}")
            for q in qs:
                print(f"    Q{q['ordinal']}: {q['text']}")
        for d in p.db.pending_drafts():
            print(f"draft #{d['id']} v{d['version']} for item #{d['item_id']}: {d['headline']}  preview={p.preview_url(d)}")
        return 0

    if args.cmd == "answer":
        ordinal, answered, total = p.record_answer(args.item_id, args.text, "text")
        print(f"recorded as Q{ordinal} ({answered}/{total})")
        return 0

    if args.cmd == "draft":
        if p.settings.interview and p.db.get_item(args.item_id) and p.db.get_item(args.item_id)["status"] == "new":
            p.prepare_questions(args.item_id)
        draft_id = p.make_draft(args.item_id)
        d = p.db.get_draft(draft_id)
        print(f"draft #{draft_id}: {d['headline']}\npreview: {p.preview_url(d)}")
        for w in p.draft_warnings(d):
            print(f"  check: {w}")
        return 0

    if args.cmd == "publish":
        if not args.yes:
            print("Refusing: pass --yes to confirm you have reviewed the preview.", file=sys.stderr)
            return 2
        url = p.publish(args.draft_id, approved_by="cli")
        print(f"published: {url}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
