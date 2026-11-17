# Agent loop — checkpoint map

The agent loop is: **Seed → Relay → Advance → Re-check**, repeated
until `next_step` returns `next: null`.
`docs/agent-loop-checkpoints.md` §2 walks the loop with a sample
project (*Payment Gateway Modernization*) across nine checkpoints
(CP1–CP9). This file maps each checkpoint to the loop step and the
tool call that drives it.

| CP | Loop step | Tool call | What happens |
| --- | --- | --- | --- |
| CP1 | Seed (pre-check) | `arckit.seed_context` | Host asks for a context folder. The `seed_context` tool description mandates: "IF THE USER HAS NOT PROVIDED A CONTEXT FOLDER, ASK THEM FIRST." No folder ⇒ bare seed degrades cleanly (`files_imported=0`, `context_index=None`). |
| CP2 | Seed | `arckit.seed_context("…", goals=…, constraints=…)` | Mints `projects/001/` (bare layout + `.meta` sidecar, F1). `GOALS.md` written with `## Goals` / `## Constraints`. A second seed mints `002`. |
| CP3 | Relay | `arckit.strategy(project_id="001")` | Returns `gate_blocked: true` — MANDATORY `PRIN` and `STKE` open. The relay **still** returns `intake` + `instructions` so the agent is ready once the gates close. OPTIONAL codes (e.g. `RISK` on strategy) are silently omitted from `gates`. |
| CP4 | Relay (prereq) | `arckit.principles` → `arckit.persist_artifact("001","PRIN",…)` | `PRIN` gate open ⇒ step back to `principles`. PRIN has no static question block, so ≥1 placeholder question. Generate `ARC-001-PRIN-v1.0.md`, persist. `PRIN` gate on `strategy` flips to `closed`. |
| CP5 | Relay (prereq) | `arckit.stakeholders` → `arckit.persist_artifact("001","STKE",…)` | `STKE` is the remaining MANDATORY gate. Persist `STKE`. `strategy` now `gate_blocked: false`. |
| CP6 | Relay | `arckit.strategy` → `arckit.persist_artifact("001","STRAT",…)` | Gates closed; generate + persist `STRAT`. `relay["intake"]` is never empty even for uncovered codes (placeholder floor). |
| CP7 | Advance | `arckit.next_step("001", completed=["principles","stakeholders","strategy"])` | An unconditional handoff target of `strategy` — one of `{roadmap, diagram, requirements}` (deterministic min-pick). |
| CP8 | Relay (prereq) | `arckit.roadmap` → `arckit.persist_artifact("001","REQ",…)` | `roadmap` is MANDATORY-gated on `REQ`. `REQ` is open; the agent asks the host "want to run requirements first?", persists `REQ`, and the relay now returns `gate_blocked: false`. |
| CP9 | Advance (terminate) | `arckit.next_step("001", completed=[…all…])` | After the completed set covers a handoff closure, `next_step` returns `next: null, reason: "All reachable handoffs completed"` ⇒ the loop terminates. An empty `completed` also returns `next: null` with the same reason. |

## Cross-cutting invariants

Pinned in `TestAgentLoop_Invariants` (`tests/mcp/test_agent_loop.py`):

- `test_relay_never_returns_empty_intake` — every one of the 101
  command relays returns ≥1 intake question (placeholder floor, F4).
- `test_persist_artifact_rejects_unknown_type` — unknown codes are
  rejected.
- `test_persist_multi_instance_sequence` — multi-instance types
  (ADR) get auto-incremented sequence numbers; a second persist does
  not clobber the first.
- `test_seed_and_persist_share_layout` — pins defect **F1**: seed and
  persist share the bare `projects/{pid}/` layout.

## Worked example (abridged)

1. `arckit.seed_context(project_name="IRAP Platform Strategy",
   goals=["PSF-aligned security strategy"],
   constraints=["IRAP-assessed cloud", "data-sovereignty region"],
   context_folder="~/docs/psf-refs/")` → `project_id: "003"`.
2. `arckit.risk(project_id="003")` → MANDATORY `PRIN` open. First
   run `arckit.principles(project_id="003")` → no open MANDATORY
   gates → answer intake → generate `PRIN` →
   `arckit.persist_artifact("003","PRIN",content)`.
3. Re-check: `arckit.check_gates("risk","003")` → `PRIN` now
   `closed`. `RISK` gate is `OPTIONAL` → not in the list. Proceed:
   `arckit.risk(project_id="003")` → gate passes → answer intake →
   generate → persist `RISK`.
4. `arckit.next_step("003", completed=["principles","risk"])` →
   next command (e.g. `"strategy"`). Repeat the relay/persist step
   until the strategy document is complete.

The agent can call `arckit.list_commands` at any point to discover a
command it has not used yet. The whole exchange stays inside one MCP
session — no manual file juggling, no need to learn the command
graph.
