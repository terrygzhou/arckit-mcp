"""End-to-end test cases: an external agent drives a sample project
through the ArcKit governance harness via the arckit-mcp MCP tools.

This suite simulates the full agent loop described in the README, i.e. an
external agent (e.g. an LLM host) that does NOT know ArcKit's command graph
by heart and instead uses the MCP relay model:

    1. Seed   — arckit.seed_context to mint a project_id
    2. Relay  — call a per-command tool (arckit.strategy, arckit.risk, …).
               Read gate_blocked; if a MANDATORY gate is open, go back to
               the prerequisite command first. Otherwise answer the intake
               questions the host asks, generate the document, and persist
               it with arckit.persist_artifact.
    3. Advance — call arckit.next_step with the commands completed so far
               to find the next one, and repeat.

The sample project is a "payment gateway modernization" project, mirroring
the worked example in requirements.md. The test suite pins the checkpoint
log of a realistic agent session:

    * checkpoint 1: host asks for a context folder → agent asks user
    * checkpoint 2: seed_context returns project_id 001
    * checkpoint 3: arckit.strategy is relayed; PRIN and STKE gates are
      open (MANDATORY) so the agent is blocked
    * checkpoint 4: agent answers host's intake questions for
      arckit.principles, generates the PRIN artefact, and persists it
    * checkpoint 5: agent answers host's intake questions for
      arckit.stakeholders, generates the STKE artefact, and persists it
    * checkpoint 6: gates re-checked → strategy no longer blocked
    * checkpoint 7: agent answers strategy intake, generates STRAT,
      persists it
    * checkpoint 8: next_step returns 'roadmap' as the next command
    * checkpoint 9: host stops — the agent records "all reachable
      handoffs completed" when roadmap + all its targets are done

Each test is isolated under tmp_path (monkeypatch.chdir) and exercises the
public functions exposed by arckit_mcp.server.

"""

from __future__ import annotations

from pathlib import Path

import arckit_mcp.server as server
from arckit_mcp.server import (
    check_gates,
    next_step,
    persist_artifact,
    run_command,
    seed_context,
)


# ---------------------------------------------------------------------------
# Fixtures: helper to persist an artefact quickly (mirrors what the agent
# would do after generating a document).
# ---------------------------------------------------------------------------

def _persist(root: Path, project_id: str, code: str, body: str = "# artefact\n") -> None:
    pid = project_id.zfill(3)
    outdir = root / "projects" / project_id
    sub = None
    from arckit_mcp._registry import SUBDIR_MAP
    sub = SUBDIR_MAP.get(code)
    if sub:
        outdir = outdir / sub
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"ARC-{pid}-{code}-v1.0.md").write_text(body, encoding="utf-8")


# ---------------------------------------------------------------------------
# Checkpoint 1 — host asks for a context folder
# ---------------------------------------------------------------------------

class TestCheckpoint1_Host_Asked_For_Context_Folder:
    """The seed_context tool description mandates: 'IF THE USER HAS NOT
    PROVIDED A CONTEXT FOLDER, ASK THEM FIRST.'  This checkpoint records
    that the agent's first action is to *ask the host* for a folder.

    The test verifies that seed_context degrades gracefully when no
    context folder is given (files_imported 0, context_index None),
    and that it errors cleanly when a *named* folder does not exist.
    """

    def test_seed_without_context_folder_is_allowed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = seed_context("Payment Gateway")
        assert result["project_id"] == "001"
        assert result["files_imported"] == 0
        assert result["context_index"] is None
        # The agent still got a usable project_id it can drive with.
        # NOTE: seed_context mints projects/001-{slug}/ on disk, while
        # persist_artifact/check_gates write/read the bare projects/{id}/
        # directory.  The two layouts do not line up — this is a real
        # consistency defect in the server (see the note in
        # TestAgentLoop_Invariants).  The agent must persist to the bare
        # directory for gates to close.
        pdir = tmp_path / "projects" / "001-payment-gateway"
        assert (pdir / "external").is_dir()

    def test_seed_with_missing_named_context_folder_is_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = seed_context(
            "Payment Gateway",
            context_folder=str(tmp_path / "does-not-exist"),
        )
        # The tool must not silently mint a project for a bad folder.
        assert "error" in result
        assert result["project_id"] is None


# ---------------------------------------------------------------------------
# Checkpoint 2 — seed_context mints project_id 001 with goals
# ---------------------------------------------------------------------------

