"""Mag7 unattended publication only proceeds through evidence and photo gates."""
from datetime import date, timedelta
from pathlib import Path
import json
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import mag7_autopublish as autopub
import mag7_pilot as pilot


def test_28_slots_rotate_seven_companies_and_end_after_four_weeks():
    slots=[pilot.assignment(pilot.START+timedelta(days=x)) for x in range(28)]
    assert slots[0] == ("TSLA",1)
    assert slots[1] == ("MSFT",1)
    assert slots[-1] == ("META",4)
    assert all(sum(t == ticker for t,_ in slots) == 4 for ticker in pilot.ROTATION)
    assert pilot.assignment(pilot.START+timedelta(days=28)) is None


def test_every_company_has_real_documentary_photo_with_manual_source_credit():
    library=json.loads((ROOT/"content/mag7-photo-library.json").read_text())
    assert set(library["photos"]) == set(pilot.ROTATION)
    for ticker in pilot.ROTATION:
        for week in (1,2,3,4):
            photo=autopub.photo_for(ticker,week)
            assert photo["source"].startswith("https://unsplash.com/photos/")
            assert "/ Unsplash" in photo["credit"]
            assert photo["year"].isdecimal()
            assert "render" not in photo["alt"].lower()
            assert "illustration" not in photo["alt"].lower()
    assert "Microsoft" in autopub.photo_for("MSFT",1)["alt"]


def test_draft_requires_worked_source_documentation_and_originality():
    sec=pilot.latest_sec("MSFT")
    body="\n".join("## "+h+"\n\n"+("Financial reporting and risk review. "*55)
                   for h in autopub.HEADINGS)
    body+="\n\n[SEC filing]("+sec["filing"]+") [IR]("+pilot.IR_PAGES["MSFT"]+") "
    body+="[Other](https://www.reuters.com/technology/) "
    body+="[Stock](https://compound.ie/stocks/msft/) "
    body+="[Earnings](https://compound.ie/wealth/earnings/)"
    candidate={
        "publish":True,"blockers":[],"body_markdown":body,
        "sources":[{"url":sec["filing"]},{"url":pilot.IR_PAGES["MSFT"]},
                   {"url":"https://www.reuters.com/technology/"}],
        "summary":"Microsoft's recent financial results, Azure investment and investor cash flow deserve scrutiny in a balanced analysis.",
        "meta_description":"Microsoft Azure AI investment, capital expenditure, operating margins and reported earnings: an independent analysis of the cash flow.",
        "title":"Microsoft Azure AI Capital Spending: What Investors Should Measure",
    }
    autopub.validate(candidate,"MSFT",sec)
    for changed in [
        {"publish":False},
        {"blockers":["Claims not verified"]},
        {"sources":[{"url":sec["filing"]}]},
        {"body_markdown":body.replace("https://compound.ie/stocks/msft/","/missing/")},
        {"body_markdown":body.replace(sec["filing"],"https://unrelated.example/")}
    ]:
        with pytest.raises(ValueError):
            autopub.validate({**candidate,**changed},"MSFT",sec)


def test_renderer_produces_annotated_non_ai_canonical_with_real_photo(monkeypatch,tmp_path):
    monkeypatch.setattr(autopub,"ROOT",tmp_path)
    (tmp_path/"content/wealth").mkdir(parents=True)
    def approved_image(photo,path):
        from PIL import Image
        path.parent.mkdir(parents=True,exist_ok=True)
        Image.new("RGB",(1600,900)).save(path,"JPEG")
    monkeypatch.setattr(autopub,"fetch_real_photo",approved_image)
    data={
        "title":"Microsoft cloud capital spending versus earnings",
        "seo_title":"Microsoft Azure AI Capital Spending: Investor Research",
        "summary":"The relationship between capital spending and future profitability is examined.",
        "meta_description":"Microsoft earnings and AI infrastructure: cash flow, costs, profitability and key factors for investors examining Azure.",
        "body_markdown":"## What changed\n\nInvestigating reported results.",
        "sources":[{"title":"SEC 10-K","url":"https://www.sec.gov/Archives/test"}],
    }
    photo={"alt":"Actual Microsoft building photographed 2022",
           "credit":"Sam Torres / Unsplash",
           "source":"https://unsplash.com/photos/a-building-with-a-microsoft-sign-on-the-side-of-it-7j-PBAMqAtI",
           "year":"2022"}
    file,image,slug=autopub.article(date(2026,10,17),"MSFT",1,data,photo)
    metadata=yaml_header(file)
    assert metadata["image"]==metadata["social_image"]
    assert metadata["publication_status"]=="published"
    assert "mag7-research" in metadata["tags"]
    assert metadata["image_source"]==photo["source"]
    assert "Unsplash" in metadata["image_credit"]
    assert metadata["require_pinned_hero"] is True
    assert image.is_file() and slug in file.name
    assert "archival photograph" in file.read_text().lower()
    with pytest.raises(ValueError,match="already exists"):
        autopub.article(date(2026,10,17),"MSFT",1,data,photo)


def yaml_header(file):
    import yaml
    return yaml.safe_load(file.read_text().split("---",2)[1])


def test_missing_credentials_never_yield_an_article(monkeypatch,tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY",raising=False)
    report=tmp_path/"review.md"
    assert autopub.run(date(2026,10,17),report)==1
    assert "Status: skipped" in report.read_text()
    assert "ANTHROPIC_API_KEY" in report.read_text()
    assert autopub.run(date(2026,11,13),tmp_path/"out.md")==3


def test_workflow_builds_before_commit_and_dispatches_pages():
    workflow=(ROOT/".github/workflows/mag7-research.yml").read_text()
    assert "permissions:" in workflow and "contents: write" in workflow
    assert "actions: write" in workflow and "issues: write" in workflow
    assert "mag7_autopublish.py" in workflow and "news_images.py" in workflow
    assert workflow.index("compound build") < workflow.index("git add --")
    assert "gh workflow run site.yml" in workflow
    assert "gh issue create" in workflow
