# ARK v2.0 Timeless — Megalithic Single-File Build
# Generated: 2026-01-04T22:56:06.627987Z

from __future__ import annotations


# === BEGIN ark_core/config.py ===
"""ARK configuration (v1). Keep constants here."""

APP_NAME = "ARK"
APP_VERSION = "1.0.0-v1-skeleton"

DEFAULT_DATA_DIRNAME = "ARK_DATA"

VAULT_SALT_SIZE = 16
FILE_NONCE_SIZE = 12

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1024  # 1 GiB soft limit for v1

# Security levels (timeless, frozen)
SECURITY_LEVELS = ("normal", "strong", "paranoid")

# Argon2id profiles (memory in KiB)
KDF_PROFILES = {
    # m=256MB, t=3, p=1
    1: {"name": "normal", "time_cost": 3, "memory_cost_kib": 256 * 1024, "parallelism": 1},
    # m=512MB, t=4, p=1
    2: {"name": "strong", "time_cost": 4, "memory_cost_kib": 512 * 1024, "parallelism": 1},
    # m=1024MB, t=4, p=1
    3: {"name": "paranoid", "time_cost": 4, "memory_cost_kib": 1024 * 1024, "parallelism": 1},
}

AUTOLOCK_SECONDS = {
    "normal": 15 * 60,
    "strong": 5 * 60,
    "paranoid": 60,
}
# === END ark_core/config.py ===


# === BEGIN ark_core/errors.py ===
"""Centralized exceptions for ARK."""

class ArkError(Exception):
    """Base class for all ARK exceptions."""

class ArkConfigError(ArkError):
    pass

class ArkVaultError(ArkError):
    pass

class ArkCryptoError(ArkError):
    pass

class ArkIOError(ArkError):
    pass
# === END ark_core/errors.py ===


# === BEGIN ark_core/utils.py ===
import os
import sys
import secrets
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
# === END ark_core/utils.py ===


# === BEGIN ark_core/logging_util.py ===
"""Minimal crash logging for local debugging.
Writes to ARK_DATA/logs/ark.log in the current working directory.
"""

import os
import traceback
from datetime import datetime
from pathlib import Path

def _log_path() -> str:
    root = Path(os.getcwd()) / "ARK_DATA" / "logs"
    root.mkdir(parents=True, exist_ok=True)
    return str(root / "ark.log")

def log_exception(exc: BaseException) -> None:
    try:
        path = _log_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + "="*80 + "\n")
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
            f.write(repr(exc) + "\n")
            f.write(traceback.format_exc() + "\n")
    except Exception:
        pass
# === END ark_core/logging_util.py ===


# === BEGIN ark_core/security/errors.py ===
"""Uniform error strategy to reduce oracle surface."""

def uniform_failure_message() -> str:
    # Same message for wrong passphrase, wrong vault phrase, corrupted file, etc.
    return "Unlock/decrypt failed."
# === END ark_core/security/errors.py ===


# === BEGIN ark_core/security/memory.py ===
"""Best-effort in-memory hygiene utilities.

Notes:
- Python cannot guarantee perfect zeroization due to copies/GC/optimizations.
- We still perform best-effort wiping for bytearray buffers we control.
"""

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
# === END ark_core/security/memory.py ===


# === BEGIN ark_core/security/keystore.py ===
"""Best-effort OS keystore helpers.

ARK v2.0 Timeless Spec:
  - Optional device pepper (32 bytes) stored in OS keystore when available.
  - Optional monotonic epoch counters stored per vault to detect rollbacks.

This module uses the `keyring` library if installed and a backend is available.
If unavailable, all functions gracefully fall back to None / False.
"""


import base64
import os
from typing import Optional



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
    """Get stored monotonic epoch for a vault.

Returns None if keyring unavailable.
"""
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
    """Set stored epoch for a vault.

Returns False if keyring unavailable.
"""
    if not _have_keyring():
        return False
    import keyring

    k = _name(f"epoch:{vault_tag}")
    keyring.set_password(_service(), k, str(int(value)))
    return True
