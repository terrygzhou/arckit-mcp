"""Tests for ``server._resolve_command_content`` (Task 2, full-command-relay).

Pins the Task 2.1–2.4 contract:

* 2.1 — maps ``arckit.{name}`` (via ``_command_key``) to
  ``source_root/plugins/{plugin}/commands/{name}.md`` and returns
  ``{"available": True, "source": <relpath>, "content": <text>,
  "refs": {...}, "unresolved": [...]}``.
* 2.2 — reference scan (Design D3): ``${CLAUDE_PLUGIN_ROOT}/<token>``
  tokens whose target lives under the plugin's ``references/`` or
  ``templates/`` directory AND exists on disk are inlined into ``refs``
  (keyed by the placeholder-relative path WITHOUT leading slash).
* 2.3 — ``unresolved``: ``scripts/``/``skills/`` tokens are path-only
  strings; tokens whose target file does not exist are
  ``{"path": ..., "missing": true}``.
* 2.4 — ``source_root=None`` returns ``{"available": False, "reason": ...}``
  without raising.

The fixture mirrors ``source_root.resolve_source_root()``'s three tiers by
constructing the source root explicitly (tmp_path checkout for isolation,
plus one test against the real sibling arc-kit checkout at
``/home/terry/projects/arc-kit``, guarded by a skip when absent — it is
expected to be present in the development environment).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from arckit_mcp.server import _resolve_command_content, run_command

# The sibling arc-kit checkout used by the development environment.
_ARC_KIT = Path("/home/terry/projects/arc-kit")


# ---------------------------------------------------------------------------
# Fixture: a synthetic arc-kit source root under tmp_path
# ---------------------------------------------------------------------------


@pytest.fixture()
def arc_root(tmp_path) -> Path:
    """Build a minimal arc-kit checkout under ``tmp_path``.

    Layout::

        {tmp}/
          plugins/arckit-claude/
            commands/
              my-cmd.md          # refs existing + missing + scripts token
              scripts-cmd.md     # refs scripts/validate-handoff
              missing-ref.md     # refs references/nope (does not exist)
            references/
              good-ref.md
              citation-instructions.md
              intake-instructions.md
              quality-checklist.md
            templates/
              my-template.md
    """
    root = tmp_path / "arc-kit"
    plugin = root / "plugins" / "arckit-claude"
    (plugin / "commands").mkdir(parents=True)
    (plugin / "references").mkdir()
    (plugin / "templates").mkdir()

    (plugin / "commands" / "my-cmd.md").write_text(
        "# my-cmd\n\n"
        "See `${CLAUDE_PLUGIN_ROOT}/references/good-ref` and "
        "`${CLAUDE_PLUGIN_ROOT}/templates/my-template`.\n\n"
        "Run `${CLAUDE_PLUGIN_ROOT}/scripts/validate-handoff`.\n\n"
        "See `${CLAUDE_PLUGIN_ROOT}/references/nope`.\n"
    )
    (plugin / "commands" / "scripts-cmd.md").write_text(
        "# scripts-cmd\n\n"
        "Run `${CLAUDE_PLUGIN_ROOT}/scripts/validate-handoff` first.\n"
    )
    (plugin / "commands" / "missing-ref.md").write_text(
        "# missing-ref\n\n"
        "See `${CLAUDE_PLUGIN_ROOT}/references/nope` for details.\n"
    )
    (plugin / "references" / "good-ref.md").write_text("Good reference body.\n")
    (plugin / "templates" / "my-template.md").write_text("# My Template\nbody\n")
    return root


# ---------------------------------------------------------------------------
# Test names from the task description, bound to the synthetic fixture
# ---------------------------------------------------------------------------


def test_resolve_command_content_requirements(arc_root):
    """Task 2.1: available, source relpath, content, refs keys.

    The requirements.md command is replicated on the fixture root; the
    sibling-checkout assertion (same contract, real file) lives in
    ``test_resolve_command_content_requirements_real_checkout`` below.
    """
    plugin = arc_root / "plugins" / "arckit-claude"
    (plugin / "commands" / "requirements.md").write_text(
        "# requirements\n\n"
        "Requirements command body (synthetic, >1000 chars)\n\n"
        + ("x" * 1100)
        + "\n"
        "`${CLAUDE_PLUGIN_ROOT}/references/citation-instructions`\n"
        "`${CLAUDE_PLUGIN_ROOT}/references/intake-instructions`\n"
        "`${CLAUDE_PLUGIN_ROOT}/references/quality-checklist`\n"
        "`${CLAUDE_PLUGIN_ROOT}/templates/requirements-template`\n"
    )
    for name, text in (
        ("citation-instructions.md", "Citation instructions body.\n"),
        ("intake-instructions.md", "Intake instructions body.\n"),
        ("quality-checklist.md", "Quality checklist body.\n"),
    ):
        (plugin / "references" / name).write_text(text)
    (plugin / "templates" / "requirements-template.md").write_text(
        "# Requirements Template\nsynthetic body\n"
    )

    result = _resolve_command_content("requirements", arc_root)

    assert result["available"] is True
    assert result["source"] == "plugins/arckit-claude/commands/requirements.md"
    assert len(result["content"]) > 1000
    expected_refs = {
        "references/citation-instructions",
        "references/intake-instructions",
        "references/quality-checklist",
        "templates/requirements-template",
    }
    assert set(result["refs"].keys()) == expected_refs
    for key in expected_refs:
        assert result["refs"][key], f"ref {key} must be non-empty"


def test_resolve_command_content_refs_match_disk(arc_root):
    """Task 2.2: each ref value equals the on-disk file's full text."""
    plugin = arc_root / "plugins" / "arckit-claude"
    result = _resolve_command_content("my_cmd", arc_root)

    assert result["available"] is True
    assert (
        result["refs"]["references/good-ref"]
        == (plugin / "references" / "good-ref.md").read_text()
    )
    assert (
        result["refs"]["templates/my-template"]
        == (plugin / "templates" / "my-template.md").read_text()
    )


