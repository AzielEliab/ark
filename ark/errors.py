"""Centralized exceptions for ARK."""


class ArkError(Exception):
    """Base class for all ARK exceptions."""


class ArkConfigError(ArkError):
    pass


class ArkVaultError(ArkError):
    pass


class ArkCryptoError(ArkError):
    pass


class ArkIOError(ArkError):
    pass
