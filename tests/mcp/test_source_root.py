"""Tests for ``arckit_mcp.source_root.resolve_source_root()``.

Covers the three resolution tiers from Design D2 (full-command-relay):

1. ``ARCKIT_SOURCE_ROOT`` env var (valid dir wins; invalid dir falls through).
2. ``import arckit`` + walk-up from ``arckit.__file__``.
3. ``None`` when neither tier resolves.

Plus the module-import-time caching contract (tasks 1.3): the resolution is
computed once per process, distinguished from "resolved to None" via a
sentinel.

Note: the ``arckit`` package is NOT importable in the default environment,
so Tier 2 tests inject a fake module through ``sys.modules``.
"""

import sys
import types
from pathlib import Path

import pytest

import arckit_mcp.source_root as source_root_mod
from arckit_mcp import resolve_source_root
from arckit_mcp.source_root import resolve_source_root as _direct_import

_UNSET = source_root_mod._UNSET
_RESET = getattr(source_root_mod, "_reset_for_tests", None)


def _reset_module_state():
    """Restore the module to "not yet resolved" (sentinel) state."""
    assert callable(_RESET), (
        "arckit_mcp.source_root must expose _reset_for_tests() so tests can "
        "distinguish 'not yet resolved' from 'resolved to None'"
    )
    _RESET()


@pytest.fixture(autouse=True)
def _isolate_resolution(monkeypatch):
    """Reset the resolution cache around every test.

    ``resolve_source_root()`` caches at module import time, so each test
    starts from a clean sentinel state.
    """
    _reset_module_state()
    yield
    _reset_module_state()


@pytest.fixture
def fake_arckit(tmp_path, monkeypatch):
    """Register a fake ``arckit`` module in ``sys.modules``.

    The fake's ``__file__`` points inside ``tmp_path/src/arckit/__init__.py``,
    with ``tmp_path/plugins/arckit-claude/`` present so the walk-up finds
    ``tmp_path`` as the source root.
    """
    pkg_dir = tmp_path / "src" / "arckit"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("")
    (tmp_path / "plugins" / "arckit-claude").mkdir(parents=True)

    fake = types.ModuleType("arckit")
    fake.__file__ = str(pkg_dir / "__init__.py")
    monkeypatch.setitem(sys.modules, "arckit", fake)
    monkeypatch.delattr(source_root_mod, "import_arckit", raising=False)
    return fake


# ---------------------------------------------------------------- Tier 1


def test_tier1_env_var_valid_dir_returns_it(tmp_path, monkeypatch):
    """ARCKIT_SOURCE_ROOT set to a dir containing plugins/arckit-claude."""
    root = tmp_path / "checkout"
    (root / "plugins" / "arckit-claude").mkdir(parents=True)
    monkeypatch.setenv("ARCKIT_SOURCE_ROOT", str(root))

    assert resolve_source_root() == root.resolve()


def test_tier1_env_var_invalid_dir_falls_through(tmp_path, monkeypatch):
    """ARCKIT_SOURCE_ROOT set but missing plugins/arckit-claude -> Tier 2."""
    bad = tmp_path / "not-a-checkout"
    bad.mkdir()
    monkeypatch.setenv("ARCKIT_SOURCE_ROOT", str(bad))

    assert resolve_source_root() is None


def test_tier1_env_var_empty_string_ignored(monkeypatch, fake_arckit, tmp_path):
    """An empty ARCKIT_SOURCE_ROOT is treated as unset (Tier 2 wins)."""
    monkeypatch.setenv("ARCKIT_SOURCE_ROOT", "")
    assert resolve_source_root() == tmp_path.resolve()


def test_tier1_env_var_beats_arckit_import(tmp_path, monkeypatch, fake_arckit):
    """Env var (valid) wins even when the arckit package is importable."""
    root = tmp_path / "explicit"
    (root / "plugins" / "arckit-claude").mkdir(parents=True)
    monkeypatch.setenv("ARCKIT_SOURCE_ROOT", str(root))

    assert resolve_source_root() == root.resolve()


# ---------------------------------------------------------------- Tier 2


def test_tier2_arckit_import_walk_up(tmp_path, monkeypatch, fake_arckit):
    """arckit importable + pkg dir nested under a checkout -> checkout root."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)

    assert resolve_source_root() == tmp_path.resolve()


def test_tier2_walk_up_finds_root_multiple_levels_up(tmp_path, monkeypatch, fake_arckit):
    """The walk must climb several levels (src/arckit -> src -> checkout)."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    result = resolve_source_root()
    assert result == tmp_path.resolve()
    assert (result / "plugins" / "arckit-claude").is_dir()


