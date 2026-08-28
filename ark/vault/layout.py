"""On-disk vault directories."""

from __future__ import annotations

from pathlib import Path

from ark.utils import ensure_dir


def blocks_bucket_dir(vault_dir: str, bucket_hex: str) -> str:
    d = Path(vault_dir) / "blocks" / bucket_hex
    ensure_dir(str(d))
    return str(d)


def blocks_root(vault_dir: str) -> str:
    d = Path(vault_dir) / "blocks"
    ensure_dir(str(d))
    return str(d)


def exports_root(vault_dir: str) -> str:
    d = Path(vault_dir) / "exports"
    ensure_dir(str(d))
    return str(d)
