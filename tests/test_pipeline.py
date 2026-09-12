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


PUBMED_XML = """<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>111</PMID><Article>
<Journal><Title>BMJ</Title><JournalIssue><PubDate><Year>2021</Year></PubDate></JournalIssue></Journal>
<ArticleTitle>Walking and mortality: a meta-analysis</ArticleTitle>
<Abstract><AbstractText Label="RESULTS">Each additional 1,000 steps a day was associated with a 15% lower risk of death.</AbstractText></Abstract>
<PublicationTypeList><PublicationType>Meta-Analysis</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"""

CI_PAGE = "GP visit cards\nChildren aged under 8 are eligible for a GP visit card. Apply online through the HSE. " + "More detail about the scheme, who qualifies, how to apply and what the card covers. " * 4


@pytest.fixture
def offline(pipeline, monkeypatch):
    """No network in tests: canned PubMed results, canned autocomplete, canned trusted pages."""
    from compound.research import parse_pubmed_xml

    monkeypatch.setattr("compound.research.pubmed_search", lambda q, n=5: parse_pubmed_xml(PUBMED_XML))
    monkeypatch.setattr("compound.research.pubmed_fetch", lambda ids: parse_pubmed_xml(PUBMED_XML) if "111" in ids else [])
    pipeline.fetch_suggestions = lambda seed: [f"{seed} ireland", f"{seed} how to claim"]
    pipeline.fetch_page_text = lambda url: CI_PAGE if "citizensinformation" in url else (_ for _ in ()).throw(RuntimeError("404"))
    return pipeline


class CitingFake:
    """A fake writer that quotes the research pack, so verification can pass."""
    triage_score = 8
    review_score = 9

    def __init__(self, base):
        self.base = base

    def __getattr__(self, name):
        return getattr(self.base, name)

    def generate_draft(self, *, kind, pillar, title, url, summary, source_text, interview, angle="", seo="", previous_draft=None, redraft_notes=None):
        from compound.llm import ArticleDraft, Figure, SourceRef

        self.last_seo = seo
        self.last_notes = redraft_notes
        if pillar == "wealth":
            figs = [Figure(value="8", label="GP card age", source_url="https://www.citizensinformation.ie/en/",
                           quote="Children aged under 8 are eligible for a GP visit card.")]
            body = "Children under 8 qualify for a GP visit card ([Citizens Information](https://www.citizensinformation.ie/en/))."
            srcs = [SourceRef(title="Citizens Information", url="https://www.citizensinformation.ie/en/")]
        else:
            q = "Each additional 1,000 steps a day was associated with a 15% lower risk of death."
            figs = [Figure(value="15%", label="lower risk of death", source_url="https://pubmed.ncbi.nlm.nih.gov/111/", quote=q),
                    Figure(value="1,000", label="steps a day", source_url="https://pubmed.ncbi.nlm.nih.gov/111/", quote=q)]
            body = "A meta-analysis found each extra 1,000 steps a day went with a 15% lower risk of death ([BMJ](https://pubmed.ncbi.nlm.nih.gov/111/))."
            srcs = [SourceRef(title="BMJ meta-analysis", url="https://pubmed.ncbi.nlm.nih.gov/111/")]
        return ArticleDraft(headline=title, slug=title.lower().replace(" ", "-")[:60], summary="What it means for you.",
                            meta_description="A plain guide for people in Ireland.", body_markdown=body, figures=figs,
                            sources=srcs, tags=[pillar], email_cta="c")

    def review_draft(self, **kw):
        return self.base.review_draft(**kw)


def test_scheduled_cycle_rotates_and_holds_by_default(offline, settings):
    from dataclasses import replace

    pipeline = offline
    pipeline.llm = CitingFake(pipeline.llm)
    pipeline.settings = replace(settings, schedule_hours=6, auto_publish="off")
    assert pipeline.schedule_due()
    rs = [pipeline.run_scheduled() for _ in range(4)]
    assert [r["pillar"] for r in rs] == ["health", "wealth", "happiness", "health"]
    assert rs[0]["published"] is None and pipeline.db.get_draft(rs[0]["draft_id"])["status"] == "pending"
    assert not pipeline.schedule_due()
    assert rs[0]["title"] != rs[3]["title"]
    # the plan reached the writer as search intent, and the pack became the item's source text
    assert "Target search query" in pipeline.llm.last_seo
    item = pipeline.db.get_item(rs[0]["item_id"])
    assert "### Source 1" in item["source_text"] and "15% lower risk" in item["source_text"]
    assert pipeline.item_plan(rs[0]["item_id"]).questions


