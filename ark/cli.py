"""Command-line interface for The ARK.

Human text is the default. Pass --json for scripts.
The phrase is the login and is never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from getpass import getpass
from typing import Sequence

from ark import __version__
from ark.config import SECURITY_LEVELS
from ark.security.errors import uniform_failure_message
from ark.security.virus import VirusFlagged, findings_as_dicts, scan_bytes
from ark.utils import resolve_data_dir

AUTHOR = "Aziel Eliab"
UI_URL = "http://127.0.0.1:8850/"


def _help_text() -> str:
    return f"""\
usage: ark [--json] [-h] <command> [<args>]

The ARK keeps files on this computer under a phrase you choose.
The phrase is the login.

Author: {AUTHOR}

commands:
  ui        Open the vault in your browser
  unlock    Open or create the vault for a phrase
  put       Store a file in the vault
  get       Copy a file out of the vault
  list      Show files in the vault
  lock      Clear the in-memory session
  doctor    Check this copy of ARK
  version   Print the version
  help      Show this help

advanced:
  sweep     Check a file before you store it
  console   Open the desktop console

options:
  -h, --help   Show this help
  --json       Print JSON for scripts

examples:
  ark
  ark ui
  ark doctor
  ark put notes.txt
  ark --help

Run `ark <command> --help` for one command.
"""


def _welcome_text() -> str:
    return f"""\
The ARK keeps files on this computer under a phrase you choose.
The phrase is the login.

Open the vault:
  ark ui
  Then go to {UI_URL}

Also:
  ark doctor     Check this copy
  ark --help     List commands