def test_resolve_command_content_unresolved_scripts(arc_root):
    """Task 2.3: scripts/ tokens land in unresolved (path-only), not refs."""
    result = _resolve_command_content("scripts_cmd", arc_root)

    assert result["available"] is True
    assert "scripts/validate-handoff" in result["unresolved"]
    # The scripts path must NOT be inlined into refs.
    assert "scripts/validate-handoff" not in result["refs"]
    # my-cmd carries one missing-ref token; the scripts token in my-cmd is
    # also path-only.
    result2 = _resolve_command_content("my_cmd", arc_root)
    assert "scripts/validate-handoff" in result2["unresolved"]
    assert "scripts/validate-handoff" not in result2["refs"]


def test_resolve_command_content_missing_file(arc_root):
    """Task 2.3: a nonexistent target -> {"path": ..., "missing": True}."""
    result = _resolve_command_content("missing_ref", arc_root)

    assert result["available"] is True
    entry = [e for e in result["unresolved"] if isinstance(e, dict)]
    assert entry == [{"path": "references/nope", "missing": True}], (
        f"unresolved entries: {result['unresolved']!r}"
    )
    assert "references/nope" not in result["refs"]


def test_resolve_command_content_no_source_root(arc_root):
    """Task 2.4: source_root=None -> available=False + reason, no exception."""
    result = _resolve_command_content("requirements", None)

    assert result == {
        "available": False,
        "reason": (
            "No arc-kit source root available. Set ARCKIT_SOURCE_ROOT or "
            "install the arckit package."
        ),
    }


# ---------------------------------------------------------------------------
# Real-checkout coverage (sibling arc-kit, development environment)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (_ARC_KIT / "plugins" / "arckit-claude").is_dir(),
    reason="sibling arc-kit checkout not present",
)
def test_resolve_command_content_requirements_real_checkout():
    """Task 2.1/2.2 against the real requirements.md on disk.

    Mirrors the task-spec assertions exactly:
    ``ARCKIT_SOURCE_ROOT=/home/terry/projects/arc-kit`` equivalent (passing
    the root directly, which is what the env var would resolve to per
    ``source_root._from_env``), ``arckit.requirements``, source relpath,
    content length, and the four expected ref keys with non-empty values.
    """
    result = _resolve_command_content("requirements", _ARC_KIT)

    assert result["available"] is True
    assert result["source"] == "plugins/arckit-claude/commands/requirements.md"
    assert len(result["content"]) > 1000
    expected = {
        "references/citation-instructions",
        "references/intake-instructions",
        "references/quality-checklist",
        "templates/requirements-template",
    }
    assert expected <= set(result["refs"].keys())
    for key in expected:
        assert result["refs"][key], f"ref {key} must be non-empty"

    # refs_match_disk against the real checkout.
    for key, value in result["refs"].items():
        disk = _ARC_KIT / "plugins" / "arckit-claude" / f"{key}.md"
        assert value == disk.read_text(), f"{key} ref does not match disk"