def test_research_led_piece_verifies_and_auto_publishes(offline, settings):
    from dataclasses import replace

    pipeline = offline
    pipeline.llm = CitingFake(pipeline.llm)
    pipeline.settings = replace(settings, auto_publish="verified")
    r = pipeline.run_scheduled("health")
    assert r["sources"] == 1 + 1  # one PubMed abstract + one trusted page
    assert r["warnings"] == [] and r["editor"]["verdict"] == "publish"
    assert r["published"] and "/health/" in r["published"]
    d = pipeline.db.get_draft(r["draft_id"])
    assert d["meta_description"].startswith("A plain guide") and d["editor_json"]
    # the published file carries the meta description and the site rendered search metadata
    path = Path(pipeline.db.published_for_item(r["item_id"])["path"])
    assert "meta_description: A plain guide" in path.read_text(encoding="utf-8")
    html = (settings.public_dir / "health" / d["slug"] / "index.html").read_text(encoding="utf-8")
    assert '<meta name="description" content="A plain guide' in html and 'rel="canonical"' in html
    assert '"@type": "Article"' in html and "pubmed.ncbi.nlm.nih.gov/111" in html

    # take it down again
    url = pipeline.unpublish(r["item_id"])
    assert url == r["published"] and not path.exists()
    assert pipeline.db.get_item(r["item_id"])["status"] == "dropped"
    assert pipeline.unpublish(r["item_id"]) is None


def test_editor_revise_path_and_holds(offline, settings):
    from dataclasses import replace

    pipeline = offline
    fake = CitingFake(pipeline.llm)
    pipeline.llm = fake
    pipeline.settings = replace(settings, auto_publish="verified", editor_min_score=8)
    fake.base.review_score = 5  # editor rejects both the draft and the revision
    r = pipeline.run_scheduled("wealth")
    assert fake.last_notes and "Editor review (score 5/10)" in fake.last_notes
    assert r["editor"]["revised_from"] and r["published"] is None
    assert any(w.startswith("editor score 5/10") for w in r["warnings"])
    assert pipeline.db.get_draft(r["draft_id"])["version"] == 2


def test_too_few_sources_holds(offline, settings, monkeypatch):
    from dataclasses import replace

    pipeline = offline
    pipeline.llm = CitingFake(pipeline.llm)
    monkeypatch.setattr("compound.research.pubmed_search", lambda q, n=5: [])
    pipeline.settings = replace(settings, auto_publish="verified", min_sources=2, deep_research=False)
    r = pipeline.run_scheduled("health")  # only the CI page fetches
    assert r["sources"] == 1 and r["published"] is None
    assert any("only 1 source" in w for w in r["warnings"])


def test_topic_bank_fixes_the_title(offline, settings, tmp_path):
    from dataclasses import replace

    pipeline = offline
    bank = tmp_path / "topics"; bank.mkdir()
    (bank / "health.md").write_text("# my list\nWhy a 20 minute walk beats a gym you never visit\n")
    pipeline.settings = replace(settings, topics_dir=bank)
    assert pipeline.bank_topic("health") == "Why a 20 minute walk beats a gym you never visit"
    plan = pipeline.plan_topic("health")
    assert plan.title == "Why a 20 minute walk beats a gym you never visit"
    pipeline.create_manual_item(plan.title, "health")
    assert pipeline.bank_topic("health") == ""  # used up -> planner chooses freely


