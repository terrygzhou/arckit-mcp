---
name: arckit-mcp-agent-loop
description: Drive the ArcKit governance harness through the arckit-mcp MCP server. Use when an agent needs to run ArcKit commands (strategy, risk, roadmap, principles, etc.) without reading command markdown — the server relays intake questions, gate status, and handoff order so the LLM does the actual document generation in-session. Covers seeding a project tree, the relay→persist→advance loop, gate-blocking semantics, and artifact naming.
---

# ArcKit MCP Agent Loop

The ArcKit MCP server (stdio) exposes the ArcKit governance harness as
tools so an agent can drive it without memorising 101 commands. The
server is a *prompt relay*: it tells the agent which gates are open,
what intake questions to answer, and where to write each result. The
agent runs the LLM generation itself and persists the result via
`arckit.persist_artifact`. The agent never reads command markdown; it
follows one loop until done.

## Tool groups

**Meta-tools** (governance logic — reach for these first):

| Tool | What it does |
| --- | --- |
| `arckit.seed_context` | Start a project tree (`projects/{NNN}/`). Returns `project_id` to use everywhere else. Ask the user for a context folder first if they haven't given one. |
| `arckit.list_commands` | Enumerate every known command with its doc-type codes and gate tiers. Discovery only, not required in the normal loop. |
| `arckit.next_step` | Walk the handoffs graph; return the next recommended command given `project_id` + commands completed so far. |
| `arckit.check_gates` | Return which prerequisite gates are open/closed for a command. `MANDATORY` hard-stop when open; `RECOMMENDED` noted; `OPTIONAL` omitted. |
| `arckit.persist_intake` | Read saved intake answers (`.arckit/intake/{command-hyphenated}.json`). Read-only — the server never writes answers. |
| `arckit.persist_artifact` | Write a generated artefact into the project tree. Multi-instance types (ADR, DIAG, …) get the next sequence number when `sequence` is omitted. |

**Per-command tools** — one `arckit.{command}` tool per ArcKit command
(101 of them), e.g. `arckit.strategy`, `arckit.risk`, `arckit.roadmap`.
Each returns `intake` (questions, answered one at a time),
`instructions` (where to run the generation and where to save the
result), `gates` + `gate_blocked` (current gate status), `doc_type`
(the doc-type code(s) the command writes), and `project_id` (echoed
back — relay symmetry, F2).

## The agent loop

### 1. Seed

`arckit.seed_context(project_name, goals, constraints, context_folder)`
returns `project_id` (e.g. `"001"`), `project_dir` (`projects/001/` —
bare layout, F1 fix), `slug` (cosmetic, payload-only), `files_imported`,
`context_index`. The server mints `projects/NNN/` with a `.meta`
sidecar recording the original project name; re-seeding the same name
is rejected with `{"error": "Project 'X' already seeded",
"project_id": null}`. If the user has already seeded a project, reuse
the existing `project_id` — do not seed a second one.

### 2. Relay

Call the per-command tool, e.g. `arckit.strategy(project_id: "001")`.

- **`gate_blocked` is true** — a `MANDATORY` gate is open. Each open
  gate entry's `code` is a doc-type code mapping to a prerequisite
  command (`PRIN` → `arckit.principles`, `STKE` →
  `arckit.stakeholders`, …). Run the prerequisite, persist its
  artefact, re-check. Full hard-stop protocol and soft-gate
  escalation in [references/gate-tiers.md](references/gate-tiers.md).
- **`gate_blocked` is false** — answer the `intake` questions one at a
  time (ask-always, answer-optional), generate the document, then
  `arckit.persist_artifact(project_id, type_code, content)` where
  `type_code` is the relay's `doc_type` field (`"STRAT"`, `"PRIN"`,
  `"STKE"`, …). Intake discipline in
  [references/intake-discipline.md](references/intake-discipline.md).

### 3. Advance

`arckit.next_step(project_id, completed: [...])` with command names
completed so far (not tool names, e.g. `["principles",
"stakeholders", "strategy"]`). Returns `{"next": "risk", "reason":
"..."}` or `{"next": null, "reason": "All reachable handoffs
completed"}` — the loop terminates on `null`. The handoffs graph is
deterministic: when several commands qualify, the
lexicographically-smallest name wins. An edge is *satisfied* when it
carries no condition or its referenced doc-type code has an artefact
present; unevaluable conditions are omitted, not assumed satisfied.
Repeat from step 2.

