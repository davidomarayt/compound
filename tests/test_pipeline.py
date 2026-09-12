"""End to end with the fake LLM: item -> questions -> answers -> draft -> preview -> approve -> published page."""
from pathlib import Path

import pytest

from compound.db import Database
from compound.llm import build_llm
from compound.pipeline import Pipeline
from compound.poller import poll_all
from compound.sources.base import Source, SourceItem
from tests.conftest import FIXTURES


class FixtureSource(Source):
    key = "revenue_ebrief"
    name = "Revenue eBriefs (fixture)"
    pillar = "wealth"

    def __init__(self, n=3):
        self.n = n

    def fetch(self):
        return [SourceItem(external_id=f"2026/no-{i:03d}2026", title=f"Revenue eBrief No. {i:03d}/26 - Rent Tax Credit",
                           url=f"https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-{i:03d}2026.aspx")
                for i in range(self.n, 0, -1)]

    def fetch_text(self, url):
        from compound.sources.base import html_to_text
        return html_to_text((FIXTURES / "revenue_ebrief.html").read_text())


@pytest.fixture
def pipeline(settings):
    return Pipeline(settings=settings, db=Database(settings.db_path), llm=build_llm(settings), sources=[FixtureSource()])


def test_first_poll_backfills_only_newest(pipeline):
    new_ids = poll_all(pipeline.db, pipeline.sources, pipeline.settings)
    assert len(new_ids) == 1
    assert len(pipeline.db.items_with_status("seen")) == 2
    # second poll: nothing new
    assert poll_all(pipeline.db, pipeline.sources, pipeline.settings) == []
    # a newly listed item after initialisation is queued as new
    pipeline.sources[0].n = 4
    assert len(poll_all(pipeline.db, pipeline.sources, pipeline.settings)) == 1


def test_full_loop(pipeline, settings):
    db = pipeline.db
    item_id = poll_all(db, pipeline.sources, settings)[0]

    qids = pipeline.prepare_questions(item_id)
    assert len(qids) == 3
    assert db.get_item(item_id)["status"] == "questions_sent"
    assert "€1,000" in db.get_item(item_id)["source_text"]

    # answers bind to questions in order; a reply-to binds explicitly
    assert pipeline.record_answer(item_id, "Shift workers should claim it now.", "voice") == (1, 1, 3)
    assert pipeline.record_answer(item_id, "Renters whose landlord isn't registered.", "text", question_id=qids[2]) == (3, 2, 3)
    assert not pipeline.all_answered(item_id)
    assert pipeline.record_answer(item_id, "Log into myAccount this week.", "text") == (2, 3, 3)
    assert pipeline.all_answered(item_id)
    # extra note after all answered becomes an untied note
    assert pipeline.record_answer(item_id, "Also mention the 2029 deadline.", "text") == (None, 3, 3)
    interview = pipeline.interview(item_id)
    assert len(interview) == 4 and interview[-1][0].startswith("Anything else")

    draft_id = pipeline.make_draft(item_id)
    d = db.get_draft(draft_id)
    assert d["status"] == "pending" and db.get_item(item_id)["status"] == "pending"
    preview = settings.public_dir / "preview" / d["preview_token"] / "index.html"
    assert preview.exists()
    html = preview.read_text()
    assert "noindex" in html and "PREVIEW" in html and "Shift workers should claim it now." in html
    assert pipeline.preview_url(d).startswith("https://example.test/preview/")
    # fake draft's figure quote is the source line, so verification passes
    assert not [w for w in pipeline.draft_warnings(d) if "not found" in w]

    # nothing in content/ before approval
    assert not list((settings.content_dir / "wealth").glob("*.md")) if (settings.content_dir / "wealth").exists() else True

    # redraft supersedes and re-renders preview
    draft2 = pipeline.make_draft(item_id, redraft_notes="Shorter intro.")
    assert db.get_draft(draft_id)["status"] == "superseded"
    assert not preview.exists()
    d2 = db.get_draft(draft2)
    assert d2["version"] == 2 and "Shorter intro." in d2["body_md"]

    with pytest.raises(PermissionError):
        pipeline.publish(draft2, approved_by="")
    with pytest.raises(ValueError):
        pipeline.publish(draft_id, approved_by="test")  # superseded, not pending

    url = pipeline.publish(draft2, approved_by="test")
    assert url == f"https://example.test/wealth/{d2['slug']}/"
    md = settings.content_dir / "wealth" / f"{d2['slug']}.md"
    assert md.exists() and "approved_by: test" in md.read_text()
    page = settings.public_dir / "wealth" / d2["slug"] / "index.html"
    assert page.exists()
    out = page.read_text()
    assert d2["headline"] in out and "Sources" in out and "Figures used" in out and "consent" in out
    assert db.get_item(item_id)["status"] == "published"
    assert db.get_draft(draft2)["status"] == "approved"
    assert not (settings.public_dir / "preview" / d2["preview_token"]).exists()
    # homepage lists it in the wealth column; tag page + search index exist
    home = (settings.public_dir / "index.html").read_text()
    assert d2["headline"] in home
    assert (settings.public_dir / "tag" / "revenue" / "index.html").exists()
    assert d2["headline"] in (settings.public_dir / "search.json").read_text()
    assert (settings.public_dir / "about" / "index.html").exists()
    assert "Disallow: /preview/" in (settings.public_dir / "robots.txt").read_text()


