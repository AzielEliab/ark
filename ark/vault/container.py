"""Per-file container format.

Header:
  MAGIC(4) | VER(1) | NONCE(12) | CIPHERTEXT_LEN(8)

Vault salt and KDF params live in vault header.bin (vault-level), not per file.
"""

from __future__ import annotations

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
