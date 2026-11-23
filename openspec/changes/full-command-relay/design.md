# Design: full-command-relay

## Context

See proposal. The relay currently answers "what should the agent do next"
(sequence / gates / persistence target) but not "what should the agent know"
(the command's procedural content, its template, its intake protocol, its
citation and quality rules). Layer 1 of the enforcement plan closes that gap by
making the full command content the instruction the agent receives.

The command files live in the sibling `arc-kit` checkout under
`plugins/{plugin}/commands/{name}.md` (e.g.
`plugins/arckit-claude/commands/requirements.md`). They reference shared
documents via `${CLAUDE_PLUGIN_ROOT}/references/...` and
`${CLAUDE_PLUGIN_ROOT}/templates/...` placeholders that only resolve in the
Claude slash-command runtime — an MCP-relayed agent has no such variable.

## Goals / Non-Goals

Goals:
- The relay payload's `command_content` carries the full command markdown, so
  the agent's instruction set is complete, not a one-liner.
- `${CLAUDE_PLUGIN_ROOT}/references/*` and `${CLAUDE_PLUGIN_ROOT}/templates/*`
  references in the command body are resolved to inlined content, so the
  MCP path has the same instruction surface as the slash path.
- The server locates the arc-kit source root without a hard import-time
  dependency, degrading gracefully when no source root is available.
- No change to generated files; command edits in arc-kit are reflected at the
  next relay call without a sync round-trip.

Non-goals:
- **Layer 2** (persist-artifact quality floor — rejecting shallow artifacts at
  persistence). Out of scope here; it requires arc-kit to declare template
  required-sections in a machine-readable way and is a separate change.
- **Layer 3** (command-completion handshake — `arckit_complete_command`).
  Out of scope here.
- Baking command content into a generated table (the "snapshot" sub-approach).
  Rejected; see D5.
- Enforcing that the agent *actually read* the content (observability). Layer 1
  is structural — it makes skipping costly and visible, not impossible.

## Decisions

### D1: Where the command content comes from — runtime read, not snapshot

`run_command` reads the command `.md` from the resolved source root at call
time. It does **not** bake contents into `_registry.py` or a new generated
file.

