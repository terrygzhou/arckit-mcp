#!/usr/bin/env bash
# arckit-mcp one-line installer (Mac / Linux)
#
#   curl -fsSL https://raw.githubusercontent.com/terrygzhou/arckit-mcp/main/install.sh | sh
#
# What it does (idempotent — re-run to upgrade):
#   1. Preflight: Python >= 3.11 and git on PATH
#   2. Clone (or pull) the repo into $ARCKIT_MCP_HOME (default: ~/.local/share/arckit-mcp/repo)
#   3. Create a venv next to the checkout and pip install the package
#   4. Register the bundled agent skill at ~/.claude/skills/arckit-mcp-agent-loop
#   5. Print the MCP client registration JSON
#
# Environment overrides:
#   ARCKIT_MCP_HOME    where the clone + venv live      (default: ~/.local/share/arckit-mcp/repo)
#   ARCKIT_MCP_REPO    git URL of the repo              (default: the public GitHub URL)
#   ARCKIT_MCP_DEV=1   also install the [dev] extra     (arckit + pytest)
#   ARCKIT_SKILL_DIR   where to register the skill      (default: ~/.claude/skills)

set -eu

REPO="${ARCKIT_MCP_REPO:-https://github.com/terrygzhou/arckit-mcp.git}"
DEST="${ARCKIT_MCP_HOME:-$HOME/.local/share/arckit-mcp/repo}"
DEV="${ARCKIT_MCP_DEV:-0}"

fail() { echo "arckit-mcp install: $*" >&2; exit 1; }

# --- 1. Preflight -----------------------------------------------------------
command -v python3 >/dev/null 2>&1 || fail "python3 not found — install Python >= 3.11"
command -v git >/dev/null 2>&1 || fail "git not found"

PYVER="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  fail "python3 is $PYVER — arckit-mcp requires Python >= 3.11"
fi
echo "arckit-mcp: python $PYVER, git $(git --version | cut -d' ' -f2)"

# --- 2. Clone or update -----------------------------------------------------
mkdir -p "$(dirname "$DEST")"
if [ -d "$DEST/.git" ]; then
  echo "arckit-mcp: updating $DEST ..."
  git -C "$DEST" pull --ff-only
else
  echo "arckit-mcp: cloning $REPO into $DEST ..."
  git clone --depth 1 "$REPO" "$DEST"
fi

# --- 3. Venv + install --------------------------------------------------------
if [ ! -d "$DEST/.venv" ]; then
  echo "arckit-mcp: creating venv at $DEST/.venv ..."
  python3 -m venv "$DEST/.venv"
fi

EXTRA=""
if [ "$DEV" = "1" ]; then
  EXTRA="[dev]"
fi
echo "arckit-mcp: installing (this can take a minute) ..."
# Refresh pip first, but tolerate the in-place self-replace (replaces the
# binary that is running, which can abort with a non-zero code on some
# systems).
"$DEST/.venv/bin/python" -m pip install -q --upgrade pip || true
"$DEST/.venv/bin/python" -m pip install -q -e "$DEST$EXTRA"

BIN="$DEST/.venv/bin/arckit-mcp"
[ -x "$BIN" ] || fail "install finished but $BIN is missing"

# --- 4. Register the agent skill (best effort) --------------------------------
# Delegates to scripts/install-skill.sh (single source of truth, shared with
# the test suite and install.ps1's semantics). The script symlinks the skill
# files so re-runs pick up in-place upgrades; falls back to a copy on
# cross-filesystem or missing-symlink cases. Non-fatal: the MCP server
# works without the skill being registered.
SKILL_SRC="$DEST/arckit_mcp/skill"
SKILL_DEST_DIR="${ARCKIT_SKILL_DIR:-$HOME/.claude/skills}"
SKILL_NAME="arckit-mcp-agent-loop"
# Use the script shipped with the fresh clone; fall back to a warning if it
# is absent (very old checkouts).
if [ -x "$DEST/scripts/install-skill.sh" ]; then
  "$DEST/scripts/install-skill.sh" "$SKILL_SRC" "$SKILL_DEST_DIR" "$SKILL_NAME"
else
  echo "arckit-mcp: warning: scripts/install-skill.sh not found at $DEST — skipping skill registration"
fi

# --- 5. Done -----------------------------------------------------------------
echo ""
echo "✓ arckit-mcp installed"
echo ""
echo "MCP client registration (paste into your MCP client config):"
echo "  {\"mcpServers\": {\"arckit\": {\"command\": \"$BIN\"}}}"
echo ""
echo "Verify: $BIN   (boots the stdio server; Ctrl-C to stop)"
echo "Upgrade later: re-run the same one-liner."
if [ "$DEV" = "1" ]; then
  echo "Dev extras installed: run tests with $DEST/.venv/bin/python -m pytest $DEST/tests -q"
fi
