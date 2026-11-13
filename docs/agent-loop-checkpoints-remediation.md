# EYW-817 — Remediation Plan for `agent-loop-checkpoints.md`

Companion to `docs/agent-loop-checkpoints.md` (EYW-817 checkpoint log).
Each defect (F1–F5) gets a concrete reaction: what to change, what to
leave, and how to verify. All paths are relative to the repo root.

**Priority order** (severity × blast radius): F1 → F3 → F5 → F2. F4 is
accepted as by-design and not on the path.

## 1. Per-finding reactions

### F1 — `seed_context` slug dir vs `persist_artifact`/`check_gates`
**bare** dir

**Status: accepted defect — pinned by
`test_seed_and_persist_use_different_layouts`, not fixed.** The
checkpoint doc documents it as a known defect; agents must persist to
the bare `projects/{project_id}/` dir returned by `_project_dir`, not
to the `project_dir` string `seed_context` returns.

**Why accepted (not fixed in this pass):**
- Fixing it ripples into `persist_artifact`, `_artifact_exists`,
  `check_gates`, `next_step`, and every generated table that keys on
  the bare id.
- Tests already pin the current behaviour; "fixing" without updating
  the test suite first would break the green 66-test baseline.
- `seed_context` is new; the bare-dir layout predates it. The
  slug dir is the *newer* artifact; aligning the older layout to it
  is a bigger migration.

**When to revisit (exit criteria for the fix):**
1. Decide the canonical layout: slug dir (`projects/NNN-{slug}/`)
   vs bare dir (`projects/{pid}/`). The slug dir is more
   human-readable; the bare dir is what every gate reader already
   resolves.
2. Update `persist_artifact`, `_artifact_exists`, `check_gates`,
   `next_step`, and `seed_context` to agree on the chosen layout.
3. Update the test that pins the layout split to assert the *new*
   behaviour.
4. Run `pytest tests/ -q`; keep 66 green (or 67+ if new tests are
   added).

