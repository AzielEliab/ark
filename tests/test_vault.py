from __future__ import annotations

from pathlib import Path

from ark.engine.ops import get_file, list_entries, put_file
from ark.engine.vault_session import open_or_create_vault
from ark.vault import header as vault_header


def test_new_phrase_creates_vault(tmp_path: Path) -> None:
    session = open_or_create_vault(str(tmp_path), "brand-new", "normal")
    assert (Path(session.vault_dir) / "header.bin").is_file()
    pid, salt, tag = vault_header.unpack((Path(session.vault_dir) / "header.bin").read_bytes())
    assert pid == 1
    assert len(salt) == 16 and len(tag) == 16
    assert list_entries(session) == []
    session.destroy()


def test_same_phrase_reopens(tmp_path: Path) -> None:
    first = open_or_create_vault(str(tmp_path), "same-phrase", "normal")
    vdir = first.vault_dir
    first.destroy()
    second = open_or_create_vault(str(tmp_path), "same-phrase", "strong")
    assert second.vault_dir == vdir
    second.destroy()


def test_wrong_phrase_creates_different_empty_vault(tmp_path: Path) -> None:
    a = open_or_create_vault(str(tmp_path), "correct horse", "normal")
    src = tmp_path / "note.txt"
    src.write_text("hello from ark")
    fid = put_file(a, str(src))
    a.destroy()
    b = open_or_create_vault(str(tmp_path), "wrong phrase", "normal")
    assert b.vault_dir != a.vault_dir
    assert list_entries(b) == []
    b.destroy()
    again = open_or_create_vault(str(tmp_path), "correct horse", "normal")
    rows = list_entries(again)
    assert len(rows) == 1
    assert rows[0]["id"] == fid
    out = tmp_path / "out.txt"
    get_file(again, fid, str(out))
    assert out.read_text() == "hello from ark"
    again.destroy()


def test_header_pack_unpack() -> None:
    blob = vault_header.pack(2, b"s" * 16, b"t" * 16)
    pid, salt, tag = vault_header.unpack(blob)
    assert pid == 2
    assert salt == b"s" * 16
    assert tag == b"t" * 16
