"""Encrypted per-vault file index."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

MANIFEST_FILENAME = "manifest.ark"


def _manifest_path(session) -> str:
    return os.path.join(session.vault_dir, MANIFEST_FILENAME)


def load_manifest(session) -> Dict[str, Any]:
    from ark.engine.decrypt import decrypt_bytes

    path = _manifest_path(session)
    if not os.path.exists(path):
        return {"version": 1, "created_at": int(time.time()), "entries": {}}
    with open(path, "rb") as f:
        blob = f.read()
    data = decrypt_bytes(session, blob)
    obj = json.loads(data.decode("utf-8"))
    obj.setdefault("entries", {})
    return obj


def save_manifest(session, manifest: Dict[str, Any]) -> str:
    from ark.engine.encrypt import encrypt_bytes

    path = _manifest_path(session)
    payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    blob = encrypt_bytes(session, payload)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
    return path
