"""AES-256-GCM helpers."""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12  # AES-GCM standard


def encrypt(plaintext: bytes, key: bytes, aad: bytes = b"") -> dict:
    """Encrypt plaintext using AES-GCM. Returns nonce + ciphertext."""
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return {"nonce": nonce, "ciphertext": ciphertext}


def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, aad: bytes = b"") -> bytes:
    """Decrypt ciphertext using AES-GCM. Raises on failure."""
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