# === END ark_core/security/keystore.py ===


# === BEGIN ark_core/security/virus.py ===
"""Mode E virus sweep.

Security-first policy:
  - If flagged, ARK refuses to encrypt/store the payload.
  - ARK does not quarantine the content; it records only hashes/reason codes in logs.

This module provides:
  - lightweight heuristic checks (always on)
  - optional offline clamscan invocation if available
"""


import hashlib
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Tuple

from blake3 import blake3


class VirusFlagged(Exception):
    """Raised when Mode E flags a payload."""


@dataclass(frozen=True)
class VirusFinding:
    kind: str
    detail: str


def _heuristics(data: bytes) -> List[VirusFinding]:
    findings: List[VirusFinding] = []

    # Simple magic / script heuristics. Conservative: flag only strong signals.
    head = data[:8192].lower()

    # Windows PE
    if len(data) > 2 and data[:2] == b"MZ":
        findings.append(VirusFinding("heuristic", "PE/MZ executable"))

    # ELF
    if data[:4] == b"\x7fELF":
        findings.append(VirusFinding("heuristic", "ELF executable"))

    # Mach-O
    if data[:4] in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"):
        findings.append(VirusFinding("heuristic", "Mach-O or fat binary"))

    # Obvious script stagers
    if b"powershell" in head and b"-enc" in head:
        findings.append(VirusFinding("heuristic", "PowerShell encoded command"))

    if b"wget" in head and b"|" in head and (b"sh" in head or b"bash" in head):
        findings.append(VirusFinding("heuristic", "download-pipe-exec pattern"))

    if b"curl" in head and b"|" in head and (b"sh" in head or b"bash" in head):
        findings.append(VirusFinding("heuristic", "download-pipe-exec pattern"))

    # Macro-ish indicators
    if b"vba" in head and b"autoopen" in head:
        findings.append(VirusFinding("heuristic", "macro autoopen indicator"))

    return findings


def _clam_available() -> bool:
    return shutil.which("clamscan") is not None


def _clam_scan_bytes(data: bytes) -> List[VirusFinding]:
    if not _clam_available():
        return []
    # Write to temp file and scan offline.
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data)
        tmp_path = tf.name
    try:
        proc = subprocess.run(
            ["clamscan", "--no-summary", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            text=True,
        )
        out = (proc.stdout or "").strip()
        # clamscan exits 0 (clean), 1 (infected), 2 (error)
        if proc.returncode == 1:
            # Example: /tmp/file: Eicar-Test-Signature FOUND
            findings = [VirusFinding("clamscan", out[-200:])]
            return findings
        return []
    except Exception as e:
        # Fail-closed for scanning engine errors? Security-first: treat as finding.
        return [VirusFinding("clamscan", f"scan error: {e}")]
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def scan_bytes(data: bytes) -> Tuple[bytes, List[VirusFinding]]:
    """Return (hash, findings)."""
    h = blake3(data).digest(length=16)
    findings = []
    findings.extend(_heuristics(data))
    findings.extend(_clam_scan_bytes(data))
    return h, findings


def scan_bytes_or_raise(data: bytes) -> None:
    _h, findings = scan_bytes(data)
    if findings:
        # Do not include hashes or verbose info in exceptions; keep uniform.
        raise VirusFlagged("ARK blocked file (Mode E)")
# === END ark_core/security/virus.py ===


# === BEGIN ark_core/crypto/keys.py ===
"""Key schedule for ARK v1.0.

Locked spec:
  - Argon2id derives K_master from phrase (+ optional pepper) and per-vault salt.
  - HKDF splits K_master into subkeys K_enc, K_meta, K_log.
  - Per-file key is derived from K_enc and a random nonce.
"""


from dataclasses import dataclass



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
# === END ark_core/crypto/keys.py ===


# === BEGIN ark_core/crypto/kdf.py ===
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from argon2.low_level import hash_secret_raw, Type


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
        type=Type.ID
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
# === END ark_core/crypto/kdf.py ===


# === BEGIN ark_core/crypto/aead.py ===
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

NONCE_SIZE = 12  # AES-GCM standard


def encrypt(plaintext: bytes, key: bytes, aad: bytes = b"") -> dict:
    """Encrypt plaintext using AES-GCM. Returns nonce + ciphertext."""
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return {"nonce": nonce, "ciphertext": ciphertext}


def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, aad: bytes = b"") -> bytes:
    """Decrypt ciphertext using AES-GCM. Raises on failure."""
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
# === END ark_core/crypto/aead.py ===


