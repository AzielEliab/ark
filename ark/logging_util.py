"""Minimal crash logging for local debugging.

Writes to <data_dir>/logs/ark.log. Never logs phrases.
"""

from __future__ import annotations

import os
import traceback
from datetime import datetime
from pathlib import Path


def _log_path() -> str:
    from ark.config import DEFAULT_DATA_DIRNAME

    root = Path(os.getcwd()) / DEFAULT_DATA_DIRNAME / "logs"
    root.mkdir(parents=True, exist_ok=True)
    return str(root / "ark.log")


def log_exception(exc: BaseException) -> None:
    try:
        path = _log_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
            f.write(type(exc).__name__ + "\n")
            f.write(traceback.format_exc() + "\n")
    except Exception:
        pass
