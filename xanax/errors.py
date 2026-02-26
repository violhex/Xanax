"""
Error hierarchy for xanax library.

All API errors are mapped to specific exception types for easier error handling.
"""


class XanaxError(Exception):
    """
    Base exception for all xanax errors.

    This is the parent class for all library-specific exceptions.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(XanaxError):
    """
    Raised when authentication fails.

    This includes:
    - 401 HTTP responses
    - Missing API key when accessing NSFW content
    - Invalid API key
    """

    def __init__(self, message: str = "Authentication failed. Check your API key.") -> None:
        super().__init__(message)


class RateLimitError(XanaxError):
    """
    Raised when API rate limit is exceeded.

    The API allows 45 requests per minute. When exceeded, a 429 response
    is returned with retry information.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please wait before making more requests.",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class NotFoundError(XanaxError):
    """
    Raised when a requested resource is not found.

    This typically corresponds to a 404 HTTP response.
    """

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message)


class ValidationError(XanaxError):
    """
    Raised when request parameters are invalid.

    This includes:
    - Using topRange without toplist sorting
    - Invalid resolution format
    - Invalid ratio format
    - Other parameter validation failures
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class APIError(XanaxError):
    """
    Raised for unexpected API errors.

    This catches any other HTTP errors that don't fit the specific
    categories above. Includes the HTTP status code for debugging.
    """

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
