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
| `arckit.seed_context` | Start a project tree (`projects/{NNN}/`). Returns `project_id` to use everywhere else. Stage 0: remind the user to provide a context folder before launching; ask if they haven't given one. |
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

## Collaboration (strategy-class work)
For strategy/transition work, **before generating the full artifact set**, surface the 2-4 high-leverage forks with the user in a single `clarify` batch (e.g. scope of the ask, cloud posture, build-vs-buy, depth of deliverable). Don't silently fill gaps with your own defaults — a relay drift is a tooling limitation, not a reason to skip user input. After the user confirms the forks, (re)generate the artifacts to match; if a fork later changes, retune the *whole set* for consistency and re-verify with a grep + gate check.

## The agent loop

### 0. Remind — context folder

Before anything else, remind the user to provide a folder of reference
documents (RFPs, legacy specs, research notes) that the seed will
import into `external/` as the project's context baseline. Ask once;
if the user has no folder to give, proceed with a bare seed
(`context_folder=None`) — the import degrades cleanly and the rest of
the loop is unchanged.

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

### What each tool returns

| Concern | Tool | Returns (exact keys) |
| --- | --- | --- |
| Seed project | `arckit.seed_context(project_name, goals?, constraints?, context_folder?)` | `{project_id, project_dir, slug, files_imported, context_index}`; on name collision `{"error": "Project 'X' already seeded", "project_id": null}`; on missing folder `{"error": "Context folder not found: …", "project_id": null}`. |
| Discover commands | `arckit.list_commands()` | `[{command, tool, overlay, gates: [{code, tier}]}]` — one entry per command; OPTIONAL gates omitted. |
| Run a command (relay) | `arckit.{command}(project_id)` | `{id, project_id, command, doc_type, intake: [{id, question, required, hint}], instructions: str, gates: [{code, tier, status}], gate_blocked: bool}`. `doc_type` is a single code (one doc-type) or a list (multi doc-type). `gates` carries MANDATORY + RECOMMENDED only; OPTIONAL omitted. `gate_blocked` is `true` iff any MANDATORY gate is open, including soft-structural inputs. |
| Check gates | `arckit.check_gates(command, project_id)` | `{command, project_id, gates: [{code, tier, status}], gate_blocked: bool}`. |
| Read saved answers | `arckit.persist_intake(project_id, command)` | `{project_id, command, found: bool, answers: object \| null, path: str}`; on a malformed file adds `"error": "Malformed intake file: …"`. **Read-only** — the server never writes answers. |
| Write an artifact | `arckit.persist_artifact(project_id, type_code, content, sequence?)` | On success `{path: str, written: true}`. On unknown `type_code`: `{"error": "Unknown doc-type code '…'. …", "written": false}`. `path` is relative to the server cwd. Multi-instance codes (ADR, DIAG, …) auto-increment the `-NNN` sequence when `sequence` is omitted. |
| Advance | `arckit.next_step(project_id, completed?)` | `{project_id, next: str \| null, reason: str}`. `next` is `null` when no handoff target qualifies. |

**Interpretation rules for client agents:**

- **Relay `gates` + `gate_blocked`** — `gate_blocked: true` means a hard-stop; read `gates` for the open MANDATORY codes and step back to the prerequisite command. The relay still returns `intake` + `instructions` so you're ready to proceed the moment the gate closes.
- **Relay `intake`** — a list of questions to interview the user one at a time. Skipped questions render `TBD` in the artifact and never contribute to `gate_blocked`. The server never returns an empty `intake` list (placeholder floor, F4).
- **Relay `instructions`** — a free-text prompt telling you to run the command in-session and save each artefact via `arckit.persist_artifact`. Treat it as a reminder, not a command to execute.
- **`persist_intake` `found: false`** — no saved answers; run the interview live. `found: true` — prefill the interview with `answers`.
- **`next_step` `next: null`** — the loop terminates; all reachable handoffs are complete. An empty `completed` list also returns `next: null` with the same reason.

### Framework evidence tools

Beyond the static tools above, the server registers a set of *dynamic*
framework-evidence tools at startup (`server.py::_register_framework_tools`),
one per tool in the generated `arckit_mcp/frameworks` package. Each is
exposed under the name `arckit.{tool_name}` — e.g.
`arckit.togaf_check_code_coverage`, `arckit.oaa_check_strategy_canvas`,
`arckit.it4it_check_value_stream`, `arckit.agent_check_tool_allowlist`.
These validate parsed architecture-evidence documents (TOGAF ADM
coverage, OAA strategy canvas / compliance evidence, IT4IT value
streams / component trace, agent registry coverage / tool allowlist).

The tools are **schema-driven and generated** — the `frameworks/`
package is produced by `arckit-mcp-sync` and is DO-NOT-EDIT. Do not
pin line numbers here; the tool set grows when a new framework
manifest lands. Common shape:

- **Registry-coverage tools** (`*_check_code_coverage`,
  `*_check_registry_coverage`): take a `codes` array (plus optional
  `mandatory` override); return
  `{valid, missing, unknown, coverage_report: {total_codes,
  covered_codes, coverage_pct}}`.
- **Structure-check tools** (`togaf_check_transition_plan`,
  `oaa_check_strategy_canvas`, `oaa_check_compliance_evidence`,
  `it4it_check_value_stream`, `it4it_check_component_trace`,
  `agent_check_tool_allowlist`): take the parsed document
  (YAML/JSON → dict); return a verdict object such as
  `{valid, problems, ...}` or a gap list `{orphaned_refs, per-stream
  counts}` depending on the tool. `oaa_check_compliance_evidence`
  additionally returns schema violations (when `jsonschema` is
  available) and a control-status rollup.
- **Common error shape:** a tool whose input fails its JSON schema
  raises `SchemaError` (the registered wrapper converts it to the
  MCP-standard `{"error": "..."}` envelope).

Each tool's description is self-documenting; the generated module's
`TOOLS` dict in `arckit_mcp/frameworks/{framework}.py` carries the
per-tool description, argument JSON-Schema, and framework codes.

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
