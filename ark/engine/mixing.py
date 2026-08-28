"""Application-layer mixing. Not an extra cryptographic assumption
beyond AES-256-GCM + Argon2id + HKDF.

Pi cycle 3-1-4: for each group of 8 storage blocks, apply the permutation
defined by a 3-cycle, a 1-cycle (fixed point), and a 4-cycle:

    (0 1 2)(3)(4 5 6 7)

That is storage-layout mixing of ciphertext bytes after AES-GCM, inverted
on decrypt. Confidentiality is AES-GCM; this permute does not add a
cryptographic assumption.

Phoenix (destroy / reseed / rebuild) is likewise application-layer:
  1. destroy-looking noise = random decoy blocks not listed in the
     encrypted manifest
  2. reseed = os.urandom for those decoys
  3. rebuild = 8-block Pi packing of the real ciphertext

Do not confuse this with "destroy the universe". Civilian software.
Decoy count follows security level (behavior, not cryptography).
"""

from __future__ import annotations

import os
import struct
from pathlib import Path

from ark.config import DECOY_COUNTS, SECURITY_LEVELS
from ark.utils import ensure_dir
from ark.vault.layout import blocks_root
from ark.vault.naming import new_file_id

# 32-byte blocks; 8 blocks = 256-byte groups.
BLOCK = 32
GROUP = 8

# new[i] comes from old[FORWARD[i]]
# cycle (0 1 2): 0->1, 1->2, 2->0
# cycle (3):     3 stays
# cycle (4 5 6 7): 4->5, 5->6, 6->7, 7->4
FORWARD = (2, 0, 1, 3, 7, 4, 5, 6)
INVERSE = (1, 2, 0, 3, 5, 6, 7, 4)


def decoy_count(level: str) -> int:
    lv = (level or "normal").lower().strip()
    if lv not in SECURITY_LEVELS:
        lv = "normal"
    return int(DECOY_COUNTS[lv])


def _permute_group(group: bytes, table: tuple[int, ...]) -> bytes:
    chunks = [group[i * BLOCK : (i + 1) * BLOCK] for i in range(GROUP)]
    return b"".join(chunks[src] for src in table)


def _permute_body(padded: bytes, table: tuple[int, ...]) -> bytes:
    out = bytearray()
    span = GROUP * BLOCK
    for i in range(0, len(padded), span):
        out.extend(_permute_group(padded[i : i + span], table))
    return bytes(out)


def mix_314(data: bytes) -> bytes:
    """Pad to 8-block groups, permute with 3-1-4, prefix original length."""
    orig = len(data)
    span = GROUP * BLOCK
    pad = (span - (orig % span)) % span
    padded = data + (b"\x00" * pad)
    mixed = _permute_body(padded, FORWARD)
    return struct.pack(">Q", orig) + mixed


def unmix_314(blob: bytes) -> bytes:
    """Inverse 3-1-4 permute and unpad."""
    if len(blob) < 8:
        raise ValueError("mixed blob too small")
    orig = struct.unpack(">Q", blob[:8])[0]
    body = blob[8:]
    span = GROUP * BLOCK
    if len(body) % span != 0:
        raise ValueError("mixed blob not aligned")
    plain = _permute_body(body, INVERSE)
    if orig > len(plain):
        raise ValueError("mixed length invalid")
    return plain[:orig]


def inject_decoys(vault_dir: str, level: str, n: int | None = None) -> int:
    """Write n random decoy files into blocks/. Not listed in the manifest.

    Phoenix step 1–2: destroy-looking noise, reseeded from os.urandom.
    """
    count = decoy_count(level) if n is None else int(n)
    if count <= 0:
        return 0
    root = Path(blocks_root(vault_dir))
    written = 0
    for _ in range(count):
        fid = new_file_id()
        bucket = fid[:2].lower()
        bdir = root / bucket
        ensure_dir(str(bdir))
        # Random bytes sized like a small mixed container. Not real ciphertext.
        payload = os.urandom(8 + GROUP * BLOCK)
        (bdir / f"{fid}.ark").write_bytes(b"ARF1" + os.urandom(1) + os.urandom(12) + os.urandom(8) + payload)
        written += 1
    return written
