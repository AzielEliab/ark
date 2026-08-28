"""Mode E virus sweep.

Local intake filter on files YOU put in YOUR vault. Not a network AV
product and not an exploit.

Security-first policy:
  - If flagged, ARK refuses to encrypt/store the payload.
  - ARK does not quarantine the content; it records only hashes/reason codes.

This module provides:
  - lightweight heuristic checks (always on)
  - optional offline clamscan invocation if available (local only)
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Tuple


class VirusFlagged(Exception):
    """Raised when Mode E flags a payload."""


@dataclass(frozen=True)
class VirusFinding:
    kind: str
    detail: str


def _digest16(data: bytes) -> bytes:
    try:
        from blake3 import blake3

        return blake3(data).digest(length=16)
    except Exception:
        return hashlib.blake2s(data, digest_size=16).digest()


def heuristics(data: bytes) -> List[VirusFinding]:
    """Mode E heuristics: PE/ELF/Mach-O, powershell -enc, curl|sh, wget|sh."""
    findings: List[VirusFinding] = []
    head = data[:8192].lower()

    if len(data) > 2 and data[:2] == b"MZ":
        findings.append(VirusFinding("heuristic", "PE/MZ executable"))

    if data[:4] == b"\x7fELF":
        findings.append(VirusFinding("heuristic", "ELF executable"))

    if data[:4] in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"):
        findings.append(VirusFinding("heuristic", "Mach-O or fat binary"))

    if b"powershell" in head and b"-enc" in head:
        findings.append(VirusFinding("heuristic", "PowerShell encoded command"))

    if b"wget" in head and b"|" in head and (b"sh" in head or b"bash" in head):
        findings.append(VirusFinding("heuristic", "download-pipe-exec pattern"))

    if b"curl" in head and b"|" in head and (b"sh" in head or b"bash" in head):
        findings.append(VirusFinding("heuristic", "download-pipe-exec pattern"))

    if b"vba" in head and b"autoopen" in head:
        findings.append(VirusFinding("heuristic", "macro autoopen indicator"))

    return findings


def _clam_available() -> bool:
    return shutil.which("clamscan") is not None


def _clam_scan_bytes(data: bytes) -> List[VirusFinding]:
    if not _clam_available():
        return []
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data)
        tmp_path = tf.name
    try:
        proc = subprocess.run(
            ["clamscan", "--no-summary", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            text=True,
        )
        out = (proc.stdout or "").strip()
        if proc.returncode == 1:
            return [VirusFinding("clamscan", out[-200:])]
        return []
    except Exception as e:
        return [VirusFinding("clamscan", f"scan error: {e}")]
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def scan_bytes(data: bytes) -> Tuple[bytes, List[VirusFinding]]:
    """Return (hash, findings). Local filter only. Does not store the payload."""
    h = _digest16(data)
    findings: List[VirusFinding] = []
    findings.extend(heuristics(data))
    findings.extend(_clam_scan_bytes(data))
    return h, findings


def scan_bytes_or_raise(data: bytes) -> None:
    _h, findings = scan_bytes(data)
    if findings:
        raise VirusFlagged("ARK blocked file (Mode E)")


def findings_as_dicts(findings: List[VirusFinding]) -> list:
    return [{"kind": f.kind, "detail": f.detail} for f in findings]
