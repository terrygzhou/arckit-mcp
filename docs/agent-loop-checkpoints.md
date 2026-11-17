# EYW-817 — External Agent ↔ ArcKit (via arckit-mcp) Checkpoint Log

Code review of `arckit-mcp` alongside the `arc-kit` harness, plus the test
cases that exercise the scenario of an **external agent** driving a sample
project through ArcKit over MCP to completion. Each checkpoint mirrors a
decision point in the agent loop — where a slash command is chosen, where
the host is asked questions, what the agent responds, and what it monitors
next — running until the host stops.

## 1. Code review summary

### 1.1 The two codebases

**`arckit-mcp`** (this repo) — a standalone MCP server exposing the ArcKit
governance harness as MCP tools. Layers:

- `arckit_mcp/_registry.py`, `gates.py`, `handoffs.py`, `intake.py` —
  **generated** data tables (regenerated from arc-kit via
  `arckit-mcp-sync` / `generate-mcp-*.py`). `_registry.py` holds
  `DOC_TYPES`, `KNOWN_TYPES`, `MULTI_INSTANCE_TYPES`, `SUBDIR_MAP`
  (e.g. `ADR → decisions/`); `intake.py` holds `INTAKE` (17 non-empty
  entries, each `{'questions': [...], 'mandatory_inputs': [...],
  'source': 'plugins/…'}`) and `COVERAGE` (177 entries: 17 `covered`,
  160 `no-static-questions`).
- `arckit_mcp/server.py` — the MCP server. Tool groups:
  - **Meta-tools**: `arckit.list_commands`, `arckit.next_step`,
    `arckit.check_gates`, `arckit.persist_artifact`, `arckit.persist_intake`,
    `arckit.seed_context`.
  - **Per-command tools**: 101 `arckit.{command}` relays, one per key in the
    generated `GATE_TIERS` table (core + overlay plugins). Each returns
    `intake` (questions to answer), `instructions` (where to run + where to
    save), `gates` + `gate_blocked`, `doc_type`.
  - **Prompt-relay model**: the agent never reads the command markdown; the
    server tells it which gates are open, what to answer, where to write; the
    agent does the LLM generation in-session and persists via
    `arckit.persist_artifact`.

**`arc-kit`** — the source harness. `plugins/arckit-claude/commands/*.md`
(core commands plus overlays) each ship front-matter `gates:` tiers
(MANDATORY / RECOMMENDED / OPTIONAL) and `handoffs:` edges that feed
`next_step`. Entry slash command is `/arckit:init`; the intake interview
contract is in `references/intake-instructions.md` (ask-always,
answer-optional — every question is put to the user one at a time, skipped
answers render as `TBD`).

### 1.2 Findings (defects + invariants)

