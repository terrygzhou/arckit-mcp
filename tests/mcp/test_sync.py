"""TDD tests for arckit_mcp.sync.sync_generated.

Red phase: these tests are written before the sync module exists.
Green phase: sync.py implements sync_generated so these pass.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the package is importable without an editable install.
_ROOT = Path(__file__).resolve().parents[2]
_pkg = _ROOT / "arckit_mcp"
if str(_pkg) not in sys.path:
    sys.path.insert(0, str(_pkg))


class TestSyncGenerated:
    def test_calls_all_three_generators(self, tmp_path: Path):
        """sync_generated runs each generator script with the local out path."""
        # Create a fake source tree with the three generator scripts.
        src = tmp_path / "arc-kit"
        scripts = src / "scripts"
        scripts.mkdir(parents=True)
        for name in ("generate-mcp-registry.py", "generate-mcp-gates.py", "generate-mcp-handoffs.py"):
            (scripts / name).write_text("# fake generator\n")

        calls: list[tuple[Path, Path]] = []

        def fake_run(cmd, **kwargs):
            # cmd[0]=python, cmd[1]=script, cmd[2]=out_path
            calls.append((Path(cmd[1]), Path(cmd[2])))
            class R:
                returncode = 0
                stdout = ""
                stderr = ""
            return R()

        with patch("arckit_mcp.sync.subprocess.run", side_effect=fake_run):
            import arckit_mcp.sync as sync_mod
            sync_mod.sync_generated(src)

        assert len(calls) == 3
        script_names = [c[0].name for c in calls]
        assert "generate-mcp-registry.py" in script_names
        assert "generate-mcp-gates.py" in script_names
        assert "generate-mcp-handoffs.py" in script_names

    def test_out_paths_point_to_local_pkg(self, tmp_path: Path):
        """Each generator receives the correct local vendor path as CLI arg."""
        src = tmp_path / "arc-kit"
        scripts = src / "scripts"
        scripts.mkdir(parents=True)
        for name in ("generate-mcp-registry.py", "generate-mcp-gates.py", "generate-mcp-handoffs.py"):
            (scripts / name).write_text("")

        calls: list[tuple[Path, Path]] = []

        def fake_run(cmd, **kwargs):
            calls.append((Path(cmd[1]), Path(cmd[2])))
            class R:
                returncode = 0
                stdout = ""
                stderr = ""
            return R()

        with patch("arckit_mcp.sync.subprocess.run", side_effect=fake_run):
            import arckit_mcp.sync as sync_mod
            sync_mod.sync_generated(src)

        out_dir = Path(sync_mod.__file__).resolve().parent
        expected = {
            "generate-mcp-registry.py": out_dir / "_registry.py",
            "generate-mcp-gates.py": out_dir / "gates.py",
            "generate-mcp-handoffs.py": out_dir / "handoffs.py",
        }
        for script, out_path in calls:
            assert out_path == expected[script.name], (
                f"{script.name} should write to {expected[script.name]}, got {out_path}"
            )

    def test_missing_generator_raises(self, tmp_path: Path):
        """A missing generator script raises FileNotFoundError."""
        src = tmp_path / "arc-kit"
        scripts = src / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "generate-mcp-registry.py").write_text("")
        # gates.py and handoffs.py intentionally absent

        with pytest.raises(FileNotFoundError):
            import arckit_mcp.sync as sync_mod
            sync_mod.sync_generated(src)
