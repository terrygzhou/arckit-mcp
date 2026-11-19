#!/usr/bin/env bash
# arckit-mcp agent-skill installer (extracted from install.sh step 4).
#
# Registers the bundled agent skill where Claude Code / agent harnesses
# discover skills (~/.claude/skills). Symlinks the files so the installed
# copy picks up in-place upgrades; falls back to a copy if symlinking
# fails (e.g. cross-filesystem). Non-fatal: the MCP server works without
# the skill being registered.
#
# Usage:
#   scripts/install-skill.sh <skill-source-dir> <skills-root> [skill-name]
#
#   skill-source-dir   dir containing SKILL.md (and optionally references/).
#                      Typically <repo>/arckit_mcp/skill.
#   skills-root        where the harness discovers skills.
#                      Default: $HOME/.claude/skills
#   skill-name         directory name under skills-root.
#                      Default: arckit-mcp-agent-loop
#
# Idempotent: re-running replaces the existing entries (rm -rf then re-link),
# so upgrades propagate in place rather than duplicating.
#
# The script is POSIX-compatible so it can run under `sh` on minimal
# systems. `ln -s` (symlink) is tried first; on failure (cross-filesystem,
# read-only, filesystem without symlink support) it falls back to a copy.
# Exit codes:
#   0  skill registered (or source missing — non-fatal warning)
#   1  usage error / bad arguments

set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <skill-source-dir> <skills-root> [skill-name]" >&2
  exit 1
fi

SKILL_SRC="$1"
SKILLS_ROOT="$2"
SKILL_NAME="${3:-arckit-mcp-agent-loop}"

if [ ! -d "$SKILL_SRC" ]; then
  echo "arckit-mcp: warning: skill source dir not found at $SKILL_SRC — skipping skill registration"
  exit 0
fi
if [ ! -f "$SKILL_SRC/SKILL.md" ]; then
  echo "arckit-mcp: warning: SKILL.md not found at $SKILL_SRC — skipping skill registration"
  exit 0
fi

SKILL_TARGET="$SKILLS_ROOT/$SKILL_NAME"
mkdir -p "$SKILL_TARGET"

# Symlink each skill entry so upgrades propagate; fall back to a copy.
# `references` is optional — some builds may omit it.
# (register_entry is a simple body, not a function, so the script stays
# POSIX `sh`-compatible — no `local`, no subshell needed.)
rm -rf "$SKILL_TARGET/SKILL.md"
if ln -s "$SKILL_SRC/SKILL.md" "$SKILL_TARGET/SKILL.md" 2>/dev/null; then
  :
else
  cp -R "$SKILL_SRC/SKILL.md" "$SKILL_TARGET/SKILL.md"
fi

if [ -d "$SKILL_SRC/references" ]; then
  rm -rf "$SKILL_TARGET/references"
  if ln -s "$SKILL_SRC/references" "$SKILL_TARGET/references" 2>/dev/null; then
    :
  else
    cp -R "$SKILL_SRC/references" "$SKILL_TARGET/references"
  fi
fi

echo "arckit-mcp: skill registered at $SKILL_TARGET (symlinked to $SKILL_SRC)"
