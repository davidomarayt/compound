from compound.llm import ArticleDraft, Figure, SourceRef
from compound.verify import unlisted_numbers, verify_figures

SRC = "The credit is €1,000 for a single person and €2,000 for a couple.\nClaims until 31 December 2029."


def _draft(figs, body):
    return ArticleDraft(headline="h", slug="h", summary="s", body_markdown=body, figures=figs,
                        sources=[SourceRef(title="r", url="https://r")], tags=[], email_cta="")


def test_verified_when_quote_and_value_match():
    d = _draft([Figure(value="€1,000", label="single", source_url="https://r", quote="The credit is €1,000 for a single person")],
               "You get €1,000 back.")
    v = verify_figures(d, SRC)[0]
    assert v["in_source"] is True and v["in_body"] and v["ok"]


def test_flagged_when_quote_missing_from_source():
    d = _draft([Figure(value="€5,000", label="made up", source_url="https://r", quote="the credit is €5,000")], "€5,000 for everyone")
    v = verify_figures(d, SRC)[0]
    assert v["in_source"] is False and not v["ok"]


def test_unclear_when_digits_present_but_quote_paraphrased():
    d = _draft([Figure(value="€2,000", label="couple", source_url="https://r", quote="couples get €2,000")], "€2,000 for couples")
    v = verify_figures(d, SRC)[0]
    assert v["in_source"] is None


def test_owner_figures_are_not_checked_against_source():
    d = _draft([Figure(value="12%", label="David's estimate", source_url="owner", quote="about 12% I'd say")], "roughly 12% of readers")
    v = verify_figures(d, SRC)[0]
    assert v["owner_supplied"] and v["ok"]


def test_unlisted_numbers_surfaces_body_numbers_without_figures():
    d = _draft([Figure(value="€1,000", label="x", source_url="https://r", quote="€1,000")], "€1,000 now, 2,500 claims by 2029, plus 3 things and 12%.")
    assert unlisted_numbers(d) == ["2,500", "12%"]


def test_unlisted_numbers_ignores_urls_and_bare_years():
    d = _draft([Figure(value="€1,000", label="x", source_url="https://r", quote="€1,000")],
               "€1,000 in the 2026 tax year ([Revenue](https://www.revenue.ie/ebrief/2026/no-0472026.aspx)); 45% of renters and 2,500 claims.")
    assert unlisted_numbers(d) == ["45%", "2,500"]