| # | Severity | Location | Finding |
|---|----------|----------|---------|
| F1 | **Defect** | `server.seed_context` vs `server._project_dir`/`persist_artifact` | `seed_context` mints `projects/001-{slug}/` on disk and returns `project_dir: "projects/001-{slug}"`, but `persist_artifact`, `check_gates`, and `_artifact_exists` resolve the bare `projects/{project_id}/` directory. The two layouts do not line up: an agent that seeds then persists to the slug dir returned by `seed_context` will **not** close any gate, because gate checks read the bare `001/` dir. Pinned by `test_seed_and_persist_use_different_layouts`. **Fixed in `fix-seed-context-layout`** — `seed_context` now mints the bare `projects/{pid}/` layout and the pinning test flips to `test_seed_and_persist_share_layout` (see OpenSpec change tasks 1.1–1.8). |
| F2 | Cosmetic | `server.run_command` | The relay payload's `id` is `ARC-{project_id}` but there is no top-level `project_id` key on the relay dict (unlike `check_gates`, which carries one). Reconstructing the id from `relay["id"]` is fine, but the asymmetry is easy to trip over. **Fixed in `fix-seed-context-layout`** — a top-level `"project_id"` key was added to the `run_command` return dict, with a matching test `test_relay_includes_project_id` (see OpenSpec change tasks 2.1–2.2). |
| F3 | Contract | `server._command_doc_types` | Doc-type codes are derived from a hand-maintained `name_map`/`overlay_map` inside `server.py`, not read from the registry. A new command or code added to arc-kit's `doc-types.mjs` will not be reflected in the relay until `server.py` is updated by hand — a silent cross-repo drift risk (generated tables stay fresh, but the mapping does not). |
| F4 | By-design | `intake.py` `COVERAGE` | 160 of 177 doc-types are `no-static-questions` (17 are `covered`); for the uncovered codes the relay degrades to a per-code placeholder question (intentional — the server must never return an empty question list). `COVERAGE` makes the gap visible. |
| F5 | Contract | `server.persist_intake` | Read/seed only (never writes `.arckit/intake/`, per spec), but the on-disk stem is the hyphenated command name (`discovery-architecture.json` for the `discovery_architecture` tool), while the MCP tool parameter is the underscored name. Agents copying the tool parameter verbatim into a file path will miss saved answers. Pinned by `test_no_write_path_for_answers` (read-only shape) and by the hyphenated-path tests in `test_intake.py`. |

### 1.3 Known limitations

Recorded as known and accepted; each item is tracked in the remediation
plan (`docs/agent-loop-checkpoints-remediation.md`) and, where a fix is
deferred to a separate OpenSpec change, cross-referenced here.

- **F1 — Layout drift between `seed_context` and `persist_artifact` /
  `check_gates` / `next_step`.** (Historical finding — fixed.)
  `seed_context` minted
  `projects/{pid}-{slug}/` on disk and returned that path as
  `project_dir`, but the three read-side tools all resolve the **bare**
  `projects/{pid}/` directory. An agent that seeds a project and then
  persists artefacts into the slug dir `seed_context` reports would write
  to a directory no gate check ever reads — no gate would close. Was
  pinned
  by `test_seed_and_persist_use_different_layouts`
  (tests/mcp/test_agent_loop.py §CP4).
  - **Fixed:** `seed_context` now mints the bare `projects/{pid}/`
    layout with a `.meta` sidecar, and the pinning test is
    `test_seed_and_persist_share_layout` (OpenSpec change
    `openspec/changes/fix-seed-context-layout/` tasks 1.1–1.8, all
    complete).

- **F2 — Missing top-level `project_id` in `run_command` relay payload.**
  (Historical finding — fixed.) The relay dict carried
  `id: "ARC-{project_id}"` but no `project_id`
  key (unlike `check_gates`). Reconstructing the id from the `id` string
  was fragile.
  - **Fixed:** a top-level `"project_id"` key was added to the
    `run_command` return dict, pinned by
    `test_relay_includes_project_id` (OpenSpec change
    `openspec/changes/fix-seed-context-layout/` tasks 2.1–2.2, all
    complete).

- **F3 — Hand-maintained `name_map` / `overlay_map` in
  `server._command_doc_types`.** The command → doc-type mapping is a
  second, hand-written copy of what the registry already knows; a new
  command or code added to arc-kit's `doc-types.mjs` will not be
  reflected in the relay until `server.py` is updated by hand. Two
  deferred remediation options:
  - **(A)** generate a `COMMAND_DOC_TYPES` table into
    `arckit_mcp/_registry.py` from the same source as the other
    generated tables (preferred);
  - **(B)** add a CI check diffing `name_map` / `overlay_map` against
    the registry and failing on drift.
  - **TICKET:** `openspec/changes/document-drift-limitations/tasks.md` task 3.2 — F3 follow-up ticket of record; the remediation owner must pick (A) or (B) and add a corresponding task under that section.

- **F4 — Placeholder `intake` floor is by design.** 160 of 177
  doc-types are `no-static-questions`; for the uncovered codes the relay
  degrades to one placeholder question per code so the server never
  returns an empty intake list. Pinned by
  `test_relay_never_returns_empty_intake`
  (tests/mcp/test_agent_loop.py §CP4).

