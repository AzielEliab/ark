"""Local ARK UI. Bind 127.0.0.1:8850 only.

Phrase field, level, unlock, list, upload encrypt (multipart), download
decrypt, sweep, lock. Dark matte/gold. Banner not-a-kernel.
Self-contained CSS, no CDN, no telemetry. Never logs phrases.
"""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from ark.config import AUTOLOCK_SECONDS, LIMITATION, SECURITY_LEVELS
from ark.engine.cleanup import close_session
from ark.security.errors import uniform_failure_message
from ark.security.virus import VirusFlagged, findings_as_dicts, scan_bytes
from ark.utils import resolve_data_dir

LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
WEB = files("ark") / "web"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


class _State:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.session = None
        self.last_activity = 0.0

    def touch(self) -> None:
        self.last_activity = time.time()

    def autolock(self) -> None:
        if self.session is None:
            return
        level = self.session.security_level or "normal"
        limit = AUTOLOCK_SECONDS.get(level, AUTOLOCK_SECONDS["normal"])
        if time.time() - self.last_activity >= limit:
            close_session(self.session)
            self.session = None


def _web_bytes(name: str) -> bytes:
    return (WEB / name).read_bytes()


def _parse_multipart(content_type: str, body: bytes) -> dict[str, tuple[str, bytes]]:
    """Minimal multipart parser. Returns field -> (filename, data)."""
    out: dict[str, tuple[str, bytes]] = {}
    if "multipart/form-data" not in (content_type or ""):
        return out
    boundary = ""
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("boundary="):
            boundary = part.split("=", 1)[1].strip().strip('"')
    if not boundary:
        return out
    raw = b"--" + boundary.encode("utf-8")
    chunks = body.split(raw)
    for chunk in chunks:
        chunk = chunk.strip(b"\r\n")
        if not chunk or chunk == b"--":
            continue
        if b"\r\n\r\n" not in chunk:
            continue
        head, data = chunk.split(b"\r\n\r\n", 1)
        if data.endswith(b"--"):
            data = data[:-2]
        data = data.rstrip(b"\r\n")
        headers = head.decode("utf-8", "replace")
        name = ""
        filename = ""
        for line in headers.split("\r\n"):
            if line.lower().startswith("content-disposition:"):
                for item in line.split(";"):
                    item = item.strip()
                    if item.startswith("name="):
                        name = item.split("=", 1)[1].strip().strip('"')
                    elif item.startswith("filename="):
                        filename = item.split("=", 1)[1].strip().strip('"')
        if name:
            out[name] = (filename, data)
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "ARK/0.1.0"
    state: _State

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: object) -> None:
        body = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or "0")
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        self.state.autolock()
        if path in {"/", "/index.html"}:
            self._send(200, _web_bytes("index.html"), MIME[".html"])
            return
        if path == "/style.css":
            self._send(200, _web_bytes("style.css"), MIME[".css"])
            return
        if path == "/app.js":
            self._send(200, _web_bytes("app.js"), MIME[".js"])
            return
        if path == "/api/status":
            sess = self.state.session
            self._json(
                200,
                {
                    "unlocked": sess is not None and not sess._destroyed,
                    "level": None if sess is None else sess.security_level,
                    "limitation": LIMITATION,
                },
            )
            return
        if path == "/api/list":
            if self.state.session is None:
                self._json(401, {"error": "locked", "limitation": LIMITATION})
                return
            from ark.engine.ops import list_entries

            self.state.touch()
            self._json(200, {"entries": list_entries(self.state.session)})
            return
        if path == "/api/get":
            if self.state.session is None:
                self._json(401, {"error": "locked"})
                return
            qs = parse_qs(parsed.query)
            fid = (qs.get("id") or [""])[0]
            if not fid:
                self._json(400, {"error": "id required"})
                return
            import tempfile

            from ark.engine.decrypt import DecryptionFailed
            from ark.engine.ops import get_file, list_entries

            name = fid
            for row in list_entries(self.state.session):
                if row["id"] == fid:
                    name = row["name"]
                    break
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.close()
            try:
                get_file(self.state.session, fid, tmp.name)
                data = Path(tmp.name).read_bytes()
            except DecryptionFailed:
                self._json(400, {"error": uniform_failure_message()})
                return
            finally:
                try:
                    os.remove(tmp.name)
                except Exception:
                    pass
            self.state.touch()
            safe = name.replace('"', "")
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{safe}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        self.state.autolock()
        raw = self._body()
        ctype = self.headers.get("Content-Type") or ""

        if path == "/api/unlock":
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "JSON body required"})
                return
            phrase = str(payload.get("phrase") or "")
            level = str(payload.get("level") or "normal")
            if not phrase:
                self._json(400, {"error": "A phrase is required."})
                return
            from ark.engine.vault_session import open_or_create_vault

            if self.state.session is not None:
                close_session(self.state.session)
            try:
                self.state.session = open_or_create_vault(self.state.data_dir, phrase, level)
            except Exception:
                self._json(400, {"error": uniform_failure_message()})
                return
            self.state.touch()
            tag = os.path.basename(self.state.session.vault_dir)
            self._json(
                200,
                {
                    "ok": True,
                    "vault": tag[:12],
                    "level": self.state.session.security_level,
                    "note": "A wrong phrase silently opens a different empty vault.",
                    "limitation": LIMITATION,
                },
            )
            return

        if path == "/api/lock":
            if self.state.session is not None:
                close_session(self.state.session)
                self.state.session = None
            self._json(200, {"ok": True, "unlocked": False})
            return

        if path == "/api/sweep":
            data = b""
            if "multipart/form-data" in ctype:
                parts = _parse_multipart(ctype, raw)
                data = (parts.get("file") or ("", b""))[1]
            else:
                try:
                    payload = json.loads(raw.decode("utf-8") or "{}")
                except json.JSONDecodeError:
                    payload = {}
                if payload.get("b64"):
                    import base64

                    data = base64.b64decode(payload["b64"])
                else:
                    data = str(payload.get("text") or "").encode("utf-8")
            _h, findings = scan_bytes(data)
            self._json(
                200,
                {
                    "flagged": bool(findings),
                    "findings": findings_as_dicts(findings),
                    "note": "Local intake filter. Payload is not stored.",
                },
            )
            return

        if path == "/api/put":
            if self.state.session is None:
                self._json(401, {"error": "locked"})
                return
            filename = "upload.bin"
            data = b""
            if "multipart/form-data" in ctype:
                parts = _parse_multipart(ctype, raw)
                filename, data = parts.get("file") or ("upload.bin", b"")
                filename = filename or "upload.bin"
            else:
                try:
                    payload = json.loads(raw.decode("utf-8") or "{}")
                except json.JSONDecodeError:
                    self._json(400, {"error": "multipart or JSON required"})
                    return
                import base64

                filename = str(payload.get("name") or "upload.bin")
                data = base64.b64decode(payload.get("b64") or b"")
            from ark.engine.ops import put_bytes

            try:
                fid = put_bytes(self.state.session, data, filename)
            except VirusFlagged:
                self._json(400, {"error": "ARK blocked file (Mode E)", "flagged": True})
                return
            self.state.touch()
            self._json(200, {"ok": True, "id": fid, "name": filename})
            return

        self._json(404, {"error": "not found"})


def make_server(host: str = "127.0.0.1", port: int = 8850, data_dir: str | None = None) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError("ARK UI binds loopback only (127.0.0.1)")
    state = _State(resolve_data_dir(data_dir))

    class Bound(Handler):
        pass

    Bound.state = state
    return ThreadingHTTPServer((host, port), Bound)


def serve(host: str = "127.0.0.1", port: int = 8850, data_dir: str | None = None) -> None:
    httpd = make_server(host, port, data_dir=data_dir)
    bound_host, bound_port = httpd.server_address[:2]
    print(
        f"ARK UI http://{bound_host}:{bound_port} "
        "(loopback only; not a kernel; local deniable vault; no telemetry)"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        try:
            handler = httpd.RequestHandlerClass
            sess = getattr(handler, "state", None)
            if sess is not None and sess.session is not None:
                close_session(sess.session)
        except Exception:
            pass
        httpd.server_close()