Rationale: command files change often (arc-kit is an active repo). A snapshot
in `_registry.py` would (a) bloat the generated file by ~30KB across 316
command files, and (b) go stale between syncs — the MCP server would serve
content that no longer matches the command the user just invoked. A runtime
read is always-fresh and keeps the generated-file rule ("DO NOT EDIT BY HAND,
regenerate after command changes") intact: we are *not* generating content,
we are *reading* it.

### D2: Source-root resolution order

`arckit_mcp.source_root.resolve_source_root()` returns a `Path | None`:

1. **`ARCKIT_SOURCE_ROOT` env var** — if set and the path contains
   `plugins/arckit-claude`, use it. This is the explicit, CI-friendly override.
2. **`arckit` package import** — `import arckit`, walk up from
   `arckit.__file__` to the directory containing `plugins/arckit-claude` (the
   same walk `arckit-mcp-sync._find_source_root` performs). This makes the
   common dev case (arc-kit installed / checked out alongside) work with zero
   configuration.
3. **`None`** — no source root available. The relay still works;
   `command_content` is omitted (or present with `available: false` and empty
   `content`/`refs`), and `instructions` remains the sole instruction. The
   server logs a one-time warning.

The resolution is performed **once at server startup** (module import of
`server.py`) and cached, not per-call — the source root does not change during
a server's lifetime.

### D3: Which references are inlined

For a command file `plugins/{plugin}/commands/{name}.md`, the resolver
scans the body for `${CLAUDE_PLUGIN_ROOT}/<relpath>` tokens and inlines those
that point at a file under the plugin's `references/` or `templates/`
directories. Specifically, Layer 1 inlines the four shared references that
appear across commands:

- `references/intake-instructions.md`
- `references/quality-checklist.md`
- `references/citation-instructions.md`
- `references/bmm-reference.md` (only when a command references it)

and any `${CLAUDE_PLUGIN_ROOT}/templates/{name}.md` the command names.

References that point at `${CLAUDE_PLUGIN_ROOT}/scripts/...` or
`${CLAUDE_PLUGIN_ROOT}/skills/...` are **not** inlined — those are executable
or skill assets, not instruction documents. They are listed in
`command_content.unresolved` so the agent knows they exist but is not given
their (irrelevant-to-instruction) content.

The `refs` object keys are the placeholder-relative path (e.g.
`"references/intake-instructions"`) and values are the file's full text. A
reference whose file does not exist is omitted from `refs` and added to
`unresolved` with a `missing: true` flag.

### D4: Graceful degradation when no source root

When `resolve_source_root()` returns `None`, `run_command` still returns the
existing payload (`id`, `project_id`, `command`, `doc_type`, `intake`,
`instructions`, `gates`, `gate_blocked`) unchanged, plus:

```json
"command_content": {
  "available": false,
  "reason": "No arc-kit source root available. Set ARCKIT_SOURCE_ROOT or install the arckit package."
}
```

This preserves the existing behaviour for clients that do not have the
arc-kit checkout (e.g. a client that installed only `arckit-mcp` via pip
without the `[dev]` extra). The `instructions` one-liner remains the sole
instruction in that case — same as today. No error is raised.

### D5: Why not a snapshot in `_registry.py`

The alternative (option 2a from the impact analysis) was to extend
`generate-mcp-registry.py` to embed `COMMAND_CONTENT: dict` into
`_registry.py`. Rejected because:

- **Staleness**: command files change frequently; a snapshot goes stale between
  syncs and the server would serve outdated instruction content.
- **Size**: ~316 command files × ~10KB average = ~3MB added to a generated
  file that is meant to be a compact table.
- **Generated-file rule**: the rule is "regenerate after arc-kit command
  changes." Baking content into `_registry.py` would make every command edit
  require a regeneration + push cycle, which is exactly the overhead a runtime
  read avoids.
- **The generated tables are membership tables** (`DOC_TYPES`, `GATE_TIERS`,
  `HANDOFFS`, `INTAKE`) — they map names to codes/relationships. Command
  *content* is not a membership fact; it is the document itself. Reading it
  at runtime is the natural fit.

### D6: `instructions` field disposition

The existing `instructions` one-liner is **retained**, not removed. It is now
positioned as a *summary* alongside `command_content.content` (the full
instruction). This keeps the payload backward-compatible for clients that read
`instructions` only. The one-liner's text is lightly reframed to point at
`command_content.content` as the authoritative instruction:

> "Execute the full command in `command_content.content` to produce {codes}
> artefact(s) for project {project_id}. Save each artefact to
> projects/{project_id}/ via arckit.persist_artifact."

## Risks / Trade-offs

- **Payload size**: a command file plus its inlined references can be ~20–40KB
  of markdown. This is a deliberate cost — it is the instruction the agent was
  missing. Clients that find the payload too large can rely on the `source`
  path to read the file themselves (the `content_source` pointer, option 1, is
  effectively subsumed: `command_content.source` *is* that pointer).
- **Source-root coupling**: the server now has a runtime dependency on the
  arc-kit checkout being available. Mitigated by D4's graceful degradation —
  without a source root, the relay behaves exactly as it does today.
- **`CLAUDE_PLUGIN_ROOT` resolution is heuristic**: we match the placeholder
  pattern rather than a full template-engine. If a command references a path
  we do not recognise as a `references/` or `templates/` document, it lands in
  `unresolved`. This is acceptable: the four shared references cover the
  instruction surface; exotic references degrade to "listed but not inlined."
- **No enforcement that the agent read the content**: Layer 1 is structural.
  It makes a shallow artifact require *deliberately discarding* four
  instruction documents. It does not detect the discard. That detection is
  Layer 2 (persist quality floor) and is explicitly out of scope.

## Open Questions

- **Should `command_content.refs` include the command's named template even
  when the command does not explicitly reference it by path** (e.g.
  `requirements.md` references
  `${CLAUDE_PLUGIN_ROOT}/templates/requirements-template.md`, but some commands
  name their template only in prose)? Decision deferred to implementation:
  the resolver will first do the mechanical placeholder scan (D3); if a command
  names a template only in prose, that template is *not* inlined in Layer 1
  and is noted in `unresolved`. A follow-up can add a command→template map.
- **Max payload guard**: is there a hard cap on `command_content` size we
  should enforce (e.g. truncate the largest command, `jsp-936.md` at ~35KB)?
  Decision deferred: no cap in Layer 1; if a client reports payload-size
  issues, add a cap + a `truncated: true` flag in a follow-up.
