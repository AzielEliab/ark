from __future__ import annotations

import os

from ark.config import KDF_PROFILES, TEST_KDF_PROFILES, active_kdf_profiles, test_kdf_enabled as kdf_env_on
from ark.crypto.kdf import derive_master_key, hkdf_expand
from ark.crypto.keys import derive_file_key, derive_subkeys


def test_test_kdf_env_is_set() -> None:
    assert os.environ.get("ARK_TEST_KDF") == "1"
    assert kdf_env_on() is True
    profiles = active_kdf_profiles()
    for pid, prof in profiles.items():
        assert prof["memory_cost_kib"] == 8 * 1024
        assert prof["time_cost"] == 1
        assert prof["memory_cost_kib"] < 256 * 1024


def test_production_profiles_stay_as_spec() -> None:
    assert KDF_PROFILES[1]["memory_cost_kib"] == 256 * 1024
    assert KDF_PROFILES[2]["memory_cost_kib"] == 512 * 1024
    assert KDF_PROFILES[3]["memory_cost_kib"] == 1024 * 1024
    assert TEST_KDF_PROFILES[1]["memory_cost_kib"] == 8 * 1024


def test_kdf_and_hkdf_roundtrip_labels() -> None:
    salt = b"0123456789abcdef"
    master = derive_master_key(b"test-phrase", salt, time_cost=1, memory_cost_kib=8 * 1024, parallelism=1)
    assert len(master) == 32
    subs = derive_subkeys(master)
    assert len(subs.enc) == 32 and len(subs.meta) == 32 and len(subs.log) == 32
    assert subs.enc != subs.meta != subs.log
    fk = derive_file_key(subs.enc, b"123456789012")
    assert len(fk) == 32
    a = hkdf_expand(master, salt=None, info=b"ARK:ENC", length=32)
    assert a == subs.enc
