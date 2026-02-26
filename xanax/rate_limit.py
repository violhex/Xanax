"""
Rate limiting handling for Wallhaven API.

The API allows 45 requests per minute. This module provides
rate limit detection and optional retry functionality.
"""

import time
from contextlib import suppress

import httpx

from xanax.errors import RateLimitError


class RateLimitHandler:
    """
    Handles rate limit detection and optional retry logic.

    The Wallhaven API allows 45 requests per minute. When exceeded,
    the API returns a 429 response.

    This handler provides:
    - Rate limit detection
    - Optional automatic retry with exponential backoff
    - Configurable retry behavior
    """

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_INITIAL_DELAY = 1.0
    DEFAULT_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        max_retries: int = 0,
        initial_delay: float = DEFAULT_INITIAL_DELAY,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> None:
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._backoff_factor = backoff_factor
        self._enabled = max_retries > 0

    @property
    def is_enabled(self) -> bool:
        """Check if retry functionality is enabled."""
        return self._enabled

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        return self._max_retries

    def get_retry_after(self, response: httpx.Response) -> int | None:
        """
        Extract retry-after value from response headers.

        Returns:
            Number of seconds to wait, or None if not specified.
        """
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return None

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given retry attempt.

        Uses exponential backoff: initial_delay * (backoff_factor ^ attempt)

        Args:
            attempt: The retry attempt number (0-indexed).

        Returns:
            Delay in seconds before the next retry.
        """
        return self._initial_delay * (self._backoff_factor**attempt)

    def should_retry(self, response: httpx.Response, attempt: int) -> bool:
        """
        Determine if a request should be retried.

        Args:
            response: The HTTP response from the API.
            attempt: Current retry attempt number.

        Returns:
            True if the request should be retried.
        """
        return response.status_code == 429 and self._enabled and attempt < self._max_retries

    def handle_rate_limit(self, response: httpx.Response) -> None:
        """
        Handle a rate limit response by raising appropriate error.

        Args:
            response: The HTTP response that triggered rate limiting.

        Raises:
            RateLimitError: Always raised for 429 responses.
        """
        retry_after = self.get_retry_after(response)
        message = "Rate limit exceeded. Please wait before making more requests."

        if retry_after:
            message = f"Rate limit exceeded. Please wait {retry_after} seconds."

        raise RateLimitError(message=message, retry_after=retry_after)

    def wait_before_retry(self, attempt: int) -> None:
        """
        Wait for the appropriate delay before retrying.

        Args:
            attempt: The retry attempt number.
        """
        if self._enabled:
            delay = self.calculate_delay(attempt)
            time.sleep(delay)

    def __repr__(self) -> str:
        return f"RateLimitHandler(enabled={self._enabled}, max_retries={self._max_retries})"


def check_rate_limit(response: httpx.Response) -> None:
    """
    Check if response indicates rate limiting and raise appropriate error.

    Args:
        response: The HTTP response from the API.

    Raises:
        RateLimitError: If response is a 429.
    """
    if response.status_code == 429:
        retry_after = None
        retry_after_header = response.headers.get("retry-after")
        if retry_after_header:
            with suppress(ValueError):
                retry_after = int(retry_after_header)

        message = "Rate limit exceeded. Please wait before making more requests."
        raise RateLimitError(message=message, retry_after=retry_after)
