"""Security helpers: uniform errors, memory wipe, optional keystore, Mode E."""

from ark.security.errors import uniform_failure_message
from ark.security.memory import zero_bytearray
from ark.security.virus import VirusFlagged, VirusFinding, scan_bytes, scan_bytes_or_raise

__all__ = [
    "VirusFlagged",
    "VirusFinding",
    "scan_bytes",
    "scan_bytes_or_raise",
    "uniform_failure_message",
    "zero_bytearray",
]