# === BEGIN ark_core/vault/layout.py ===
from pathlib import Path



def blocks_bucket_dir(vault_dir: str, bucket_hex: str) -> str:
    d = Path(vault_dir) / "blocks" / bucket_hex
    ensure_dir(str(d))
    return str(d)


def blocks_root(vault_dir: str) -> str:
    d = Path(vault_dir) / "blocks"
    ensure_dir(str(d))
    return str(d)


def exports_root(vault_dir: str) -> str:
    d = Path(vault_dir) / "exports"
    ensure_dir(str(d))
    return str(d)
# === END ark_core/vault/layout.py ===


# === BEGIN ark_core/vault/naming.py ===
import uuid

def new_file_id() -> str:
    """Generate a random opaque file id for on-disk storage."""
    return uuid.uuid4().hex
# === END ark_core/vault/naming.py ===


# === BEGIN ark_core/vault/header.py ===
"""Vault header format.

header.bin is stored in the vault root directory.

Fields (binary):
  MAGIC(4) | VER(1) | PARAMS_ID(1) | SALT(16) | VERIFY_TAG(16)

- SALT is per-vault random.
- VERIFY_TAG is derived from K_meta and is used to locate the vault for a given phrase.

This header contains no plaintext phrase, no vault name, and no global index.
"""


import struct
from typing import Tuple

MAGIC = b"ARV1"
VERSION = 1

FMT = ">4sBB16s16s"
SIZE = struct.calcsize(FMT)


def pack(params_id: int, salt: bytes, verify_tag: bytes) -> bytes:
    if not (0 <= params_id <= 255):
        raise ValueError("params_id must fit in a byte")
    if len(salt) != 16:
        raise ValueError("salt must be 16 bytes")
    if len(verify_tag) != 16:
        raise ValueError("verify_tag must be 16 bytes")
    return struct.pack(FMT, MAGIC, VERSION, params_id, salt, verify_tag)


def unpack(blob: bytes) -> Tuple[int, bytes, bytes]:
    if len(blob) < SIZE:
        raise ValueError("header too small")
    magic, ver, params_id, salt, verify_tag = struct.unpack(FMT, blob[:SIZE])
    if magic != MAGIC:
        raise ValueError("bad magic")
    if ver != VERSION:
        raise ValueError("unsupported version")
    return params_id, salt, verify_tag
# === END ark_core/vault/header.py ===


# === BEGIN ark_core/vault/manifest.py ===
import json
import os
from typing import Dict, Any

MANIFEST_FILENAME = "manifest.ark"

def _manifest_path(session) -> str:
    return os.path.join(session.vault_dir, MANIFEST_FILENAME)

def load_manifest(session) -> Dict[str, Any]:
    path = _manifest_path(session)
    if not os.path.exists(path):
        return {"version": 1, "created_at": int(__import__("time").time()), "entries": {}}
    with open(path, "rb") as f:
        blob = f.read()
    data = decrypt_bytes(session, blob)
    obj = json.loads(data.decode("utf-8"))
    obj.setdefault("entries", {})
    return obj

def save_manifest(session, manifest: Dict[str, Any]) -> str:
    path = _manifest_path(session)
    payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    blob = encrypt_bytes(session, payload)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
    return path
# === END ark_core/vault/manifest.py ===


# === BEGIN ark_core/vault/container.py ===
"""Per-file container format.

Stored for each encrypted payload.

Header:
  MAGIC(4) | VER(1) | NONCE(12) | CIPHERTEXT_LEN(8)

Vault salt and KDF params live in vault header.bin (vault-level), not per file.
"""


