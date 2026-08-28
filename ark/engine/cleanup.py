"""Session cleanup helpers."""

from __future__ import annotations

from ark.engine.vault_session import ArkVaultSession


def close_session(session: ArkVaultSession) -> None:
    """Central place to close a session."""
    try:
        session.destroy()
    except Exception:
        pass
