"""Encryption engine.

Security-first:
  - Always runs Mode E virus sweep before writing encrypted payloads.
  - Uses per-file random nonce and HKDF-derived file key.
  - Applies Pi 3-1-4 mixing to ciphertext as application-layer packing.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ark.config import FILE_NONCE_SIZE, MAX_FILE_SIZE_BYTES
from ark.crypto.keys import derive_file_key
from ark.engine.mixing import mix_314
from ark.security.virus import scan_bytes_or_raise
from ark.vault.container import pack_header


def encrypt_bytes(session, plaintext: bytes) -> bytes:
    if len(plaintext) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File too large for ARK v1")

    # Mode E sweep (mandatory)
    scan_bytes_or_raise(plaintext)

    nonce = os.urandom(FILE_NONCE_SIZE)
    file_key = derive_file_key(session.subkeys.enc, nonce)
    ciphertext = AESGCM(file_key).encrypt(nonce, plaintext, b"ARK:V1")
    mixed = mix_314(ciphertext)
    return pack_header(nonce, len(mixed)) + mixed


def encrypt_file(session, in_path: str, out_path: str) -> str:
    with open(in_path, "rb") as f:
        plaintext = f.read()
    blob = encrypt_bytes(session, plaintext)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(blob)
    os.replace(tmp_path, out_path)
    return out_path
