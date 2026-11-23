# Tasks: full-command-relay

## 1. Source-root resolution

- [ ] 1.1 Create `arckit_mcp/source_root.py` with
  `resolve_source_root() -> Path | None` implementing the three-tier
  resolution from Design D2: (a) `ARCKIT_SOURCE_ROOT` env var if set and
  containing `plugins/arckit-claude`; (b) `import arckit` + walk up from
  `arckit.__file__` to the dir containing `plugins/arckit-claude` (mirror
  `arckit_mcp/sync.py::_find_source_root`); (c) `None` otherwise. Verify:
  `python3 -c "from arckit_mcp.source_root import resolve_source_root;
  print(resolve_source_root())"` returns the sibling checkout path when
  `arckit` is importable, and `None` when it is not.
- [ ] 1.2 Export `resolve_source_root` from `arckit_mcp/__init__.py` so it is
  importable as `from arckit_mcp import resolve_source_root`. Verify: the
  import succeeds and the function is callable.
- [ ] 1.3 Cache the resolution result at module import of `source_root.py`
  (a module-level `_RESOLVED_ROOT: Path | None | _UNSET` sentinel) so it is
  computed once, not per call. Verify: calling `resolve_source_root()` twice
  returns the same object without re-running the import/walk.

## 2. Command-content resolution helper

- [ ] 2.1 Add `_resolve_command_content(command: str, source_root: Path) ->
  dict` to `server.py`. It maps the `arckit.{plugin}/{name}` key (via
  `_command_key`) to the command file path
  `source_root/plugins/{plugin}/commands/{name}.md`, reads the full text, and
  returns `{"available": True, "source": "<relpath>", "content": "<text>",
  "refs": {...}, "unresolved": [...]}`. Verify: for `requirements`, the
  returned `source` is `plugins/arckit-claude/commands/requirements.md` and
  `content` is non-empty and matches the file on disk.
- [ ] 2.2 Implement the reference scan (Design D3): regex-match
  `\$\{CLAUDE_PLUGIN_ROOT\}/([a-zA-Z0-9_/-]+)` in the command body; for each
  token whose target lives under the plugin's `references/` or `templates/`,
  inline the file's full text into `refs` (keyed by the placeholder-relative
  path, no leading slash). Verify: for `requirements`, `refs` contains
  `references/intake-instructions`, `references/quality-checklist`, and
  `references/citation-instructions` (the three the command references), each
  with non-empty text matching the on-disk file.
- [ ] 2.3 Add `unresolved`: tokens that point at `scripts/` or `skills/` are
  listed here (path only, no inlined content); tokens whose target file does
  not exist are listed with `{"path": ..., "missing": true}`. Verify: for a
  command that invokes `${CLAUDE_PLUGIN_ROOT}/scripts/validate-handoff`, the
  token appears in `unresolved`, not in `refs`.
- [ ] 2.4 Handle the no-source-root case: when `source_root is None`,
  `_resolve_command_content` returns
  `{"available": False, "reason": "No arc-kit source root available. Set
  ARCKIT_SOURCE_ROOT or install the arckit package."}` and raises nothing.
  Verify: calling it with `None` returns that dict.

## 3. Wire into `run_command`

- [ ] 3.1 In `run_command`, call `_resolve_command_content` (using the cached
  `resolve_source_root()` from task 1.3) and add its result as the
  `command_content` key on the returned payload. The existing keys
  (`id`, `project_id`, `command`, `doc_type`, `intake`, `instructions`,
  `gates`, `gate_blocked`) are unchanged. Verify:
  `arckit-mcp-call arckit.requirements '{"project_id":"001"}'` shows
  `command_content.available == true` and `command_content.content` is the
  full command markdown.
- [ ] 3.2 Reframe `_instructions` (Design D6) so the one-liner points at
  `command_content.content` as the authoritative instruction. Verify: the
  returned `instructions` text mentions `command_content.content` and still
  names the doc-type codes and `arckit.persist_artifact`.
- [ ] 3.3 Confirm backward compatibility: a client reading only the pre-
  existing fields sees them unchanged in shape and meaning. Verify: run the
  existing relay tests (below) and confirm the only *new* top-level key is
  `command_content`.

## 4. Tests

- [ ] 4.1 New `tests/mcp/test_command_content.py`. Test
  `test_relay_includes_command_content`: seed a project, call
  `arckit.requirements`, assert `command_content.available is True`,
  `command_content.source == "plugins/arckit-claude/commands/requirements.md"`,
  and `len(command_content.content) > 1000` (the command is a full document,
  not a stub). Verify: passes against the sibling arc-kit checkout.
- [ ] 4.2 Test `test_relay_inlines_shared_references`: assert
  `command_content.refs` contains `references/intake-instructions` and
  `references/quality-checklist` with non-empty values, and that each value
  equals the on-disk file's text. Verify: passes.
- [ ] 4.3 Test `test_relay_lists_unresolved_scripts`: assert a command that
  invokes a `${CLAUDE_PLUGIN_ROOT}/scripts/...` path lists that path in
  `command_content.unresolved` and does *not* inline it into `refs`. Verify:
  passes.
- [ ] 4.4 Test `test_relay_graceful_when_no_source_root`: monkeypatch
  `resolve_source_root` to return `None` (or set `ARCKIT_SOURCE_ROOT` to a
  non-existent path and clear the `arckit` import), call a command, assert
  `command_content.available is False` and that the existing payload keys are
  all still present and correct. Verify: passes, and `instructions` remains
  the sole instruction in this branch.
- [ ] 4.5 Regression: run `python3 -m pytest tests/mcp/test_agent_loop.py
  tests/mcp/test_intake.py -q` and confirm
  `test_relay_never_returns_empty_intake` and `test_no_write_path_for_answers`
  remain green. Verify: baseline still holds (the `command_content` addition
  does not disturb the intake or write-path contracts).

## 5. Docs

- [ ] 5.1 Add a short section to `docs/agent-loop-checkpoints.md` noting that
  Layer 1 (full-command-relay) is in place: the relay now carries the full
  command markdown + resolved references, closing the "agent never receives
  command markdown" gap. Note that Layers 2 (persist quality floor) and 3
  (completion handshake) are separate changes. Verify: the doc reads
  coherently with the existing F3/F4/F5 "Known limitations" section.

## 6. Validation

- [ ] 6.1 `python3 -m pytest tests/ -q` — full suite green (baseline 87 passed
  + the new command-content tests). Verify: no new failures.
- [ ] 6.2 Boot test: `python3 -m arckit_mcp` starts the stdio server without
  import errors (the new `source_root.py` module and the `command_content`
  wiring must not break startup). Verify: the server boots and the existing
  tools are listed.
