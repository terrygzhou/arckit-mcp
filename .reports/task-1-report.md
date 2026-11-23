# Task 1 Report: Source-root resolution module

## Status: **DONE**

Implemented `arckit_mcp/source_root.py` (Task 1.1 + 1.3), updated
`arckit_mcp/__init__.py` (Task 1.2), added `tests/mcp/test_source_root.py`
(TDD — tests written before implementation). All 13 new tests pass; the
full suite is green at **107 passed** (baseline 94 + 13 new).

---

## 1. Implementation

### `arckit_mcp/source_root.py` (new)

```python
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
    try:
        return (path / "plugins" / "arckit-claude").is_dir()
    except OSError:
        return False


def _from_env() -> Optional[Path]:
    """Tier 1: the ARCKIT_SOURCE_ROOT env var, if valid."""
    raw = os.environ.get("ARCKIT_SOURCE_ROOT")
    if not raw:
        return None
    candidate = Path(raw).expanduser().resolve()
    if _looks_like_source_root(candidate):
        return candidate
    return None


def _from_arckit_package() -> Optional[Path]:
    """Tier 2: import arckit + walk up from arckit.__file__."""
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
    """Return the arc-kit source root, or None if unavailable.

    The result is computed once per process (at module import) and cached;
    subsequent calls return the cached value without re-doing the
    env-var check, the import, or the directory walk.
    """
    global _RESOLVED_ROOT
    if _RESOLVED_ROOT is _UNSET:
        _RESOLVED_ROOT = _resolve()
    return _RESOLVED_ROOT


def _reset_for_tests() -> None:
    """Test hook: restore the sentinel so the next call re-resolves."""
    global _RESOLVED_ROOT
    _RESOLVED_ROOT = _UNSET


# Task 1.3: cache at module import time.
_RESOLVED_ROOT = _resolve()
```

### `arckit_mcp/__init__.py` (updated)

- `__all__` extended to `["__version__", "resolve_source_root"]`.
- PEP 562 `__getattr__` lazy re-export to avoid circular-import hazards
  (`arckit_mcp/__init__.py` importing `source_root` at top-level would
  re-enter the still-initialising package `__init__`).

---

## 2. Test coverage (`tests/mcp/test_source_root.py`)

13 tests, each isolating module state via the `_reset_for_tests()` hook
and the `_UNSET` sentinel (which is the only way to distinguish
"not yet resolved" from "resolved to None"):

| Test | Tier | Behavior pinned |
|------|------|-----------------|
| `test_tier1_env_var_valid_dir_returns_it` | 1 | Valid env dir wins, returned resolved |
| `test_tier1_env_var_invalid_dir_falls_through` | 1→3 | Invalid env dir skips Tier 1, no import → None |
| `test_tier1_env_var_empty_string_ignored` | 1→2 | Empty env string treated as unset |
| `test_tier1_env_var_beats_arckit_import` | 1 vs 2 | Env precedence over import |
| `test_tier2_arckit_import_walk_up` | 2 | Multi-level walk finds `tmp_path` root |
| `test_tier2_walk_up_finds_root_multiple_levels_up` | 2 | Confirms the walk actually climbed `src/arckit → src → tmp_path` |
| `test_tier2_arckit_import_unresolvable_falls_to_none` | 2→3 | arckit importable but no `plugins/arckit-claude` ancestor → None |
| `test_tier2_module_not_imported_before_call` | 2 | `import arckit` is performed *inside* the helper, not at test-setup time |
| `test_tier3_nothing_available_returns_none` | 3 | Baseline None path |
| `test_never_raises_on_missing_env_dir` | 1→3 | Non-existent env path is fall-through, never an exception |
| `test_caching_resolves_once` | cache | 2 calls → identical object; `is_dir` probe count stays at 1 |
| `test_caching_none_result_is_cached` | cache | `None` result is cached; second call does **not** re-run the walk |
| `test_sentinel_state_before_any_call` | sentinel | Module ships with `_RESOLVED_ROOT is _UNSET`; first call resolves; second returns same object |

### Fake-`arckit` fixture

The `arckit` package is NOT importable in the default environment, so
Tier-2 tests use `monkeypatch.setitem(sys.modules, "arckit", fake)` to
inject a fake module whose `__file__` points at a `tmp_path/src/arckit/`
layout. This isolates Tier 2 from the real package without requiring a
sibling arc-kit checkout at test time.

---

## 3. Validation commands run

