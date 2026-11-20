"""F3 fallback: unmapped commands degrade to their gate codes, not ``[]``.

``_command_doc_types`` (server.py) resolves a command's doc-type codes via the
hand-maintained ``name_map`` / ``overlay_map``. When a command is not in either
map (the F3 "silent gap" — most of the 101 commands), the *documented* behavior
is to fall back to the gate codes the command reads (its non-OPTIONAL
``GATE_TIERS`` keys). These tests pin that the fallback is implemented, so a
future regression that re-introduces a bare ``return []`` — and thus a bare
generic intake for ~70 registry commands — fails here.
"""

from __future__ import annotations

from arckit_mcp.gates import GATE_TIERS
from arckit_mcp.server import _command_doc_types, _command_key, _intake_questions


def _gate_fallback(name: str) -> list[str]:
    """Expected doc-type codes: the command's non-OPTIONAL gate codes."""
    key = _command_key(name)
    tiers = GATE_TIERS.get(key, {})
    return sorted(code for code, tier in tiers.items() if tier != "OPTIONAL")


def test_unmapped_command_with_gates_returns_its_gate_codes() -> None:
    """``devops`` is not in name_map/overlay_map; it must surface its gates."""
    key = _command_key("devops")
    assert "devops" not in ("requirements", "strategy", "roadmap")  # not well-known
    codes = _command_doc_types(key)
    expected = _gate_fallback("devops")
    assert codes == expected, "unmapped command must fall back to its gate codes"
    # It has at least one MANDATORY/RECOMMENDED gate code, so it is non-empty.
    assert codes, "expected non-empty gate-code fallback for `devops`"
    # devops has PRIN + REQ as MANDATORY gates, so both must surface.
    assert "PRIN" in codes and "REQ" in codes
    # All fallback codes are known doc-type codes, not ad-hoc tokens.
    from arckit_mcp._registry import KNOWN_TYPES
    assert all(c in KNOWN_TYPES for c in codes), f"unexpected codes: {codes}"


def test_unmapped_command_with_no_gates_returns_empty() -> None:
    """A command with no prerequisite gates legitimately still yields ``[]``."""
    key = _command_key("analyze")
    assert GATE_TIERS.get(key, {}) == {}, "test premise: `analyze` has no gate tiers"
    assert _command_doc_types(key) == []


def test_intake_questions_never_empty_for_unmapped_command() -> None:
    """The relay payload must stay non-empty for the fallback commands."""
    questions = _intake_questions("devops")
    assert questions, "`devops` intake must not be empty"
    # Fallback commands are `no-static-questions`, so the floor is per-code
    # placeholder questions — one per non-OPTIONAL gate code.
    assert len(questions) == len(_gate_fallback("devops"))


def test_generic_intake_for_command_with_no_gates() -> None:
    """No-gates unmapped commands keep the single generic placeholder floor."""
    questions = _intake_questions("analyze")
    assert len(questions) == 1
    assert "Provide the project context for analyze" in questions[0]["question"]


def test_mapped_well_known_command_still_returns_name_map_code() -> None:
    """Regression: the primary (mapped) path is unchanged by the fallback."""
    assert _command_doc_types(_command_key("requirements")) == ["REQ"]
    assert _command_doc_types(_command_key("strategy")) == ["STRAT"]
    assert _command_doc_types(_command_key("stakeholders")) == ["STKE"]
