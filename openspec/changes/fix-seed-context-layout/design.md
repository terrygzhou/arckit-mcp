# Design: fix-seed-context-layout

## Context

`arckit_mcp/server.py` is the MCP server for the ArcKit governance harness.
`seed_context` (server.py ~line 250–335) mints a project directory; the
rest of the harness (`persist_artifact`, `check_gates`, `_artifact_exists`,
`next_step`, all via `_project_dir`, server.py:48–51) resolves the **bare**
`projects/{pid}/`. The two layouts do not line up (finding F1,
`docs/agent-loop-checkpoints.md`). F2 is a payload-symmetry nit in
`run_command` (server.py:476+).

## Goals / Non-Goals

Goals:
- One layout for the whole harness: `projects/{pid}/` everywhere.
- Seed collision detection that survives across invocations without
  scanning slug-suffixed names.
- Relay payload symmetry (`project_id` key present in `run_command`
  responses, matching `check_gates`).

Non-goals:
- F3 (auto-generating the doc-type mapping) — tracked separately,
  documented as a known limitation, not solved here.
- Re-architecting the prompt-relay model.
- Changes to gate-logic (`check_gates` behaviour on existing bare trees is
  untouched).

## Decisions

### D1: Align `seed_context` to the bare layout (not the reverse)

Aligning the read side (`persist_artifact`, `check_gates`,
`_artifact_exists`, `next_step`) to the slug layout would touch every
caller of `_project_dir`. Aligning `seed_context` to the bare layout is one
function + its collision check. Lowest surprise: the slug remains
available as a return field for humans, the directory stays the stable,
machine-facing key.

Alternatives considered:
- Add a slug→id indirection file (`.arckit/projects.json`) the read side
  consults. Rejected: the read side already works on bare ids; indirection
  adds a second failure mode.

### D2: Collision detection via a sidecar `.meta` file

Currently: collision = `any(p.name.endswith(f"-{slug}") for p in
projects_root.iterdir())`. That check goes away with the slug dir.
New: `seed_context` writes `projects/{pid}/.meta` containing at minimum
the original project name (JSON or key-value; JSON is fine at this scale).
Collision check = scan existing `projects/NNNN/.meta` files for a matching
name. O(number of projects), trivial for a governance harness.

Alternatives:
- Keep a global `projects/.index` registry. Rejected: one more shared file
  to corrupt for no benefit.
- Fall back to scanning slug names. Rejected: we are removing slug names.

### D3: Add `project_id` to the relay dict (additive)

`run_command` returns its dict; insert `"project_id": project_id` next to
`"id": f"ARC-{project_id}"`. Purely additive; no consumer breakage.

### D4: F4 is a no-op, pinned by existing invariant

The `test_relay_never_returns_empty_intake` invariant already pins the
placeholder floor. No code change; add a comment referencing finding F4 if
desired during implementation.

## Risks / Trade-offs

- **External consumer of the slug `project_dir`** → none found in-repo
  (grep of `project_dir` consumers). Verify once more at implementation
  time before landing. Rollback = revert server.py:283/295/335 + the test
  rename; no gate-logic involved, so bare trees behave exactly as before.
- **Pre-existing trees with slug-suffixed dirs** (projects seeded before
  the fix) → they keep working with `check_gates` only if their artefacts
  were written to the bare dir; a tree that wrote artefacts into the slug
  dir has broken gates and must be re-seeded post-fix. Migration:
  `git mv` / `cp` slug-dir contents into the bare dir manually, or re-seed.
  Document in the PR description.
- **`.meta` format drift** → keep it trivially parseable (JSON object with
  `name` and `pid`); add a tolerant reader that ignores unknown keys.

## Migration Plan

1. Land F1 + F2 + flipped tests in one PR (PR 1).
2. Add `project_id` relay test (F2) — may ride along.
3. No database/state migration; on-disk `projects/` trees are
   user-local. Pre-fix slug trees: document the manual move in the PR.

## Open Questions

- `.meta` sidecar: JSON vs plain key-value? (Decide at implementation;
  JSON recommended.) Does not change specs.
