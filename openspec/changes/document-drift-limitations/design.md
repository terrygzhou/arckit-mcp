# Design: document-drift-limitations

## Context

See proposal. F3/F4 are the "document + don't solve now" findings from the
EYW-817 remediation plan. No architecture change is in scope.

## Goals / Non-Goals

Goals:
- Make the known limitation (F3) discoverable in-repo, with the two
  candidate follow-ups spelled out.
- Pin the by-design placeholder-intake behaviour (F4) with a comment so it
  is not "fixed" in error later.

Non-goals:
- Auto-generating the doc-type table (option A) or a CI drift check
  (option B) — deferred to a follow-up ticket.

## Decisions

### D1: Where the limitation is documented

`docs/agent-loop-checkpoints.md` is the findings record; the new "Known
limitations" section goes directly under §1.2 Findings so a reader of the
review meets it in context. A `server.py` comment points at that section.

## Risks / Trade-offs

- **Comment-only change in `server.py`** → zero runtime risk; verified by
  the full suite.
- **Limitation could outlive the doc** if the doc is deleted → the
  follow-up ticket (filed at implementation time) is the durable record.

## Open Questions

- Which follow-up ticket system to file F3 in, and the ticket id to cite
  in the doc. (Decide at implementation time; not needed for the docs.)
