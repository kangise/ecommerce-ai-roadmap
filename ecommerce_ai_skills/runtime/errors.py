"""Errors exposed by the runtime boundary.

The API maps these errors to stable JSON responses.  Keeping the errors
explicit prevents an integration failure from being mistaken for success.
"""


class RuntimeErrorBase(Exception):
    """Base class for expected runtime errors."""


class ValidationError(RuntimeErrorBase):
    pass


class AuthenticationError(RuntimeErrorBase):
    pass


class AuthorizationError(RuntimeErrorBase):
    pass


class ConflictError(RuntimeErrorBase):
    pass


class NotFoundError(RuntimeErrorBase):
    pass


class ConnectorError(RuntimeErrorBase):
    pass


class MissingCredentialError(ConnectorError):
    pass


class ConnectorNotConfiguredError(ConnectorError):
    pass


class ExternalServiceError(ConnectorError):
    pass


class RateLimitError(RuntimeErrorBase):
    """The caller exceeded the in-process request budget."""

    def __init__(self, message: str = "request rate limit exceeded", retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after
