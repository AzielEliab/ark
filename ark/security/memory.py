"""Best-effort in-memory hygiene utilities.

Notes:
- Python cannot guarantee perfect zeroization due to copies/GC/optimizations.
- We still perform best-effort wiping for bytearray buffers we control.
"""

from __future__ import annotations

import ctypes
from typing import Optional


def zero_bytearray(buf: Optional[bytearray]) -> None:
    """Overwrite a bytearray in place (best effort)."""
    if buf is None:
        return
    try:
        length = len(buf)
        if length <= 0:
            return
        ptr = (ctypes.c_char * length).from_buffer(buf)
        ctypes.memset(ctypes.addressof(ptr), 0, length)
    except Exception:
        try:
            for i in range(len(buf)):
                buf[i] = 0
        except Exception:
            pass
