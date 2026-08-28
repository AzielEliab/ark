"""Key schedule for ARK.

Locked spec:
  - Argon2id derives K_master from phrase (+ optional pepper) and per-vault salt.
  - HKDF splits K_master into subkeys K_enc, K_meta, K_log.
  - Per-file key is derived from K_enc and a random nonce.
  Info labels: ARK:ENC / ARK:META / ARK:LOG / ARK:FILE.
"""

from __future__ import annotations

from dataclasses import dataclass

from ark.crypto.kdf import hkdf_expand


@dataclass(frozen=True)
class Subkeys:
    enc: bytes
    meta: bytes
    log: bytes


def derive_subkeys(k_master: bytes) -> Subkeys:
    # HKDF salt intentionally None (equivalent to empty) since k_master is already hardened by Argon2id.
    k_enc = hkdf_expand(k_master, salt=None, info=b"ARK:ENC", length=32)
    k_meta = hkdf_expand(k_master, salt=None, info=b"ARK:META", length=32)
    k_log = hkdf_expand(k_master, salt=None, info=b"ARK:LOG", length=32)
    return Subkeys(enc=k_enc, meta=k_meta, log=k_log)


def derive_file_key(k_enc: bytes, nonce: bytes) -> bytes:
    # Use nonce as HKDF salt to ensure unique per-file keys.
    return hkdf_expand(k_enc, salt=nonce, info=b"ARK:FILE", length=32)


def derive_export_key(k_master: bytes) -> bytes:
    return hkdf_expand(k_master, salt=None, info=b"ARK:EXPORT", length=32)