import struct
from typing import Tuple

MAGIC = b"ARF1"
VERSION = 1

HEADER_FMT = ">4sB12sQ"
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(file_nonce: bytes, ciphertext_len: int) -> bytes:
    if len(file_nonce) != 12:
        raise ValueError("file_nonce must be 12 bytes")
    return struct.pack(HEADER_FMT, MAGIC, VERSION, file_nonce, int(ciphertext_len))


def unpack_header(data: bytes) -> Tuple[bytes, int]:
    if len(data) < HEADER_SIZE:
        raise ValueError("Invalid container: header too small")
    magic, version, file_nonce, ciphertext_len = struct.unpack(HEADER_FMT, data[:HEADER_SIZE])
    if magic != MAGIC:
        raise ValueError("Invalid container: bad magic")
    if version != VERSION:
        raise ValueError("Unsupported container version")
    return file_nonce, int(ciphertext_len)
# === END ark_core/vault/container.py ===


# === BEGIN ark_core/vault/identity.py ===
"""Vault identity resolution.

ARK v1.0 doctrine:
  - Every phrase is a login.
  - Every phrase deterministically opens exactly one vault.
  - No vault registry / selector UI.

Implementation reality:
  - Vaults live on disk under opaque random directory names.
  - A vault header stores its salt and a verification tag.
  - On login, ARK scans existing vaults and checks the verification tag.
  - If no match exists, a new vault is created.

This avoids storing any phrase-derived path that would allow simple enumeration.
"""


import os
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from blake3 import blake3



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


def vaults_base_dir(base_dir: str) -> str:
    root = Path(base_dir) / DEFAULT_DATA_DIRNAME / "vaults"
    ensure_dir(str(root))
    return str(root)


def iter_vault_dirs(base_dir: str) -> Iterable[str]:
    root = Path(vaults_base_dir(base_dir))
    if not root.exists():
        return []
    for p in root.iterdir():
        if p.is_dir():
            yield str(p)


def new_vault_dir(base_dir: str) -> str:
    """Create a new opaque vault directory."""
    root = Path(vaults_base_dir(base_dir))
    ensure_dir(str(root))
    # 128-bit opaque id
    vid = os.urandom(16).hex()
    vdir = root / vid
    ensure_dir(str(vdir))
    return str(vdir)


def compute_verify_tag(k_meta: bytes) -> bytes:
    return blake3(b"ARK:VERIFY" + k_meta).digest(length=16)
# === END ark_core/vault/identity.py ===


# === BEGIN ark_core/engine/session.py ===
from dataclasses import dataclass
from typing import Optional



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
        self._destroyed = True
# === END ark_core/engine/session.py ===


# === BEGIN ark_core/engine/vault_session.py ===
"""Open/create vault sessions.

Implements ARK v1.0 Timeless Spec decisions 1–9.
"""


import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple



def _profile_for_level(level: str) -> Tuple[int, dict]:
    lv = (level or "normal").lower().strip()
    if lv not in SECURITY_LEVELS:
        lv = "normal"
    # Map level -> params_id
    params_id = 1 if lv == "normal" else 2 if lv == "strong" else 3
    return params_id, KDF_PROFILES[params_id]


@dataclass
class ArkVaultSession:
    """Ephemeral session state for an unlocked vault."""

    phrase_bytes: bytearray
    base_dir: str
    vault_dir: str
    params_id: int
    salt: bytes
    k_master: bytearray
    subkeys: Subkeys
    export_key: bytes
    security_level: str
    _destroyed: bool = False

    def destroy(self) -> None:
        if self._destroyed:
            return
        # Best-effort zeroization
        zero_bytearray(self.phrase_bytes)
        zero_bytearray(self.k_master)
        self._destroyed = True


