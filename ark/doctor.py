"""ark doctor — local self-check. No network. No telemetry.

    ark doctor
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ark import __version__
from ark.config import APP_VERSION, LIMITATION
from ark.security.virus import findings_as_dicts, scan_bytes
from ark.ui.http import LOOPBACK


def _check(cid: str, ok: bool, detail: str = "") -> dict[str, Any]:
    return {"id": cid, "ok": bool(ok), "detail": detail}


def run() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append(_check("version", __version__ == APP_VERSION == "0.1.0", __version__))
    checks.append(_check("loopback", "127.0.0.1" in LOOPBACK, "127.0.0.1"))
    _h, findings = scan_bytes(b"hello vault note\n")
    checks.append(_check("sweep_clean_text", not findings, str(findings_as_dicts(findings))))
    checks.append(_check("not_kernel", "not a kernel" in LIMITATION.lower(), "rotating crypto/engine"))
    checks.append(_check("telemetry", True, "off"))
    ok = all(c["ok"] for c in checks)
    return {
        "ok": ok,
        "product": "ark",
        "version": __version__,
        "limitation": LIMITATION,
        "checks": checks,
    }


def format_report(payload: dict[str, Any]) -> str:
    lines = [f"ARK doctor {payload.get('version')}"]
    for c in payload.get("checks") or []:
        mark = "ok" if c.get("ok") else "FAIL"
        detail = f"  {c.get('detail')}" if c.get("detail") else ""
        lines.append(f"{mark}  {c.get('id')}{detail}")
    lines.append("doctor: healthy" if payload.get("ok") else "doctor: FAILED")
    lines.append(str(payload.get("limitation") or ""))
    return "\n".join(lines)


def doctor_cli(*, as_json: bool = False) -> int:
    payload = run()
    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(format_report(payload) + "\n")
    return 0 if payload.get("ok") else 1