Author: {AUTHOR}
"""


def _welcome_payload() -> dict:
    return {
        "product": "ark",
        "version": __version__,
        "author": AUTHOR,
        "summary": "Local vault. The phrase you choose is the login.",
        "next": ["ark ui", "ark doctor", "ark --help"],
        "ui": UI_URL,
    }


class FriendlyParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if getattr(self, "_ark_top", False):
            return _help_text()
        return super().format_help()

    def error(self, message: str) -> None:
        cmd = getattr(self, "_ark_cmd", None)
        sys.stderr.write(_friendly_error(cmd, message) + "\n")
        raise SystemExit(2)


def _friendly_error(cmd: str | None, message: str) -> str:
    choice = re.search(r"invalid choice: '([^']+)'", message)
    if choice and cmd is None:
        name = choice.group(1)
        return f'Unknown command "{name}". Try: ark ui   or   ark --help'
    if cmd == "get" and "required" in message:
        return (
            "get needs a file id and --out PATH. "
            "Try: ark list   then   ark get <file-id> --out restored.txt"
        )
    if "required" in message and re.search(r"\bfile\b", message):
        if cmd == "sweep":
            return "Name the file to check. Try: ark sweep notes.txt"
        return "Name the file to store. Try: ark put notes.txt"
    if choice is not None:
        bad = choice.group(1)
        return (
            f'Unknown level "{bad}". Use normal, strong, or paranoid. '
            "Try: ark unlock --level normal"
        )
    if "unrecognized arguments" in message:
        return f"{message}. Try: ark --help"
    plain = message[:1].upper() + message[1:] if message else "That command could not run."
    if plain and not plain.endswith("."):
        plain += "."
    hint = "ark --help" if not cmd else f"ark {cmd} --help"
    return f"{plain} Try: {hint}"


def _wants_json(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "as_json", False) or getattr(args, "cmd_json", False))


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def _build_parser() -> FriendlyParser:
    parser = FriendlyParser(
        prog="ark",
        add_help=True,
    )
    parser._ark_top = True
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print JSON for scripts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=FriendlyParser)

    def add(name: str, summary: str, description: str, example: str) -> FriendlyParser:
        command = sub.add_parser(
            name,
            help=summary,
            description=description,
            epilog=f"example:\n  {example}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        command._ark_cmd = name
        command.add_argument(
            "--json",
            action="store_true",
            dest="cmd_json",
            help="Print JSON for scripts.",
        )
        return command

    add(
        "doctor",
        "Check this copy of ARK",
        "Check this copy of ARK. No network.",
        "ark doctor",
    )
    add("version", "Print the version", "Print the ARK version.", "ark version")
    add("help", "Show help", "Show ARK commands.", "ark help")

    p_ui = add(
        "ui",
        "Open the vault in your browser",
        "Open the local vault in your browser. Loopback only.",
        "ark ui",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8850, help="Port (default 8850).")
    p_ui.add_argument("--data", default=None, help="Data directory (default ./ARK_DATA).")

    p_con = add(
        "console",
        "Open the desktop console",
        "Open the desktop console. Needs a display.",
        "ark console",
    )
    p_con.add_argument("--data", default=None, help="Data directory (default ./ARK_DATA).")

    def _vault_args(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--phrase",
            default=None,
            help="Vault phrase. Else ARK_PHRASE, else a prompt. Never printed.",
        )
        command.add_argument(
            "--level",
            default="normal",
            choices=list(SECURITY_LEVELS),
            help="How soon the vault locks itself: normal, strong, or paranoid.",
        )
        command.add_argument("--data", default=None, help="Data directory (default ./ARK_DATA).")

    p_un = add(
        "unlock",
        "Open or create the vault for a phrase",
        "Open or create the vault for a phrase. One shot, then the session closes.",
        'ark unlock --phrase "your phrase"',
    )
    _vault_args(p_un)

    p_put = add(
        "put",
        "Store a file in the vault",
        "Store a file in the vault. The intake check runs first.",
        "ark put notes.txt",
    )
    p_put.add_argument("file")
    _vault_args(p_put)

    p_get = add(
        "get",
        "Copy a file out of the vault",
        "Copy a file out of the vault.",
        "ark get <file-id> --out restored.txt",
    )
    p_get.add_argument("file_id")
    p_get.add_argument("--out", required=True, dest="out_path")
    _vault_args(p_get)

    p_list = add(
        "list",
        "Show files in the vault",
        "Show files in the vault for this phrase.",
        "ark list",
    )
    _vault_args(p_list)

    p_sw = add(
        "sweep",
        "Check a file before you store it",
        "Check a file with the local intake filter. The file is not stored.",
        "ark sweep notes.txt",
    )
    p_sw.add_argument("file")

    add(
        "lock",
        "Clear the in-memory session",
        "CLI commands are one-shot. This reminds you there is no session to clear.",
        "ark lock",
    )
    return parser


def _resolve_phrase(explicit: str | None) -> str:
    phrase = explicit if explicit not in (None, "") else os.environ.get("ARK_PHRASE")
    if not phrase:
        try:
            phrase = getpass("Phrase: ")
        except (EOFError, KeyboardInterrupt):
            print(
                "A phrase is required. Pass --phrase, set ARK_PHRASE, or type one when asked.",
                file=sys.stderr,
            )
            raise SystemExit(2) from None
    if not phrase:
        print(
            "A phrase is required. Pass --phrase, set ARK_PHRASE, or type one when asked.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return phrase


def _open(args: argparse.Namespace):
    from ark.engine.vault_session import open_or_create_vault

    data_dir = resolve_data_dir(getattr(args, "data", None))
    phrase = _resolve_phrase(getattr(args, "phrase", None))
    level = getattr(args, "level", None) or "normal"
    return open_or_create_vault(data_dir, phrase, level)


def _fail_file(exc: OSError, path: str, command: str) -> int:
    if isinstance(exc, IsADirectoryError):
        print(f'"{path}" is a folder. Name a file. Try: ark {command} notes.txt', file=sys.stderr)
    elif isinstance(exc, FileNotFoundError):
        print(f'No file at "{path}". Check the path, then try: ark {command} notes.txt', file=sys.stderr)
    else:
        print(f'Could not read "{path}". Check the path and permissions, then try again.', file=sys.stderr)
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    as_json = _wants_json(args)

    if args.cmd in (None, "help"):
        if args.cmd is None and as_json:
            _print_json(_welcome_payload())
        elif args.cmd is None:
            sys.stdout.write(_welcome_text())
        else:
            sys.stdout.write(_help_text())
        return 0

    if args.cmd == "version":
        if as_json:
            _print_json({"product": "ark", "version": __version__, "author": AUTHOR})
        else:
            print(f"ark {__version__}")
        return 0

    if args.cmd == "doctor":
        from ark.doctor import doctor_cli

        return doctor_cli(as_json=as_json)

    if args.cmd == "ui":
        from ark.ui import serve

        try:
            serve(
                host=args.host,
                port=args.port,
                data_dir=resolve_data_dir(args.data),
                as_json=as_json,
            )
        except ValueError as exc:
            print(f"{exc}. Try: ark ui", file=sys.stderr)
            return 2
        except OSError as exc:
            reason = exc.strerror or "the port is not available"
            print(
                f"Could not open the vault UI on {args.host}:{args.port} ({reason}). "
                "Try: ark ui --port 8851",
                file=sys.stderr,
            )
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
        if as_json:
            _print_json(
                {
                    "ok": True,
                    "persistent_session": False,
                    "note": "CLI commands are one-shot; no persistent session to lock.",
                }
            )
        else:
            print("CLI commands are one-shot; no persistent session to lock.")
            print("The vault window clears in-memory keys. Run: ark ui")
        return 0

    if args.cmd == "sweep":
        try:
            with open(args.file, "rb") as handle:
                data = handle.read()
        except OSError as exc:
            return _fail_file(exc, args.file, "sweep")
        _digest, findings = scan_bytes(data)
        payload = {
            "flagged": bool(findings),
            "findings": findings_as_dicts(findings),
            "note": "Local intake filter. Not a network AV product. Payload is not stored.",
        }
        if as_json:
            _print_json(payload)
        elif findings:
            print("Blocked (Mode E). This file was not stored.")
            for item in payload["findings"]:
                print(f"{item['kind']}: {item['detail']}")
        else:
            print("clean. Nothing was stored.")
        return 1 if findings else 0

    session = None
    try:
        if args.cmd == "unlock":
            session = _open(args)
            tag = os.path.basename(session.vault_dir)[:12]
            if as_json:
                _print_json({"ok": True, "vault": tag, "level": session.security_level})
            else:
                print(f"Opened vault {tag}…")
                print("A different phrase opens a different vault.")
            return 0

        if args.cmd == "put":
            from ark.engine.ops import put_file

            try:
                session = _open(args)
                fid = put_file(session, args.file)
            except VirusFlagged:
                print(
                    "Blocked (Mode E). This file was not stored. Try: ark sweep notes.txt",
                    file=sys.stderr,
                )
                return 1
            except ValueError as exc:
                if "too large" in str(exc).lower():
                    print(
                        "That file is too large to store (limit 1 GiB). Try a smaller file.",
                        file=sys.stderr,
                    )
                    return 2
                raise
            except OSError as exc:
                return _fail_file(exc, args.file, "put")
            if as_json:
                _print_json({"id": fid, "name": os.path.basename(args.file)})
            else:
                print(f"Stored {os.path.basename(args.file)}")
                print(fid)
            return 0

        if args.cmd == "get":
            from ark.engine.decrypt import DecryptionFailed
            from ark.engine.ops import get_file

            session = _open(args)
            try:
                get_file(session, args.file_id, args.out_path)
            except DecryptionFailed:
                print(
                    uniform_failure_message() + " Check the phrase and the file id, then try again.",
                    file=sys.stderr,
                )
                return 1
            except OSError as exc:
                print(
                    f'Could not write "{args.out_path}". {exc.strerror or "Check the folder, then try again."}',
                    file=sys.stderr,
                )
                return 2
            if as_json:
                _print_json({"path": args.out_path, "id": args.file_id})
            else:
                print(f"Saved {args.out_path}")
            return 0

        if args.cmd == "list":
            from ark.engine.ops import list_entries

            session = _open(args)
            rows = list_entries(session)
            if as_json:
                _print_json(rows)
            elif not rows:
                print("No files in this vault yet.")
            else:
                for row in rows:
                    print(f"{row['id']}  {row['name']}")
            return 0
    finally:
        if session is not None:
            session.destroy()

    print(f'Unknown command "{args.cmd}". Try: ark ui   or   ark --help', file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
