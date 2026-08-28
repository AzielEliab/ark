"""This tree is The ARK only. Not merged into sibling products."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "ark"

FORBIDDEN_ROOTS = frozenset(
    {
        "forgereceipts",
        "zionpattern",
        "zion_pattern",
        "zion_pattern_solver",
        "decisiongate",
        "azos",
        "az_os",
        "veillock",
        "vibelock",
        "godlock",
        "codelock",
        "shadowlock",
        "temporallock",
        "staticclock",
        "miragegrid",
        "glossafilter",
        "clce",
        "azclce",
        "az_clce",
    }
)


def _root_of(name: str) -> str:
    return name.split(".")[0].lower().replace("-", "_")


def test_package_never_imports_siblings() -> None:
    import ark  # noqa: F401
    import ark.cli  # noqa: F401
    import ark.ui  # noqa: F401
    import ark.engine.encrypt  # noqa: F401

    for name in list(sys.modules):
        assert _root_of(name) not in FORBIDDEN_ROOTS


def test_source_imports_isolated() -> None:
    for py in PKG.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert _root_of(alias.name) not in FORBIDDEN_ROOTS
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert _root_of(node.module) not in FORBIDDEN_ROOTS


def test_not_inside_sibling_products() -> None:
    text = str(ROOT)
    assert text.endswith("/ark") or text.endswith("\\ark") or "/ark" in text
    assert "forgereceipts" not in text
    assert "azos" not in Path(ROOT.name).as_posix()
    assert (PKG / "engine" / "encrypt.py").is_file()
    assert not (ROOT / "azos").exists()
    assert not (ROOT / "godlock").exists()
    assert not (ROOT / "forgereceipts").exists()
    assert not (ROOT / "glossafilter").exists()


def test_worker_isolated() -> None:
    toml = (ROOT / "workers" / "download-tracker" / "wrangler.toml").read_text(encoding="utf-8")
    assert 'name = "ark-download-tracker"' in toml
    assert 'account_id = "ac575a9b822bea2bed97d0ab73aed238"' in toml
    assert 'binding = "DOWNLOADS"' in toml
    assert "/count" in toml
    assert "/download" in toml
    assert "/stats" in toml
    src = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(encoding="utf-8")
    assert 'const PROJECT = "ark"' in src
    assert "ark-0.1.0.tar.gz" in src
    assert "ark|__total__" in src or 'PROJECT + "|__total__"' in src
    assert "Isolated counter" in src
    assert "env.ASSETS.fetch" in src
    assert "private, no-store" in src
    assert "/v1/sweep" in src
    assert "/v1/levels" in src
    assert "unlock" not in src.lower() or "Do NOT add unlock" in src or "never" in src.lower()
    lowered = src.lower().replace("-", "").replace("_", "").replace(" ", "")
    assert "forgereceipts" not in lowered
    assert "godlock" not in lowered
    assert "azos" not in lowered or "standalone" in src.lower()
    engine = (ROOT / "workers" / "download-tracker" / "src" / "engine.js").read_text(encoding="utf-8")
    assert "no clamscan" in engine.lower()
    assert "which(" not in engine.lower()
    assert "passphrase" in engine.lower()  # mentioned only as something we do NOT accept
    assert "takes a passphrase" in engine.lower()
    assert "encrypt/decrypt" in engine.lower()


def test_readme_honest_scope() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    low = readme.lower()
    assert "not a kernel" in low
    assert "deniable" in low
    assert "forgotten phrase" in low
    assert "950/1000" not in readme
    assert "do not treat this as" in low
    assert "military-grade" in low  # denied, not claimed
    assert "Forks are welcome" in readme
    assert "ark-download-tracker.vibelock.workers.dev" in readme
    assert "standalone" in low
    assert "az-os" in low or "AZ-OS" in readme
