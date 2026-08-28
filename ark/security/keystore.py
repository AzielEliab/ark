"""Best-effort OS keystore helpers.

Optional device pepper (32 bytes) stored in OS keystore when available.
Optional monotonic epoch counters stored per vault to detect rollbacks.

Uses the `keyring` library if installed and a backend is available.
If unavailable, all functions gracefully fall back to None / False.
"""

from __future__ import annotations

import base64
import os
from typing import Optional

from ark.config import APP_NAME


def _service() -> str:
    return f"{APP_NAME}_KEYSTORE"


def _name(key: str) -> str:
    return f"{APP_NAME}:{key}"


def _have_keyring() -> bool:
    try:
        import keyring  # noqa: F401

        return True
    except Exception:
        return False


def get_or_create_pepper() -> Optional[bytes]:
    """Return a device-held 32-byte pepper, creating it if needed.

    If keyring is unavailable, returns None.
    """
    if not _have_keyring():
        return None
    import keyring

    k = _name("pepper")
    raw = keyring.get_password(_service(), k)
    if raw:
        try:
            b = base64.b64decode(raw.encode("ascii"))
            if len(b) == 32:
                return b
        except Exception:
            pass
    pep = os.urandom(32)
    keyring.set_password(_service(), k, base64.b64encode(pep).decode("ascii"))
    return pep


def get_epoch(vault_tag: str) -> Optional[int]:
    """Get stored monotonic epoch for a vault. None if keyring unavailable."""
    if not _have_keyring():
        return None
    import keyring

    k = _name(f"epoch:{vault_tag}")
    raw = keyring.get_password(_service(), k)
    if raw is None:
        return 0
    try:
        return int(raw)
    except Exception:
        return 0


def set_epoch(vault_tag: str, value: int) -> bool:
    """Set stored epoch for a vault. False if keyring unavailable."""
    if not _have_keyring():
        return False
    import keyring

    k = _name(f"epoch:{vault_tag}")
    keyring.set_password(_service(), k, str(int(value)))
    return True
