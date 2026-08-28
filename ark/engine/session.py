"""Ephemeral ARK session state (phrase-level, pre-vault)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ark.security.memory import zero_bytearray


@dataclass
class ArkSession:
    """
    Ephemeral ARK session state.

    HARDENING:
    - master_key stored as bytearray so we can best-effort wipe on destroy().
    - destroy() should be called when UI closes.
    """

    master_key: bytearray
    phrase: str
    base_dir: str = "."
    aad_tag: bytes = b"ARK_V1"
    user_label: Optional[str] = None
    _destroyed: bool = False

    def destroy(self) -> None:
        if self._destroyed:
            return
        zero_bytearray(self.master_key)
        self.phrase = ""
        self._destroyed = True
