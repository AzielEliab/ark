"""Command-line interface for The ARK.

    ark version
    ark ui
    ark unlock --phrase ... --level normal
    ark put FILE
    ark get FILE_ID --out PATH
    ark list
    ark sweep FILE
    ark lock
    ark console   # tkinter; skipped when no display

Phrase may be --phrase or ARK_PHRASE. Never printed.
One-shot commands: each put/get/list opens, works, and destroys the session.
Not a kernel. Local deniable vault. Loopback UI.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from getpass import getpass
from typing import Sequence

from ark import __version__
from ark.config import LIMITATION, SECURITY_LEVELS
from ark.security.errors import uniform_failure_message
from ark.security.virus import VirusFlagged, findings_as_dicts, scan_bytes
from ark.utils import resolve_data_dir


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ark",
        description=(
            "The ARK (Aziel Rotating Kernel) — local deniable vault "
            "(Aziel Eliab, 2026). Not a kernel, not a bootable OS. "
            "Every phrase is a login. Loopback UI: `ark ui` at http://127.0.0.1:8850."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_ui = sub.add_parser("ui", help="Serve the local ARK UI on 127.0.0.1:8850 (loopback only).")
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8850, help="Port (default 8850).")
    p_ui.add_argument("--data", default=None, help="Data directory (default ./ARK_DATA).")

    p_con = sub.add_parser("console", help="Optional tkinter console (skipped without a display).")
    p_con.add_argument("--data", default=None)

    def _vault_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--phrase", default=None, help="Vault phrase. Else ARK_PHRASE, else prompt. Never printed.")
        p.add_argument("--level", default="normal", choices=list(SECURITY_LEVELS), help="Security level (behavior: autolock + decoys).")
        p.add_argument("--data", default=None, help="Data directory (default ./ARK_DATA).")

    p_un = sub.add_parser("unlock", help="Open or create the vault for this phrase (one-shot).")
    _vault_args(p_un)

    p_put = sub.add_parser("put", help="Encrypt FILE into the vault (Mode E first).")
    p_put.add_argument("file")
    _vault_args(p_put)

    p_get = sub.add_parser("get", help="Decrypt FILE_ID to --out PATH.")
    p_get.add_argument("file_id")
    p_get.add_argument("--out", required=True, dest="out_path")
    _vault_args(p_get)

    p_list = sub.add_parser("list", help="List files in the vault for this phrase.")
    _vault_args(p_list)
    p_list.add_argument("--json", action="store_true", dest="as_json")

    p_sw = sub.add_parser("sweep", help="Mode E local intake filter on FILE. Does not store the payload.")
    p_sw.add_argument("file")
    p_sw.add_argument("--json", action="store_true", dest="as_json")

    sub.add_parser("lock", help="Destroy in-memory session. CLI is one-shot; UI lock zeroizes keys.")

    return parser


def _resolve_phrase(explicit: str | None) -> str:
    phrase = explicit if explicit not in (None, "") else os.environ.get("ARK_PHRASE")
    if not phrase:
        phrase = getpass("Phrase: ")
    if not phrase:
        raise SystemExit("A phrase is required.")
    return phrase


def _open(args):
    from ark.engine.vault_session import open_or_create_vault

    data_dir = resolve_data_dir(getattr(args, "data", None))
    phrase = _resolve_phrase(getattr(args, "phrase", None))
    level = getattr(args, "level", None) or "normal"
    return open_or_create_vault(data_dir, phrase, level)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"ark {__version__}")
        return 0

    if args.cmd == "ui":
        from ark.ui import serve

        try:
            serve(host=args.host, port=args.port, data_dir=resolve_data_dir(args.data))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.cmd == "console":
        from ark.ui.console import launch_login_safe

        try:
            launch_login_safe(data_dir=resolve_data_dir(args.data))
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.cmd == "lock":
        print("CLI commands are one-shot; no persistent session to lock. UI lock zeroizes in-memory keys.")
        return 0

    if args.cmd == "sweep":
        with open(args.file, "rb") as f:
            data = f.read()
        _h, findings = scan_bytes(data)
        payload = {
            "flagged": bool(findings),
            "findings": findings_as_dicts(findings),
            "note": "Local intake filter. Not a network AV product. Payload is not stored.",
        }
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            if findings:
                print("ARK blocked file (Mode E)")
                for item in payload["findings"]:
                    print(f"{item['kind']}: {item['detail']}")
            else:
                print("clean")
        return 1 if findings else 0

    session = None
    try:
        if args.cmd == "unlock":
            session = _open(args)
            tag = os.path.basename(session.vault_dir)
            print(f"opened {tag[:12]}…")
            print("A wrong phrase would have opened a different empty vault (deniability).")
            return 0

        if args.cmd == "put":
            from ark.engine.ops import put_file

            session = _open(args)
            try:
                fid = put_file(session, args.file)
            except VirusFlagged:
                print("ARK blocked file (Mode E)", file=sys.stderr)
                return 1
            print(fid)
            return 0

        if args.cmd == "get":
            from ark.engine.ops import get_file
            from ark.engine.decrypt import DecryptionFailed

            session = _open(args)
            try:
                get_file(session, args.file_id, args.out_path)
            except DecryptionFailed:
                print(uniform_failure_message(), file=sys.stderr)
                return 1
            print(args.out_path)
            return 0

        if args.cmd == "list":
            from ark.engine.ops import list_entries

            session = _open(args)
            rows = list_entries(session)
            if args.as_json:
                print(json.dumps(rows, indent=2))
            else:
                if not rows:
                    print("(empty vault)")
                for row in rows:
                    print(f"{row['id']}  {row['name']}")
            return 0
    finally:
        if session is not None:
            session.destroy()

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
