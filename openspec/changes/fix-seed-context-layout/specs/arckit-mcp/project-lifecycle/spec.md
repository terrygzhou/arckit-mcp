# Capability: arckit-mcp/project-lifecycle

On-disk project layout and lifecycle for the arckit-mcp server.

## ADDED Requirements

### Requirement: Seed mints a bare numbered project directory

`arckit.seed_context` SHALL create the project directory as
`projects/{pid}/` where `{pid}` is the next free 3-digit id
(`001`, `002`, …). The project name slug SHALL NOT appear in the
directory name.

#### Scenario: Fresh seed

- **WHEN** `seed_context("Payment Gateway Modernization", …)` is called in a
  tree with no existing projects
- **THEN** `projects/001/` exists on disk
- **AND** the response has `project_id: "001"` and
  `project_dir: "projects/001"`

#### Scenario: Second seed

- **WHEN** a second `seed_context` call is made
- **THEN** `projects/002/` is minted (bare layout, no slug suffix)

### Requirement: Returned project_dir matches the read-back layout

The `project_dir` returned by `seed_context` SHALL be the directory that
`arckit.persist_artifact` and `arckit.check_gates` resolve for the same
`project_id`.

#### Scenario: Seed → persist closes a gate

- **WHEN** an agent seeds a project, then persists the `PRIN` artefact via
  `persist_artifact(project_id, "PRIN", …)`
- **AND** both calls target the layout returned by the seed
- **THEN** `check_gates` reports the `PRIN` gate closed
- **AND** no orphan slug-suffixed directory remains in `projects/`

### Requirement: Seed returns the slug as a field, not in the path

The seed response SHALL include a `slug` field carrying the
human-readable slug so callers that need it can still use it, without
encoding it into the on-disk directory name.

#### Scenario: Slug field present

- **WHEN** `seed_context("Payment Gateway Modernization", …)` succeeds
- **THEN** the response contains `slug: "payment-gateway-modernization"`
- **AND** no directory named `001-payment-gateway-modernization` exists

### Requirement: Re-seeding an existing project name is rejected

Seeding a project whose name was already seeded SHALL be rejected,
regardless of the id that would be minted. The mapping from name to id
SHALL be persisted (e.g. a sidecar metadata file inside
`projects/{pid}/`) so the check survives across server invocations.

#### Scenario: Duplicate name rejected

- **WHEN** `seed_context` is called with a name that already exists under
  any `projects/{pid}/`
- **THEN** the response is an error of the form
  `{"error": "Project '<name>' already seeded", "project_id": null}`
- **AND** no new `projects/{pid}/` directory is created

### Requirement: Seed writes GOALS.md into the bare directory

When goals or constraints are supplied, `seed_context` SHALL write
`GOALS.md` with `## Goals` / `## Constraints` sections into
`projects/{pid}/GOALS.md`.

#### Scenario: Goals written

- **WHEN** `seed_context(name, goals=["…"], constraints=["…"])` succeeds
- **THEN** `projects/{pid}/GOALS.md` contains both sections
