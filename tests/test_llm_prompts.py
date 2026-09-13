from pathlib import Path

from compound.llm import draft_prompt, load_style_samples, normalise_tags, questions_prompt, slugify


def test_prompts_fill_without_breaking_on_braces():
    p = questions_prompt(kind="news", pillar="wealth", title="T", url="U", source_text="{weird} {braces}", n_questions=3)
    assert "{weird} {braces}" in p and "{n_questions}" not in p and "3 short" in p
    d = draft_prompt(kind="news", pillar="wealth", title="T", url="U", summary="S", source_text="src",
                     interview=[("Q?", "A.")], samples=["I write like this."], previous_draft="old", redraft_notes="tighter")
    assert "I write like this." in d and "Q1: Q?" in d and "Owner: A." in d and "tighter" in d and "<previous>" in d
    assert "{" not in d.replace("{weird}", "")  # every placeholder replaced


def test_style_samples_ignore_comments(tmp_path: Path):
    (tmp_path / "voice-samples.md").write_text("# heading\n\n- One sentence.\nTwo sentence.\n")
    assert load_style_samples(tmp_path) == ["One sentence.", "Two sentence."]


def test_slug_and_tags():
    assert slugify("Rent Tax Credit rises to €1,000 for 2026!") == "rent-tax-credit-rises-to-eur1-000-for-2026"
    assert normalise_tags(["Budget 2027", "budget-2027", "PAYE", ""]) == ["budget-2027", "paye"]
