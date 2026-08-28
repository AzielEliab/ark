"""Vault identity resolution.

ARK doctrine:
  - Every phrase is a login.
  - Every phrase deterministically opens exactly one vault.
  - No vault registry / selector UI.

Implementation:
  - Vaults live on disk under opaque random directory names.
  - A vault header stores its salt and a verification tag.
  - On login, ARK scans existing vaults and checks the verification tag.
  - If no match exists, a new vault is created.

That IS deniability: a wrong phrase silently creates/opens a different empty vault.
Empty vault indistinguishable from wrong phrase.

This avoids storing any phrase-derived path that would allow simple enumeration.
"""

from __future__ import annotations

import hashlib
import os
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from ark.utils import ensure_dir


def _digest16(data: bytes) -> bytes:
    try:
        from blake3 import blake3

        return blake3(data).digest(length=16)
    except Exception:
        return hashlib.blake2s(data, digest_size=16).digest()


def canonical_phrase(phrase: str) -> bytes:
    """Canonicalize a phrase for KDF input.

    - Normalize Unicode to NFKC to reduce accidental variants.
    - Preserve case and internal spacing.
    - Strip only trailing newlines from copy/paste.
    """
    p = unicodedata.normalize("NFKC", phrase).rstrip("\r\n")
    return p.encode("utf-8")


@dataclass(frozen=True)
class VaultMatch:
    vault_dir: str
    header_path: str
    salt: bytes
    verify_tag: bytes
    params_id: int


def vaults_base_dir(data_dir: str) -> str:
    root = Path(data_dir) / "vaults"
    ensure_dir(str(root))
    return str(root)


def iter_vault_dirs(data_dir: str) -> Iterable[str]:
    root = Path(vaults_base_dir(data_dir))
    if not root.exists():
        return []
    out = []
    for p in root.iterdir():
        if p.is_dir():
            out.append(str(p))
    return out


def new_vault_dir(data_dir: str) -> str:
    """Create a new opaque vault directory."""
    root = Path(vaults_base_dir(data_dir))
    ensure_dir(str(root))
    vid = os.urandom(16).hex()
    vdir = root / vid
    ensure_dir(str(vdir))
    return str(vdir)


def compute_verify_tag(k_meta: bytes) -> bytes:
    return _digest16(b"ARK:VERIFY" + k_meta)
