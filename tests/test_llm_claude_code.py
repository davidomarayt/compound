"""ClaudeCodeLLM shells out to `claude -p`; these tests stub the subprocess."""
import json
from pathlib import Path

import pytest

from compound.llm import ArticleDraft, ClaudeCodeLLM, LLMError, Triage


class R:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


@pytest.fixture
def llm(monkeypatch):
    monkeypatch.setattr("compound.llm.shutil.which", lambda name: "/usr/bin/claude" if name == "claude" else None)
    return ClaudeCodeLLM(bin="claude", model="", style_dir=Path("style"))


def test_structured_output_is_parsed(llm, monkeypatch):
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        seen["input"] = kw["input"]
        return R(json.dumps({"is_error": False, "num_turns": 1, "duration_ms": 1200, "total_cost_usd": 0.01,
                             "structured_output": {"score": 8, "reason": "affects renters", "angle": "renters", "summary": "s"}}))

    monkeypatch.setattr("compound.llm.subprocess.run", fake_run)
    t = llm.generate_triage(kind="news", pillar="wealth", title="t", url="u", source_text="Rent credit €1,000")
    assert isinstance(t, Triage) and t.score == 8
    assert seen["cmd"][:2] == ["/usr/bin/claude", "-p"] and "--json-schema" in seen["cmd"] and "--bare" in seen["cmd"]
    assert seen["cmd"][seen["cmd"].index("--tools") + 1] == ""
    assert seen["cmd"][seen["cmd"].index("--effort") + 1] == "low"  # triage runs at low effort
    assert "Rent credit €1,000" in seen["input"]
    assert "--model" not in seen["cmd"]


def test_model_flag_and_result_string_fallback(monkeypatch):
    monkeypatch.setattr("compound.llm.shutil.which", lambda name: "/usr/bin/claude")
    llm = ClaudeCodeLLM(bin="claude", model="sonnet", style_dir=Path("style"))
    draft = {"headline": "h", "slug": "h", "summary": "s", "body_markdown": "b", "figures": [], "sources": [], "tags": ["x"], "email_cta": "c"}
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        return R(json.dumps({"result": json.dumps(draft)}))  # older envelope: JSON inside `result`

    monkeypatch.setattr("compound.llm.subprocess.run", fake_run)
    d = llm.generate_draft(kind="manual", pillar="health", title="t", url="", summary="", source_text="", interview=[])
    assert isinstance(d, ArticleDraft) and d.headline == "h"
    assert seen["cmd"][seen["cmd"].index("--model") + 1] == "sonnet"


@pytest.mark.parametrize("resp, needle", [
    (R("", returncode=1, stderr="Not logged in. Run `claude` to log in."), "Not logged in"),
    (R(json.dumps({"is_error": True, "result": "You've hit your usage limit"}), 0), "usage limit"),
    (R("not json"), "non-JSON"),
    (R(json.dumps({"result": "plain prose, no schema"}), 0), "no structured output"),
])
def test_failures_become_llm_errors(llm, monkeypatch, resp, needle):
    monkeypatch.setattr("compound.llm.subprocess.run", lambda cmd, **kw: resp)
    with pytest.raises(LLMError, match=needle):
        llm.generate_triage(kind="news", pillar="wealth", title="t", url="u", source_text="x")


def test_missing_binary_is_clear(monkeypatch):
    monkeypatch.setattr("compound.llm.shutil.which", lambda name: None)
    llm = ClaudeCodeLLM(bin="claude", model="", style_dir=Path("style"))
    with pytest.raises(LLMError, match="not found"):
        llm.generate_triage(kind="news", pillar="wealth", title="t", url="u", source_text="x")


def test_build_llm_selects_backend(settings):
    from dataclasses import replace
    from compound.llm import ClaudeLLM, FakeLLM, build_llm

    assert isinstance(build_llm(settings), FakeLLM)
    real = replace(settings, fake_llm=False)
    assert type(build_llm(replace(real, llm_backend="claude-code"))) is ClaudeCodeLLM
    assert type(build_llm(replace(real, llm_backend="api"))) is ClaudeLLM
