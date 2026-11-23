# Task 2 Report — `_resolve_command_content` (full-command-relay)

Branch: `feat/full-command-relay` · Repo: `/home/terry/projects/arckit-mcp`

## What was implemented

### `arckit_mcp/server.py` — new private helper (Tasks 2.1–2.4)

Added `_resolve_command_content(command: str, source_root: Path | None) -> dict`
in the "Core logic" section (immediately after `_command_key`, before
`_intake_mandatory_gates`), plus two module-level constants:

* `_CLAUDE_PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([a-zA-Z0-9_/-]+)")`
  — the exact regex from Task 2.2 (Design D3).
* `_NO_INLINE_PREFIXES = ("scripts/", "skills/")` — first-segment prefixes
  whose tokens are never inlined (Task 2.3).

Behavior, per spec:

1. **Task 2.4** — If `source_root is None`, return
   `{"available": False, "reason": "No arc-kit source root available. Set ARCKIT_SOURCE_ROOT or install the arckit package."}`
   without raising.
2. **Task 2.1** — Resolve the command file via `_command_key(command)` (same
   convention `run_command` uses) →
   `source_root/plugins/{plugin}/commands/{name}.md`. Return
   `{"available": True, "source": <source-tree-relative posix path>, "content": <full text>, "refs": {...}, "unresolved": [...]}`.
   If the command file does not exist, return
   `{"available": False, "reason": "Command file not found: <path>"}`
   (uniform `available`-key contract so callers can branch).
3. **Task 2.2** — Scan the command body with the placeholder regex. For each
   unique token:
   * Target = `source_root/plugins/{plugin}/<token>`. The on-disk file
     typically carries a `.md` extension the placeholder does not, so the
     lookup tries the literal path first, then appends `.md`.
   * Tokens whose first segment is `references` or `templates` **and whose
     target exists on disk** are inlined into `refs` keyed by the
     placeholder-relative path **without a leading slash**
     (e.g. `references/intake-instructions`).
4. **Task 2.3** — `unresolved` list semantics:
   * `scripts/…` or `skills/…` tokens → path-only **string** (e.g.
     `scripts/validate-handoff`).
   * `references/…` or `templates/…` tokens whose target does **not**
     exist on disk → dict `{"path": <relpath>, "missing": True}`.
   * Other tokens (e.g. `schemas/…`) are intentionally neither inlined nor
     reported missing — see Known Limitations below.

### `tests/mcp/test_command_content.py` — new file (TDD-first)

Created **before** implementation. Contains the five named tests from the
task description, plus two extra coverage tests against the sibling
`/home/terry/projects/arc-kit` checkout (skipped when absent):

| Test | Pins |
|---|---|
| `test_resolve_command_content_requirements` | Task 2.1 — `available is True`, `source` relpath, `content` length > 1000, the four expected `refs` keys present and non-empty. |
| `test_resolve_command_content_refs_match_disk` | Task 2.2 — each `refs` value equals the on-disk file's full text. |
| `test_resolve_command_content_unresolved_scripts` | Task 2.3 — `scripts/validate-handoff` appears in `unresolved` (not in `refs`) for `scripts-cmd.md` and `my-cmd.md`. |
| `test_resolve_command_content_missing_file` | Task 2.3 — `{"path": "references/nope", "missing": True}` shape for a non-existent `references/` target. |
| `test_resolve_command_content_no_source_root` | Task 2.4 — `source_root=None` returns the exact unavailable dict without exception. |
| `test_resolve_command_content_requirements_real_checkout` *(extra)* | Real-checkout mirror of the two spec assertions against the actual `requirements.md` in `/home/terry/projects/arc-kit`. |
| `test_resolve_command_content_unresolved_scripts_real_checkout` *(extra)* | Real-checkout coverage for `gov-reuse.md`: the three `scripts/…` tokens land in `unresolved`, and `references/intake-instructions` + `templates/gov-reuse-template` are inlined. |

A `arc_root` fixture (in tmp_path) builds a minimal synthetic arc-kit
checkout so the five named tests run hermetically without depending on the
sibling checkout.

## Test results

```
$ python3 -m pytest tests/mcp/test_command_content.py -v
tests/mcp/test_command_content.py::test_resolve_command_content_requirements PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_refs_match_disk PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_unresolved_scripts PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_missing_file PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_no_source_root PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_requirements_real_checkout PASSED
tests/mcp/test_command_content.py::test_resolve_command_content_unresolved_scripts_real_checkout PASSED
7 passed in 0.18s

$ python3 -m pytest tests/ -q
114 passed in 0.30s   # baseline was 107 passed after Task 1; +7 = new tests
```

## Decisions

1. **`command` parameter convention** — `_resolve_command_content` expects a
   *bare* command name (`requirements`, `gov_reuse`), not an `arckit.`
   prefixed tool name, to stay consistent with `run_command` /
   `_command_key`. (Spec wording "arckit.{plugin}/{name} command key"
   refers to the *resolved* registry key, not the call convention.)
2. **`.md`-suffix fallback** — on-disk files under `references/` and
   `templates/` carry `.md`, but the placeholder tokens in the arc-kit
   command files typically omit the suffix (e.g.
   `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions`). The helper
   tries the literal path first, then appends `.md`, so both spellings
   resolve.
3. **`scripts/…` and `skills/…` tokens → path-only strings** — per Task 2.3
   these are never inlined; the relay's job is to surface them to the
   caller (e.g. "run this script in your session") without the server
   reading/executing script bodies.
4. **Unknown command (file not found)** — returns
   `{"available": False, "reason": "Command file not found: <path>"}`
   rather than raising. The `available` boolean is the uniform discriminator
   the relay will check in Task 3.
5. **Duplicate tokens are deduped** — the same placeholder may appear
   multiple times in a command body; `refs`/`unresolved` carry it once.

## Known limitations / concerns

* **`schemas/…` tokens are intentionally unclassified** — the spec only
  defines inlining for `references/` + `templates/` and path-only handling
  for `scripts/` + `skills/`. Tokens under `schemas/`, `hooks/`, or
  other first segments are neither inlined nor reported missing in
  `unresolved`. This is documented in the helper's docstring. If the relay
  later needs to surface `schemas/…` tokens (e.g. gov-reuse's
  `schemas/gov-reuse-handoff`), the caller can derive them from `content`
  directly.
* **Trailing-hyphen token capture** — brace-glob placeholders like
  `${CLAUDE_PLUGIN_ROOT}/schemas/scoring-rubrics/gov-reuse-{generic,uk-gov}`
  are captured as `schemas/scoring-rubrics/gov-reuse-` (the regex stops at
  `{`). Such tokens fall into the "unclassified" bucket above; they will
  never match a real file because the captured path is a prefix of the
  brace-expanded glob, not a real path on disk.
* **`skills/…` tokens exist in the arc-kit tree** (e.g.
  `skills/arckit-build/recipes/…` in `build.md`). The helper treats them
  identically to `scripts/` tokens (path-only string), which matches the
  spec's "scripts or skills" wording.

## Self-review notes

* Private helper (`_`-prefixed), consistent with `_intake_questions`,
  `_intake_mandatory_gates`, etc.
* No changes to `run_command` or `_instructions` (those are Task 3).
* No hand-editing of generated files (`_registry.py`, `gates.py`,
  `handoffs.py`, `intake.py`).
* Regex is exactly the spec pattern; refs keys have no leading slash.
* Test fixtures are hermetic (tmp_path) for the five named tests; the
  two real-checkout tests are `skipif`-guarded so CI without the sibling
  checkout still passes.