@pytest.mark.skipif(
    not (_ARC_KIT / "plugins" / "arckit-claude").is_dir(),
    reason="sibling arc-kit checkout not present",
)
def test_resolve_command_content_unresolved_scripts_real_checkout():
    """Task 2.3 against the real gov-reuse.md scripts tokens."""
    result = _resolve_command_content("gov_reuse", _ARC_KIT)

    assert result["available"] is True
    scripts_paths = {
        "scripts/bash/create-project",
        "scripts/bash/generate-document-id",
        "scripts/validate-handoff",
    }
    assert scripts_paths <= set(result["unresolved"])
    for p in scripts_paths:
        assert p not in result["refs"]
    # refs are still inlined from the real checkout.
    assert "references/intake-instructions" in result["refs"]
    assert "templates/gov-reuse-template" in result["refs"]


# ---------------------------------------------------------------------------
# Task 3 relay-level tests: run_command carries command_content
# ---------------------------------------------------------------------------


def test_run_command_includes_command_content(
    tmp_path, monkeypatch, arc_root
):
    """Task 4.1: run_command carries command_content when source root available."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "arckit_mcp.server.resolve_source_root", lambda: arc_root
    )
    relay = run_command("my_cmd", "001")
    cc = relay["command_content"]
    assert cc["available"] is True
    assert cc["source"] == "plugins/arckit-claude/commands/my-cmd.md"
    assert len(cc["content"]) > 0
    # refs are inlined (Task 2.2): good-ref + my-template present.
    assert "references/good-ref" in cc["refs"]
    assert "templates/my-template" in cc["refs"]
    # scripts token is in unresolved (Task 2.3), not in refs.
    assert "scripts/validate-handoff" in cc["unresolved"]
    assert "scripts/validate-handoff" not in cc["refs"]
    # missing reference is flagged (Task 2.3).
    assert any(
        isinstance(m, dict) and m.get("path") == "references/nope"
        for m in cc["unresolved"]
    )


def test_run_command_command_content_unavailable(
    tmp_path, monkeypatch
):
    """Task 4.3: command_content is available=false when no source root."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "arckit_mcp.server.resolve_source_root", lambda: None
    )
    relay = run_command("requirements", "001")
    cc = relay["command_content"]
    assert cc["available"] is False
    assert "ARCKIT_SOURCE_ROOT" in cc["reason"]
    assert "arckit package" in cc["reason"]


def test_run_command_existing_keys_unchanged(tmp_path, monkeypatch, arc_root):
    """Task 4.4: backward compat — all existing keys present and unchanged."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "arckit_mcp.server.resolve_source_root", lambda: arc_root
    )
    relay = run_command("my_cmd", "001")
    for key in (
        "id",
        "project_id",
        "command",
        "doc_type",
        "intake",
        "instructions",
        "gates",
        "gate_blocked",
    ):
        assert key in relay, f"existing key '{key}' missing from relay payload"
    assert relay["id"] == "ARC-001"
    assert relay["project_id"] == "001"
    assert relay["command"] == "my-cmd"
    assert isinstance(relay["intake"], list)
    assert isinstance(relay["gates"], list)


def test_instructions_points_at_command_content(tmp_path, monkeypatch):
    """Task 3.2 / D6: instructions one-liner reframed to point at command_content.content."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "arckit_mcp.server.resolve_source_root", lambda: None
    )
    relay = run_command("requirements", "001")
    instructions = relay["instructions"]
    # Must point at command_content.content as the authoritative instruction.
    assert "command_content.content" in instructions
    # Must still name the doc-type code.
    assert "REQ" in instructions
    # Must still name arckit.persist_artifact.
    assert "arckit.persist_artifact" in instructions
    # Must still name the project id.
    assert "001" in instructions
