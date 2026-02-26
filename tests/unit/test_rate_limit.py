"""
Tests for xanax rate limit handler.
"""

import pytest

from unittest.mock import Mock

from xanax.errors import RateLimitError
from xanax.rate_limit import RateLimitHandler, check_rate_limit


class TestRateLimitHandler:
    def test_default_disabled(self):
        handler = RateLimitHandler()
        assert handler.is_enabled is False
        assert handler.max_retries == 0

    def test_enabled_with_retries(self):
        handler = RateLimitHandler(max_retries=3)
        assert handler.is_enabled is True
        assert handler.max_retries == 3

    def test_calculate_delay(self):
        handler = RateLimitHandler(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
        assert handler.calculate_delay(0) == 1.0
        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 4.0

    def test_should_retry_when_enabled(self):
        handler = RateLimitHandler(max_retries=3)
        response = Mock()
        response.status_code = 429

        assert handler.should_retry(response, 0) is True
        assert handler.should_retry(response, 1) is True
        assert handler.should_retry(response, 2) is True
        assert handler.should_retry(response, 3) is False

    def test_should_retry_when_disabled(self):
        handler = RateLimitHandler(max_retries=0)
        response = Mock()
        response.status_code = 429

        assert handler.should_retry(response, 0) is False

    def test_should_not_retry_non_429(self):
        handler = RateLimitHandler(max_retries=3)
        response = Mock()
        response.status_code = 200

        assert handler.should_retry(response, 0) is False

    def test_get_retry_after_from_header(self):
        handler = RateLimitHandler()
        response = Mock()
        response.headers = {"retry-after": "60"}

        assert handler.get_retry_after(response) == 60

    def test_get_retry_after_invalid(self):
        handler = RateLimitHandler()
        response = Mock()
        response.headers = {"retry-after": "invalid"}

        assert handler.get_retry_after(response) is None

    def test_get_retry_after_missing(self):
        handler = RateLimitHandler()
        response = Mock()
        response.headers = {}

        assert handler.get_retry_after(response) is None

    def test_handle_rate_limit_raises(self):
        handler = RateLimitHandler()
        response = Mock()
        response.status_code = 429
        response.headers = {}

        with pytest.raises(RateLimitError) as exc_info:
            handler.handle_rate_limit(response)

        assert "Rate limit" in exc_info.value.message


class TestCheckRateLimit:
    def test_raises_on_429(self):
        response = Mock()
        response.status_code = 429
        response.headers = {}

        with pytest.raises(RateLimitError):
            check_rate_limit(response)

    def test_does_nothing_on_success(self):
        response = Mock()
        response.status_code = 200

        check_rate_limit(response)
