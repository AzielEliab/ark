"""Decryption engine.

Uniform failure behavior to reduce oracle surfaces.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ark.crypto.keys import derive_file_key
from ark.engine.mixing import unmix_314
from ark.security.errors import uniform_failure_message
from ark.vault.container import HEADER_SIZE, unpack_header


class DecryptionFailed(Exception):
    pass


def decrypt_bytes(session, blob: bytes) -> bytes:
    try:
        nonce, ct_len = unpack_header(blob)
        mixed = blob[HEADER_SIZE : HEADER_SIZE + ct_len]
        if len(mixed) != ct_len:
            raise DecryptionFailed(uniform_failure_message())
        ciphertext = unmix_314(mixed)
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
