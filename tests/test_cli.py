from __future__ import annotations

import os
from pathlib import Path

from ark.cli import main


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert "ark 0.1.0" in capsys.readouterr().out


def test_cli_put_get_list_sweep(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("ARK_PHRASE", "cli-test-phrase")
    src = tmp_path / "note.txt"
    src.write_text("cli payload text")
    data = str(tmp_path / "data")
    assert main(["put", str(src), "--data", data, "--level", "normal"]) == 0
    fid = capsys.readouterr().out.strip()
    assert len(fid) == 32
    assert main(["list", "--data", data]) == 0
    listed = capsys.readouterr().out
    assert fid in listed
    assert "note.txt" in listed
    out = tmp_path / "out.txt"
    assert main(["get", fid, "--out", str(out), "--data", data]) == 0
    assert out.read_text() == "cli payload text"
    assert main(["sweep", str(src)]) == 0
    assert "clean" in capsys.readouterr().out
    mz = tmp_path / "fake.exe"
    mz.write_bytes(b"MZ" + b"\x00" * 8)
    assert main(["sweep", str(mz)]) == 1
    swept = capsys.readouterr().out + capsys.readouterr().err
    assert "Mode E" in swept or "PE/MZ" in swept


def test_cli_never_prints_phrase(tmp_path: Path, capsys, monkeypatch) -> None:
    secret = "never-print-this-phrase-xyz"
    monkeypatch.setenv("ARK_PHRASE", secret)
    src = tmp_path / "a.txt"
    src.write_text("x")
    data = str(tmp_path / "d")
    main(["put", str(src), "--data", data])
    main(["list", "--data", data])
    main(["unlock", "--data", data])
    dumped = capsys.readouterr().out + capsys.readouterr().err
    assert secret not in dumped


def test_cli_lock(capsys) -> None:
    assert main(["lock"]) == 0
    assert "one-shot" in capsys.readouterr().out
