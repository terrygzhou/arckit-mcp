# Tasks: fix-seed-context-layout

## 1. F1 — Reconcile `seed_context` layout with the read side

- [ ] 1.1 Change `seed_context` to mint `projects/{pid}/` instead of
  `projects/{pid}-{slug}/` (server.py ~line 295: `target =
  projects_root / f"{pid}-{slug}"` → `projects_root / pid`). Verify:
  `python -m pytest tests/mcp/test_seed_context.py -q` reveals the
  assertions that must flip (expected red → green after 1.2).
- [ ] 1.2 Change `seed_context`'s return payload: `project_dir:
  f"projects/{pid}"` and add a `slug` field (server.py ~line 335).
  Verify: a unit test asserting the response shape.
- [ ] 1.3 Write a `projects/{pid}/.meta` sidecar (JSON, at minimum
  `{"name": …, "pid": …}`) during seeding, and re-key the collision check
  (server.py ~line 283) to scan existing `.meta` files for the same
  name. Verify: `seed_context("X")` then `seed_context("X")` → the second
  call returns `{"error": "Project 'X' already seeded", "project_id":
  null}` and no new dir is created.
- [ ] 1.4 Update `tests/mcp/test_seed_context.py` to assert the bare
  layout (`projects/001/`, `project_dir == "projects/001"`), the `slug`
  field, and the duplicate-name rejection. Verify: full file green.
- [ ] 1.5 Flip `test_seed_and_persist_use_different_layouts`
  (tests/mcp/test_agent_loop.py ~line 495) to
  `test_seed_and_persist_share_layout`: seed mints `projects/001/`,
  `persist_artifact("001","PRIN",…)` writes into `projects/001/`,
  `check_gates` sees the gate closed, no slug dir exists. Verify: test
  passes.
- [ ] 1.6 Update `TestCheckpoint2_Seed_Project` (and any other CP2
  assertions) from `project_dir == "projects/001-payment-gateway-
  modernization"` to `project_dir == "projects/001"`. Verify: `python -m
  pytest tests/mcp/test_agent_loop.py -q` → 24 passing.
- [ ] 1.7 End-to-end invariant check: seed → persist PRIN →
  `check_gates` shows the gate closed in one tree; no orphan slug dir.
  Verify: a manual or scripted run under `tmp_path` (reuse the agent-loop
  fixture style).
- [ ] 1.8 Grep the whole repo (and note it in the PR description) to
  confirm no consumer reads the slug-suffixed `project_dir`. Verify: no
  hits outside `seed_context`'s own return.

## 2. F2 — Relay payload symmetry

- [ ] 2.1 Add `"project_id": project_id` to `run_command`'s return dict,
  next to `"id"` (server.py ~lines 483–491). Verify: existing suite
  still green.
- [ ] 2.2 Add `test_relay_includes_project_id` asserting the key is
  present and equals the id used (in `tests/mcp/test_agent_loop.py`
  invariants or a relay test module). Verify: new test passes.

## 3. Verification & docs

- [ ] 3.1 Run the full suite `python -m pytest tests/ -q` from the repo
  root. Verify: all tests pass (66 → 67+ with the new F2 test), no
  regressions.
- [ ] 3.2 Add a note in `docs/agent-loop-checkpoints.md` §1.2 findings:
  F1 marked fixed in this change, F2 marked fixed. Verify: doc updated.
- [ ] 3.3 Confirm `README.md` / `pyproject.toml` use `python` (not
  `python3`) and therefore leave `docs/agent-loop-checkpoints.md` §3
  `python -m pytest` as-is (remediation plan decision). Verify: no
  `python3` invocations in repo tooling.
  TICKET: `openspec/changes/fix-seed-context-layout/tasks.md` task 3.3
  is the ticket-of-record for the `python` vs `python3` tooling
  constraint. See `docs/agent-loop-checkpoints.md` §1.3 for context.
