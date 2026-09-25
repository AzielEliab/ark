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
    fid = capsys.readouterr().out.strip().splitlines()[-1]
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


def test_console_without_display(monkeypatch, capsys) -> None:
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert main(["console"]) == 2
    err = capsys.readouterr().err
    assert "ark ui" in err
    assert "Traceback" not in err


def test_bare_command_welcome(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "ark ui" in out
    assert "127.0.0.1:8850" in out
    assert "Aziel Eliab" in out
    assert "Traceback" not in out


def test_help_lists_next_step(capsys) -> None:
    try:
        code = main(["--help"])
    except SystemExit as exc:
        code = exc.code
    assert code == 0
    out = capsys.readouterr().out
    assert "ark ui" in out
    assert "examples:" in out
    assert "commands:" in out


def test_unknown_command_has_next_step(capsys) -> None:
    try:
        code = main(["bogus"])
    except SystemExit as exc:
        code = exc.code
    assert code == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "ark --help" in err
    assert "Traceback" not in err


def test_get_missing_args_has_next_step(capsys) -> None:
    try:
        code = main(["get"])
    except SystemExit as exc:
        code = exc.code
    assert code == 2
    err = capsys.readouterr().err
    assert "ark get" in err
    assert "Traceback" not in err


def test_put_missing_file(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("ARK_PHRASE", "cli-test-phrase")
    code = main(["put", str(tmp_path / "missing.txt"), "--data", str(tmp_path / "data")])
    assert code == 2
    err = capsys.readouterr().err
    assert "No file" in err
    assert "Traceback" not in err


def test_version_and_list_json(tmp_path: Path, capsys, monkeypatch) -> None:
    import json

    assert main(["--json", "version"]) == 0
    version = json.loads(capsys.readouterr().out)
    assert version["version"] == "0.1.0"
    assert version["author"] == "Aziel Eliab"
    monkeypatch.setenv("ARK_PHRASE", "cli-test-phrase")
    src = tmp_path / "note.txt"
    src.write_text("json path")
    data = str(tmp_path / "data")
    assert main(["put", str(src), "--data", data, "--json"]) == 0
    stored = json.loads(capsys.readouterr().out)
    assert len(stored["id"]) == 32
    assert stored["name"] == "note.txt"
    assert main(["list", "--json", "--data", data]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert isinstance(rows, list)
    assert {"id", "name", "color", "created_at"} <= set(rows[0])
