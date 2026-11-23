"""ArcKit MCP server.

Exposes the ArcKit architecture-governance harness as MCP tools so an AI
agent can inspect projects, check gate tiers, walk handoff chains, and
persist artefacts without leaving the session.

The module ships four layers:

* ``_registry`` (generated) - canonical doc-type codes, subdirs, multi-instance
  set, and regimes, emitted from ``plugins/arckit-claude/config/doc-types.mjs``
  by ``scripts/generate-mcp-registry.py``.
* ``gates`` (generated) - per-command gate-tier tables (MANDATORY /
  RECOMMENDED / OPTIONAL codes), emitted from the command markdown bodies by
  ``scripts/generate-mcp-gates.py``.
* ``handoffs`` (generated) - the handoff graph, emitted from command
  frontmatter by ``scripts/generate-mcp-handoffs.py``.
* ``server`` - the MCP server entry point (wired up in a follow-up task).
"""

__version__ = "0.1.0"

__all__ = ["__version__", "resolve_source_root"]


def __getattr__(name: str):
    """Lazy re-export of :func:`arckit_mcp.source_root.resolve_source_root`.

    Deferred (PEP 562) so that importing ``arckit_mcp`` never re-enters
    the package's own ``__init__`` while it is still being initialised.
    """
    if name == "resolve_source_root":
        from arckit_mcp.source_root import resolve_source_root

        return resolve_source_root
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
