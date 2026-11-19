# Repository Guidelines

## Project Structure & Module Organization

`arckit_mcp/` is a Python MCP server (stdio) that exposes the ArcKit governance harness as tools: `server.py` is the entry point, `__main__.py` supports `python3 -m arckit_mcp`, and `sync.py` regenerates derived tables. `_registry.py`, `gates.py`, `handoffs.py`, and `intake.py` are GENERATED — each begins with a "DO NOT EDIT BY HAND" docstring. Tests live in `tests/mcp/` (`conftest.py` plus per-area files), a JSON-RPC-over-stdio harness is `scripts/dev/arckit-mcp-call.py`, docs are in `docs/`, and in-flight changes are tracked under `openspec/changes/`.

## Build, Test, and Development Commands

- `python3 -m pytest tests/ -q` — baseline 87 passed (run from repo root; the README's `python -m pytest` assumes the shared venv at `~/.local/share/arckit-mcp/.venv`).
- `arckit-mcp-sync` (or `arckit-mcp-sync --source-root ~/projects/arc-kit`) regenerates `_registry.py`, `gates.py`, `handoffs.py`; the console script comes from `pyproject.toml [project.scripts]` and needs the `arckit` package or `--source-root`.
- Regenerate `intake.py`: `ARCKIT_MCP_ROOT=$PWD python3 ../arc-kit/scripts/generate-mcp-intake.py` (sibling arc-kit checkout).
- Boot test: `arckit-mcp` or `python3 -m arckit_mcp` (stdio MCP server).
- Single tool call: `python3 scripts/dev/arckit-mcp-call.py TOOL '<args-json>'` (resolves `$ARCKIT_MCP_BIN` → repo `.venv` → PATH).
- Install: `pip install -e ~/projects/arckit-mcp` (`[dev]` extra pulls `arckit` + `pytest`).

## Generated-Files Rule

Never hand-edit `_registry.py`, `gates.py`, `handoffs.py`, or `intake.py` (each says DO NOT EDIT BY HAND); regenerate after arc-kit command changes instead. The hand-maintained `name_map`/`overlay_map` in `server.py` can silently drift when arc-kit adds a doc-type/command (known limitation F3, documented in `docs/agent-loop-checkpoints.md` "Known limitations" and `openspec/changes/document-drift-limitations`); follow-ups: auto-generate a `COMMAND_DOC_TYPES` table (option A) or a CI drift check (option B). F4 — placeholder intake for no-static-questions codes — is by design and pinned by `test_relay_never_returns_empty_intake`.

## Testing Guidelines

Baseline invariants (`docs/agent-loop-checkpoints-remediation.md` §3): 87 passed; `test_relay_never_returns_empty_intake` and `test_no_write_path_for_answers` must stay green. `test_seed_and_persist_share_layout` pins the F1 fix (seed mints bare `projects/{pid}/` + `.meta` sidecar; slug is a separate payload field; duplicate names rejected — see `openspec/changes/fix-seed-context-layout`, all tasks checked). `test_skill_install.py` pins the installer's skill registration step (extracted to `scripts/install-skill.sh` — single source of truth shared by install.sh, install.ps1, and the test suite). Keep tests in `tests/mcp/` near the affected area.

## Commit & Pull Request Guidelines

Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:` (same style as the arc-kit repo). Note `openspec/` change artifacts for larger changes; PRs should list validation commands (minimum `python3 -m pytest tests/ -q`) and link the `openspec/changes/<id>` tracking the work.

## Security & Configuration Tips

No secrets or `.env` files in the repo. Generated outputs under `arckit_mcp/` are rebuildable — don't "fix" them by hand. `arckit-mcp-sync` without `--source-root` assumes the `arckit` package import; point `--source-root` at the arc-kit checkout when developing against it.
