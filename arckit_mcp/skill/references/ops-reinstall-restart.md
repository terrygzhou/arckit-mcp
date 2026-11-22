# Reinstall & restart the arckit-mcp server

Do this when the user says "reinstall arckit-mcp" or "restart arckit-mcp".
The gateway (`systemd --user`, parent of everything on the box) owns
`arckit-mcp` as a stdio child; a code update means restart the CHILD,
never the gateway.

## Reinstall / update — the real entry point is install.sh

The installed tree ships `install.sh` and `scripts/install-skill.sh`; it
does **not** ship a `reinstall.sh` — so don't invent one (a
`--project-id --agent-loop-hook` form is not in the tree). `install.sh`
is idempotent and is the supported reinstall/update path:

    bash install.sh
    # (1) pull latest ARC-Kit + arckit-mcp
    # (2) set up the .venv
    # (3) pip install -e arckit-mcp/   <- relinks the editable install, refreshes the console script
    # (4) register the agent-loop skill into agent dirs (install-skill.sh)

Each step is re-runnable. Step (3) refreshes the code on disk, but the
**running** stdio child still holds the old code until restarted.

## Restart the stdio child (gateway auto-respawns)

    pgrep -f 'repo/\.venv/bin/arckit-mcp'   # the stdio child PID(s)
    kill -TERM <pid>                          # the child ONLY

The gateway respawns a fresh `arckit-mcp` child within ~30-60s.

- **Find the child by the binary path**, not the bare string
  `arckit-mcp`: the antigravity IDE matches `--add-dir .../arckit-mcp`
  and is not the gateway's server. Target `repo/.venv/bin/arckit-mcp`.
- **Never** `systemctl --user restart hermes-gateway` for a code update
  — that SIGTERMs every terminal child. Only `systemctl --user start
  hermes-gateway` if the gateway itself is down.
- **Expect a one-call transient:** the first arckit tool call that runs
  mid-transition can return `arckit-mcp lost its stdio subprocess`. That
  is not the end state — a follow-up call + `pgrep` confirming a new
  short-etime PID is the success check.
- **Verify:** `pgrep -f 'repo/\.venv/bin/arckit-mcp'` shows a fresh PID
  and a live arckit tool call (e.g. `arckit.seed_context`) succeeds
  against it.
- Only after a full gateway (re)start does the agent-loop skill hook
  need re-registering: re-run `install.sh` if `hermes doctor` shows the
  `arckit-mcp-agent-loop` hook as `not-found` / expired.
