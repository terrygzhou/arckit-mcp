# Tasks: document-drift-limitations

## 1. Documentation

- [ ] 1.1 Add a "Known limitations" section to
  `docs/agent-loop-checkpoints.md` under/after §1.2 Findings, recording
  F3 (hand-maintained `_command_doc_types` mapping, cross-repo drift risk)
  and the two deferred options:
  (A) generate a `COMMAND_DOC_TYPES` table into `arckit_mcp/_registry.py`
  from the same source as the other generated tables (preferred);
  (B) add a CI check diffing `name_map`/`overlay_map` against the
  registry and failing on drift. Verify: section present and readable.
- [ ] 1.2 Note in that section that F4 is by-design, covered by
  `test_relay_never_returns_empty_intake` (the placeholder floor).
  Verify: section present.

## 2. Code comments (no behaviour change)

- [ ] 2.1 Add a short comment above `server._command_doc_types`
  (server.py ~line 412+) stating the mapping is hand-maintained,
  references the F3 finding + the "Known limitations" section, and names
  the two deferred options. Verify: comment present, no diff to
  executable code.
- [ ] 2.2 Add a short comment at the placeholder-intake fallback (where
  `no-static-questions` codes degrade to one placeholder question)
  stating the non-empty floor is intentional by-design (F4) and pinned by
  `test_relay_never_returns_empty_intake`. Verify: comment present.

## 3. Verification & follow-up

- [ ] 3.1 Run `python -m pytest tests/ -q`. Verify: full suite green, no
  behaviour change from the comment additions.
- [ ] 3.2 File (or record where to file) the F3 follow-up ticket and cite
  its id in the "Known limitations" section. Verify: ticket id referenced
  in the doc.
