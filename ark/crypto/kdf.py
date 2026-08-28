"""Argon2id master-key derivation and HKDF-SHA256 expansion."""

from __future__ import annotations

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_master_key(
    passphrase: bytes,
    salt: bytes,
    *,
    time_cost: int,
    memory_cost_kib: int,
    parallelism: int = 1,
    length: int = 32,
) -> bytes:
    """Derive a master key from a phrase using Argon2id.

    NOTE: memory_cost is expressed in KiB for argon2-cffi.
    """
    return hash_secret_raw(
        secret=passphrase,
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost_kib,
        parallelism=parallelism,
        hash_len=length,
        type=Type.ID,
    )


def hkdf_expand(
    key_material: bytes,
    *,
    salt: bytes | None,
    info: bytes,
    length: int = 32,
) -> bytes:
    """HKDF expansion (SHA-256)."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
    )
    return hkdf.derive(key_material)
