"""
Tests for xanax error classes.
"""


from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    XanaxError,
)


class TestXanaxError:
    def test_base_error_message(self):
        err = XanaxError("test error")
        assert err.message == "test error"
        assert str(err) == "test error"

    def test_base_error_inheritance(self):
        err = XanaxError("test")
        assert isinstance(err, Exception)


class TestAuthenticationError:
    def test_default_message(self):
        err = AuthenticationError()
        assert "API key" in err.message

    def test_custom_message(self):
        err = AuthenticationError("Custom auth error")
        assert err.message == "Custom auth error"


class TestRateLimitError:
    def test_default_message(self):
        err = RateLimitError()
        assert "Rate limit" in err.message

    def test_with_retry_after(self):
        err = RateLimitError(retry_after=60)
        assert err.retry_after == 60

    def test_without_retry_after(self):
        err = RateLimitError()
        assert err.retry_after is None


class TestNotFoundError:
    def test_default_message(self):
        err = NotFoundError()
        assert err.message == "Resource not found."

    def test_custom_message(self):
        err = NotFoundError("Custom not found")
        assert err.message == "Custom not found"


class TestValidationError:
    def test_carries_message(self):
        err = ValidationError("Invalid parameter")
        assert err.message == "Invalid parameter"


class TestAPIError:
    def test_includes_status_code(self):
        err = APIError("API failed", status_code=500)
        assert err.status_code == 500

    def test_message_accessible(self):
        err = APIError("API failed", status_code=500)
        assert err.message == "API failed"
