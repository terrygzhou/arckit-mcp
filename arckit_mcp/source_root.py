"""Resolve the arc-kit source root (Design D2, full-command-relay change).

The source root is the top of an arc-kit checkout: the directory that
contains ``plugins/arckit-claude``.  Resolution tries, in order:

1. The ``ARCKIT_SOURCE_ROOT`` environment variable — used only when the
   path it names actually contains ``plugins/arckit-claude``; a set-but-
   invalid value falls through to Tier 2 instead of failing.
2. ``import arckit`` — resolve ``arckit.__file__`` and walk up its parents
   until a directory containing ``plugins/arckit-claude`` is found.
   Mirrors :func:`arckit_mcp.sync._find_source_root` (the only difference
   is this function returns ``None`` instead of raising ``SystemExit``).
3. ``None`` — no source root available.

The result is cached at module import time (``_RESOLVED_ROOT``) using a
sentinel that distinguishes "not yet resolved" from "resolved to None",
so the import/walk runs at most once per process.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Optional

__all__ = ["resolve_source_root"]

# Sentinel: distinguishes "not yet resolved" from a genuine None result.
_UNSET = object()

# Cached at module import; assigned once by the _resolve() call below.
_RESOLVED_ROOT: object = _UNSET

_MARKER = "plugins/arckit-claude"


def _looks_like_source_root(path: Path) -> bool:
    """True when ``path`` contains the ``plugins/arckit-claude`` directory."""
    try:
        return (path / "plugins" / "arckit-claude").is_dir()
    except OSError:
        return False


def _from_env() -> Optional[Path]:
    """Tier 1: the ``ARCKIT_SOURCE_ROOT`` env var, if valid."""
    raw = os.environ.get("ARCKIT_SOURCE_ROOT")
    if not raw:
        return None
    candidate = Path(raw).expanduser().resolve()
    if _looks_like_source_root(candidate):
        return candidate
    return None


def _from_arckit_package() -> Optional[Path]:
    """Tier 2: ``import arckit`` + walk up from ``arckit.__file__``."""
    try:
        arckit = importlib.import_module("arckit")
    except ImportError:
        return None
    file_path = getattr(arckit, "__file__", None)
    if not file_path:
        return None
    pkg_dir = Path(file_path).resolve().parent
    for candidate in pkg_dir.parents:
        if _looks_like_source_root(candidate):
            return candidate
    return None


def _resolve() -> Optional[Path]:
    """Run the three tiers once; never raises."""
    for tier in (_from_env, _from_arckit_package):
        try:
            result = tier()
        except Exception:
            result = None
        if result is not None:
            return result
    return None


def resolve_source_root() -> Optional[Path]:
    """Return the arc-kit source root, or ``None`` if unavailable.

    The result is computed once per process (at module import) and cached;
    subsequent calls return the cached value without re-doing the env-var
    check, the import, or the directory walk.
    """
    global _RESOLVED_ROOT
    if _RESOLVED_ROOT is _UNSET:
        _RESOLVED_ROOT = _resolve()
    return _RESOLVED_ROOT  # type: ignore[return-value]


def _reset_for_tests() -> None:
    """Test hook: restore the sentinel so the next call re-resolves."""
    global _RESOLVED_ROOT
    _RESOLVED_ROOT = _UNSET


# Task 1.3: cache at module import time.
_RESOLVED_ROOT = _resolve()
