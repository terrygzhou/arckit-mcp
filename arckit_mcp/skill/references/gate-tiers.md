# Gate tiers

Every command in the ArcKit registry carries a gate-tier table
(`GATE_TIERS`, generated). Tiers describe how the *absence* of a
prerequisite artefact affects the command:

| Tier | Meaning |
| --- | --- |
| `MANDATORY` | Prerequisite artefact is required. Open gate ⇒ `gate_blocked: true` — hard-stop. The agent must complete the prerequisite command and persist its artefact before proceeding. |
| `RECOMMENDED` | Prerequisite artefact is strongly suggested. Noted in the `gates` list, visible to the agent, but does **not** set `gate_blocked`. |
| `OPTIONAL` | Prerequisite artefact is purely optional. **Silently omitted** from the `gates` list — the agent never sees it. |

## Hard-stop protocol

When `gate_blocked` is `true`:

1. Read the `gates` list from the relay response. Each entry is
   `{code, tier, status}`.
2. Identify every entry with `tier == "MANDATORY"` and `status == "open"`.
3. For each open MANDATORY code, the gate's `code` is a doc-type code
   that corresponds to a prerequisite command:
   - `PRIN` → `arckit.principles`
   - `STKE` → `arckit.stakeholders`
   - `REQ`  → `arckit.requirements`
   - etc. (the `name_map` / `overlay_map` in `server.py` defines the
     reverse mapping; see `F3` in `known-limitations`)
4. Run the prerequisite command, answer its intake, generate its
   document, and `arckit.persist_artifact(project_id, code, content)`.
5. Re-check: `arckit.check_gates(command, project_id)` — confirm the
   gate is now `closed`.
6. Repeat until `gate_blocked` is `false`.

## Soft-gate escalation

`check_gates` also evaluates *soft structural gates* — `mandatory_inputs`
entries in the `INTAKE` table for the command's doc-type code. A soft
gate is a structural input the command cannot generate without (e.g. a
specific source document). Soft gates behave identically to hard
MANDATORY gates:

- Open soft MANDATORY gate ⇒ `gate_blocked: true`.
- On a collision (same `code` appears in both the hard-gate table and
  the soft-gate table), the soft-gate tier wins: the hard-gate entry is
  **escalated in place** to `MANDATORY`, not duplicated.
- Skipped intake questions render `TBD` in the artefact and **never**
  contribute to `gate_blocked`. Only missing *structural* MANDATORY
  prerequisite inputs do.

## Source

`arckit_mcp/server.py` — `check_gates()` (line 128),
`_intake_mandatory_gates()`, `GATE_TIERS` in `arckit_mcp/gates.py`
(generated). Spec: `openspec/specs/arckit-mcp-gates`.
