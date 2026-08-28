"""Local UI: loopback only, GET / contains ARK."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from ark.ui import LOOPBACK, make_server


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def test_ui_get_root_contains_ark(tmp_path) -> None:
    httpd = make_server("127.0.0.1", 0, data_dir=str(tmp_path))
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
        assert "ARK" in html
        assert "The ARK" in html
        assert "not a kernel" in html.lower()
        assert "cdnjs" not in html.lower() and "unpkg" not in html.lower() and "jsdelivr" not in html.lower()
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/style.css", timeout=3) as resp:
            css = resp.read().decode("utf-8")
        assert "c9a227" in css or "--gold" in css
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/unlock",
            data=json.dumps({"phrase": "ui-test-phrase", "level": "normal"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["ok"] is True
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/list", timeout=5) as resp:
            listed = json.loads(resp.read().decode("utf-8"))
        assert listed["entries"] == []
    finally:
        httpd.shutdown()
        httpd.server_close()