- **F5 — Hyphenated on-disk intake stem vs underscored tool parameter.**
  `persist_intake` writes / reads `.arckit/intake/{hyphenated-stem}.json`
  (e.g. `discovery-architecture.json`), while the MCP tool parameter is
  underscored (`discovery_architecture`). An agent that copies the tool
  parameter verbatim into a file path will miss saved answers.
  - **Status:** by design; the function is read/seed-only and never
    writes to `.arckit/intake/`. Pinned by
    `test_no_write_path_for_answers` (tests/mcp/test_intake.py).
  - **Stop-word note (F3b):** `_STOP_WORDS` in `server.py` (used by
    `_derive_source_id` to build citation source-ids from file stems) is
    a hand-maintained copy of the stop-list in arc-kit's
    `citation-instructions.md` §Source ID Rules.  If arc-kit adds or
    removes a word, the derived source-ids will silently diverge from
    arc-kit's derivation until the list is synced.  Same cross-repo
    drift risk as F3, narrower surface.

### 1.4 What the tests now cover

`tests/mcp/test_agent_loop.py` (24 tests) drives a **payment gateway
modernization** sample project through the full relay loop and pins each
checkpoint. Full suite: **66 passing** (42 pre-existing + 24 new) —
`test_agent_loop` 24, `test_gates` 4, `test_intake` 22, `test_next_step` 5,
`test_seed_context` 8, `test_sync` 3.

## 2. Checkpoint log (external agent drives the sample project)

Sample project: *Payment Gateway Modernization*. Goals: cut infra cost 40%,
PCI-DSS L1, `< 2 s` latency. Constraints: no new vendors, GovCloud.

### CP1 — Host asked for a context folder
- **Decision:** agent reaches for `arckit.seed_context` first.
- **Host asks:** "Do you have a folder of reference documents (RFPs, legacy
  specs, research) to import?"