### 4. Re-check

After persisting an artefact, `arckit.check_gates(command,
project_id)` confirms the gate it closed is now `closed` — the
verification step before advancing.

## Gate hierarchy

| Tier | Behaviour |
| --- | --- |
| `MANDATORY` | Open → `gate_blocked: true` → hard-stop. Complete the prerequisite command and persist its artefact first. |
| `RECOMMENDED` | Noted in `gates`, does not set `gate_blocked`. |
| `OPTIONAL` | Omitted from `gates` entirely — invisible to the agent. |

A MANDATORY soft-gate (from `INTAKE` mandatory inputs) colliding with a
same-code hard-gate entry at a lower tier escalates the hard entry in
place — not duplicated. Skipped intake questions render `TBD` in the
artefact and never contribute to `gate_blocked`; only missing
structural MANDATORY inputs do. Protocol:
[references/gate-tiers.md](references/gate-tiers.md).

## Artefact naming

`arckit.persist_artifact` writes `projects/{project_id}/ARC-{pid}-{TYPE}-v1.0.md`
(`{pid}` 3-digit project id, `{TYPE}` the doc-type code).
Multi-instance types (ADR, DIAG, …) get a `-{NNN}` sequence segment
(omitted `sequence` → next available by scanning existing artefacts)
and land in the `SUBDIR_MAP` subdirectory (e.g. `decisions/` for
ADR). Unknown codes are rejected. `seed_context` mints `projects/NNN/`
with a `.meta` sidecar (`{"name", "pid"}`) — bare layout canonical
(F1 fix); `slug` is payload-only. Details:
[references/artifact-naming.md](references/artifact-naming.md).

## Loop checkpoints (CP1–CP9)

`docs/agent-loop-checkpoints.md` §2 walks the full loop across nine
checkpoints on the *Payment Gateway Modernization* sample project. The
CP1–CP9 mapping (context-folder ask → seed → relay-blocked → unblock
prereqs → unblock relay → advance → gated handoff → terminate) and an
abridged IRAP worked example live in
[references/agent-loop.md](references/agent-loop.md).

## Known limitations (pinned in code)

- **F4** — placeholder intake for no-static-questions codes is by
  design. Pinned by `test_relay_never_returns_empty_intake`.
- **F5** — `persist_intake` reads hyphenated stems
  (`.arckit/intake/{command-hyphenated}.json`) while the MCP parameter
  is underscored; copying the parameter into a path misses saved
  answers. Pinned by `test_no_write_path_for_answers` (`discovery` →
  `discovery.json`).
- **F3** — hand-maintained `name_map` / `overlay_map` in `server.py`
  can drift when the registry adds commands; new commands fall back to
  generic placeholder intake with no doc-type codes.

Development tooling and test commands live in `AGENTS.md`, not in
this client-agent runbook.

## Sources

- `arckit_mcp/server.py` — `seed_context()` (line 257),
  `run_command()` (~line 522), `check_gates()` (line 128),
  `persist_intake()` (line 540), `persist_artifact()` (line 585),
  `_next_sequence()` (line 622), `_register_meta_tools()` (line 638).
- `arckit_mcp/gates.py`, `arckit_mcp/handoffs.py`,
  `arckit_mcp/intake.py`, `arckit_mcp/_registry.py` — generated tables
  (DO NOT EDIT BY HAND; regenerate with `arckit-mcp-sync` /
  `generate-mcp-intake.py`).
- `docs/agent-loop-checkpoints.md` §1–§2 — checkpoint log and
  known-limitations notes.
- `docs/agent-loop-checkpoints-remediation.md` §3 — baseline
  invariants.
- `openspec/changes/fix-seed-context-layout/` — F1 + F2 change.

## References

- [references/gate-tiers.md](references/gate-tiers.md) — tier semantics, hard-stop protocol, soft-gate escalation.
- [references/intake-discipline.md](references/intake-discipline.md) — one-question-at-a-time, sole-persister rule, `persist_intake` read-only, `.arckit/intake/` layout, placeholder degradation.
- [references/artifact-naming.md](references/artifact-naming.md) — `ARC-{pid}-{CODE}[-NNN]-vN.N.md`, sequencing, `SUBDIR_MAP`, `.meta` sidecar.
- [references/agent-loop.md](references/agent-loop.md) — CP1–CP9 mapping and worked example.