**Interim mitigation (works today):**
- Agents persist to the bare `projects/{project_id}/` dir, *not* the
  `project_dir` returned by `seed_context`. The relay's
  `instructions` field already points at the bare dir ("Save each
  artefact to `projects/{project_id}/`").
- If you need the slug dir for human browsing, it stays on disk;
  gates just don't read it.

### F2 — Relay `id` asymmetry (no top-level `project_id` key)

**Reaction: leave as-is, document the asymmetry.** The relay payload
carries `id` = `ARC-{project_id}`; `check_gates` carries
`project_id`. The asymmetry is cosmetic — reconstructing the id from
`relay["id"]` is a 4-char prefix strip. Adding a top-level
`project_id` to the relay would bloat every relay payload and is not
worth the breaking change (MCP clients already key off the tool
name). The checkpoint doc §1.2 notes the asymmetry so reviewers
don't "fix" it by accident.

**Exit criteria:** none — no change planned.

### F3 — Hand-maintained `name_map`/`overlay_map` in `server.py`

**Reaction: replace the hand-maintained maps with generated data.**
The `GATE_TIERS` table (generated) already carries the command key
(`arckit-claude/{name}`) and the gate codes. `server.py` re-derives
doc-type codes from a separate hand-maintained `name_map`/
`overlay_map`, which drifts when arc-kit adds a command or a
doc-type.

**Plan:**
1. Extend `generate-mcp-registry.py` to also emit a
   `command → [doc-type codes]` mapping alongside `GATE_TIERS`.
   The generated table would live in a new module
   (`arckit_mcp/_registry.py` or a new `_command_codes.py`).
2. Replace `_command_doc_types` in `server.py` with a read from the
   generated table.
3. Drop the hand-maintained `name_map` / `overlay_map` from
   `server.py`.
4. Add a test: `test_command_doc_types_match_generated_table` —
   for every key in `GATE_TIERS`, the generated
   command→codes table must agree with the registry's
   `DOC_TYPES` membership.
5. Run `pytest tests/ -q`; keep green.

**Verification:**
- `grep -n "name_map\|overlay_map" arckit_mcp/server.py` returns
  nothing (maps deleted).
- The new test passes.
- `arckit.list_commands` output is unchanged (same 101 commands,
  same gate tiers).

**Interim mitigation (works today):**
- After regenerating the `GATE_TIERS` table via
  `arckit-mcp-sync`, also hand-update `server.py`'s
  `name_map`/`overlay_map` to cover the new commands. The
  hand-maintenance step is the silent drift risk; a code review
  checklist item ("did the sync also touch `server.py`?")
  mitigates it.

### F4 — 160 of 177 doc-types are `no-static-questions`

**Reaction: accepted, by-design.** The checkpoint doc §1.2 F4
documents the gap. The relay degrades to a per-code placeholder
question (`Provide inputs for the {type name} artefact.`) for every
uncovered code; the 17 covered codes (those with a generated
`INTAKE` entry) get the template question list. `COVERAGE` makes
the gap visible without changing behaviour.

**Plan:** none. The placeholder floor is intentional — the server
must never return an empty intake list, and the checkpoint doc
invariant `test_relay_never_returns_empty_intake` pins that.

**Exit criteria:** none — no change planned. Future arc-kit work
may cover more codes; `COVERAGE` + `INTAKE` will regenerate.

### F5 — `persist_intake` stem is hyphenated, not underscored

**Reaction: document + test, no behaviour change.** The MCP tool
parameter is the underscored command name
(`discovery_architecture`); the on-disk stem is the hyphenated
form (`discovery-architecture.json`), derived by
`command.replace("_", "-")`. Agents copying the tool parameter
verbatim into a file path will miss saved answers.

**Plan:**
1. Add a test `test_persist_intake_stem_is_hyphenated` that
   asserts: for tool name `discovery_architecture`, the on-disk
   path is `.arckit/intake/discovery-architecture.json`, not
   `.arckit/intake/discovery_architecture.json`.
2. No behaviour change — the stem is hyphenated by design (to
   match the arc-kit command file names). The existing tool
   description ("Read saved .arckit/intake/{command}.json answers")
   is already close; the test pins the hyphenation.

**Verification:**
- The new test passes.
- `test_no_write_path_for_answers` (existing) still passes —
  `persist_intake` is read-only.

**Interim mitigation (works today):**
- Agents reading saved intake answers use the hyphenated stem, not
  the tool parameter. The tool description in
  `arckit_mcp/server.py` should make this explicit.

## 2. Work order

| Order | Finding | Change | Test impact |
|-------|---------|--------|-------------|
| 1 | F5 | Test + doc-comment the hyphenated `persist_intake` stem | +1 test (`test_persist_intake_stem_is_hyphenated`) |
| 2 | F3 | Replace hand-maintained `name_map`/`overlay_map` with generated command→codes table | +1 test (`test_command_doc_types_match_generated_table`) |
| 3 | F2 | No change (documented) | — |
| 4 | F4 | No change (by-design, documented) | — |
| 5 | F1 | No change (accepted defect, pinned by test; revisit when the layout migration is scheduled) | — |

## 3. Baseline invariants (must stay green)

- `pytest tests/ -q` → **66 passed** (42 pre-existing + 24
  checkpoint tests in `test_agent_loop.py`).
- Per-file: `test_agent_loop` 24, `test_gates` 4, `test_intake` 22,
  `test_next_step` 5, `test_seed_context` 8, `test_sync` 3.
- `test_seed_and_persist_use_different_layouts` continues to pin
  the F1 defect (slug vs bare dir) — do **not** "fix" it in this
  pass.
- `test_relay_never_returns_empty_intake` continues to pin the
  F4 placeholder floor.
- `test_no_write_path_for_answers` continues to pin the
  `persist_intake` read-only shape.

## 4. Verification record (this pass)

- **Command:** `python -m pytest tests/ -q` (run from repo root)
- **Outcome:** `66 passed in 0.21s`.
- No code changes in this pass; this doc is the reaction/plan
  document. Code changes (F3, F5) land in a follow-up pass with
  their tests.
