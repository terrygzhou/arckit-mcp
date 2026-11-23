# Proposal: full-command-relay

Source: gap analysis of the ArcKit prompt-relay model — the MCP path produces
simpler artifacts than the slash-command path because the relay payload carries
only *governance* metadata (gates, intake state, persistence target) and a
deliberately terse `instructions` one-liner. The client agent never receives the
command's full procedural markdown through MCP, so it has no instruction set to
follow beyond "run the command and persist." Empirical evidence: a 4-line
`ARC-002-PRIN-v1.0.md` produced through the MCP path versus the 1026-line
`requirements-template.md` the slash-command path hands the model.

This is **Layer 1** of the enforcement plan: make the full command content the
*sole instruction* the agent has, so producing a shallow artifact requires
deliberately discarding a complete, visible instruction set rather than
defaulting to a terse one-liner.

## Why

Today `run_command` returns:

```
{
  "id", "project_id", "command", "doc_type",
  "intake",          // placeholder or static questions
  "instructions",    // 2-sentence stub: "Run the X command ... Save each artefact ..."
  "gates", "gate_blocked"
}
```

The `instructions` field is the *only* instruction the agent receives, and it is
deliberately minimal (`server._instructions`, ~2 sentences). The command's full
markdown — its role preamble, intake protocol, template reference, quality
checklist, citation rules — never reaches the agent through the MCP path. The
agent is left to "run the command in your session," which, outside a
slash-command runtime, means it has no command to run: it only has the
one-liner. That is the root cause of simpler artifacts.

The fix is to invert the contract: the relay payload's instruction *is* the full
command content. There is no shorter alternative to fall back to, because the
full markdown is what the tool hands the agent. This does not require the agent
to load the command "through some other means" (system prompt, file read,
slash command) — the MCP call itself is the delivery mechanism.

## What Changes

- **New payload field `command_content`** on every `arckit.{command}` relay
  response, carrying the full command markdown plus its resolved reference
  documents:
  - `command_content.content` — the full text of the command's `.md` file.
  - `command_content.source` — the relative path of that command file (for
    traceability / the agent's own read).
  - `command_content.refs` — an object mapping each `${CLAUDE_PLUGIN_ROOT}/...`
    reference the command body points at (template, intake-instructions,
    citation-instructions, quality-checklist) to that referenced file's full
    content. This resolves the `CLAUDE_PLUGIN_ROOT` placeholder that only
    exists in the slash-command runtime, so the MCP-relayed agent has the
    same instruction surface the slash path does.
- **Source-root configuration** for the server to locate the arc-kit checkout:
  the server must read command files and templates at call time. A new
  `arckit_mcp.source_root` module exposes `resolve_source_root()`, which
  honours (in order) an explicit `ARCKIT_SOURCE_ROOT` env var, the
  `arckit-mcp-sync --source-root` resolution path (import `arckit` package and
  walk up to `plugins/arckit-claude`), and a fallback to "no source root
  available" (relay still works, `command_content` is omitted or flagged
  unavailable — see Design D4).
- **`server.run_command`** populates `command_content` by reading the command
  file from the resolved source root and inlining referenced files. The existing
  `instructions` one-liner is retained (backward-compatible) but is now a
  *summary* alongside the full content, not the sole instruction.
- **Spec delta** for the existing `arckit-mcp/command-relay` capability
  (established by `fix-seed-context-layout`) capturing the `command_content`
  field and the source-root resolution rule as an extension of the relay
  payload contract.
- **No change to generated files** (`_registry.py`, `gates.py`, `handoffs.py`,
  `intake.py`). The command file *contents* are read at runtime from the source
  tree, not baked into a generated table — so command edits in arc-kit are
  reflected immediately on the next relay call without a sync round-trip.
  (This is the "2b / runtime read" sub-approach; the trade-off vs. a snapshot
  is recorded in Design D5.)
- **Tests**: new `tests/mcp/test_command_content.py` asserting that
  (a) the relay response carries `command_content.content` matching the command
  file, (b) `refs` resolves the known shared references, (c) the behaviour when
  no source root is available is graceful (field omitted / `available: false`),
  and (d) the existing `test_relay_never_returns_empty_intake` and
  `test_no_write_path_for_answers` remain green.

## Capabilities

### New Capabilities

(none — the command-relay capability already exists, established by
`fix-seed-context-layout`, which added the top-level `project_id` key and the
never-empty `intake` contract to `arckit-mcp/command-relay`)

### Modified Capabilities

- `arckit-mcp/command-relay` (existing): this change extends the relay payload
  contract by adding a `command_content` object (full command markdown +
  resolved `CLAUDE_PLUGIN_ROOT` references) to every `arckit.{command}` relay
  response, and adds the source-root resolution rule (`ARCKIT_SOURCE_ROOT`
  env var → `arckit` package import → graceful-absence fallback). It also
  reframes the `instructions` field to name `command_content.content` as the
  authoritative instruction when available.

## Impact

- `arckit_mcp/server.py`: `run_command` (add `command_content`), `_instructions`
  (reframe as summary), new helper `_resolve_command_content`.
- `arckit_mcp/source_root.py` (new): `resolve_source_root()` + the
  `ARCKIT_SOURCE_ROOT` env-var contract.
- `arckit_mcp/__init__.py`: export `resolve_source_root` (optional).
- `tests/mcp/test_command_content.py` (new): the four assertions above.
- `docs/agent-loop-checkpoints.md`: add a note that the relay now delivers full
  command content (Layer 1 of the enforcement plan), closing the
  "agent never receives command markdown" gap.
- External consumers: clients that read only the existing fields
  (`id`, `project_id`, `command`, `doc_type`, `intake`, `instructions`,
  `gates`, `gate_blocked`) are unaffected — `command_content` is additive.
  Rollback surface is limited to removing the `command_content` block from
  `run_command` and deleting `source_root.py`.
