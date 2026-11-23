# Relationship to [terrygzhou/arc-kit](https://github.com/terrygzhou/arc-kit)

arckit-mcp is a **standalone consumer** of the arc-kit (architecture-governance
harness) project. It vendors **generated data files** that arc-kit's generator
scripts produce from its `plugins/` tree. The coupling is one-directional:
arc-kit owns the generators and their sources of truth; arckit-mcp imports the
outputs.

## 1. Data dependency (generated files, one-way)

`arckit_mcp/_registry.py`, `gates.py`, `handoffs.py`, `intake.py`, and the
whole `arckit_mcp/frameworks/` package are generated **from** arc-kit sources,
not written by hand. Each carries a "DO NOT EDIT BY HAND" header.

| arckit-mcp file | arc-kit generator | arc-kit source of truth |
|---|---|---|
| `arckit_mcp/_registry.py` | `scripts/generate-mcp-registry.py` | `plugins/arckit-claude/config/doc-types.mjs` |
| `arckit_mcp/gates.py` | `scripts/generate-mcp-gates.py` | command markdown under `plugins/*/commands/` |
| `arckit_mcp/handoffs.py` | `scripts/generate-mcp-handoffs.py` | command markdown under `plugins/*/commands/` |
| `arckit_mcp/intake.py` | `scripts/generate-mcp-intake.py` | `plugins/*/templates/*.md` (the `## Intake Interview Questions` blocks) |
| `arckit_mcp/frameworks/*` | `scripts/generate-mcp-evidence.py` | `plugins/*/mcp-evidence.json` manifests (per-framework tool groups + embedded schemas) |

`_registry.py` exports `DOC_TYPES`, `SUBDIR_MAP`, `MULTI_INSTANCE_TYPES`, and
`KNOWN_TYPES`. `gates.py` exports `GATE_TIERS`. `handoffs.py` exports
`HANDOFFS`. `intake.py` exports `INTAKE`, `COVERAGE`, and `PARSER_NOTES`.
`frameworks/__init__.py` exports `FRAMEWORK_TOOLS`, `FRAMEWORK_MODULES`, and
the embedded `SCHEMAS` dict (the union of every JSON schema referenced by any
`mcp-evidence.json`, so the server works from any install location without
touching the plugin tree).

## 2. Packaging dependency (optional, dev-only)

`pyproject.toml`'s `[project.optional-dependencies]` `dev` extra pulls in
`arckit` (the arc-kit CLI package, currently v6.12.0) plus `pytest`. The
`arckit` import is only used by `arckit_mcp/sync.py` to **auto-discover** the
arc-kit source tree. It is **not required to run the MCP server** — the
generated files are committed, so the server is self-contained.

## 3. Dev workflow coupling

`arckit_mcp/sync.py` (console script `arckit-mcp-sync`) is a thin wrapper that
runs arc-kit's three single-file generators against the local
`arckit_mcp/` directory:

```bash
arckit-mcp-sync                              # auto-discovers the installed arckit package
arckit-mcp-sync --source-root ~/projects/arc-kit   # or point at a sibling checkout
```

`intake.py` is regenerated directly (it is not wrapped by `sync.py`):

```bash
ARCKIT_MCP_ROOT=$PWD python3 ../arc-kit/scripts/generate-mcp-intake.py
```

arc-kit's generators default to writing into the **sibling**
`../arckit-mcp/arckit_mcp/` directory (default output path in each generator is
`REPO_ROOT.parent / "arckit-mcp"`); the `ARCKIT_MCP_ROOT` env var or a CLI arg
overrides the output location, so regeneration also works for non-sibling
checkouts.

## 4. When to regenerate (and what triggers it)

Regenerate the generated files **whenever the arc-kit source of truth
changes**, i.e. after any commit on the arc-kit side that touches one of
the tables' inputs:

