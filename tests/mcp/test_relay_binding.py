"""Regression: each per-command relay tool relays its own command.

``_register_command_tools`` builds one relay closure per registry command in a
single loop. If a closure captured the loop's mutable outer variable by
reference (late binding), every tool would silently execute the *last* command
in the sorted loop — observed as all 115 relay tools returning the
``transition-architecture`` payload. These tests call each registered relay and
pin the ``command`` field of its payload.
"""

from __future__ import annotations

from arckit_mcp.gates import GATE_TIERS
from arckit_mcp.server import mcp as _mcp

_META_TOOLS = {
    "arckit.list_commands",
    "arckit.check_gates",
    "arckit.next_step",
    "arckit.persist_artifact",
    "arckit.persist_intake",
    "arckit.seed_context",
}


def _relay_tools() -> dict:
    """Registered relay tool name → raw fn (excludes the meta tools)."""
    tools = _mcp._tool_manager._tools
    return {
        n: t.fn
        for n, t in tools.items()
        if n.startswith("arckit.") and n not in _META_TOOLS
    }


def test_every_relay_tool_relays_its_own_command() -> None:
    """The relay payload's ``command`` field must match the tool's command."""
    relays = _relay_tools()
    checked = 0
    for key in sorted(GATE_TIERS):
        plugin, name = key.split("/", 1)
        tname = f"arckit.{name.replace('-', '_')}"
        assert tname in relays, f"no relay tool registered for {tname}"
        payload = relays[tname](project_id="999")
        assert payload["command"] == name, (
            f"{tname} relayed {payload['command']!r} instead of {name!r} "
            "(late-binding closure captured the last loop command)"
        )
        checked += 1
    assert checked == len(GATE_TIERS), (
        f"only {checked}/{len(GATE_TIERS)} relay tools present"
    )


def test_no_relay_shares_a_closure_cell() -> None:
    """Structural tripwire: each relay binds its own command cell.

    A shared late-bound cell would hold one command (the last loop value)
    for every tool; after the factory fix each closure's first cell is its
    own command name.
    """
    relays = _relay_tools()
    for key in sorted(GATE_TIERS):
        plugin, name = key.split("/", 1)
        tname = f"arckit.{name.replace('-', '_')}"
        fn = relays.get(tname)
        if fn is None:
            continue
        cells = [c.cell_contents for c in (fn.__closure__ or [])]
        assert cells and cells[0] == name, (
            f"{tname} closure cells {cells!r}; first must be its own "
            f"command {name!r}"
        )

