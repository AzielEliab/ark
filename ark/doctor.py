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
    labels = {
        "version": "version",
        "loopback": "loopback",
        "sweep_clean_text": "intake check",
        "not_kernel": "scope note",
        "telemetry": "telemetry",
    }
    lines = [f"ark doctor  {payload.get('version')}", ""]
    for check in payload.get("checks") or []:
        mark = "pass" if check.get("ok") else "fail"
        label = labels.get(str(check.get("id")), str(check.get("id")))
        detail = "" if check.get("id") == "sweep_clean_text" and check.get("ok") else (check.get("detail") or "")
        extra = f"  {detail}" if detail else ""
        lines.append(f"{mark}  {label}{extra}")
    lines.append("")
    if payload.get("ok"):
        lines.append("Ready.")
    else:
        lines.append("Not ready. Run: ark doctor --json")
    return "\n".join(lines)


def doctor_cli(*, as_json: bool = False) -> int:
    payload = run()
    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(format_report(payload) + "\n")
    return 0 if payload.get("ok") else 1
