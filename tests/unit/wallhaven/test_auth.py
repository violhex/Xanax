"""
Tests for Wallhaven authentication handler.
"""

import pytest

from xanax.sources.wallhaven.auth import AuthHandler


class TestAuthHandler:
    def test_no_api_key_initially(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        auth = AuthHandler()
        assert auth.has_api_key is False

    def test_with_api_key(self) -> None:
        auth = AuthHandler(api_key="test-key-123")
        assert auth.has_api_key is True

    def test_empty_string_not_authenticated(self) -> None:
        auth = AuthHandler(api_key="")
        assert auth.has_api_key is False

    def test_env_var_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WALLHAVEN_API_KEY", "env-key-456")
        auth = AuthHandler()
        assert auth.has_api_key is True
        assert auth.api_key == "env-key-456"

    def test_explicit_key_overrides_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WALLHAVEN_API_KEY", "env-key-456")
        auth = AuthHandler(api_key="explicit-key")
        assert auth.api_key == "explicit-key"

    def test_get_headers_without_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        auth = AuthHandler()
        headers = auth.get_headers()
        assert headers == {}

    def test_get_headers_with_key(self) -> None:
        auth = AuthHandler(api_key="test-key-123")
        headers = auth.get_headers()
        assert headers == {"X-API-Key": "test-key-123"}

    def test_check_nsfw_without_nsfw(self) -> None:
        auth = AuthHandler()
        assert auth.check_nsfw_access(False) is True

    def test_check_nsfw_with_nsfw_no_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        auth = AuthHandler()
        assert auth.check_nsfw_access(True) is False

    def test_check_nsfw_with_nsfw_with_key(self) -> None:
        auth = AuthHandler(api_key="test-key")
        assert auth.check_nsfw_access(True) is True

    def test_repr_does_not_expose_key(self) -> None:
        auth = AuthHandler(api_key="secret-key-123")
        repr_str = repr(auth)
        assert "secret-key" not in repr_str
        assert "yes" in repr_str

    def test_str_does_not_expose_key(self) -> None:
        auth = AuthHandler(api_key="secret-key-123")
        str_val = str(auth)
        assert "secret-key" not in str_val
