"""PIA launch tracker: verified editorial data, safe states and rendered canonical."""
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from compound.site.build import build_site
from compound.site.pia import load_pia_launch_tracker

SOURCE = Path(__file__).resolve().parents[1] / "content" / "pia-launch-tracker.yml"


def test_pia_launch_dataset_has_cited_and_nonmisleading_milestones():
    data = load_pia_launch_tracker(SOURCE)
    assert data is not None
    assert data["checked"] == "2026-11-15"
    assert data["target_date"] == "2027-07-01"
    assert len(data["milestones"]) == 7
    assert [m["state"] for m in data["milestones"]] == [
        "confirmed", "confirmed", "confirmed", "confirmed", "unverified", "unverified", "target"
    ]
    assert all(m["source_url"].startswith("https://") for m in data["milestones"])
    amended = data["milestones"][3]
    assert amended["id"] == "bill-committee-amended"
    assert amended["date"] == "2026-11-12"
    assert "section 27" in amended["summary"].lower()
    assert "data.oireachtas.ie" in amended["source_url"]
    assert "subject to" in data["milestones"][-1]["summary"].lower()


def test_pia_launch_tracker_visible_on_original_canonical(settings):
    (settings.content_dir / "pia-launch-tracker.yml").write_text(
        SOURCE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    build_site(settings)
    hub = (settings.public_dir / "pia" / "index.html").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://example.test/pia/">' in hub
    assert 'id="pia-launch-tracker"' in hub
    assert 'href="#pia-launch-tracker"' in hub
    assert "PIA Ireland launch tracker" in hub
    assert "2026-11-15" in hub
    assert '<time datetime="2027-07-01">1 July 2027</time>' in hub
    assert "Event verified" in hub and "Not yet verified" in hub and "Target only" in hub
    assert "Revenue technical forum notice" in hub
    assert "Oireachtas Bill 98/2026" in hub
    assert "Committee-amended Finance Bill text published" in hub
    assert "12 November 2026" in hub
    assert "/pia/providers/" in hub
    assert "not real-time government data" in hub
    assert "/static/pia-centre.css?v=3" in hub
    assert "Account applications are open" not in hub


def test_pia_launch_tracker_missing_fixture_does_not_break_site(settings):
    assert load_pia_launch_tracker(settings.content_dir / "pia-launch-tracker.yml") is None
    build_site(settings)
    hub = (settings.public_dir / "pia" / "index.html").read_text(encoding="utf-8")
    assert 'id="pia-launch-tracker"' not in hub


@pytest.mark.parametrize("mutation", [
    lambda data: data["milestones"][4].update({"state": "confirmed"}),
    lambda data: data["milestones"][0].update({"date": "2027-08-01"}),
    lambda data: data["milestones"][6].update({"date": "2027-08-01"}),
    lambda data: data["milestones"][1].update({"source_url": "http://example.org"}),
    lambda data: data["milestones"][6].update({"state": "confirmed"}),
])
def test_pia_launch_tracker_rejects_unverified_or_unsupported_claims(tmp_path, mutation):
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    mutation(data)
    target = tmp_path / "launch.yml"
    target.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError):
        load_pia_launch_tracker(target)
