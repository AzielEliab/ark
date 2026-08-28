"""Filesystem and platform helpers."""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path
from typing import Optional


def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def is_windows() -> bool:
    return os.name == "nt"


def best_effort_hide_console_relaunch(argv: Optional[list] = None) -> bool:
    """Windows only: relaunch with pythonw.exe to avoid console."""
    if not is_windows():
        return False
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        return False
    pythonw = exe[:-10] + "pythonw.exe" if exe.lower().endswith("python.exe") else None
    if not pythonw or not os.path.exists(pythonw):
        return False
    if argv is None:
        argv = sys.argv
    try:
        import subprocess

        subprocess.Popen([pythonw] + argv, close_fds=True)
        return True
    except Exception:
        return False


def random_bytes(n: int) -> bytes:
    return secrets.token_bytes(n)


def resolve_data_dir(explicit: str | None = None) -> str:
    """Data dir is ./ARK_DATA under cwd, or --data. Never a cloud vault."""
    from ark.config import DEFAULT_DATA_DIRNAME

    if explicit:
        p = Path(explicit).expanduser().resolve()
    else:
        p = (Path.cwd() / DEFAULT_DATA_DIRNAME).resolve()
    ensure_dir(str(p))
    return str(p)
