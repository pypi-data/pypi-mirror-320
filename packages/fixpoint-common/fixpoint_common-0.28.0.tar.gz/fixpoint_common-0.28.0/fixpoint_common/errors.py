"""Package-wide errors and exceptions for Fixpoint."""

__all__ = [
    "FixpointError",
    "NotFoundError",
    "ConfigError",
]


class FixpointError(Exception):
    """Base class for all Fixpoint errors."""


class NotFoundError(FixpointError):
    """The requested resource was not found."""


class ConfigError(FixpointError):
    """Error in configuration"""


class UnauthorizedError(FixpointError):
    """The request is unauthorized."""