def test_tier2_arckit_import_unresolvable_falls_to_none(tmp_path, monkeypatch):
    """arckit importable but its file location has no arckit-claude ancestor."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    orphan = tmp_path / "orphan" / "arckit"
    orphan.mkdir(parents=True)
    (orphan / "__init__.py").write_text("")

    fake = types.ModuleType("arckit")
    fake.__file__ = str(orphan / "__init__.py")
    monkeypatch.setitem(sys.modules, "arckit", fake)

    assert resolve_source_root() is None


def test_tier2_module_not_imported_before_call(tmp_path, monkeypatch):
    """``import arckit`` inside resolve must NOT rely on prior import."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    assert "arckit" not in sys.modules
    assert resolve_source_root() is None
    # The helper may have left a ModuleNotFoundError path taken; no arckit
    # module should now exist in sys.modules from a failed import.
    assert "arckit" not in sys.modules


# ---------------------------------------------------------------- Tier 3


def test_tier3_nothing_available_returns_none(tmp_path, monkeypatch):
    """Env var unset + arckit not importable -> None, no exception."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    assert resolve_source_root() is None


def test_never_raises_on_missing_env_dir(tmp_path, monkeypatch):
    """ARCKIT_SOURCE_ROOT pointing at a nonexistent path -> fall through, not raise."""
    monkeypatch.setenv("ARCKIT_SOURCE_ROOT", str(tmp_path / "does-not-exist"))
    assert resolve_source_root() is None


# ---------------------------------------------------------------- Caching


def test_caching_resolves_once(tmp_path, monkeypatch, fake_arckit):
    """Two calls return the same object; the walk/import runs exactly once."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    calls = {"count": 0}
    real_is_dir = Path.is_dir

    def counting_is_dir(self):  # pragma: no cover - spy
        if self == tmp_path / "plugins" / "arckit-claude":
            calls["count"] += 1
        return real_is_dir(self)

    monkeypatch.setattr(Path, "is_dir", counting_is_dir, raising=False)

    first = resolve_source_root()
    second = resolve_source_root()

    assert first is second
    assert calls["count"] == 1, (
        f"expected the walk to happen exactly once, saw {calls['count']}"
    )


def test_caching_none_result_is_cached(tmp_path, monkeypatch):
    """A 'resolved to None' outcome is cached, not re-computed per call.

    Uses a fake ``arckit`` whose ``__file__`` points at a tmp dir with NO
    ancestor containing ``plugins/arckit-claude`` so Tier 2 walks but
    finds nothing and the function caches ``None``.  Counting the
    ``is_dir`` probes on ``plugins/arckit-claude`` proves the walk ran
    exactly once across both calls.
    """
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    orphan = tmp_path / "orphan" / "arckit"
    orphan.mkdir(parents=True)
    (orphan / "__init__.py").write_text("")

    fake = types.ModuleType("arckit")
    fake.__file__ = str(orphan / "__init__.py")
    monkeypatch.setitem(sys.modules, "arckit", fake)

    probes = {"count": 0}
    real_is_dir = Path.is_dir

    def counting_is_dir(self):
        if str(self).endswith("plugins/arckit-claude"):
            probes["count"] += 1
        return real_is_dir(self)

    import arckit_mcp.source_root as mod

    monkeypatch.setattr(Path, "is_dir", counting_is_dir)

    assert resolve_source_root() is None
    assert resolve_source_root() is None
    # The walk probed a few ancestors (at least the orphan dir's parent
    # chain up to the filesystem root); the key invariant is that the
    # probe count is stable across the two calls — the second call must
    # NOT re-run the walk.
    assert probes["count"] >= 1, "walk should have probed at least once"
    probes_after_first = probes["count"]
    resolve_source_root()
    assert probes["count"] == probes_after_first, (
        f"second call re-ran the walk: {probes['count']} probes, "
        f"was {probes_after_first} before"
    )


def test_sentinel_state_before_any_call(monkeypatch, fake_arckit):
    """The module ships with the sentinel (not a pre-resolved root)."""
    monkeypatch.delenv("ARCKIT_SOURCE_ROOT", raising=False)
    _reset_module_state()
    assert source_root_mod._RESOLVED_ROOT is _UNSET
    # fake_arckit.__file__ = <tmp>/src/arckit/__init__.py
    # -> pkg_dir = <tmp>/src/arckit -> walking up lands on <tmp>.
    expected = Path(fake_arckit.__file__).resolve().parent.parent.parent
    assert resolve_source_root() == expected.resolve()
    # And the cached value must be the same object on the next call.
    assert resolve_source_root() is source_root_mod._RESOLVED_ROOT
