from __future__ import annotations

from pathlib import Path

from ark.crypto.aead import decrypt, encrypt
from ark.engine.decrypt import DecryptionFailed, decrypt_bytes
from ark.engine.encrypt import encrypt_bytes
from ark.engine.vault_session import open_or_create_vault
from ark.security.errors import uniform_failure_message


def test_aead_roundtrip() -> None:
    key = b"k" * 32
    box = encrypt(b"hello ark", key, aad=b"ARK:V1")
    assert decrypt(box["ciphertext"], key, box["nonce"], aad=b"ARK:V1") == b"hello ark"


def test_roundtrip_encrypt_decrypt(tmp_path: Path) -> None:
    session = open_or_create_vault(str(tmp_path), "alpha phrase", "normal")
    blob = encrypt_bytes(session, b"plain text allowed")
    assert decrypt_bytes(session, blob) == b"plain text allowed"
    session.destroy()


def test_wrong_key_uniform_fail(tmp_path: Path) -> None:
    a = open_or_create_vault(str(tmp_path), "phrase-a", "normal")
    blob = encrypt_bytes(a, b"secret payload text")
    b = open_or_create_vault(str(tmp_path), "phrase-b", "normal")
    try:
        decrypt_bytes(b, blob)
        raise AssertionError("should have failed")
    except DecryptionFailed as exc:
        assert str(exc) == uniform_failure_message()
        assert str(exc) == "Unlock/decrypt failed."
    a.destroy()
    b.destroy()
