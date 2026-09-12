"""The review message is the thing David reads on his phone; make sure it carries the right bits."""
from compound.bot import Bot
from compound.db import Database
from compound.llm import build_llm
from compound.pipeline import Pipeline


def test_review_text_has_headline_figures_and_preview(settings):
    p = Pipeline(settings=settings, db=Database(settings.db_path), llm=build_llm(settings), sources=[])
    item_id = p.db.insert_item(source_key="manual", external_id="x", pillar="wealth", title="Rent Tax Credit rises to €1,000",
                               url="https://www.revenue.ie/x", summary=None, published_at=None, kind="manual",
                               source_text="The credit is €1,000 for a single person.")
    p.prepare_questions(item_id)
    p.record_answer(item_id, "Claim it.", "text")
    did = p.make_draft(item_id)
    text = Bot(settings, p).review_text(p.db.get_draft(did))
    assert "Draft v1" in text and "€1,000" in text and "Figures used (1)" in text
    assert "✅" in text and "/preview/" in text
    assert "<b>" in text  # HTML mode