def test_untrusted_urls_are_dropped_and_pmc_resolves_to_pubmed(monkeypatch):
    from compound.research import build_pack, is_trusted, parse_pubmed_xml

    assert is_trusted("https://tilda.tcd.ie/news-events/2025/x/")
    assert is_trusted("https://joint-research-centre.ec.europa.eu/loneliness")
    assert is_trusted("https://www.cdc.gov/x") and is_trusted("https://www.ox.ac.uk/x")
    assert not is_trusted("https://blog.example.com/x") and not is_trusted("https://alone.ie/contact/")

    monkeypatch.setattr("compound.research.pmc_to_pmid", lambda pmcid: "111" if pmcid == "PMC9593938" else "")
    monkeypatch.setattr("compound.research.pubmed_fetch", lambda ids: parse_pubmed_xml(PUBMED_XML) if ids == ["111"] else [])
    pack = build_pack(
        pubmed_queries=[],
        urls=["https://blog.example.com/x", "https://www.revenue.ie/en/", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9593938/"],
        fetch_page=lambda u: "Revenue page\n" + "x" * 300,
    )
    assert [s.url for s in pack.sources] == ["https://www.revenue.ie/en/", "https://pubmed.ncbi.nlm.nih.gov/111/"]


def test_figures_verify_against_their_cited_pages():
    from compound.llm import ArticleDraft, Figure, SourceRef
    from compound.verify import verify_figures

    draft = ArticleDraft(
        headline="h", slug="h", summary="s",
        body_markdown="Children under 8 get a GP visit card. Call 112 or 999 in an emergency. Honey before 1 year is unsafe.",
        figures=[
            Figure(value="8", label="GP card age", source_url="https://hse.example/gp", quote="Children aged under 8 are eligible for a GP visit card."),
            Figure(value="112 or 999", label="emergency", source_url="https://hse.example/fever", quote="Call 112 or 999 if your child is unresponsive."),
            Figure(value="1 year", label="honey", source_url="https://hse.example/missing", quote="Do not give honey to babies under 1 year."),
        ],
        sources=[SourceRef(title="HSE", url="https://hse.example/gp")], tags=["kids"], email_cta="c",
    )
    pages = {
        "https://hse.example/gp": "GP visit cards. Children aged under 8 are eligible for a GP visit card. Apply online.",
        "https://hse.example/fever": "Fever in children. Call 112 or 999 if your child is unresponsive.",
        "https://hse.example/missing": "",
    }
    res = {r["label"]: r for r in verify_figures(draft, "", pages)}
    assert res["GP card age"]["ok"] and res["emergency"]["ok"]
    assert res["honey"]["in_source"] is False and not res["honey"]["ok"]


def test_owner_topic_goes_through_research_flow(offline, settings):
    from dataclasses import replace

    pipeline = offline
    pipeline.llm = CitingFake(pipeline.llm)
    pipeline.settings = replace(settings, auto_publish="verified", schedule_hours=6)
    r = pipeline.run_scheduled("health", fixed_title="Vitamin D in Ireland: who needs a supplement")
    assert r["title"] == "Vitamin D in Ireland: who needs a supplement"
    assert r["sources"] == 2 and r["published"]
    assert pipeline.item_plan(r["item_id"]).target_query
    assert pipeline.schedule_due()  # an owner-requested piece does not count as the scheduled one


def test_deep_research_feeds_the_pack_and_the_writer(offline, settings, monkeypatch):
    from dataclasses import replace

    pipeline = offline
    fake = CitingFake(pipeline.llm)
    pipeline.llm = fake
    # the planner names no PubMed queries for wealth, so the study can only come from the research report
    monkeypatch.setattr("compound.research.pubmed_search", lambda q, n=5: [])
    pipeline.settings = replace(settings, auto_publish="verified", deep_research=True)
    r = pipeline.run_scheduled("wealth")
    item = pipeline.db.get_item(r["item_id"])
    assert "pubmed.ncbi.nlm.nih.gov/111" in item["research_json"]  # PMID from the report was fetched as an abstract
    assert "(fake) research summary" in item["research_notes"]
    assert "Research notes" in fake.last_seo and "walking lowers mortality" in fake.last_seo
    assert r["sources"] == 2 and r["published"]

    pipeline.settings = replace(settings, auto_publish="verified", deep_research=False)
    r2 = pipeline.run_scheduled("wealth")
    assert pipeline.db.get_item(r2["item_id"])["research_notes"] == ""


def test_schedule_accepts_fractions_of_an_hour(pipeline, settings):
    from dataclasses import replace
    from datetime import datetime, timedelta, timezone

    pipeline.settings = replace(settings, schedule_hours=0.25)
    pipeline.db.set_state(pipeline.SCHEDULE_LAST_KEY, (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat())
    assert not pipeline.schedule_due()
    pipeline.db.set_state(pipeline.SCHEDULE_LAST_KEY, (datetime.now(timezone.utc) - timedelta(minutes=16)).isoformat())
    assert pipeline.schedule_due()


def test_ad_slots_render_only_when_configured(pipeline, settings):
    from dataclasses import replace
    from compound.site.build import build_site

    pipeline.llm = CitingFake(pipeline.llm)
    pipeline.settings = replace(settings, auto_publish="always", deep_research=False)
    r = pipeline.run_scheduled("health")
    slug = pipeline.db.get_draft(r["draft_id"])["slug"]
    page = settings.public_dir / "health" / slug / "index.html"
    assert "adsbygoogle" not in page.read_text(encoding="utf-8")
    assert not (settings.public_dir / "ads.txt").exists()

    (settings.content_dir / "site.yml").write_text(
        "adsense:\n  client: ca-pub-123\n  slots:\n    article_top: '111'\n    article_bottom: ''\n    feed: '333'\n"
    )
    build_site(settings)
    html = page.read_text(encoding="utf-8")
    assert "adsbygoogle.js?client=ca-pub-123" in html
    assert html.count('data-ad-slot="111"') == 1 and 'data-ad-slot=""' not in html  # blank bottom slot not rendered
    assert 'data-ad-slot="333"' in (settings.public_dir / "health" / "index.html").read_text(encoding="utf-8")
    assert (settings.public_dir / "ads.txt").read_text() == "google.com, pub-123, DIRECT, f08c47fec0942fa0\n"
    # previews never carry ads
    from compound.site.build import render_preview
    art = pipeline._article_from_draft(pipeline.db.get_draft(r["draft_id"]), pipeline.db.get_item(r["item_id"]))
    render_preview(settings, "tok123", art)
    assert "adsbygoogle" not in (settings.public_dir / "preview" / "tok123" / "index.html").read_text(encoding="utf-8")


def test_signup_form_hidden_until_configured(pipeline, settings):
    from dataclasses import replace
    from compound.site.build import build_site

    build_site(replace(settings, email_form_action=""))
    home = settings.public_dir / "index.html"
    assert "signup-form" not in home.read_text(encoding="utf-8")
    (settings.content_dir / "site.yml").write_text("email_form_action: https://app.kit.com/forms/123/subscriptions\n")
    build_site(settings)
    html = home.read_text(encoding="utf-8")
    assert 'action="https://app.kit.com/forms/123/subscriptions"' in html and 'name="email_address"' in html
