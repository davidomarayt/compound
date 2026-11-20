import json
from datetime import date
from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compound.site.health_conditions import load_conditions


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def catalogue(tmp_path):
    index = [["T", "Test topic", "https://www2.hse.ie/conditions/test-topic/"]]
    guide = {
        "kind": "test",
        "summary": "A health test.",
        "symptoms": ["Purpose."],
        "causes": ["Measurements."],
        "diagnosis": ["Preparation."],
        "care": ["Appointment."],
        "complications": ["Aftercare."],
        "help": ["Results."],
        "sources": {"HSE test guidance": index[0][2]},
    }
    content = {
        "checked": date(2026, 11, 20),
        "sources": {},
        "evidence": {},
        "guides": {"test-topic": guide},
    }
    (tmp_path / "health-conditions-index.json").write_text(json.dumps(index), encoding="utf-8")
    return content


def test_missing_evidence_requires_a_documented_gap(tmp_path, catalogue):
    (tmp_path / "health-conditions.yml").write_text(yaml.safe_dump(catalogue), encoding="utf-8")
    with pytest.raises(ValueError, match="Incomplete condition guide: test-topic"):
        load_conditions(tmp_path, set())


@pytest.mark.parametrize(
    ("kind", "schema_type", "section", "evidence_heading"),
    [
        ("test", "MedicalTest", "Preparing for the appointment", "Irish testing figures"),
        ("procedure", "MedicalProcedure", "How to prepare", "Irish procedure figures"),
        ("service", "Service", "What to consider", "Irish service figures"),
        ("symptom", "MedicalSymptom", "How it is assessed", "Irish data on this symptom"),
        ("topic", "Thing", "What to know", "Irish data and evidence"),
        ("contraception", "Thing", "How to use or access it", "Irish contraception figures"),
        ("vaccination", "MedicalProcedure", "What it protects against", "Irish vaccination figures"),
    ],
)
def test_guide_formats_documented_irish_data_gap(
    tmp_path, catalogue, kind, schema_type, section, evidence_heading
):
    catalogue["guides"]["test-topic"]["kind"] = kind
    catalogue["guides"]["test-topic"]["evidence_gap"] = "The source gives no national count."
    (tmp_path / "health-conditions.yml").write_text(yaml.safe_dump(catalogue), encoding="utf-8")
    directory = load_conditions(tmp_path, set())
    entry = directory["featured"][0]
    assert directory["evidence_count"] == 0
    assert entry["url"] == "/health/conditions/test-topic/"

    env = Environment(
        loader=FileSystemLoader(ROOT / "compound/site/templates"),
        autoescape=select_autoescape(["html"]),
    )
    html = env.get_template("health_condition.html").render(
        entry=entry,
        directory=directory,
        conditions_url="/health/conditions/",
        site_url="https://compound.ie",
        title=entry["name"],
        adsense={"slots": {}},
        analytics={},
    )
    assert f'"@type": "{schema_type}"' in html
    assert f"<h2>{section}</h2>" in html
    assert f"<h2>{evidence_heading}</h2>" in html
    assert "The source gives no national count." in html
    assert "<figcaption>" not in html


def test_abortion_uses_procedure_language():
    content = ROOT / "content"
    editorial = yaml.safe_load((content / "health-conditions.yml").read_text(encoding="utf-8"))
    related_urls = {url for guide in editorial["guides"].values() for url in guide.get("links", {}).values()}
    directory = load_conditions(content, related_urls)
    entry = next(item for item in directory["featured"] if item["url"] == "/health/conditions/abortion/")

    assert entry["schema_type"] == "MedicalProcedure"
    assert dict(entry["sections"])["complications"] == "Aftercare and warning signs"
    assert entry["records"][0]["measure"] == "procedure"
    assert entry["records"][0]["label"] == "Reported terminations of pregnancy"