def open_or_create_vault(base_dir: str, phrase: str, security_level: str) -> ArkVaultSession:
    """Open the vault for phrase. If none exists, create a new one.

    The function scans existing vault headers to find a matching verification tag.
    """
    params_id, prof = _profile_for_level(security_level)
    phrase_b = canonical_phrase(phrase)
    phrase_buf = bytearray(phrase_b)

    pepper = get_or_create_pepper()  # optional

    # Try match existing vaults
    for vdir in iter_vault_dirs(base_dir):
        hpath = str(Path(vdir) / "header.bin")
        try:
            blob = Path(hpath).read_bytes()
            pid, salt, verify_tag = vault_header.unpack(blob)
            prof0 = KDF_PROFILES.get(pid)
            if not prof0:
                continue
            # derive key for this vault header
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
                # Found it
                export_key = derive_export_key(k_master)
                return ArkVaultSession(
                    phrase_bytes=phrase_buf,
                    base_dir=base_dir,
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

    # Create new vault
    vdir = new_vault_dir(base_dir)
    ensure_dir(vdir)
    ensure_dir(str(Path(vdir) / "blocks"))
    for i in range(256):
        ensure_dir(str(Path(vdir) / "blocks" / f"{i:02x}"))

    salt = os.urandom(16)
    passphrase = bytes(phrase_buf) + (pepper or b"")
    # Use requested security level's profile for new vault
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
        base_dir=base_dir,
        vault_dir=vdir,
        params_id=params_id,
        salt=salt,
        k_master=bytearray(k_master),
        subkeys=subs,
        export_key=export_key,
        security_level=prof["name"],
    )
# === END ark_core/engine/vault_session.py ===


# === BEGIN ark_core/engine/encrypt.py ===
"""Encryption engine.

Security-first:
  - Always runs Mode E virus sweep before writing encrypted payloads.
  - Uses per-file random nonce and HKDF-derived file key.
"""


import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM



def encrypt_bytes(session, plaintext: bytes) -> bytes:
    if len(plaintext) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File too large for ARK v1")

    # Mode E sweep (mandatory)
    scan_bytes_or_raise(plaintext)

    nonce = os.urandom(FILE_NONCE_SIZE)
    file_key = derive_file_key(session.subkeys.enc, nonce)
    ciphertext = AESGCM(file_key).encrypt(nonce, plaintext, b"ARK:V1")
    return pack_header(nonce, len(ciphertext)) + ciphertext


def encrypt_file(session, in_path: str, out_path: str) -> str:
    with open(in_path, "rb") as f:
        plaintext = f.read()
    blob = encrypt_bytes(session, plaintext)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(blob)
    os.replace(tmp_path, out_path)
    return out_path
# === END ark_core/engine/encrypt.py ===


# === BEGIN ark_core/engine/decrypt.py ===
"""Decryption engine.

Uniform failure behavior to reduce oracle surfaces.
"""


import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM



class DecryptionFailed(Exception):
    pass


def decrypt_bytes(session, blob: bytes) -> bytes:
    try:
        nonce, ct_len = unpack_header(blob)
        ciphertext = blob[HEADER_SIZE:HEADER_SIZE + ct_len]
        if len(ciphertext) != ct_len:
            raise DecryptionFailed(uniform_failure_message())
        file_key = derive_file_key(session.subkeys.enc, nonce)
        return AESGCM(file_key).decrypt(nonce, ciphertext, b"ARK:V1")
    except DecryptionFailed:
        raise
    except Exception:
        raise DecryptionFailed(uniform_failure_message())


def decrypt_file(session, in_path: str, out_path: str) -> str:
    with open(in_path, "rb") as f:
        blob = f.read()
    plaintext = decrypt_bytes(session, blob)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(plaintext)
    os.replace(tmp_path, out_path)
    return out_path
# === END ark_core/engine/decrypt.py ===


# === BEGIN ark_core/engine/cleanup.py ===
"""Session cleanup helpers."""



def close_session(session: ArkVaultSession) -> None:
    """Central place to close a session."""
    try:
        session.destroy()
    except Exception:
        pass
# === END ark_core/engine/cleanup.py ===


