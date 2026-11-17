# Artifact naming

## File name

`arckit.persist_artifact(project_id, type_code, content, sequence=None)`
writes to:

```
projects/{project_id}/ARC-{pid}-{TYPE}-v1.0.md
```

- `{pid}` is the 3-digit project id (e.g. `001` — `project_id.zfill(3)`).
- `{TYPE}` is the upper-cased doc-type code from the relay's `doc_type`
  field (e.g. `PRIN`, `STKE`, `STRAT`).
- `v1.0` is the current artefact version; all writes land at `v1.0`.

## Multi-instance sequencing

Doc-type codes in `MULTI_INSTANCE_TYPES` (e.g. `ADR`, `DIAG`) allow
more than one artefact per project. They get a `-NNN` sequence
segment:

```
projects/{pid}/ARC-{pid}-{TYPE}-{NNN}-v1.0.md
```

- When `sequence` is omitted, the next available number is assigned
  by scanning existing artefacts (root **and** the `SUBDIR_MAP`
  subdirectory) for the pattern
  `ARC-{pid}-{TYPE}-\d{3}-v\d+\.\d+\.md` and taking `max + 1`.
- A second persist does **not** clobber the first — a new sequence
  number is minted. Pinned by
  `test_persist_multi_instance_sequence`
  (`tests/mcp/test_agent_loop.py`).

## SUBDIR_MAP

Some doc-type codes land in a subdirectory of the project root
instead of the root. `SUBDIR_MAP` maps the code to the subdirectory
(e.g. `ADR` → `decisions/`). The directory is created on first
persist (`mkdir(parents=True, exist_ok=True)`).

- If the code is in `SUBDIR_MAP`, the artefact lands in
  `projects/{pid}/<subdir>/ARC-{pid}-{TYPE}[-NNN]-v1.0.md`.
- Sequence scanning covers both the root and the subdirectory, so
  numbering stays monotonic across both.

## `.meta` sidecar (F1)

`arckit.seed_context` mints `projects/{NNN}/` (bare layout — F1 fix)
with a **`.meta` sidecar** at the project root:

```
projects/001/.meta
```

Content (JSON):

```json
{ "name": "Payment Gateway Modernization", "pid": "001" }
```

- Records the original project name.
- Re-seeding the **same name** is rejected: the server scans
  existing `.meta` files; a name collision returns
  `{"error": "Project 'X' already seeded", "project_id": null}`.
- The `slug` returned by `seed_context` is a **payload-only**
  cosmetic field — it is not part of the on-disk path (F1 fix: the
  old slug-divergence is gone). The canonical path is
  `projects/{NNN}/` with the `.meta` sidecar.

## Rejection rules

- **Unknown doc-type codes** are rejected:
  `{"error": "Unknown doc-type code '…'. Valid codes come from the
  doc-types.mjs registry.", "written": false}`. Pinned by
  `test_persist_artifact_rejects_unknown_type`.
- All project-state lookups are relative to the server's working
  directory (`projects/{project_id}/`), so launch `arckit-mcp` from
  the root of the ArcKit working tree.

## Source

`arckit_mcp/server.py` — `persist_artifact()` (line 585),
`_next_sequence()` (line 622), `_project_dir()`, `.meta` handling in
`seed_context()` (line 257). `SUBDIR_MAP`, `MULTI_INSTANCE_TYPES`,
`KNOWN_TYPES` imported from the generated `arckit_mcp/_registry.py`.
