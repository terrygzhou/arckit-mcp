"""Conftest for the arckit-mcp pytest suite.

Adds the repo root to ``sys.path`` so the test suite can import
``arckit_mcp`` without an editable install.
"""

import sys
from pathlib import Path

# arckit_mcp/ lives at the repo root, next to tests/.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