| Trigger (arc-kit-side change) | File to regenerate | Command |
|---|---|---|
| `plugins/arckit-claude/config/doc-types.mjs` (add/remove/rename a doc-type, or its category/regime/subdir) | `_registry.py` | `arckit-mcp-sync` |
| Command markdown under `plugins/*/commands/` (gate tier of a prerequisite, handoff edges, MANDATORY-tier prerequisite inputs) | `gates.py` | `arckit-mcp-sync` |
| Command markdown under `plugins/*/commands/` (handoff edges / next-step graph) | `handoffs.py` | `arckit-mcp-sync` |
| `## Intake Interview Questions` blocks in `plugins/*/templates/*.md` or `plugins/arckit-claude/plugins/**/templates/*.md` | `intake.py` | `ARCKIT_MCP_ROOT=$PWD python3 ../arc-kit/scripts/generate-mcp-intake.py` |
| Any `plugins/*/mcp-evidence.json` manifest (add a framework tool, change its JSON-schema arguments, add a referenced schema file) | `frameworks/` (whole package + `SCHEMAS.json`) | `arckit-mcp-sync` |
| Add a new plugin overlay that ships commands / doc-types / templates / manifest | All of the above | `arckit-mcp-sync` + the intake generator |

In practice the trigger is a **diff on the arc-kit side** — pull the
upstream `arc-kit` repo, run the generators, and diff `arckit_mcp/` before
committing. The generated files are committed, so any arc-kit command
change that is not re-generated will silently diverge from what the MCP
server reports. A CI drift check (option B under §5) is the planned
follow-up that makes this drift *detectable* automatically.

Also regenerate when:
- you bump the `arckit` dev-extra (`pip install -e .[dev]` pulls a newer
  `arckit-cli`) and want the generated tables to match the installed
  package's source tree.
- you are developing against a local `arc-kit` checkout rather than the
  installed package — pass `--source-root` to `arckit-mcp-sync` or
  `ARCKIT_MCP_ROOT` to the intake generator so they point at your checkout
  instead of the installed package.

## 5. Runtime: no hard dependency on the `arckit` package

`arckit_mcp/server.py` imports only from
`arckit_mcp.{_registry,gates,handoffs,intake,frameworks}` and
`mcp.server.fastmcp` — **no runtime import of the `arckit` package**. The
generated tables are self-contained (schemas embedded in `SCHEMAS.json`), so
the MCP server boots from any install location without an arc-kit checkout or
the `arckit` package installed.

## 6. Drift risks / known limitations

Documented in `docs/agent-loop-checkpoints.md` ("Known limitations") and
`openspec/changes/document-drift-limitations/`:

- **F3** — the hand-maintained `name_map` / `overlay_map` in `server.py` can
  silently drift when arc-kit adds a doc-type or command, because unlike
  the table files they are *not* regenerated (see §4 for the triggers that
  *do* regenerate the table files). Follow-ups: auto-generate a
  `COMMAND_DOC_TYPES` table (option A) or a CI drift check (option B).
- **F4** — placeholder intake for no-static-questions codes is by design,
  pinned by `test_relay_never_returns_empty_intake`.

## Diagram

```
terrygzhou/arc-kit (source of truth)
├── plugins/arckit-claude/config/doc-types.mjs ────┐
├── plugins/*/commands/*.md ────────────────────────┤
├── plugins/*/templates/*.md ───────────────────────┤
├── plugins/*/mcp-evidence.json ────────────────────┤
├── scripts/generate-mcp-*.py  (5 generators) ──────┘
│
│   run via arckit-mcp-sync (wrapped) or directly (intake)
▼
terrygzhou/arckit-mcp (this repo)
├── arckit_mcp/_registry.py, gates.py, handoffs.py, intake.py   ← generated, committed
├── arckit_mcp/frameworks/ (agent, it4it, oaa, togaf + SCHEMAS.json) ← generated, committed
├── arckit_mcp/server.py   ← hand-maintained MCP entry; imports the generated tables
└── arckit_mcp/sync.py     ← thin wrapper around arc-kit's generators (optional `arckit` pkg)
```

## Commit-style contract

arckit-mcp follows the same conventional-commit style as arc-kit
(`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`), and PRs should
reference `openspec/changes/<id>` for larger changes (see `AGENTS.md`).
