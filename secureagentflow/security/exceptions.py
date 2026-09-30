"""Security-layer exceptions."""


class SecurityError(Exception):
    """Base class for security policy failures."""


class IdentityError(SecurityError):
    """Raised when a sender identity cannot be authenticated."""


class ReplayError(SecurityError):
    """Raised when a message is outside the time window or already seen."""


class PermissionDenied(SecurityError):
    """Raised when a capability policy denies an operation."""


class QuarantinedInput(SecurityError):
    """Raised when an input is quarantined by policy."""
