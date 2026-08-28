from __future__ import annotations

from pathlib import Path

from ark.config import AUTOLOCK_SECONDS, DECOY_COUNTS
from ark.engine.mixing import decoy_count, inject_decoys, mix_314, unmix_314
from ark.engine.vault_session import open_or_create_vault
from ark.security.memory import zero_bytearray


def test_mix_314_roundtrip() -> None:
    for size in (0, 1, 31, 32, 255, 256, 257, 1024, 4096):
        data = bytes((i * 17) % 256 for i in range(size))
        mixed = mix_314(data)
        assert unmix_314(mixed) == data
        if size >= 256:
            assert mixed[8:] != data[: len(mixed) - 8]


def test_decoy_count_by_level() -> None:
    assert decoy_count("normal") == 0
    assert decoy_count("strong") == 2
    assert decoy_count("paranoid") == 8
    assert DECOY_COUNTS["paranoid"] == 8


def test_inject_decoys(tmp_path: Path) -> None:
    session = open_or_create_vault(str(tmp_path), "decoy-phrase", "strong")
    n = inject_decoys(session.vault_dir, "strong")
    assert n == 2
    blocks = list(Path(session.vault_dir).joinpath("blocks").rglob("*.ark"))
    assert len(blocks) == 2
    session.destroy()


def test_autolock_seconds() -> None:
    assert AUTOLOCK_SECONDS["normal"] == 15 * 60
    assert AUTOLOCK_SECONDS["strong"] == 5 * 60
    assert AUTOLOCK_SECONDS["paranoid"] == 60


def test_zeroization() -> None:
    buf = bytearray(b"secret-key-material-32bytes!!")
    zero_bytearray(buf)
    assert buf == bytearray(len(buf))
