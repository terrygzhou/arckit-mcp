# Capability: arckit-mcp/command-relay

Payload contract for the per-command MCP relay tools
(`arckit.{command}`).

## ADDED Requirements

### Requirement: Relay payload carries a top-level project_id

Every `arckit.{command}` relay response SHALL include a top-level
`project_id` key equal to the id the call was made with, alongside the
existing `id` (`ARC-{project_id}`) field. This SHALL match the shape of
the `check_gates` response, which already carries `project_id`.

#### Scenario: Relay includes project_id

- **WHEN** `arckit.strategy(project_id="001")` is relayed
- **THEN** the response dict contains `"project_id": "001"`
- **AND** `"id": "ARC-001"`

### Requirement: Relay intake is never empty

For any command whose doc-type has no static intake questions, the relay
SHALL return at least one placeholder question. No relay of any of the
~101 command tools SHALL return an empty `intake` list.

#### Scenario: Placeholder floor

- **WHEN** a relay for a `no-static-questions` code (e.g. `strategy`)
  is called
- **THEN** `intake` contains ≥ 1 question
