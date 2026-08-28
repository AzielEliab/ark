"""Vault header format.

header.bin is stored in the vault root directory.

Fields (binary):
  MAGIC(4) | VER(1) | PARAMS_ID(1) | SALT(16) | VERIFY_TAG(16)

- SALT is per-vault random.
- VERIFY_TAG is derived from K_meta and is used to locate the vault for a given phrase.

This header contains no plaintext phrase, no vault name, and no global index.
"""

from __future__ import annotations

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
