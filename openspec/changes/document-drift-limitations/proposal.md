# Proposal: document-drift-limitations

Source: `docs/agent-loop-checkpoints.md` (EYW-817) findings F3 + F4,
remediation plan `docs/agent-loop-checkpoints-remediation.md`.

## Why

F3 (tracked, deferred by decision): the doc-type mapping inside
`server._command_doc_types` is hand-maintained (`name_map` /
`overlay_map`) and does not auto-refresh when arc-kit adds a command or
code to `doc-types.mjs` — a silent cross-repo drift risk. The remediation
plan explicitly defers the architectural fix (auto-generation of a
`COMMAND_DOC_TYPES` table, or a CI drift check) to a follow-up ticket, but
requires the limitation to be *documented* now.

F4: `intake.COVERAGE` marking most core codes `no-static-questions` and
the relay degrading to one placeholder is by-design, not a defect. It is
pinned by `test_relay_never_returns_empty_intake`. This change confirms
that with an explanatory comment rather than a code change.

## What Changes

- Add a "Known limitations" section to
  `docs/agent-loop-checkpoints.md` recording F3: hand-maintained doc-type
  mapping, drift risk, and the two deferred options (A: generate
  `COMMAND_DOC_TYPES` into `_registry.py`; B: CI drift check).
- Add a brief comment in `server.py` near `_command_doc_types` and near the
  placeholder-intake fallback referencing F3 / F4 (by-design), so a future
  reader knows the gap is intentional and tracked.
- File/record a follow-up ticket reference in the doc (no actual ticket
  system change in-repo).
- No code behaviour change; F4 test remains as-is.

## Capabilities

### New Capabilities

(none — `skip_specs: true` is set; this is a docs-only change with no
spec-level behaviour change)

### Modified Capabilities

(none)

## Impact

- `docs/agent-loop-checkpoints.md`: new "Known limitations" section.
- `arckit_mcp/server.py`: comment-only additions near
  `_command_doc_types` and the intake placeholder fallback.
- No API, no dependency, no test changes.
