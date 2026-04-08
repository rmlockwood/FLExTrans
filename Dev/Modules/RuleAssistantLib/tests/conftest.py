"""Pytest configuration for tests."""

import sys
from pathlib import Path

# Add the parent of src-py directory to the path so imports work correctly
src_py_parent = Path(__file__).parent.parent.parent
if str(src_py_parent) not in sys.path:
    sys.path.insert(0, str(src_py_parent))