class TestCheckpoint2_Seed_Project:
    """The host decides to seed a project.  The agent calls
    seed_context with goals and constraints; the returned project_id
    is what every subsequent relay tool uses."""

    def test_seed_returns_project_id_001(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = seed_context(
            "Payment Gateway Modernization",
            goals=[
                "Cut infrastructure cost 40%",
                "PCI-DSS Level 1 compliance",
                "< 2 s end-to-end latency",
            ],
            constraints=["No new vendors", "Must stay on GovCloud"],
        )
        assert result["project_id"] == "001"
        assert result["project_dir"] == "projects/001-payment-gateway-modernization"
        assert result["files_imported"] == 0
        assert result["context_index"] is None

    def test_seed_writes_goals_md(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context(
            "Payment Gateway",
            goals=["g1"],
            constraints=["c1"],
        )
        goals_md = (
            tmp_path
            / "projects"
            / "001-payment-gateway"
            / "GOALS.md"
        ).read_text(encoding="utf-8")
        assert "## Goals" in goals_md
        assert "## Constraints" in goals_md
        assert "g1" in goals_md
        assert "c1" in goals_md

    def test_second_seed_mints_002(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Alpha")
        second = seed_context("Beta")
        assert second["project_id"] == "002"


# ---------------------------------------------------------------------------
# Checkpoint 3 — arckit.strategy relay shows MANDATORY gates open
# ---------------------------------------------------------------------------

class TestCheckpoint3_Strategy_Blocked_On_Mandatory_Gates:
    """The agent's first relay call is arckit.strategy.  Its MANDATORY
    gates (PRIN, STKE) are open because no artefacts exist yet — the
    relay must report gate_blocked=True and the agent must step back
    to the prerequisites before generating STRAT."""

    def test_strategy_relay_reports_gate_blocked_true(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        relay = run_command("strategy", "001")
        assert relay["gate_blocked"] is True
        # Every MANDATORY gate on strategy must be open.
        mandatory_open = {
            g["code"]
            for g in relay["gates"]
            if g["tier"] == "MANDATORY" and g["status"] == "open"
        }
        assert mandatory_open >= {"PRIN", "STKE"}
        # The relay still returns intake + instructions so the agent
        # can answer host questions as soon as gates close.
        assert len(relay["intake"]) > 0
        assert relay["instructions"]
        assert relay["command"] == "strategy"
        # run_command carries the project id in the "id" field.
        assert relay["id"] == "ARC-001"

    def test_check_gates_only_lists_mandatory_and_recommended(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        result = check_gates("strategy", "001")
        codes = {g["code"] for g in result["gates"]}
        # OPTIONAL codes (e.g. RISK) are silently omitted.
        assert "RISK" not in codes
        # MANDATORY codes are present.
        assert "PRIN" in codes
        assert "STKE" in codes


# ---------------------------------------------------------------------------
# Checkpoint 4 — agent answers host intake for principles → persists PRIN
# ---------------------------------------------------------------------------

class TestCheckpoint4_Principles_Artefact:
    """When strategy is blocked on PRIN, the agent runs
    arckit.principles, answers host's intake questions (one at a
    time — ask-always, answer-optional), generates the document,
    and persists it with arckit.persist_artifact.  After that the
    PRIN gate is closed.
    """

    def test_principles_relay_has_no_gate_tiers(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        relay = run_command("principles", "001")
        # principles has no gate tiers of its own — the agent can
        # always proceed.
        assert relay["gate_blocked"] is False
        assert relay["gates"] == []
        # The relay still relays intake questions so the host is
        # asked.
        assert len(relay["intake"]) > 0

    def test_persist_prin_closes_the_gate(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        # Before persisting, PRIN is open.
        before = check_gates("strategy", "001")
        assert any(
            g["code"] == "PRIN" and g["status"] == "open"
            for g in before["gates"]
        )
        # The agent generates the PRIN document and persists it.
        result = persist_artifact("001", "PRIN", "# Principles\n")
        assert result["written"] is True
        # Now the gate is closed.
        after = check_gates("strategy", "001")
        assert all(
            g["status"] == "closed"
            for g in after["gates"]
            if g["code"] == "PRIN"
        )

    def test_principles_relay_intake_is_non_empty(self, tmp_path, monkeypatch):
        """Even though principles has no doc-type code in the
        registry mapping, the relay still returns at least one
        intake question so the host is asked something."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        relay = run_command("principles", "001")
        assert len(relay["intake"]) >= 1
        q = relay["intake"][0]
        assert "question" in q
        assert "required" in q


# ---------------------------------------------------------------------------
# Checkpoint 5 — agent answers host intake for stakeholders → persists STKE
# ---------------------------------------------------------------------------

class TestCheckpoint5_Stakeholders_Artefact:
    """After PRIN, STKE is the remaining MANDATORY gate on
    strategy.  The agent runs arckit.stakeholders, answers host's
    questions, and persists the STKE artefact."""

    def test_stakeholders_relay_is_unblocked(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        relay = run_command("stakeholders", "001")
        assert relay["gate_blocked"] is False
        # stakeholders has no gates of its own.

    def test_persist_stke_closes_the_last_mandatory_gate(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        # STKE is still open.
        gates = check_gates("strategy", "001")
        assert any(
            g["code"] == "STKE" and g["status"] == "open"
            for g in gates["gates"]
        )
        # Agent persists STKE.
        result = persist_artifact("001", "STKE", "# Stakeholders\n")
        assert result["written"] is True
        # Now strategy is no longer blocked.
        gates = check_gates("strategy", "001")
        assert gates["gate_blocked"] is False


# ---------------------------------------------------------------------------
# Checkpoint 6 — strategy relay is now unblocked; agent generates STRAT
# ---------------------------------------------------------------------------

class TestCheckpoint6_Strategy_Unblocked:
    """After both PRIN and STKE artefacts exist, the strategy relay
    reports gate_blocked=False and the agent can generate STRAT."""

    def test_strategy_unblocked_after_prin_stke(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        relay = run_command("strategy", "001")
        assert relay["gate_blocked"] is False

    def test_strategy_intake_questions_are_relayed(
        self, tmp_path, monkeypatch
    ):
        """Even for STRAT (no static intake data — it is a
        'no-static-questions' doc-type), the relay must return at
        least one placeholder question so the host is always asked."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        relay = run_command("strategy", "001")
        assert len(relay["intake"]) >= 1
        # The placeholder question is the only one for STRAT.
        assert relay["intake"][0]["required"] is True


# ---------------------------------------------------------------------------
# Checkpoint 7 — agent persists STRAT; roadmap becomes reachable
# ---------------------------------------------------------------------------

class TestCheckpoint7_Strategy_Artefact:
    """The agent generates the STRAT document and persists it.
    After this, next_step from a completed [strategy] should
    surface 'roadmap' as a candidate (roadmap's MANDATORY gates on
    PRIN+REQ will then gate it — a separate checkpoint)."""

    def test_persist_strat_writes_document(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        result = persist_artifact("001", "STRAT", "# Strategy\n")
        assert result["written"] is True
        # persist_artifact writes to the bare projects/{id}/ directory
        # (not the slug dir seed_context minted) — see the consistency
        # note in TestAgentLoop_Invariants.
        path = tmp_path / "projects" / "001" / "ARC-001-STRAT-v1.0.md"
        assert path.is_file()
        assert path.read_text(encoding="utf-8") == "# Strategy\n"

    def test_next_step_from_completed_strategy_points_to_roadmap(
        self, tmp_path, monkeypatch
    ):
        """After [principles, stakeholders, strategy] are done,
        next_step must surface 'roadmap' (an unconditional handoff
        from strategy)."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        persist_artifact("001", "STRAT", "# Strategy\n")
        result = next_step(
            "001",
            completed=["principles", "stakeholders", "strategy"],
        )
        # roadmap is an unconditional target of strategy; the
        # deterministic min-pick may also yield 'diagram' or
        # 'requirements' (also strategy handoffs).  We only assert
        # the returned next is one of those.
        assert result["next"] in {"roadmap", "diagram", "requirements"}
        assert result["project_id"] == "001"


# ---------------------------------------------------------------------------
# Checkpoint 8 — roadmap is gated on MANDATORY PRIN + REQ
# ---------------------------------------------------------------------------

class TestCheckpoint8_Roadmap_Gated_On_Req:
    """roadmap has PRIN and REQ as MANDATORY gates.  After PRIN is
    persisted but REQ is not, the roadmap relay must report
    gate_blocked=True so the agent knows to run requirements first."""

    def test_roadmap_blocked_until_req_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        # REQ not yet persisted → roadmap is blocked.
        relay = run_command("roadmap", "001")
        assert relay["gate_blocked"] is True
        open_mandatory = {
            g["code"]
            for g in relay["gates"]
            if g["tier"] == "MANDATORY" and g["status"] == "open"
        }
        assert open_mandatory == {"REQ"}

    def test_persist_req_unblocks_roadmap(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        persist_artifact("001", "PRIN", "# Principles\n")
        persist_artifact("001", "STKE", "# Stakeholders\n")
        persist_artifact("001", "REQ", "# Requirements\n")
        relay = run_command("roadmap", "001")
        assert relay["gate_blocked"] is False


# ---------------------------------------------------------------------------
# Checkpoint 9 — host stops: next_step reports all reachable completed
# ---------------------------------------------------------------------------

class TestCheckpoint9_Host_Stops:
    """When every reachable handoff from the commands the agent has
    completed is itself completed, next_step returns next=None with
    a reason string.  This is the 'host stops' checkpoint — the
    agent has nothing more to do."""

    def test_next_step_all_reachable_completed(
        self, tmp_path, monkeypatch
    ):
        # Build a minimal handoff closure:
        #   stakeholders → [requirements, risk]
        #   requirements → [research]
        # Complete all of them → no candidate remains.
        monkeypatch.chdir(tmp_path)
        original = {k: v for k, v in server.HANDOFFS.items()}
        try:
            monkeypatch.setitem(
                server.HANDOFFS, "arckit-claude/stakeholders",
                [("requirements", "", ""), ("risk", "", "")],
            )
            monkeypatch.setitem(
                server.HANDOFFS, "arckit-claude/requirements",
                [("research", "", "")],
            )
            monkeypatch.setitem(server.HANDOFFS, "arckit-claude/risk", [])
            monkeypatch.setitem(server.HANDOFFS, "arckit-claude/research", [])
            result = next_step(
                "001",
                completed=[
                    "stakeholders", "requirements", "risk", "research",
                ],
            )
            assert result["next"] is None
            assert result["reason"] == "All reachable handoffs completed"
            assert result["project_id"] == "001"
        finally:
            # Restore the real handoff graph for later tests.
            server.HANDOFFS.clear()
            server.HANDOFFS.update(original)

    def test_next_step_with_empty_completed_is_none(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = next_step("001", completed=[])
        assert result["next"] is None
        assert result["reason"] == "All reachable handoffs completed"


# ---------------------------------------------------------------------------
# Cross-cutting invariants for the agent loop
# ---------------------------------------------------------------------------

class TestAgentLoop_Invariants:
    """Properties that must hold at every checkpoint so the relay
    model is safe for an external agent to drive."""

    def test_relay_never_returns_empty_intake(self, tmp_path, monkeypatch):
        """For every command in GATE_TIERS the relay must return at
        least one intake question — even for commands whose
        doc-type codes are 'no-static-questions'."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        from arckit_mcp.gates import GATE_TIERS
        for key in GATE_TIERS:
            cmd = key.split("/", 1)[1]
            relay = run_command(cmd, "001")
            assert len(relay["intake"]) >= 1, (
                f"command {cmd} relayed an empty intake list"
            )

    def test_persist_artifact_rejects_unknown_type(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        result = persist_artifact("001", "NOT-A-CODE", "# x\n")
        assert result["written"] is False
        assert "Unknown doc-type" in result["error"]

    def test_seed_and_persist_use_different_layouts(
        self, tmp_path, monkeypatch
    ):
        """Documents a real consistency defect: seed_context mints
        projects/001-{slug}/ on disk, but persist_artifact and
        check_gates use the bare projects/{id}/ directory.  Until the
        server reconciles the two, an agent that seeds and then persists
        must write to the bare directory for gates to close."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        # seed created the slug dir
        assert (tmp_path / "projects" / "001-payment-gateway").is_dir()
        # persist writes to the bare dir (creating it fresh)
        persist_artifact("001", "PRIN", "# Principles\n")
        bare = tmp_path / "projects" / "001" / "ARC-001-PRIN-v1.0.md"
        assert bare.is_file()
        # The slug dir does NOT receive the artefact.
        slug = tmp_path / "projects" / "001-payment-gateway" / "ARC-001-PRIN-v1.0.md"
        assert not slug.is_file()

    def test_persist_multi_instance_sequence(self, tmp_path, monkeypatch):
        """Multi-instance types (ADR) get a sequence number.  A
        second persist with the same code must land under a new
        sequence so the agent does not clobber the first."""
        monkeypatch.chdir(tmp_path)
        seed_context("Payment Gateway")
        first = persist_artifact("001", "ADR", "# ADR-001\n")
        second = persist_artifact("001", "ADR", "# ADR-002\n")
        assert first["written"] and second["written"]
        assert first["path"] != second["path"]
        first_seq = first["path"].split("-")[-2]
        second_seq = second["path"].split("-")[-2]
        assert first_seq == "001"
        assert second_seq == "002"
