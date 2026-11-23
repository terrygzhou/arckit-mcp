# Capability: arckit-mcp/command-relay

Payload contract for the per-command MCP relay tools
(`arckit.{command}`). This change extends the contract established by
`fix-seed-context-layout` (top-level `project_id`, never-empty intake) by
adding the full command content to the relay payload.

## ADDED Requirements

### Requirement: The relay response carries full command content

Every `arckit.{command}` relay response SHALL include a top-level
`command_content` object that carries the full markdown of the command the
agent is being asked to execute, so that the agent's instruction set is the
complete procedural content rather than a summary one-liner.

The `command_content` object SHALL contain:

- `available` (boolean) — whether the command file could be located and read.
- `source` (string, when `available` is true) — the source-tree-relative path
  of the command file (e.g.
  `plugins/arckit-claude/commands/requirements.md`), given so a client that
  prefers to read the file itself has a pointer.
- `content` (string, when `available` is true) — the full text of the command
  file, unmodified.
- `refs` (object, when `available` is true) — a map from a
  `CLAUDE_PLUGIN_ROOT`-relative reference path (no leading slash) to the full
  text of the referenced file, for references the command body points at
  under the plugin's `references/` or `templates/` directories.
- `unresolved` (array, when `available` is true) — reference paths that could
  not be inlined: executable/skill assets (e.g. `scripts/...`, `skills/...`)
  listed by path only, and missing files listed as
  `{"path": ..., "missing": true}`.

#### Scenario: Relay for `requirements` carries the full command markdown

- **WHEN** the agent calls `arckit.requirements` with a valid `project_id` and
  an arc-kit source root is available
- **THEN** the response contains `command_content.available: true`,
  `command_content.source: "plugins/arckit-claude/commands/requirements.md"`,
  and `command_content.content` equal to the full text of that command file
  (length in the thousands, not a stub)

#### Scenario: Shared references are inlined

- **WHEN** the command body references
  `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` and
  `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md`
- **THEN** `command_content.refs` contains keys
  `references/intake-instructions` and `references/quality-checklist`, each
  mapped to the full text of the corresponding on-disk file

#### Scenario: Script and skill references are not inlined

- **WHEN** the command body references
  `${CLAUDE_PLUGIN_ROOT}/scripts/validate-handoff`
- **THEN** that path appears in `command_content.unresolved` and does NOT
  appear as a key in `command_content.refs`

### Requirement: The server resolves the arc-kit source root

The server SHALL locate the arc-kit checkout (the source root that contains
`plugins/arckit-claude`) by trying, in order: (1) the `ARCKIT_SOURCE_ROOT`
environment variable, if set and pointing at a directory containing
`plugins/arckit-claude`; (2) the `arckit` Python package's own location,
walking up from `arckit.__file__` to the directory that contains
`plugins/arckit-claude`; (3) failing both, "no source root available." The
resolution SHALL be performed once at server startup and cached, not
recomputed per relay call.

#### Scenario: Explicit env var wins

- **WHEN** `ARCKIT_SOURCE_ROOT` is set to a directory containing
  `plugins/arckit-claude`
- **THEN** `resolve_source_root()` returns that directory, regardless of
  whether the `arckit` package is importable

#### Scenario: Package-import fallback

- **WHEN** `ARCKIT_SOURCE_ROOT` is unset but the `arckit` package is
  importable and its file location sits inside an arc-kit checkout
- **THEN** `resolve_source_root()` returns the checkout root (the ancestor
  directory that contains `plugins/arckit-claude`)

#### Scenario: Resolution is cached at startup

- **WHEN** `resolve_source_root()` is called more than once during a server's
  lifetime
- **THEN** the underlying import/walk is performed only once and subsequent
  calls return the cached result

### Requirement: The relay degrades gracefully when no source root is available

When no arc-kit source root can be resolved, the relay response SHALL still
return the pre-existing payload fields (`id`, `project_id`, `command`,
`doc_type`, `intake`, `instructions`, `gates`, `gate_blocked`) unchanged, and
SHALL set `command_content.available` to `false` with a `reason` explaining how
to provide a source root. The server SHALL NOT raise an error or fail the
relay call in this case.

#### Scenario: No source root yields a graceful payload

- **WHEN** neither `ARCKIT_SOURCE_ROOT` nor an importable `arckit` package is
  available and the agent calls `arckit.requirements`
- **THEN** the response contains all pre-existing payload fields with their
  usual values, `command_content.available: false`, and
  `command_content.reason` naming `ARCKIT_SOURCE_ROOT` or the `arckit`
  package as the remedy, and no exception is raised

## MODIFIED Requirements

### Requirement: Relay instructions name the authoritative instruction source

The `instructions` field of the relay response SHALL direct the agent to the
authoritative instruction content. When `command_content.available` is true,
`instructions` SHALL reference `command_content.content` as the instruction to
execute, in addition to naming the doc-type code(s) to produce and the
`arckit.persist_artifact` persistence target into `projects/{project_id}/`.
When `command_content.available` is false (no source root), `instructions`
SHALL remain the sole instruction and retain its pre-change wording of naming
the doc-type code(s) and persistence target. The field is never empty.

#### Scenario: Instructions point at the full content when available

- **WHEN** `command_content.available` is true
- **THEN** the `instructions` text references `command_content.content` as
  the instruction to execute, in addition to naming the doc-type code(s) and
  the `arckit.persist_artifact` persistence target

#### Scenario: Instructions remain self-sufficient when unavailable

- **WHEN** `command_content.available` is false
- **THEN** the `instructions` text still names the doc-type code(s) to produce
  and the `arckit.persist_artifact` persistence target, and is non-empty
