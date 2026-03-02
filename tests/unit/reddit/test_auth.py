"""
Tests for Reddit OAuth2 authentication helpers.
"""

import time
from unittest.mock import Mock, patch

import pytest

from xanax.errors import AuthenticationError
from xanax.sources.reddit.auth import AsyncRedditAuth, RedditAuth

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_token_response(
    status_code: int = 200,
    access_token: str = "test-token-abc",
    expires_in: int = 3600,
) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "scope": "*",
    }
    return response


# ---------------------------------------------------------------------------
# RedditAuth (sync)
# ---------------------------------------------------------------------------


class TestRedditAuth:
    def _make_auth(self) -> RedditAuth:
        return RedditAuth(
            client_id="my-client-id",
            client_secret="my-client-secret",
            user_agent="python:test/1.0 (by u/testuser)",
        )

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_get_token_fetches_on_first_call(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        token = auth.get_token()

        assert token == "test-token-abc"
        mock_client.post.assert_called_once()

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_get_token_reuses_cached_token(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        token1 = auth.get_token()
        token2 = auth.get_token()

        assert token1 == token2
        # Should only call the token endpoint once
        assert mock_client.post.call_count == 1

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_get_token_refetches_when_expired(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.side_effect = [
            _make_token_response(access_token="token-1"),
            _make_token_response(access_token="token-2"),
        ]
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        auth.get_token()

        # Simulate expiry by forcing the expiry time into the past
        auth._token_expiry = time.time() - 1

        token2 = auth.get_token()
        assert token2 == "token-2"
        assert mock_client.post.call_count == 2

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_401_raises_authentication_error(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response(status_code=401)
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        with pytest.raises(AuthenticationError) as exc_info:
            auth.get_token()
        assert (
            "client_id" in str(exc_info.value).lower()
            or "authentication" in str(exc_info.value).lower()
        )

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_non_200_non_401_raises_authentication_error(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response(status_code=500)
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        with pytest.raises(AuthenticationError):
            auth.get_token()

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_missing_access_token_raises_authentication_error(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        bad_response = Mock()
        bad_response.status_code = 200
        bad_response.json.return_value = {"token_type": "bearer"}  # no access_token
        mock_client.post.return_value = bad_response
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        with pytest.raises(AuthenticationError):
            auth.get_token()

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_get_headers_returns_correct_authorization(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response(access_token="mytoken")
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        headers = auth.get_headers()

        assert headers["Authorization"] == "Bearer mytoken"
        assert headers["User-Agent"] == "python:test/1.0 (by u/testuser)"

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_post_uses_basic_auth(self, mock_client_cls: Mock) -> None:
        """Token POST must use HTTP Basic (client_id, client_secret)."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        auth.get_token()

        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["auth"] == ("my-client-id", "my-client-secret")
        assert call_kwargs["data"] == {"grant_type": "client_credentials"}

    def test_repr_no_token(self) -> None:
        auth = self._make_auth()
        assert "token_cached=False" in repr(auth)

    @patch("xanax.sources.reddit.auth.httpx.Client")
    def test_repr_with_token(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        auth.get_token()
        assert "token_cached=True" in repr(auth)


# ---------------------------------------------------------------------------
# AsyncRedditAuth
# ---------------------------------------------------------------------------


class TestAsyncRedditAuth:
    def _make_auth(self) -> AsyncRedditAuth:
        return AsyncRedditAuth(
            client_id="my-client-id",
            client_secret="my-client-secret",
            user_agent="python:test/1.0 (by u/testuser)",
        )

    @patch("xanax.sources.reddit.auth.httpx.AsyncClient")
    async def test_get_token_fetches_on_first_call(self, mock_client_cls: Mock) -> None:
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        token = await auth.get_token()

        assert token == "test-token-abc"
        mock_client.post.assert_called_once()

    @patch("xanax.sources.reddit.auth.httpx.AsyncClient")
    async def test_get_token_reuses_cached_token(self, mock_client_cls: Mock) -> None:
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = _make_token_response()
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        t1 = await auth.get_token()
        t2 = await auth.get_token()

        assert t1 == t2
        assert mock_client.post.call_count == 1

    @patch("xanax.sources.reddit.auth.httpx.AsyncClient")
    async def test_get_token_refetches_when_expired(self, mock_client_cls: Mock) -> None:
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.side_effect = [
            _make_token_response(access_token="token-1"),
            _make_token_response(access_token="token-2"),
        ]
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        await auth.get_token()
        auth._token_expiry = time.time() - 1
        token2 = await auth.get_token()

        assert token2 == "token-2"
        assert mock_client.post.call_count == 2

    @patch("xanax.sources.reddit.auth.httpx.AsyncClient")
    async def test_401_raises_authentication_error(self, mock_client_cls: Mock) -> None:
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = _make_token_response(status_code=401)
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        with pytest.raises(AuthenticationError):
            await auth.get_token()

    @patch("xanax.sources.reddit.auth.httpx.AsyncClient")
    async def test_get_headers_returns_correct_authorization(self, mock_client_cls: Mock) -> None:
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value = _make_token_response(access_token="async-token")
        mock_client_cls.return_value = mock_client

        auth = self._make_auth()
        headers = await auth.get_headers()

        assert headers["Authorization"] == "Bearer async-token"
        assert headers["User-Agent"] == "python:test/1.0 (by u/testuser)"

    def test_repr_no_token(self) -> None:
        auth = self._make_auth()
        assert "token_cached=False" in repr(auth)
