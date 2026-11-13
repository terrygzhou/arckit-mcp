# Proposal: fix-seed-context-layout

Source: `docs/agent-loop-checkpoints.md` (EYW-817) findings F1 + F2, remediation
plan `docs/agent-loop-checkpoints-remediation.md`.

## Why

F1 (the one confirmed defect): `arckit.seed_context` mints
`projects/{pid}-{slug}/` on disk and returns that path as `project_dir`, but
`persist_artifact`, `check_gates`, and `_artifact_exists` all resolve the
**bare** `projects/{pid}/` directory. An agent that seeds a project and then
persists to the returned slug-suffixed directory will write artefacts into a
directory nothing ever reads — no gate will ever close. Pinned by
`test_seed_and_persist_use_different_layouts`.

F2 (cosmetic): `run_command`'s relay payload carries `id: "ARC-{project_id}"`
but no top-level `project_id` key, unlike `check_gates`. Reconstructing the
id from the `id` string is fragile.

## What Changes

- **BREAKING** (on-disk layout): `seed_context` mints `projects/{pid}/`
  instead of `projects/{pid}-{slug}/`. The slug is retained as a `slug` field
  in the return payload, not in the directory name.
- `seed_context` returns `project_dir: "projects/{pid}"` — matching what
  `persist_artifact` actually reads.
- `seed_context` collision detection re-keyed from slug-suffix name matching
  to name→id tracking: a sidecar `projects/{pid}/.meta` records the original
  project name; a seed with the same name under any id is rejected.
- `persist_artifact`, `check_gates`, `_artifact_exists`, `next_step`:
  **no change** (already use the bare layout).
- F2: `run_command` relay payload gains a top-level `"project_id"` key.
- Test flip: `test_seed_and_persist_use_different_layouts` →
  `test_seed_and_persist_share_layout` (seed and persist now use the same
  directory). Checkpoint CP2 assertions updated to
  `project_dir == "projects/001"`.
- Optional: new `test_relay_includes_project_id`.

## Capabilities

### New Capabilities

- `arckit-mcp/project-lifecycle`: The on-disk project layout contract —
  `seed_context` creates `projects/{pid}/`, the returned `project_dir` always
  matches the directory that `persist_artifact` and `check_gates` read back,
  and re-seeding with an existing project name is rejected.

- `arckit-mcp/command-relay`: The command relay payload contract — every
  `arckit.{command}` relay response carries a top-level `project_id` key.

### Modified Capabilities

(none — no specs exist yet under `openspec/specs/`; this is the first spec
for this repo)

## Impact

- `arckit_mcp/server.py`: `seed_context` (mint + return + collision check),
  `run_command` (add `project_id` key).
- `tests/mcp/test_agent_loop.py`: flip layout test, update CP2 assertions.
- `tests/mcp/test_seed_context.py`: likely asserts the slug dir layout;
  must be updated to the bare layout.
- External consumers: none found in-repo consuming the returned slug
  `project_dir`. Rollback surface is limited to `seed_context` in
  server.py + the two test files.
