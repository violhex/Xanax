"""
Tests for xanax authentication handler.
"""

import pytest

from xanax.auth import AuthHandler
from xanax.enums import Purity


class TestAuthHandler:
    def test_no_api_key_initially(self):
        auth = AuthHandler()
        assert auth.has_api_key is False

    def test_with_api_key(self):
        auth = AuthHandler(api_key="test-key-123")
        assert auth.has_api_key is True

    def test_empty_string_not_authenticated(self):
        auth = AuthHandler(api_key="")
        assert auth.has_api_key is False

    def test_get_headers_without_key(self):
        auth = AuthHandler()
        headers = auth.get_headers()
        assert headers == {}

    def test_get_headers_with_key(self):
        auth = AuthHandler(api_key="test-key-123")
        headers = auth.get_headers()
        assert headers == {"X-API-Key": "test-key-123"}

    def test_get_query_params_without_key(self):
        auth = AuthHandler()
        params = auth.get_query_params()
        assert params == {}

    def test_get_query_params_with_key(self):
        auth = AuthHandler(api_key="test-key-123")
        params = auth.get_query_params()
        assert params == {"apikey": "test-key-123"}

    def test_check_nsfw_without_nsfw(self):
        auth = AuthHandler()
        assert auth.check_nsfw_access(False) is True

    def test_check_nsfw_with_nsfw_no_key(self):
        auth = AuthHandler()
        assert auth.check_nsfw_access(True) is False

    def test_check_nsfw_with_nsfw_with_key(self):
        auth = AuthHandler(api_key="test-key")
        assert auth.check_nsfw_access(True) is True

    def test_repr_does_not_expose_key(self):
        auth = AuthHandler(api_key="secret-key-123")
        repr_str = repr(auth)
        assert "secret-key" not in repr_str
        assert "yes" in repr_str

    def test_str_does_not_expose_key(self):
        auth = AuthHandler(api_key="secret-key-123")
        str_val = str(auth)
        assert "secret-key" not in str_val
