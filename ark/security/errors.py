"""Uniform error strategy to reduce oracle surface."""


def uniform_failure_message() -> str:
    # Same message for wrong passphrase, wrong vault phrase, corrupted file, etc.
    return "Unlock/decrypt failed."
