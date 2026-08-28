"""Open/create vault sessions.

Every phrase is a login. If no header matches, a new vault is created.
That IS deniability: a wrong phrase silently creates/opens a different empty vault.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from ark.config import SECURITY_LEVELS, active_kdf_profiles, params_id_for_level
from ark.crypto.kdf import derive_master_key
from ark.crypto.keys import Subkeys, derive_export_key, derive_subkeys
from ark.security.keystore import get_or_create_pepper
from ark.security.memory import zero_bytearray
from ark.utils import ensure_dir
from ark.vault import header as vault_header
from ark.vault.identity import (
    canonical_phrase,
    compute_verify_tag,
    iter_vault_dirs,
    new_vault_dir,
)


def _profile_for_level(level: str) -> Tuple[int, dict]:
    lv = (level or "normal").lower().strip()
    if lv not in SECURITY_LEVELS:
        lv = "normal"
    params_id = params_id_for_level(lv)
    return params_id, active_kdf_profiles()[params_id]


@dataclass
class ArkVaultSession:
    """Ephemeral session state for an unlocked vault."""

    phrase_bytes: bytearray
    data_dir: str
    vault_dir: str
    params_id: int
    salt: bytes
    k_master: bytearray
    subkeys: Subkeys
    export_key: bytes
    security_level: str
    _destroyed: bool = False

    @property
    def base_dir(self) -> str:
        # Back-compat alias used by megalith call sites.
        return self.data_dir

    def destroy(self) -> None:
        if self._destroyed:
            return
        zero_bytearray(self.phrase_bytes)
        zero_bytearray(self.k_master)
        self.export_key = b""
        self.subkeys = Subkeys(enc=b"", meta=b"", log=b"")
        self._destroyed = True


def open_or_create_vault(data_dir: str, phrase: str, security_level: str) -> ArkVaultSession:
    """Open the vault for phrase. If none exists, create a new one.

    Scans existing vault headers for a matching verification tag.
    A wrong phrase does not fail: it creates/opens a different empty vault.
    """
    params_id, prof = _profile_for_level(security_level)
    phrase_b = canonical_phrase(phrase)
    phrase_buf = bytearray(phrase_b)
    profiles = active_kdf_profiles()

    pepper = get_or_create_pepper()  # optional

    for vdir in iter_vault_dirs(data_dir):
        hpath = str(Path(vdir) / "header.bin")
        try:
            blob = Path(hpath).read_bytes()
            pid, salt, verify_tag = vault_header.unpack(blob)
            prof0 = profiles.get(pid)
            if not prof0:
                continue
            passphrase = bytes(phrase_buf) + (pepper or b"")
            k_master = derive_master_key(
                passphrase,
                salt,
                time_cost=prof0["time_cost"],
                memory_cost_kib=prof0["memory_cost_kib"],
                parallelism=prof0.get("parallelism", 1),
            )
            subs = derive_subkeys(k_master)
            if compute_verify_tag(subs.meta) == verify_tag:
                export_key = derive_export_key(k_master)
                return ArkVaultSession(
                    phrase_bytes=phrase_buf,
                    data_dir=data_dir,
                    vault_dir=vdir,
                    params_id=pid,
                    salt=salt,
                    k_master=bytearray(k_master),
                    subkeys=subs,
                    export_key=export_key,
                    security_level=prof0["name"],
                )
        except Exception:
            continue

    vdir = new_vault_dir(data_dir)
    ensure_dir(vdir)
    ensure_dir(str(Path(vdir) / "blocks"))
    for i in range(256):
        ensure_dir(str(Path(vdir) / "blocks" / f"{i:02x}"))

    salt = os.urandom(16)
    passphrase = bytes(phrase_buf) + (pepper or b"")
    k_master = derive_master_key(
        passphrase,
        salt,
        time_cost=prof["time_cost"],
        memory_cost_kib=prof["memory_cost_kib"],
        parallelism=prof.get("parallelism", 1),
    )
    subs = derive_subkeys(k_master)
    verify_tag = compute_verify_tag(subs.meta)
    Path(vdir, "header.bin").write_bytes(vault_header.pack(params_id, salt, verify_tag))

    export_key = derive_export_key(k_master)
    return ArkVaultSession(
        phrase_bytes=phrase_buf,
        data_dir=data_dir,
        vault_dir=vdir,
        params_id=params_id,
        salt=salt,
        k_master=bytearray(k_master),
        subkeys=subs,
        export_key=export_key,
        security_level=prof["name"],
    )
