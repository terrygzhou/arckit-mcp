"""Regenerate vendored generated files from an installed ArcKit package.

The generators in ``scripts/`` read ``plugins/arckit-claude/config/doc-types.mjs``
and the command markdown under ``plugins/*/commands/``.  When ArcKit is
installed as a package (``pip install arckit``), those files ship inside the
package data.  This module locates the installed package's source tree and
regenerates ``_registry.py``, ``gates.py``, and ``handoffs.py`` into the
vendor directory so the standalone repo always has fresh generated data.

Usage (console script ``arckit-mcp-sync``)::

    arckit-mcp-sync [--source-root PATH]

``--source-root`` points at the installed ArcKit source tree.  When omitted
the script auto-discovers the tree from the ``arckit`` package location.
"""

from __future__ import annotations

import argparse
import importlib
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _find_source_root() -> Path:
    """Locate the installed ArcKit source tree."""
    try:
        import arckit  # noqa: F401
    except ImportError:
        raise SystemExit(
            "arckit package not found. Install it with `pip install arckit` "
            "or pass --source-root explicitly."
        )
    pkg_dir = Path(arckit.__file__).resolve().parent
    # arckit CLI package: src/arckit_cli → parent is src/ → parent is repo root
    # or: plugins/arckit-claude is a sibling of src/
    root = pkg_dir.parent.parent
    if not (root / "plugins" / "arckit-claude").is_dir():
        # Fallback: maybe the package is installed from a different layout
        for candidate in pkg_dir.parents:
            if (candidate / "plugins" / "arckit-claude").is_dir():
                root = candidate
                break
    return root


def sync_generated(sources_root: Path) -> None:
    """Regenerate all three generated files into the local arckit_mcp dir.

    The generators in ``sources_root/scripts/`` are executed via
    ``python3``.  Each one writes to the path given as its first CLI arg
    (the CLI-arg override that was wired into the generators), so we pass
    the local vendor path explicitly.
    """
    local_pkg = Path(__file__).resolve().parent
    generator_dir = sources_root / "scripts"
    local_files = {
        "generate-mcp-registry.py": local_pkg / "_registry.py",
        "generate-mcp-gates.py": local_pkg / "gates.py",
        "generate-mcp-handoffs.py": local_pkg / "handoffs.py",
    }
    for script_name, out_path in local_files.items():
        script = generator_dir / script_name
        if not script.is_file():
            raise FileNotFoundError(f"Generator not found: {script}")
        print(f"sync: regenerating {out_path.name} ...")
        result = subprocess.run(
            [sys.executable, str(script), str(out_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            raise SystemExit(f"Generator {script_name} failed (rc={result.returncode})")
        print(f"sync: {out_path.name} OK")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate arckit_mcp generated files from installed ArcKit.",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="Path to the ArcKit source tree (default: auto-discover)",
    )
    args = parser.parse_args(argv)

    source_root = args.source_root or _find_source_root()
    print(f"sync: source root = {source_root}")
    sync_generated(source_root)


if __name__ == "__main__":
    main()