# === BEGIN ark_core/ui/colors.py ===
PALETTE=['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'indigo', 'violet', 'pink', 'white', 'gray', 'black']
THEME_BG="#000000"
THEME_PANEL="#0b0b0b"
THEME_FG="#d4af37"
TAG_HEX={
    'red': '#f44',
    'orange': '#f93',
    'yellow': '#fe6',
    'green': '#5f8',
    'cyan': '#4df',
    'blue': '#47f',
    'indigo': '#75f',
    'violet': '#b4f',
    'pink': '#f6d',
    'white': '#fff',
    'gray': '#bbb',
    'black': '#000',
}

def normalize_color(s:str)->str:
    return (s or "").strip().lower()
def tag_to_hex(tag:str)->str:
    return TAG_HEX.get(normalize_color(tag), "")
# === END ark_core/ui/colors.py ===


# === BEGIN ark_core/ui/console.py ===
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox



def _vault_tag(session) -> str:
    # Opaque on-disk vault directory name
    return os.path.basename(session.vault_dir)


def _safe_tag_hex(tag: str) -> str:
    hx = tag_to_hex(tag)
    # black-on-black is invisible; keep it readable
    if hx.lower() in ("#000", "#000000"):
        return "#bbb"
    return hx or THEME_FG


class ConsoleWindow(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("ARK - Vault Console")
        self.geometry("820x520")
        self.configure(bg=THEME_BG)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.vault_tag = _vault_tag(session)
        self.blocks_root = blocks_root(session.vault_dir)
        self.exp_dir = exports_root(session.vault_dir)

        self.manifest = load_manifest(session)
        self.entries = self.manifest.get("entries", {})

        top = tk.Frame(self, bg=THEME_BG)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text=f"Vault: {self.vault_tag[:12]}…", bg=THEME_BG, fg=THEME_FG).pack(side="left")
        tk.Label(top, text="Filter (color):", bg=THEME_BG, fg=THEME_FG).pack(side="left", padx=(18, 6))
        self.search = tk.Entry(top, width=18, bg=THEME_PANEL, fg=THEME_FG, insertbackground=THEME_FG)
        self.search.pack(side="left")
        tk.Button(top, text="Apply", command=self.refresh_list, bg=THEME_PANEL, fg=THEME_FG).pack(side="left", padx=6)

        mid = tk.Frame(self, bg=THEME_BG)
        mid.pack(fill="both", expand=True, padx=10)

        self.listbox = tk.Listbox(mid, bg=THEME_PANEL, fg=THEME_FG, selectbackground="#333333", activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._on_select())

        right = tk.Frame(mid, width=260, bg=THEME_BG)
        right.pack(side="right", fill="y", padx=(10, 0))

        tk.Label(right, text="Tag color (12):", bg=THEME_BG, fg=THEME_FG).pack(anchor="w")
        self.color_var = tk.StringVar(value="")
        om = tk.OptionMenu(right, self.color_var, *PALETTE)
        om.config(bg=THEME_PANEL, fg=THEME_FG, activebackground=THEME_PANEL, activeforeground=THEME_FG, highlightthickness=0)
        om["menu"].config(bg=THEME_PANEL, fg=THEME_FG)
        om.pack(fill="x", pady=(0, 8))

        tk.Button(right, text="Set Color Tag", command=self.set_color, bg=THEME_PANEL, fg=THEME_FG).pack(fill="x", pady=(0, 14))

        tk.Button(right, text="Encrypt File…", command=self.encrypt_pick, bg=THEME_PANEL, fg=THEME_FG).pack(fill="x", pady=4)
        tk.Button(right, text="Encrypt Files… (Multi)", command=self.encrypt_multi, bg=THEME_PANEL, fg=THEME_FG).pack(fill="x", pady=4)
        tk.Button(right, text="Decrypt Selected…", command=self.decrypt_selected, bg=THEME_PANEL, fg=THEME_FG).pack(fill="x", pady=4)
        tk.Button(right, text="Refresh", command=self.refresh_list, bg=THEME_PANEL, fg=THEME_FG).pack(fill="x", pady=4)

        self.status = tk.Label(self, text="", anchor="w", bg=THEME_BG, fg=THEME_FG)
        self.status.pack(fill="x", padx=10, pady=(6, 10))

        self.refresh_list()

    def _on_close(self):
        close_session(self.session)
        self.destroy()

    def _list_encrypted_files(self):
        try:
            out = []
            for bucket in os.listdir(self.blocks_root):
                bdir = os.path.join(self.blocks_root, bucket)
                if not os.path.isdir(bdir):
                    continue
                for f in os.listdir(bdir):
                    if f.lower().endswith(".ark"):
                        out.append(os.path.join(bucket, f))
            return sorted(out)
        except FileNotFoundError:
            os.makedirs(self.blocks_root, exist_ok=True)
            return []

    def _enc_path_for_id(self, fid: str) -> str:
        bucket = fid[:2].lower()
        bdir = os.path.join(self.blocks_root, bucket)
        os.makedirs(bdir, exist_ok=True)
        return os.path.join(bdir, f"{fid}.ark")

    def _display_row(self, file_id: str, meta: dict) -> str:
        name = meta.get("name") or "(unnamed)"
        color = (meta.get("color") or "").strip()
        prefix = f"[{color}] " if color else ""
        return f"{prefix}{name}  —  {file_id}.ark"

    def refresh_list(self):
        want = normalize_color(self.search.get())
        self.listbox.delete(0, tk.END)

        disk_ids = set(os.path.basename(fn)[:-4] for fn in self._list_encrypted_files())

        items = []
        for fid, meta in self.entries.items():
            if fid in disk_ids:
                items.append((meta.get("created_at", 0), meta.get("name", ""), fid, meta))
        items.sort()

        shown = 0
        for _, __, fid, meta in items:
            color = normalize_color(meta.get("color", ""))
            if want and color != want:
                continue
            row = self._display_row(fid, meta)
            self.listbox.insert(tk.END, row)
            idx = self.listbox.size() - 1
            if color:
                self.listbox.itemconfig(idx, fg=_safe_tag_hex(color))
            shown += 1

        self.status.config(text=f"Encrypted files: {len(disk_ids)} | Showing: {shown} | Filter: {want or 'none'}")

    def _current_file_id(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        display = self.listbox.get(sel[0])
        if " —  " not in display:
            return None
        tail = display.split(" —  ", 1)[1].strip()
        return tail[:-4] if tail.lower().endswith(".ark") else None

    def _on_select(self):
        fid = self._current_file_id()
        if fid:
            self.color_var.set((self.entries.get(fid, {}) or {}).get("color", "") or "")

    def _persist_manifest(self):
        self.manifest["entries"] = self.entries
        save_manifest(self.session, self.manifest)

    def set_color(self):
        fid = self._current_file_id()
        if not fid:
            messagebox.showinfo("ARK", "Select a file first.")
            return
        c = normalize_color(self.color_var.get())
        if c and c not in PALETTE:
            messagebox.showerror("ARK", "Invalid color.")
            return
        meta = self.entries.get(fid) or {}
        meta["color"] = c
        meta.setdefault("created_at", int(time.time()))
        self.entries[fid] = meta
        try:
            self._persist_manifest()
        except Exception:
            messagebox.showerror("ARK", uniform_failure_message())
            return
        self.refresh_list()

    def encrypt_pick(self):
        in_path = filedialog.askopenfilename(title="Select file to encrypt")
        if not in_path:
            return
        self._encrypt_paths([in_path])

    def encrypt_multi(self):
        paths = filedialog.askopenfilenames(title="Select files to encrypt (multi)")
        if not paths:
            return
        self._encrypt_paths(list(paths))

    def _encrypt_paths(self, paths):
        ok = 0
        failed = 0
        for in_path in paths:
            try:
                orig_name = os.path.basename(in_path)
                fid = new_file_id()
                out_path = self._enc_path_for_id(fid)
                encrypt_file(self.session, in_path, out_path)
                self.entries[fid] = {"name": orig_name, "color": "", "created_at": int(time.time())}
                ok += 1
            except Exception:
                failed += 1

        try:
            self._persist_manifest()
        except Exception:
            messagebox.showerror("ARK", uniform_failure_message())
            return

        self.refresh_list()
        if failed:
            messagebox.showwarning("ARK", f"Encrypted {ok} file(s). {failed} failed.")
        else:
            self.status.config(text=f"Encrypted {ok} file(s) into: {self.blocks_root}")

    def decrypt_selected(self):
        fid = self._current_file_id()
        if not fid:
            messagebox.showinfo("ARK", "Select an encrypted item first.")
            return

        in_path = self._enc_path_for_id(fid)
        meta = self.entries.get(fid, {})
        suggested_name = meta.get("name") or (fid + ".out")
        suggested = os.path.join(self.exp_dir, suggested_name)

        out_path = filedialog.asksaveasfilename(
            title="Save decrypted file as",
            initialfile=os.path.basename(suggested)
        )
        if not out_path:
            return

        try:
            decrypt_file(self.session, in_path, out_path)
            self.status.config(text=f"Decrypted: {out_path}")
        except Exception:
            messagebox.showerror("ARK", uniform_failure_message())


def launch_console(session):
    app = ConsoleWindow(session)
    app.mainloop()
# === END ark_core/ui/console.py ===


# === BEGIN ark_core/ui/login.py ===
import tkinter as tk
from tkinter import messagebox

import os



class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ARK - Unlock")
        self.resizable(False, False)
        self.configure(bg=THEME_BG)

        lbl1 = tk.Label(self, text="Phrase (this IS the login)", bg=THEME_BG, fg=THEME_FG)
        lbl1.grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")
        self.phrase_entry = tk.Entry(self, width=38, show="•", bg=THEME_PANEL, fg=THEME_FG, insertbackground=THEME_FG)
        self.phrase_entry.grid(row=1, column=0, padx=10, pady=(0, 10))
        self.phrase_entry.focus_set()

        lbl2 = tk.Label(self, text="Security level", bg=THEME_BG, fg=THEME_FG)
        lbl2.grid(row=2, column=0, padx=10, pady=(0, 4), sticky="w")
        self.level_var = tk.StringVar(value=SECURITY_LEVELS[1])
        om = tk.OptionMenu(self, self.level_var, *SECURITY_LEVELS)
        om.config(bg=THEME_PANEL, fg=THEME_FG, activebackground=THEME_PANEL, activeforeground=THEME_FG, highlightthickness=0)
        om["menu"].config(bg=THEME_PANEL, fg=THEME_FG)
        om.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        btn = tk.Button(self, text="Unlock", command=self.unlock, bg=THEME_PANEL, fg=THEME_FG, activebackground=THEME_BG, activeforeground=THEME_FG)
        btn.grid(row=4, column=0, padx=10, pady=(0, 12), sticky="ew")
        self.bind("<Return>", lambda e: self.unlock())

    def unlock(self):
        base_dir = os.getcwd()
        phrase = self.phrase_entry.get()
        if not phrase:
            messagebox.showerror("ARK", "A phrase is required.")
            return

        try:
            level = self.level_var.get() or "strong"
            session = open_or_create_vault(base_dir, phrase, level)
        except Exception as e:
            messagebox.showerror("ARK", f"Unlock failed: {e}")
            return
        finally:
            # best-effort clear entry widget content
            try:
                self.phrase_entry.delete(0, tk.END)
            except Exception:
                pass

        self.destroy()
        launch_console(session)


def launch_login():
    app = LoginWindow()
    app.mainloop()
# === END ark_core/ui/login.py ===

# === ENTRYPOINT ===
def main():
    # Best-effort hide console relaunch for windowed UX (Windows).
    try:
        if 'best_effort_hide_console_relaunch' in globals() and best_effort_hide_console_relaunch():
            return
    except Exception:
        pass
    try:
        launch_login()
    except NameError:
        # If UI entry wasn't included for any reason, fail clearly.
        raise RuntimeError("UI entrypoint missing: launch_login()")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            log_exception(e)
        except Exception:
            pass
        raise
