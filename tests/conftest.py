"""Tests use tiny Argon2id and a tmp data dir. Never 256–1024 MiB."""

from __future__ import annotations

import os

os.environ["ARK_TEST_KDF"] = "1"