def test_slug_collision_gets_suffix(pipeline, settings):
    db = pipeline.db
    for _ in range(2):
        item_id = db.insert_item(source_key="manual", external_id=f"m{_}", pillar="health", title="Same title",
                                 url=None, summary=None, published_at=None, kind="manual", source_text="")
        pipeline.prepare_questions(item_id)
        pipeline.record_answer(item_id, "a", "text")
        did = pipeline.make_draft(item_id)
        pipeline.publish(did, approved_by="test")
    files = sorted(p.name for p in (settings.content_dir / "health").glob("*.md"))
    assert files == ["same-title-2.md", "same-title.md"]


def test_drop_rejects_pending_draft(pipeline):
    item_id = pipeline.create_manual_item("Why night shifts wreck sleep", "health")
    pipeline.prepare_questions(item_id)
    did = pipeline.make_draft(item_id)
    pipeline.drop(item_id)
    assert pipeline.db.get_draft(did)["status"] == "rejected"
    assert pipeline.db.get_item(item_id)["status"] == "dropped"


def test_draft_without_interview(pipeline, settings):
    """INTERVIEW=0 path: a fresh item can be drafted with no questions; the draft step fetches the source."""
    db = pipeline.db
    item_id = poll_all(db, pipeline.sources, settings)[0]
    assert db.get_item(item_id)["status"] == "new" and not db.get_item(item_id)["source_text"]
    draft_id = pipeline.make_draft(item_id)
    d = db.get_draft(draft_id)
    assert db.get_item(item_id)["status"] == "pending"
    assert "€1,000" in db.get_item(item_id)["source_text"]
    assert d["headline"] and pipeline.preview_url(d).startswith("https://example.test/preview/")


def test_triage_scores_and_skips(pipeline, settings, monkeypatch):
    """Triage stores the score, reason and angle; a low score can be skipped and reopened."""
    db = pipeline.db
    item_id = poll_all(db, pipeline.sources, settings)[0]
    assert pipeline.needs_triage(item_id)

    pipeline.llm.triage_score = 2
    t = pipeline.triage(item_id)
    row = db.get_item(item_id)
    assert t.score == 2 and row["relevance"] == 2 and row["triage_note"] and row["angle"] == ""
    assert row["summary"].startswith("(fake)")  # triage fills the summary when the source had none
    assert not pipeline.needs_triage(item_id)  # scored once, never re-scored

    pipeline.skip(item_id)
    assert db.get_item(item_id)["status"] == "skipped"
    assert item_id not in {it["id"] for it in db.open_items()}

    # /open on a skipped item drafts it anyway; the angle (empty here) does not break the prompt
    draft_id = pipeline.make_draft(item_id)
    assert db.get_draft(draft_id)["headline"]


