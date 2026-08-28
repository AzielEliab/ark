"""Opaque file identifiers."""

from __future__ import annotations

import uuid


def new_file_id() -> str:
    """Generate a random opaque file id for on-disk storage."""
    return uuid.uuid4().hex
