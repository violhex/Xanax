"""
Rate-limiting handler shared across all xanax source clients.

Provides rate-limit detection and optional retry logic with exponential
backoff. Each source client instantiates one of these with its own
``max_retries`` setting.
"""

import time
from contextlib import suppress
from typing import NoReturn

import httpx

from xanax.errors import RateLimitError


class RateLimitHandler:
    """
    Handles rate limit detection and optional retry logic.

    When a source returns a 429 response this handler either raises
    :class:`~xanax.errors.RateLimitError` immediately (``max_retries=0``)
    or waits and retries with exponential backoff.

    Args:
        max_retries: Maximum retry attempts on 429. Default is 0 (fail-fast).
        initial_delay: Initial wait in seconds before the first retry.
        backoff_factor: Multiplier applied to the delay after each attempt.
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
        """Whether retry functionality is enabled."""
        return self._enabled

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        return self._max_retries

    def get_retry_after(self, response: httpx.Response) -> int | None:
        """Extract the Retry-After value from response headers, if present."""
        retry_after = response.headers.get("retry-after")
        if retry_after:
            with suppress(ValueError):
                return int(retry_after)
        return None

    def calculate_delay(self, attempt: int) -> float:
        """Return the backoff delay in seconds for the given attempt number."""
        return self._initial_delay * (self._backoff_factor**attempt)

    def should_retry(self, response: httpx.Response, attempt: int) -> bool:
        """Return True if the request should be retried."""
        return response.status_code == 429 and self._enabled and attempt < self._max_retries

    def handle_rate_limit(self, response: httpx.Response) -> NoReturn:
        """Raise :class:`~xanax.errors.RateLimitError` for a 429 response."""
        retry_after = self.get_retry_after(response)
        message = "Rate limit exceeded. Please wait before making more requests."
        if retry_after:
            message = f"Rate limit exceeded. Please wait {retry_after} seconds."
        raise RateLimitError(message=message, retry_after=retry_after)

    def wait_before_retry(self, attempt: int) -> None:
        """Block for the appropriate delay before the next retry."""
        if self._enabled:
            time.sleep(self.calculate_delay(attempt))

    def __repr__(self) -> str:
        return f"RateLimitHandler(enabled={self._enabled}, max_retries={self._max_retries})"


def check_rate_limit(response: httpx.Response) -> None:
    """
    Raise :class:`~xanax.errors.RateLimitError` if the response is a 429.

    A lightweight helper for clients that do not use :class:`RateLimitHandler`.
    """
    if response.status_code == 429:
        retry_after: int | None = None
        with suppress(ValueError):
            header = response.headers.get("retry-after")
            if header:
                retry_after = int(header)
        message = "Rate limit exceeded. Please wait before making more requests."
        raise RateLimitError(message=message, retry_after=retry_after)
