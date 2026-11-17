# Intake discipline

## One-question-at-a-time

The relay response's `intake` field is a **list** of questions, but the
agent interviews the host **one question at a time**:

1. Present `intake[0]` (question + hint) to the user.
2. Record the answer; present `intake[1]`; and so on.
3. Answers are skippable — a skipped question renders `TBD` in the
   generated artefact and never contributes to `gate_blocked`.
4. After the interview, generate the document and call
   `arckit.persist_artifact(project_id, doc_type_code, content)`.

The interview is the **host's** job — the agent drives it, the host
answers. The agent never fabricates answers.

## Sole-persister rule

The MCP server is **read/seed only** for intake answers. The
`arckit.persist_intake` tool reads saved answer files but **never
writes** — there is no write path for answers through the server
(pinned by `test_no_write_path_for_answers` in
`tests/mcp/test_intake.py`). The interview owner (Agent A, or the
human user) is the sole persister of answers into
`.arckit/intake/{command-hyphenated}.json`.

This means:

- If the user has pre-answered questions for a command (e.g. a bulk
  build), `arckit.persist_intake(project_id, command)` returns
  `{"found": true, "answers": {...}, "path": ".arckit/intake/…", …}`
  and the agent can prefill the interview.
- If no saved file exists, the response is
  `{"found": false, "answers": null}` — no error; the agent proceeds
  with a fresh interview.

## `.arckit/intake/` layout

```
.arckit/intake/
├── discovery.json
├── requirements.json
├── value-network.json
└── …
```

- One JSON file per command. The stem is the **hyphenated** command
  name: `value_network` → `value-network.json`
  (`_` → `-`, `command.replace("_", "-")` in `server.py`).
- The MCP tool parameter is **underscored** (`value_network`); the
  on-disk stem is **hyphenated** (`value-network`). An agent that
  copies the tool parameter verbatim into a file path will miss saved
  answers. This is the **F5** known limitation, documented in
  `docs/agent-loop-checkpoints.md` §1.3.
- File contents: a JSON object mapping question ids to answers
  (shape defined by the interview owner; the server parses with
  `json.loads` and surfaces `{"error": "Malformed intake file: …"}`
  on a parse failure).

## Placeholder degradation (F4, by design)

The `intake` field is populated from statically-generated `INTAKE`
data. The generated `COVERAGE` dict marks each doc-type code as
`covered` or `no-static-questions`:

- **Covered codes** (overlays: `togaf-adm`, `it4it`, `oaa`,
  `agent-architecture`): the relay returns the full template-derived
  question list.
- **No-static-questions codes** (the large majority of doc-types in
  the core `arckit-claude` plugin): the relay degrades to **one
  placeholder question per code**. This is intentional — the server
  must never return an empty intake list. The `COVERAGE` report makes
  the gap visible so consumers can decide whether to warn the user or
  proceed.
- **Commands with no doc-type codes in the registry**: the relay
  returns one generic question:
  `"Provide the project context for {command}."`.

The invariant `test_relay_never_returns_empty_intake` pins this
floor.

## Source

`arckit_mcp/server.py` — `persist_intake()` (line 540),
`_intake_questions()` (line 395), `INTAKE` / `COVERAGE` in
`arckit_mcp/intake.py` (generated). Spec:
`openspec/specs/arckit-mcp-intake`.