def test_triage_angle_reaches_draft_prompt(pipeline, settings):
    from compound.llm import draft_prompt

    db = pipeline.db
    item_id = poll_all(db, pipeline.sources, settings)[0]
    pipeline.llm.triage_score = 9
    pipeline.triage(item_id)
    assert db.get_item(item_id)["angle"].startswith("(fake) renters")
    text = draft_prompt(
        kind="news", pillar="wealth", title="t", url="u", summary="", source_text="s", interview=[], samples=[],
        previous_draft=None, redraft_notes=None, angle=db.get_item(item_id)["angle"],
    )
    assert "## Reader angle\n(fake) renters" in text
    assert "## Reader angle" not in draft_prompt(
        kind="news", pillar="wealth", title="t", url="u", summary="", source_text="s", interview=[], samples=[],
        previous_draft=None, redraft_notes=None,
    )


def test_manual_items_and_disabled_threshold_skip_triage(pipeline, settings, monkeypatch):
    manual = pipeline.create_manual_item("Rent tax credit explained", "wealth")
    assert not pipeline.needs_triage(manual)
    from dataclasses import replace
    pipeline.settings = replace(settings, min_relevance=0)
    item_id = poll_all(pipeline.db, pipeline.sources, pipeline.settings)[0]
    assert not pipeline.needs_triage(item_id)


def test_scheduled_cycle_rotates_and_holds_by_default(pipeline, settings):
    from dataclasses import replace

    pipeline.settings = replace(settings, schedule_hours=6, auto_publish="off")
    assert pipeline.schedule_due()  # never run yet
    r1 = pipeline.run_scheduled()
    r2 = pipeline.run_scheduled()
    r3 = pipeline.run_scheduled()
    r4 = pipeline.run_scheduled()
    assert [r["pillar"] for r in (r1, r2, r3, r4)] == ["health", "wealth", "happiness", "health"]
    assert r1["published"] is None and pipeline.db.get_draft(r1["draft_id"])["status"] == "pending"
    assert not pipeline.schedule_due()  # just ran
    # topics do not repeat: the fake proposes from the count of recent titles
    assert r1["title"] != r4["title"]


def test_scheduled_cycle_publishes_when_verified(pipeline, settings):
    from dataclasses import replace

    pipeline.settings = replace(settings, auto_publish="verified", site_base_url="https://example.test")
    r = pipeline.run_scheduled("wealth")
    d = pipeline.db.get_draft(r["draft_id"])
    if pipeline.draft_warnings(d):
        assert r["published"] is None and d["status"] == "pending"
    else:
        assert r["published"].startswith("https://example.test/wealth/") and d["status"] == "approved"
        assert pipeline.db.published_for_item(r["item_id"])["approved_by"] == "auto:verified"


def test_topic_bank_takes_priority(pipeline, settings, tmp_path):
    from dataclasses import replace

    bank = tmp_path / "topics"; bank.mkdir()
    (bank / "health.md").write_text("# my list\nWhy a 20 minute walk beats a gym you never visit\nSecond idea\n")
    pipeline.settings = replace(settings, topics_dir=bank)
    assert pipeline.pick_topic("health") == ("Why a 20 minute walk beats a gym you never visit", "")
    pipeline.create_manual_item("Why a 20 minute walk beats a gym you never visit", "health")
    assert pipeline.pick_topic("health") == ("Second idea", "")
    pipeline.create_manual_item("Second idea", "health")
    assert pipeline.pick_topic("health")[0].startswith("(fake) health topic")  # bank exhausted -> Claude
