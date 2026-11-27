"""Shared pytest configuration.

Points the application at a throwaway SQLite file *before* ``app`` is imported so
no test ever touches the developer's real ``lecmerge.db``.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="lecmerge-test-"))
os.environ.setdefault("LECMERGE_DATABASE_URL", f"sqlite:///{_TEST_DB_DIR / 'test.db'}")
