"""Minimal local put/get. Uses ARK_TEST_KDF if set. Never prints the phrase."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ark.engine.ops import get_file, put_file
from ark.engine.vault_session import open_or_create_vault

def main() -> None:
    data_dir = tempfile.mkdtemp(prefix="ark-ex-")
    phrase = os.environ.get("ARK_PHRASE") or "example-only-not-a-secret"
    session = open_or_create_vault(data_dir, phrase, "normal")
    src = Path(data_dir) / "note.txt"
    src.write_text("hello from The ARK")
    fid = put_file(session, str(src))
    out = Path(data_dir) / "out.txt"
    get_file(session, fid, str(out))
    print("file_id", fid)
    print("roundtrip", out.read_text())
    session.destroy()

if __name__ == "__main__":
    main()
