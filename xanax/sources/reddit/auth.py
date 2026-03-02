"""
OAuth2 authentication helpers for the Reddit API.

Reddit requires app-only OAuth2 for all authenticated API access, even
for reading public subreddits. :class:`RedditAuth` and
:class:`AsyncRedditAuth` transparently fetch and cache access tokens,
re-fetching automatically when fewer than 60 seconds remain before expiry.

Token endpoint: ``POST https://www.reddit.com/api/v1/access_token``
Grant type: ``client_credentials``
Auth: HTTP Basic (client_id : client_secret)
"""

import time

import httpx

from xanax.errors import AuthenticationError


class RedditAuth:
    """
    Manages OAuth2 app-only authentication for the Reddit API (synchronous).

    Transparently fetches and caches access tokens, re-fetching when less than
    60 seconds remain before expiry. The token endpoint requires HTTP Basic
    authentication using the app ``client_id`` and ``client_secret``.

    Example:
        auth = RedditAuth(
            client_id="my-client-id",
            client_secret="my-client-secret",
            user_agent="python:myapp/1.0 (by u/myname)",
        )
        headers = auth.get_headers()  # {"Authorization": "Bearer <token>", ...}

    Args:
        client_id: Reddit app client ID from https://www.reddit.com/prefs/apps.
        client_secret: Reddit app client secret.
        user_agent: Required User-Agent string. Reddit rejects requests without
                    a meaningful UA. Recommended format:
                    ``platform:app_id/version (by u/username)``.
    """

    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    # Refresh this many seconds before the token actually expires
    _EXPIRY_BUFFER_SECONDS = 60

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._token: str | None = None
        self._token_expiry: float = 0.0

    def get_token(self) -> str:
        """
        Return a valid access token, fetching a new one if expired.

        A new token is fetched when no token has been cached yet, or when
        fewer than 60 seconds remain until the current token expires.

        Returns:
            A valid Bearer access token string.

        Raises:
            AuthenticationError: If the token endpoint rejects the credentials.
        """
        if self._token is None or time.time() >= self._token_expiry:
            self._fetch_token()
        assert self._token is not None
        return self._token

    def _fetch_token(self) -> None:
        """
        POST to the token endpoint and cache the result.

        Raises:
            AuthenticationError: If the response status is not 200, or if the
                response body does not contain an ``access_token``.
        """
        with httpx.Client() as client:
            response = client.post(
                self.TOKEN_URL,
                auth=(self._client_id, self._client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": self._user_agent},
            )

        if response.status_code == 401:
            raise AuthenticationError(
                "Reddit authentication failed. Check your client_id and client_secret."
            )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Reddit token request failed with status {response.status_code}."
            )

        body = response.json()
        token = body.get("access_token")
        if not token:
            raise AuthenticationError("Reddit token response did not contain an access_token.")

        expires_in: int = body.get("expires_in", 3600)
        self._token = token
        self._token_expiry = time.time() + expires_in - self._EXPIRY_BUFFER_SECONDS

    def get_headers(self) -> dict[str, str]:
        """
        Return HTTP headers required for authenticated Reddit API requests.

        Calls :meth:`get_token` internally, fetching a fresh token if needed.

        Returns:
            Dictionary containing ``Authorization`` and ``User-Agent`` headers.
        """
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "User-Agent": self._user_agent,
        }

    def __repr__(self) -> str:
        has_token = self._token is not None
        return f"RedditAuth(client_id={self._client_id!r}, token_cached={has_token})"


class AsyncRedditAuth:
    """
    Manages OAuth2 app-only authentication for the Reddit API (asynchronous).

    Async counterpart to :class:`RedditAuth`. All token operations are
    coroutines — ``await auth.get_token()`` returns a valid Bearer token,
    fetching a new one if the cache is stale.

    Example:
        auth = AsyncRedditAuth(
            client_id="my-client-id",
            client_secret="my-client-secret",
            user_agent="python:myapp/1.0 (by u/myname)",
        )
        headers = await auth.get_headers()

    Args:
        client_id: Reddit app client ID.
        client_secret: Reddit app client secret.
        user_agent: Required User-Agent string.
    """

    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    _EXPIRY_BUFFER_SECONDS = 60

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._token: str | None = None
        self._token_expiry: float = 0.0

    async def get_token(self) -> str:
        """
        Return a valid access token, fetching a new one if expired.

        Returns:
            A valid Bearer access token string.

        Raises:
            AuthenticationError: If the token endpoint rejects the credentials.
        """
        if self._token is None or time.time() >= self._token_expiry:
            await self._fetch_token()
        assert self._token is not None
        return self._token

    async def _fetch_token(self) -> None:
        """
        POST to the token endpoint and cache the result.

        Raises:
            AuthenticationError: If the response status is not 200, or if the
                response body does not contain an ``access_token``.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                auth=(self._client_id, self._client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": self._user_agent},
            )

        if response.status_code == 401:
            raise AuthenticationError(
                "Reddit authentication failed. Check your client_id and client_secret."
            )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Reddit token request failed with status {response.status_code}."
            )

        body = response.json()
        token = body.get("access_token")
        if not token:
            raise AuthenticationError("Reddit token response did not contain an access_token.")

        expires_in: int = body.get("expires_in", 3600)
        self._token = token
        self._token_expiry = time.time() + expires_in - self._EXPIRY_BUFFER_SECONDS

    async def get_headers(self) -> dict[str, str]:
        """
        Return HTTP headers required for authenticated Reddit API requests.

        Calls :meth:`get_token` internally, fetching a fresh token if needed.

        Returns:
            Dictionary containing ``Authorization`` and ``User-Agent`` headers.
        """
        return {
            "Authorization": f"Bearer {await self.get_token()}",
            "User-Agent": self._user_agent,
        }

    def __repr__(self) -> str:
        has_token = self._token is not None
        return f"AsyncRedditAuth(client_id={self._client_id!r}, token_cached={has_token})"
