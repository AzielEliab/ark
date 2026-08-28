"""The ARK (Aziel Rotating Kernel).

Local deniable vault. Every phrase is a login. One phrase → one vault.
AES-256-GCM, Argon2id, HKDF subkeys, Mode E intake filter.

Not a kernel, not a bootable OS, not a worm, not kernel isolation.
"Rotating Kernel" means the rotating crypto/engine, not a Linux/Windows kernel.

Author: Aziel Eliab, 2026. Apache-2.0.

Standalone from AZ-OS, GodLock, ForgeReceipts.

Forks are welcome and always allowed.
"""

from __future__ import annotations

from ark.config import APP_NAME, AUTOLOCK_SECONDS, SECURITY_LEVELS

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "APP_NAME",
    "AUTOLOCK_SECONDS",
    "SECURITY_LEVELS",
    "__version__",
]