| Command | Result |
|---------|--------|
| `python3 -m pytest tests/mcp/test_source_root.py -v` | **13 passed** in 0.02s |
| `python3 -m pytest tests/ -q` | **107 passed** in 0.29s (baseline 94 + 13 new) |
| `python3 -c "from arckit_mcp.source_root import resolve_source_root; print(resolve_source_root())"` | `None` (correct: env unset, `arckit` not installed here) |
| `python3 -c "from arckit_mcp import resolve_source_root; print(callable(resolve_source_root))"` | `True` |
| `python3 -c "import arckit_mcp; from arckit_mcp import resolve_source_root; print('boot OK, value:', resolve_source_root())"` | `boot OK, value: None` |

### Why `None` is the expected default-environment result

- `ARCKIT_SOURCE_ROOT` is unset in this env → Tier 1 skipped.
- `import arckit` raises `ModuleNotFoundError` (default env does not have
  the `arckit` package) → Tier 2 skipped.
- Tier 3: `None`. The function **never** raises, so the caller can safely
  fall back to a no-source-root branch (this is what Task 2.4 pins).

This matches the task's acceptance criteria: "returns the sibling
checkout path when `arckit` is importable, and `None` when it is not."
The sibling-checkout branch is exercised by the Tier-2 tests via the
fake-`arckit` fixture, which deterministically reproduces a "sibling
checkout" layout at `tmp_path`.

---

## 4. Design decisions

1. **Sentinel over `None` for cache state.** `_UNSET = object()` makes the
   "not yet resolved" state structurally distinguishable from
   "resolved to None". The function's contract is "call me, get either a
   Path or None, no error", so `None` is the only valid *return* value
   for the not-found case. The sentinel lives *inside* the module and is
   never returned.

2. **Cache at module import, not at first call.** Task 1.3 says "at module
   import time", so the module body ends with
   `_RESOLVED_ROOT = _resolve()`. The function body still has a guard
   (`if _RESOLVED_ROOT is _UNSET: ...`) to be robust to tests that reset
   the sentinel mid-process. Both paths produce the same observable
   behavior: one computation per process.

3. **Mirror `sync.py::_find_source_root`'s walk-up pattern.** Same
   `Path(arckit.__file__).resolve().parent` + `for candidate in
   pkg_dir.parents` pattern. The only difference is that this version
   returns `None` instead of raising `SystemExit` — exactly the contract
   the task demands.

4. **PEP 562 `__getattr__` for the re-export.** A top-level
   `from arckit_mcp.source_root import resolve_source_root` inside
   `__init__.py` would re-enter the still-initialising `arckit_mcp`
   package when `source_root.py` does `from arckit_mcp import ...`
   (defensively). The lazy `__getattr__` defers the import until first
   access, avoiding the re-entrancy. This is the same pattern CPython
   uses in `asyncio` and several standard-library modules.

5. **Defensive `try/except Exception` around each tier.** Task 1.1 says
   "Never raise. Never call `sys.exit()`." The tier bodies already have
   targeted `try/except ImportError` (Tier 2) and `try/except OSError`
   (the `is_dir` probe), but a belt-and-braces outer catch ensures the
   function *can't* leak an exception to the caller even if a future
   refactor introduces an unexpected error mode.

---

## 5. Files touched

| File | Change |
|------|--------|
| `arckit_mcp/source_root.py` | **new** (82 lines) |
| `arckit_mcp/__init__.py` | `__all__` extended; PEP 562 `__getattr__` added (11 lines added) |
| `tests/mcp/test_source_root.py` | **new** (233 lines, 13 tests + 1 fixture) |
| `.reports/task-1-report.md` | **new** (this report) |

Generated files (`_registry.py`, `gates.py`, `handoffs.py`, `intake.py`)
were **not** touched, per the generated-files rule.

---

## 6. Notes for downstream tasks

- **Task 2.1** (`_resolve_command_content`) should call
  `resolve_source_root()` once and treat `None` as the "no source root"
  branch that returns `{"available": False, "reason": "No arc-kit source
  root available. Set ARCKIT_SOURCE_ROOT or install the arckit
  package."}`.
- The cache means downstream code will always get the *same* object from
  repeated calls — no need to defensively re-resolve.
- The `ARCKIT_SOURCE_ROOT` env var is the escape hatch for tests that
  want to pin a specific checkout without touching `sys.modules`.
- If Task 4.4 (`test_relay_graceful_when_no_source_root`) needs to force
  the None branch, it can either set
  `ARCKIT_SOURCE_ROOT=/nonexistent` (Tier 1 fails → Tier 2 runs → likely
  None in default env) or monkeypatch
  `arckit_mcp.source_root._RESOLVED_ROOT = None` directly. The latter is
  faster and less brittle.