- **Response:** agent asks the user (mandated by the `seed_context` tool
  description: "IF THE USER HAS NOT PROVIDED A CONTEXT FOLDER, ASK THEM
  FIRST"). No folder supplied, so the agent proceeds with a bare seed.
- **Monitored:** `seed_context` degrades cleanly (`files_imported=0`,
  `context_index=None`); errors cleanly on a *named* folder that does not
  exist.
- **Test:** `TestCheckpoint1_Host_Asked_For_Context_Folder`.

### CP2 — Seed the project
- **Decision:** host confirms goals/constraints; agent calls
  `seed_context("Payment Gateway Modernization", goals=…, constraints=…)`.
- **Response:** `project_id: "001"`,
  `project_dir: "projects/001-payment-gateway-modernization"`; `GOALS.md`
  written with `## Goals` / `## Constraints`.
- **Monitored:** a second seed mints `002`; the returned id is usable with
  `check_gates`.
- **Test:** `TestCheckpoint2_Seed_Project`.

### CP3 — Relay `strategy`; MANDATORY gates open
- **Decision:** first relay call is `arckit.strategy(project_id=001)`.
- **Host asks:** (implicitly) "What are the prerequisites?"
- **Response:** relay returns `gate_blocked: true` — `PRIN` and `STKE`
  (both MANDATORY) are open. Relay still returns `intake` + `instructions`
  so the agent is ready once the gates close.
- **Monitored:** OPTIONAL codes (e.g. `RISK` on strategy) are silently
  omitted from `gates`; MANDATORY open ⇒ `gate_blocked` true.
- **Test:** `TestCheckpoint3_Strategy_Blocked_On_Mandatory_Gates`.

### CP4 — Unblock `PRIN`: run `principles`, answer host, persist
- **Decision:** `PRIN` gate open → agent steps back to `arckit.principles`.
- **Host asks:** the intake questions (PRIN has no static question block,
  so ≥1 placeholder).
- **Response:** agent generates `ARC-001-PRIN-v1.0.md` and persists it with
  `arckit.persist_artifact("001","PRIN", …)`.
- **Monitored:** `persist_artifact` returns `written: true`; after persist
  the `PRIN` gate on `strategy` flips to `closed`.
- **Test:** `TestCheckpoint4_Principles_Artefact`.

### CP5 — Unblock `STKE`: run `stakeholders`, answer host, persist
- **Decision:** after `PRIN`, `STKE` is the remaining MANDATORY gate. Agent
  runs `arckit.stakeholders`, answers host's intake, persists `STKE`.
- **Response:** `ARC-001-STKE-v1.0.md` written; `strategy` now
  `gate_blocked: false`.
- **Monitored:** last MANDATORY gate closes; `gate_blocked` becomes false.
- **Test:** `TestCheckpoint5_Stakeholders_Artefact`.

### CP6 — `strategy` now unblocked; agent generates `STRAT`
- **Decision:** gates closed; agent generates the `STRAT` document.
- **Host asks:** strategy intake (placeholder — `no-static-questions`).
- **Response:** `ARC-001-STRAT-v1.0.md` persisted; `relay["intake"]` is
  never empty even for uncovered codes (placeholder floor).
- **Monitored:** `gate_blocked` false; non-empty intake.
- **Test:** `TestCheckpoint6_Strategy_Unblocked`.

### CP7 — Persist `STRAT`; `next_step` surfaces the next command
- **Decision:** agent calls
  `arckit.next_step("001", completed=["principles","stakeholders","strategy"])`.
- **Response:** an unconditional handoff target of `strategy` — one of
  `{roadmap, diagram, requirements}` (deterministic min-pick).
- **Monitored:** the handoffs graph yields a concrete next command.
- **Test:** `TestCheckpoint7_Strategy_Artefact`.

### CP8 — `roadmap` gated on MANDATORY `REQ`
- **Decision:** agent relays `arckit.roadmap`.
- **Host asks:** "roadmap is blocked on `REQ` — want to run requirements
  first?"
- **Response:** relay returns `gate_blocked: true`, open MANDATORY set =
  `{REQ}` (PRIN already closed). Agent persists `REQ`; relay now
  `gate_blocked: false`.
- **Monitored:** closing `REQ` unblocks `roadmap`.
- **Test:** `TestCheckpoint8_Roadmap_Gated_On_Req`.

### CP9 — Host stops: all reachable handoffs complete
- **Decision:** after the completed set covers a handoff closure, agent calls
  `arckit.next_step` once more.
- **Host asks:** (nothing — host stops).
- **Response:** `next_step` returns `next: null`,
  `reason: "All reachable handoffs completed"` → loop terminates.
- **Monitored:** empty `completed` ⇒ `next: null` with the same reason.
- **Test:** `TestCheckpoint9_Host_Stops`.

### Cross-cutting invariants
`TestAgentLoop_Invariants`:
- `test_relay_never_returns_empty_intake` — every one of the 101 command
  relays returns ≥1 intake question (placeholder floor).
- `test_persist_artifact_rejects_unknown_type` — unknown codes rejected.
- `test_persist_multi_instance_sequence` — multi-instance types (ADR) get
  auto-incremented sequence numbers; a second persist does not clobber the
  first.
- `test_seed_and_persist_use_different_layouts` — pins defect **F1**.

## 3. How to run

```bash
cd ~/projects/arckit-mcp
python -m pytest tests/ -q          # 66 passed
python -m pytest tests/mcp/test_agent_loop.py -v   # the new 24
```

## 4. Verification record

- **Command:** `python -m pytest tests/ -q` (run from repo root)
- **Outcome:** `66 passed in 0.21s` (42 pre-existing + 24 new).
- No regressions; the new suite is isolated under `tmp_path` +
  `monkeypatch.chdir`, so it does not touch the real `projects/` tree.
