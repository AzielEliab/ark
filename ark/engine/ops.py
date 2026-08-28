"""High-level vault operations: put, get, list, lock."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from ark.engine.encrypt import encrypt_file
from ark.engine.decrypt import decrypt_file
from ark.engine.mixing import inject_decoys
from ark.vault.layout import blocks_root
from ark.vault.manifest import load_manifest, save_manifest
from ark.vault.naming import new_file_id


def enc_path_for_id(vault_dir: str, fid: str) -> str:
    bucket = fid[:2].lower()
    bdir = Path(blocks_root(vault_dir)) / bucket
    bdir.mkdir(parents=True, exist_ok=True)
    return str(bdir / f"{fid}.ark")


def put_file(session, in_path: str, name: str | None = None) -> str:
    """Encrypt a local file into the vault. Mode E runs inside encrypt_file."""
    orig_name = name or os.path.basename(in_path)
    fid = new_file_id()
    out_path = enc_path_for_id(session.vault_dir, fid)
    encrypt_file(session, in_path, out_path)
    inject_decoys(session.vault_dir, session.security_level)
    manifest = load_manifest(session)
    entries = manifest.setdefault("entries", {})
    entries[fid] = {"name": orig_name, "color": "", "created_at": int(time.time())}
    save_manifest(session, manifest)
    return fid


def put_bytes(session, data: bytes, name: str) -> str:
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data)
        tmp = tf.name
    try:
        return put_file(session, tmp, name=name)
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def get_file(session, file_id: str, out_path: str) -> str:
    in_path = enc_path_for_id(session.vault_dir, file_id)
    if not os.path.exists(in_path):
        from ark.engine.decrypt import DecryptionFailed
        from ark.security.errors import uniform_failure_message

        raise DecryptionFailed(uniform_failure_message())
    return decrypt_file(session, in_path, out_path)


def list_entries(session) -> list[dict[str, Any]]:
    manifest = load_manifest(session)
    entries = manifest.get("entries") or {}
    rows = []
    for fid, meta in entries.items():
        path = enc_path_for_id(session.vault_dir, fid)
        if not os.path.exists(path):
            continue
        rows.append(
            {
                "id": fid,
                "name": meta.get("name") or "(unnamed)",
                "color": meta.get("color") or "",
                "created_at": meta.get("created_at") or 0,
            }
        )
    rows.sort(key=lambda r: (r["created_at"], r["name"], r["id"]))
    return rows
