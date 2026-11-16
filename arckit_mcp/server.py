"""ArcKit MCP server.

Exposes the ArcKit governance harness to MCP-capable agents:

* 101 per-command tools (``arckit.requirements``, ``arckit.oaa_adm_lite``,
  …) that relay each command's intake questions, instructions, and gate
  status to the calling agent (prompt-relay model — the agent runs the LLM
  generation itself).
* Three meta-tools: ``arckit.list_commands``, ``arckit.next_step``,
  ``arckit.check_gates``.
* One callback: ``arckit.persist_artifact``.

The doc-type registry (``_registry.py``), gate-tier table (``gates.py``),
and handoffs graph (``handoffs.py``) are generated files — do not edit by
hand.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from arckit_mcp._registry import (
    DOC_TYPES,
    KNOWN_TYPES,
    MULTI_INSTANCE_TYPES,
    SUBDIR_MAP,
)
from arckit_mcp.gates import GATE_TIERS
from arckit_mcp.handoffs import HANDOFFS
from arckit_mcp.intake import COVERAGE, INTAKE

mcp = FastMCP("arckit")

# ---------------------------------------------------------------------------
# Project-state helpers
# ---------------------------------------------------------------------------

_ARTIFACT_RE = re.compile(
    r"^ARC-(?P<project>\d{3})-(?P<code>[A-Z0-9]+)(?:-(?P<seq>\d{3}))?-"
    r"(?P<version>v\d+\.\d+)\.md$"
)


def _project_dir(project_id: str, root: str | None = None) -> Path:
    """Resolve ``projects/{project_id}/`` relative to *root* (default cwd)."""
    base = Path(root) if root else Path.cwd()
    return base / "projects" / project_id


def _artifact_exists(code: str, project_id: str, root: str | None = None) -> bool:
    """True if an artefact for *code* exists in the project directory.

    Multi-instance types look under the ``SUBDIR_MAP`` subdirectory first
    (e.g. ``decisions/`` for ADR), then the project root.
    """
    from arckit_mcp._registry import SUBDIR_MAP

    pdir = _project_dir(project_id, root)
    if not pdir.is_dir():
        return False
    sub = SUBDIR_MAP.get(code)
    candidates = []
    if sub:
        candidates.append(pdir / sub)
    candidates.append(pdir)
    prefix = f"ARC-{project_id}-{code}"
    pfx = project_id.split("-")[0]
    for cdir in candidates:
        if not cdir.is_dir():
            continue
        for f in cdir.iterdir():
            m = _ARTIFACT_RE.match(f.name)
            if m and m.group("code") == code and m.group("project") == pfx:
                return True
    return False


def _gate_status(code: str, project_id: str, root: str | None = None) -> str:
    return "closed" if _artifact_exists(code, project_id, root) else "open"


# ---------------------------------------------------------------------------
# Core logic (shared by meta-tools and per-command tools)
# ---------------------------------------------------------------------------

def _command_key(name: str) -> str:
    """Convert a command name to its GATE_TIERS / HANDOFFS key.

    Per-command tool names are ``arckit.{name_with_underscores}``; the
    generated tables are keyed by ``{plugin}/{name}`` (e.g.
    ``arckit-claude/requirements`` or ``arckit-oaa/oaa-adm-lite``).
    """
    for key in GATE_TIERS:
        if key.endswith("/" + name.replace("_", "-")):
            return key
    # Fall back: build a default key so unknown commands still work with
    # empty gates/handoffs.
    return f"arckit-claude/{name.replace('_', '-')}"


def _intake_mandatory_gates(command: str, project_id: str) -> list[dict]:
    """Soft-gate entries for structurally missing MANDATORY intake inputs.

    ``INTAKE[code]["mandatory_inputs"]`` names prerequisite artefacts that
    are *structural* for the doc-type's intake. They are checked the same
    way hard MANDATORY gates are checked (``_gate_status``); when the
    prerequisite artefact does not exist, an open ``{"code": ...,
    "tier": "MANDATORY"}`` gate is emitted. Skipped *intake questions*
    never produce a gate entry — they render as ``TBD`` in the artefact
    and do not block (soft gate, per the spec).
    """
    key = _command_key(command)
    out: list[dict] = []
    for code in _command_doc_types(key):
        entry = INTAKE.get(code)
        if not entry:
            continue
        for input_code in entry.get("mandatory_inputs", []):
            if _gate_status(input_code, project_id) == "open":
                out.append({"code": input_code, "tier": "MANDATORY", "status": "open"})
    return out


def check_gates(command: str, project_id: str) -> dict:
    """Return gate status for *command* in project *project_id*.

    Shape (per spec ``arckit-mcp-gates``):

    * ``gates``: list of ``{code, tier, status}`` — MANDATORY and
      RECOMMENDED gates only; OPTIONAL gates are omitted silently. A
      MANDATORY soft-gate entry (from ``INTAKE`` mandatory inputs) that
      collides with a same-code hard-gate entry at a lower tier
      *escalates* the hard-gate entry in place — the entry is not
      duplicated.
    * ``gate_blocked``: True iff any MANDATORY gate is open, including
      the soft structural-gate entries from ``INTAKE`` mandatory inputs.

    Skipped intake questions render ``TBD`` and never contribute to
    ``gate_blocked``; only missing structural MANDATORY prerequisite
    inputs do.
    """
    key = _command_key(command)
    tiers = GATE_TIERS.get(key, {})
    gates = []
    blocked = False
    seen: set[str] = set()
    for code, tier in sorted(tiers.items()):
        if tier == "OPTIONAL":
            continue  # silently skipped per spec
        status = _gate_status(code, project_id)
        if tier == "MANDATORY" and status == "open":
            blocked = True
        gates.append({"code": code, "tier": tier, "status": status})
        seen.add(code)
    for entry in _intake_mandatory_gates(command, project_id):
        if entry["code"] in seen:
            # A hard-gate entry for the same code already exists;
            # escalate its tier to MANDATORY if the soft-gate says
            # the input is MANDATORY (soft-gate tier wins on collision).
            for g in gates:
                if g["code"] == entry["code"]:
                    if entry["tier"] == "MANDATORY" and g["tier"] != "MANDATORY":
                        g["tier"] = "MANDATORY"
                        if g["status"] == "open":
                            blocked = True
            continue
        gates.append(entry)
        seen.add(entry["code"])
        if entry["status"] == "open":
            blocked = True
    return {
        "command": command,
        "project_id": project_id,
        "gates": gates,
        "gate_blocked": blocked,
    }


def next_step(project_id: str, completed: list[str] | None = None) -> dict:
    """Walk the handoffs graph and return the next recommended command.

    A handoff edge from a completed command is *satisfied* when it carries
    no condition, or when the condition's referenced doc-type code has an
    artefact present in the project. Edges with an unevaluable condition
    are omitted (per spec — not assumed satisfied).
    """
    completed_set = set(completed or [])
    # Collect candidate next steps from completed commands' handoffs.
    candidates: dict[str, str] = {}  # target → reason (condition text)
    for cmd in completed_set:
        key = _command_key(cmd)
        for target, cond_text, cond_code in HANDOFFS.get(key, []):
            if target in completed_set:
                continue
            if not cond_code:
                if not cond_text:
                    candidates.setdefault(target, "")
            elif _artifact_exists(cond_code, project_id):
                candidates.setdefault(target, cond_text or f"{cond_code} present")
            # else: condition not met — omit
    if not candidates:
        return {
            "project_id": project_id,
            "next": None,
            "reason": "All reachable handoffs completed",
        }
    target = min(candidates)  # deterministic pick when several qualify
    reason = candidates[target] or "No condition; recommended next step"
    return {"project_id": project_id, "next": target, "reason": reason}


# KNOWN LIMITATION (F3b, docs/agent-loop-checkpoints.md §1.3, sub-item of
# the F5 stop-word note): this stop-list is a hand-maintained copy of the
# citation stop-word list defined in arc-kit's
# plugins/arckit-claude/references/citation-instructions.md §Source ID
# Rules.  If arc-kit adds or removes a word, source-id derivation here
# will silently diverge from arc-kit's derivation until this set is
# synced by hand.  Same cross-repo drift risk as F3, narrower surface.
_STOP_WORDS = {
    "the", "and", "of", "for", "in", "a", "an", "to", "with",
    "on", "by", "from", "at", "as", "is", "are", "that", "this",
}

_VERSION_SUFFIX_RE = re.compile(
    r"[-_]v\d+(?:\.\d+)?$", re.IGNORECASE
)


def _slugify(name: str) -> str:
    s = re.sub(r"[\s_]+", "-", name.strip().lower())
    s = re.sub(r"-{2,}", "-", s)
    return s


def _derive_source_id(filename: str) -> str:
    """Derive a short Source ID from an imported document's filename.

    Mirrors ``plugins/arckit-claude/references/citation-instructions.md``
    §Source ID Rules: strip the extension, strip any version suffix
    (``-v2``, ``_v3``, ``-v1.2``), take the first letter of each
    significant word (stopping the article/conjunction/preposition stop
    list), and uppercase.
    """
    stem = Path(filename).stem
    stem = _VERSION_SUFFIX_RE.sub("", stem)
    words = re.split(r"[-_\s]+", stem.lower())
    letters = [w[0] for w in words if w and w not in _STOP_WORDS]
    if not letters:
        letters = [w[0] for w in words if w]
    return "".join(letters).upper()


def seed_context(
    project_name: str,
    goals: list[str] | None = None,
    constraints: list[str] | None = None,
    context_folder: str | None = None,
) -> dict:
    """Seed a new project tree with pre-project context.

    Mints a new ``projects/NNN/`` directory (bare layout — no slug in the
    directory name), writes a ``GOALS.md`` with the given
    goals/constraints, optionally imports a folder of reference documents
    into ``external/`` (counting all files for ``files_imported``), writes
    ``external/CONTEXT.md`` as a source index when files were imported, and
    records the original project name in a sidecar ``.meta`` JSON file so
    that re-seeding the same name is rejected.

    Returns::

        {
            "project_id": "NNN",
            "project_dir": "projects/NNN",
            "slug": "nnn-slug",
            "files_imported": N,
            "context_index": "external/CONTEXT.md" or None,
        }

    Collision (a project with the same name is already seeded, tracked via
    the ``.meta`` sidecar) returns::

        {"error": str, "project_id": None}
    """
    root = Path.cwd()
    slug = _slugify(project_name)
    projects_root = root / "projects"
    projects_root.mkdir(parents=True, exist_ok=True)

    # Collision: a project with this name was already seeded.  The name→id
    # mapping is persisted in the .meta sidecar inside each project dir, so
    # the check survives across server invocations.
    for p in projects_root.iterdir():
        if not p.is_dir():
            continue
        meta = p / ".meta"
        if not meta.is_file():
            continue
        try:
            existing = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(existing, dict) and existing.get("name") == project_name:
            return {"error": f"Project '{project_name}' already seeded", "project_id": None}

    # Mint the next free 3-digit id.
    taken: set[str] = set()
    for d in projects_root.iterdir():
        if d.is_dir():
            m = re.match(r"^(\d{3})", d.name)
            if m:
                taken.add(m.group(1))
    pid = f"{next(i for i in range(1, 1000) if f'{i:03d}' not in taken):03d}"

    target = projects_root / pid
    (target / "external").mkdir(parents=True)

    # .meta sidecar: name-keyed record so collision detection survives
    # without slug-suffixed directory names.
    (target / ".meta").write_text(
        json.dumps({"name": project_name, "pid": pid}, indent=2) + "\n"
    )

    # GOALS.md
    sections: list[str] = []
    if goals:
        sections.append("## Goals\n\n" + "\n".join(f"- {g}" for g in goals))
    if constraints:
        sections.append("## Constraints\n\n" + "\n".join(f"- {c}" for c in constraints))
    if sections:
        (target / "GOALS.md").write_text("\n\n".join(sections) + "\n")

    # Context folder import
    files_imported = 0
    context_index: str | None = None
    if context_folder:
        src = Path(context_folder)
        if not src.is_dir():
            return {"error": f"Context folder not found: {context_folder}", "project_id": None}
        ext_dir = target / "external"
        ext_dir.mkdir(parents=True, exist_ok=True)
        # Copy all files, preserving subdirectory structure
        imported_names: list[str] = []
        for f in sorted(src.rglob("*")):
            if f.is_file():
                dest = ext_dir / f.relative_to(src)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(f.read_bytes())
                files_imported += 1
                imported_names.append(str(f.relative_to(src)))
        if imported_names:
            lines = ["# External Context Index\n"]
            for name in imported_names:
                sid = _derive_source_id(name)
                lines.append(f"- **{sid}** — `{name}`")
            (ext_dir / "CONTEXT.md").write_text("\n".join(lines) + "\n")
            context_index = "external/CONTEXT.md"

    return {
        "project_id": pid,
        "project_dir": f"projects/{pid}",
        "slug": slug,
        "files_imported": files_imported,
        "context_index": context_index,
    }


def list_commands() -> list[dict]:
    """Enumerate all known commands with doc-type codes and gate tiers."""
    out: list[dict] = []
    for key in sorted(GATE_TIERS):
        plugin, name = key.split("/", 1)
        overlay = "core" if plugin == "arckit-claude" else plugin.removeprefix(
            "arckit-"
        )
        tiers = GATE_TIERS[key]
        out.append(
            {
                "command": name,
                "tool": f"arckit.{name.replace('-', '_')}",
                "overlay": overlay,
                "gates": [
                    {"code": code, "tier": tier}
                    for code, tier in sorted(tiers.items())
                    if tier != "OPTIONAL"
                ],
            }
        )
    return out


def _intake_questions(command: str) -> list[dict]:
    """Return the command's intake question list.

    When the command's doc-type codes have generated intake data in
    ``intake.INTAKE`` (``COVERAGE[code] == "covered"``), return the
    template-derived question list. Otherwise fall back to the
    synthetic per-doc-type placeholder questions (or a generic one when
    the command has no registry doc-type codes), so no command's intake
    payload ever becomes empty.
    """
    key = _command_key(command)
    code_map = _command_doc_types(key)
    for code in sorted(code_map):
        entry = INTAKE.get(code)
        if entry and COVERAGE.get(code) == "covered":
            return [
                {
                    "id": f"{command}-{code.lower()}-{i}",
                    "question": q,
                    "required": True,
                    "hint": "From generated intake data (template question block).",
                }
                for i, q in enumerate(entry.get("questions", []), start=1)
            ]
    if not code_map:
        return [
            {
                "id": f"{command}-intake",
                "question": f"Provide the project context for {command}.",
                "required": True,
                "hint": "Answer the command's intake questions per its prompt.",
            }
        ]
    # KNOWN LIMITATION (F4, docs/agent-loop-checkpoints.md §1.3): the
    # placeholder floor is intentional by-design — 160 of 177 doc-types are
    # "no-static-questions", so they degrade to one per-code placeholder
    # question here. The server must never return an empty intake list;
    # the invariant test_relay_never_returns_empty_intake pins this.
    questions = []
    for i, code in enumerate(sorted(code_map), start=1):
        meta = DOC_TYPES.get(code, {})
        questions.append(
            {
                "id": f"{command}-{code.lower()}-{i}",
                "question": f"Provide inputs for the {meta.get('name', code)} artefact.",
                "required": True,
                "hint": f"Feeds {code} generation.",
            }
        )
    return questions


# KNOWN LIMITATION (F3, docs/agent-loop-checkpoints.md §1.3):
# ``name_map`` / ``overlay_map`` below are hand-maintained. They duplicate
# the registry's ``DOC_TYPES`` membership as a command→codes table, and the
# two can drift apart when the registry grows commands without the maps
# being updated (silent gap: new commands return [] → generic placeholder
# intake, no doc-type codes). Two deferred remediation options:
#   (A) generate a COMMAND_DOC_TYPES table into arckit_mcp/_registry.py
#       from the same source as the other generated tables (preferred);
#   (B) add a CI check diffing these maps against the registry and
#       failing on drift.
# Ticket-of-record: openspec/changes/fix-seed-context-layout/tasks.md §3.2.
def _command_doc_types(key: str) -> list[str]:
    """Doc-type codes a command writes, from the registry.

    A command's doc-type code is derived from its name when the name maps to
    a registry entry (e.g. ``requirements`` → REQ); otherwise we fall back
    to the gate codes the command reads. This keeps the function pure and
    registry-driven.
    """
    plugin, name = key.split("/", 1)
    # Direct name → code mapping for the well-known commands.
    name_map = {
        "requirements": ["REQ"],
        "stakeholders": ["STKE"],
        "strategy": ["STRAT"],
        "roadmap": ["ROAD"],
        "adr": ["ADR"],
        "risk": ["RISK"],
        "sobc": ["SOBC"],
        "principles": ["PRIN"],
    }
    if name in name_map:
        return name_map[name]
    # Overlay doc-type codes.
    overlay_map = {
        "oaa-adm-lite": ["OAAL"],
        "product-architecture": ["OAPR"],
        "agile-governance": ["OAGOV"],
        "agile-security": ["OASEC"],
        "agile-strategy": ["OASTR"],
        "it4it-value-network": ["ITVN"],
        "it4it-value-stream": ["ITVS"],
        "it4it-strategy-portfolio": ["ITSF"],
        "it4it-develop-test": ["ITDT"],
        "it4it-consume-fulfil": ["ITCF"],
        "it4it-operate-assure": ["ITOA"],
        "adm-preliminary": ["ADMP"],
        "application-inventory": ["APPR"],
        "application-rationalization": ["APP"],
        "architecture-board": ["BORD"],
        "architecture-change": ["ACHG"],
        "architecture-repository": ["REPO"],
        "business-capability-map": ["BPCM"],
        "data-architecture": ["DATA"],
        "discovery": ["DISC"],
        "gap-analysis": ["GAPA"],
        "technology-architecture": ["TECH"],
        "transition-architecture": ["TRANS"],
    }
    if name in overlay_map:
        return overlay_map[name]
    return []


def _instructions(command: str, project_id: str) -> str:
    key = _command_key(command)
    codes = _command_doc_types(key) or ["<TYPE>"]
    return (
        f"Run the {command} command in your session to produce "
        f"{'/'.join(codes)} artefact(s) for project {project_id}. "
        f"Save each artefact to projects/{project_id}/ via "
        f"arckit.persist_artifact."
    )


def run_command(command: str, project_id: str) -> dict:
    """Prompt-relay response for a per-command tool."""
    key = _command_key(command)
    name = key.split("/", 1)[1]
    codes = _command_doc_types(key)
    gate_report = check_gates(name, project_id)
    return {
        "id": f"ARC-{project_id}",
        "project_id": project_id,
        "command": name,
        "doc_type": codes[0] if len(codes) == 1 else codes,
        "intake": _intake_questions(name),
        "instructions": _instructions(name, project_id),
        "gates": gate_report["gates"],
        "gate_blocked": gate_report["gate_blocked"],
    }


def persist_intake(project_id: str, command: str) -> dict:
    """Read saved intake answers for *command* from the project tree.

    Read/seed only, per spec: Agent A (the interview owner) remains the
    sole persister of answers — the server never writes
    ``.arckit/intake/``. Returns the parsed JSON so a bulk build can
    prefill the interview without prompting the user::

        {
            "project_id": "001",
            "command": "requirements",
            "found": True,
            "answers": {...},
            "path": ".arckit/intake/requirements.json",
        }

    When no saved file exists, returns ``{"found": False, "answers": None}``
    with no error.
    """
    # KNOWN LIMITATION (F5, docs/agent-loop-checkpoints.md §1.3): the
    # on-disk stem is the hyphenated command name (``_`` → ``-``), while
    # the MCP tool parameter is underscored. An agent that copies the
    # tool parameter verbatim into a file path will miss saved answers.
    # Pinned by ``test_no_write_path_for_answers``
    # (tests/mcp/test_intake.py) — ``discovery`` → ``discovery.json``
    # is the canonical example — and by the read-only shape of this
    # function (never writes to ``.arckit/intake/``).
    stem = command.replace("_", "-")
    path = Path(".arckit") / "intake" / f"{stem}.json"
    result = {
        "project_id": project_id,
        "command": command,
        "found": False,
        "answers": None,
        "path": str(path),
    }
    if path.is_file():
        result["found"] = True
        try:
            result["answers"] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            result["error"] = f"Malformed intake file: {exc}"
    return result


def persist_artifact(
    project_id: str, type_code: str, content: str, sequence: int | None = None
) -> dict:
    """Write *content* to ``projects/{project_id}/ARC-{pid}-{TYPE}-v1.0.md``.

    Multi-instance types get a ``-{NNN}`` sequence segment; when
    *sequence* is omitted the next available number is assigned by
    scanning existing artefacts (root and any ``SUBDIR_MAP`` subdir).
    Unknown doc-type codes are rejected.
    """
    code = type_code.upper()
    if code not in KNOWN_TYPES:
        return {
            "error": (
                f"Unknown doc-type code '{type_code}'. "
                f"Valid codes come from the doc-types.mjs registry."
            ),
            "written": False,
        }
    pid = project_id.zfill(3)
    pdir = _project_dir(project_id)
    sub = SUBDIR_MAP.get(code)
    outdir = pdir / sub if sub else pdir
    outdir.mkdir(parents=True, exist_ok=True)

    if code in MULTI_INSTANCE_TYPES:
        if sequence is None:
            sequence = _next_sequence(outdir, code, pid)
        filename = f"ARC-{pid}-{code}-{int(sequence):03d}-v1.0.md"
    else:
        filename = f"ARC-{pid}-{code}-v1.0.md"

    path = outdir / filename
    path.write_text(content, encoding="utf-8")
    return {"path": str(path), "written": True}


def _next_sequence(outdir: Path, code: str, pid: str) -> int:
    prefix = f"ARC-{pid}-{code}-"
    best = 0
    for f in outdir.iterdir():
        m = re.match(
            rf"^ARC-{pid}-{code}-(\d{{3}})-v\d+\.\d+\.md$", f.name
        )
        if m:
            best = max(best, int(m.group(1)))
    return best + 1


# ---------------------------------------------------------------------------
# MCP tool registration
# ---------------------------------------------------------------------------

def _register_meta_tools() -> None:
    @mcp.tool(
        name="arckit.list_commands",
        description="List all ArcKit commands with their doc-type codes and gate tiers.",
    )
    def arckit_list_commands() -> list[dict]:
        """List all ArcKit commands with their doc-type codes and gate tiers."""
        return list_commands()

    @mcp.tool(
        name="arckit.check_gates",
        description=(
            "Check which prerequisite gates are open/closed for a command. "
            "MANDATORY gates hard-stop when open; RECOMMENDED are noted; "
            "OPTIONAL are omitted."
        ),
    )
    def arckit_check_gates(command: str, project_id: str) -> dict:
        """Check which prerequisite gates are open/closed for a command."""
        return check_gates(command, project_id)

    @mcp.tool(
        name="arckit.next_step",
        description="Return the next recommended command from the handoffs graph.",
    )
    def arckit_next_step(project_id: str, completed: list[str] | None = None) -> dict:
        """Return the next recommended command from the handoffs graph."""
        return next_step(project_id, completed)

    @mcp.tool(
        name="arckit.persist_artifact",
        description=(
            "Persist a generated artefact into the project tree. "
            "Multi-instance types (ADR, DIAG, …) get the next sequence "
            "number when *sequence* is omitted."
        ),
    )
    def arckit_persist_artifact(
        project_id: str,
        type_code: str,
        content: str,
        sequence: int | None = None,
    ) -> dict:
        """Persist a generated artefact into the project tree."""
        return persist_artifact(project_id, type_code, content, sequence)

    @mcp.tool(
        name="arckit.persist_intake",
        description=(
            "Read saved .arckit/intake/{command}.json answers for a project "
            "so a bulk build can prefill the intake interview. Read/seed "
            "only — the server never writes intake answers; the interview "
            "agent remains the sole persister."
        ),
    )
    def arckit_persist_intake(project_id: str, command: str) -> dict:
        """Read saved intake answers for a command (read/seed only)."""
        return persist_intake(project_id, command)

    @mcp.tool(
        name="arckit.seed_context",
        description=(
            "Seed a new project tree with pre-project context: goals, "
            "constraints, and/or a folder of reference documents. "
            "Returns the project_id for use with all other arckit.* tools. "
            "IF THE USER HAS NOT PROVIDED A CONTEXT FOLDER, ASK THEM FIRST "
            "for a path to a folder of reference documents (e.g. external/ "
            "or a path like /home/user/my-refs) before calling this tool."
        ),
    )
    def arckit_seed_context(
        project_name: str,
        goals: list[str] | None = None,
        constraints: list[str] | None = None,
        context_folder: str | None = None,
    ) -> dict:
        """Seed a new project tree with pre-project context."""
        return seed_context(project_name, goals, constraints, context_folder)


def _register_command_tools() -> None:
    for key in sorted(GATE_TIERS):
        plugin, name = key.split("/", 1)
        tiers = GATE_TIERS[key]
        tier_labels = ", ".join(
            f"{c}:{t}" for c, t in sorted(tiers.items()) if t != "OPTIONAL"
        ) or "no gates"
        codes = _command_doc_types(key)
        code_text = " ".join(codes) if codes else "multiple types"

        desc = (
            f"ArcKit command '{name}' (overlay: {plugin}). "
            f"Doc-type(s): {code_text}. Gates: {tier_labels}. "
            f"Returns intake questions, instructions, and gate status; "
            f"the agent runs the generation and persists via "
            f"arckit.persist_artifact."
        )

        tool_name = f"arckit.{name.replace('-', '_')}"
        command = name

        @mcp.tool(name=tool_name, description=desc)
        def relay(project_id: str) -> dict:
            """Relay the command's intake questions and gate status."""
            return run_command(command, project_id)

        relay.__name__ = tool_name.replace(".", "_")


_register_meta_tools()
_register_command_tools()


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
