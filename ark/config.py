"""ARK configuration (v0.1). Keep constants here.

Production Argon2id profiles stay as spec (256/512/1024 MiB).
Tests MUST set ARK_TEST_KDF=1 to use tiny memory_cost (8 MiB, t=1).
"""

from __future__ import annotations

import os

APP_NAME = "ARK"
APP_VERSION = "0.1.0"

DEFAULT_DATA_DIRNAME = "ARK_DATA"

VAULT_SALT_SIZE = 16
FILE_NONCE_SIZE = 12

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1024  # 1 GiB soft limit

SECURITY_LEVELS = ("normal", "strong", "paranoid")

# Argon2id profiles (memory in KiB). Production defaults as spec.
KDF_PROFILES = {
    1: {"name": "normal", "time_cost": 3, "memory_cost_kib": 256 * 1024, "parallelism": 1},
    2: {"name": "strong", "time_cost": 4, "memory_cost_kib": 512 * 1024, "parallelism": 1},
    3: {"name": "paranoid", "time_cost": 4, "memory_cost_kib": 1024 * 1024, "parallelism": 1},
}

# Tiny profiles used ONLY when ARK_TEST_KDF=1. Never a production default.
TEST_KDF_PROFILES = {
    1: {"name": "normal", "time_cost": 1, "memory_cost_kib": 8 * 1024, "parallelism": 1},
    2: {"name": "strong", "time_cost": 1, "memory_cost_kib": 8 * 1024, "parallelism": 1},
    3: {"name": "paranoid", "time_cost": 1, "memory_cost_kib": 8 * 1024, "parallelism": 1},
}

AUTOLOCK_SECONDS = {
    "normal": 15 * 60,
    "strong": 5 * 60,
    "paranoid": 60,
}

# Application-layer decoy counts (behavior, not cryptography).
DECOY_COUNTS = {
    "normal": 0,
    "strong": 2,
    "paranoid": 8,
}

LIMITATION = (
    "Not a kernel, not a bootable OS, not a worm, not kernel isolation. "
    '"Rotating Kernel" means the rotating crypto/engine, not a Linux/Windows kernel. '
    "Local deniable vault. Forgotten phrase = permanent loss. Weak phrase = isolated "
    "vault compromise. Does not defeat live OS compromise while unlocked. Civilian software. "
    "HSM, kernel isolation, and classified OS are out of scope. Virus sweep is a local "
    "intake filter on files YOU put in YOUR vault, not a network AV product and not an exploit. "
    "A wrong phrase silently opens a different empty vault (deniability). Loopback UI, no telemetry. "
    "Hosted API never logs phrases and never stores vaults."
)


def test_kdf_enabled() -> bool:
    return os.environ.get("ARK_TEST_KDF") == "1"


def active_kdf_profiles() -> dict:
    """Return Argon2id profiles. Test env uses 8 MiB / t=1 only when ARK_TEST_KDF=1."""
    if test_kdf_enabled():
        return TEST_KDF_PROFILES
    return KDF_PROFILES


def params_id_for_level(level: str) -> int:
    lv = (level or "normal").lower().strip()
    if lv not in SECURITY_LEVELS:
        lv = "normal"
    return 1 if lv == "normal" else 2 if lv == "strong" else 3
