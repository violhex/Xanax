"""
Async Xanax client for interacting with Wallhaven API.

Provides an asynchronous interface identical to :class:`~xanax.client.Xanax`
but built on ``httpx.AsyncClient`` for use with ``asyncio``.
"""

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx

from xanax.auth import AuthHandler
from xanax.enums import Purity
from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
)
from xanax.models import (
    Collection,
    CollectionListing,
    SearchResult,
    Tag,
    UserSettings,
    Wallpaper,
)
from xanax.pagination import PaginationHelper
from xanax.rate_limit import RateLimitHandler
from xanax.search import SearchParams


class AsyncXanax:
    """
    Async client for Wallhaven API v1.

    Drop-in async counterpart to :class:`~xanax.client.Xanax`. All public methods
    are coroutines. Use as an async context manager for automatic resource cleanup.

    The API key can be passed directly or read from the ``WALLHAVEN_API_KEY``
    environment variable.

    Example:
        async with AsyncXanax(api_key="your-api-key") as client:
            results = await client.search(SearchParams(query="anime"))

            async for wallpaper in client.aiter_wallpapers(SearchParams(query="nature")):
                print(wallpaper.path)

    Args:
        api_key: Wallhaven API key for authenticated requests.
                 Falls back to the ``WALLHAVEN_API_KEY`` environment variable.
                 Optional but required for NSFW content.
        timeout: Request timeout in seconds. Default is 30.
        max_retries: Maximum number of retries on rate limiting (429).
                     Default is 0 (fail-fast). Set to 3 for automatic retry
                     with exponential backoff.
    """

    BASE_URL = "https://wallhaven.cc/api/v1"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> None:
        self._auth = AuthHandler(api_key=api_key)
        self._rate_limit = RateLimitHandler(max_retries=max_retries)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        )

    @property
    def is_authenticated(self) -> bool:
        """Check if the client has an API key configured."""
        return self._auth.has_api_key

    def _check_nsfw_access(self, purity: list[Purity]) -> None:
        if Purity.NSFW in purity and not self._auth.has_api_key:
            raise AuthenticationError(
                "NSFW content requires an API key. "
                "Please provide your API key when creating the AsyncXanax client."
            )

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        attempt: int = 0,
    ) -> httpx.Response:
        headers = self._auth.get_headers()
        response = await self._client.request(method, url, params=params, headers=headers)

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed. Please check your API key.")

        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {url}")

        if response.status_code == 429:
            if self._rate_limit.should_retry(response, attempt):
                delay = self._rate_limit.calculate_delay(attempt)
                await asyncio.sleep(delay)
                return await self._request(method, url, params, attempt + 1)
            self._rate_limit.handle_rate_limit(response)

        if response.status_code >= 400:
            raise APIError(
                message=f"API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        return response

    async def wallpaper(self, wallpaper_id: str) -> Wallpaper:
        """
        Get information about a specific wallpaper.

        Args:
            wallpaper_id: The wallpaper ID (e.g., "94x38z").

        Returns:
            Wallpaper object with full details.

        Raises:
            AuthenticationError: If trying to access an NSFW wallpaper without an API key.
            NotFoundError: If the wallpaper does not exist.
        """
        url = self._build_url(f"w/{wallpaper_id}")
        response = await self._request("GET", url)

        data = response.json()
        return Wallpaper(**data["data"])

    async def search(self, params: SearchParams) -> SearchResult:
        """
        Search for wallpapers with the given parameters.

        Args:
            params: SearchParams object with search criteria.

        Returns:
            SearchResult containing list of wallpapers and pagination metadata.

        Raises:
            ValidationError: If parameters are invalid.
            AuthenticationError: If NSFW requested without an API key.
        """
        self._check_nsfw_access(params.purity)

        url = self._build_url("search")
        query_params = params.to_query_params()

        response = await self._request("GET", url, params=query_params)
        data = response.json()

        return SearchResult(**data)

    async def tag(self, tag_id: int) -> Tag:
        """
        Get information about a specific tag.

        Args:
            tag_id: The tag ID.

        Returns:
            Tag object with tag details.

        Raises:
            NotFoundError: If the tag does not exist.
        """
        url = self._build_url(f"tag/{tag_id}")
        response = await self._request("GET", url)

        data = response.json()
        return Tag(**data["data"])

    async def settings(self) -> UserSettings:
        """
        Get the authenticated user's settings.

        Requires an API key.

        Returns:
            UserSettings object with user preferences.

        Raises:
            AuthenticationError: If no API key is configured.
        """
        if not self._auth.has_api_key:
            raise AuthenticationError(
                "User settings require an API key. "
                "Please provide your API key when creating the AsyncXanax client."
            )

        url = self._build_url("settings")
        response = await self._request("GET", url)

        data = response.json()
        return UserSettings(**data["data"])

    async def collections(self, username: str | None = None) -> list[Collection]:
        """
        Get collections for the authenticated user or another user.

        If ``username`` is provided, returns public collections for that user.
        If ``username`` is omitted, returns the authenticated user's own collections
        (requires an API key).

        Args:
            username: Optional username to get public collections from.

        Returns:
            List of Collection objects.

        Raises:
            AuthenticationError: If trying to access own collections without an API key.
        """
        if username is None and not self._auth.has_api_key:
            raise AuthenticationError(
                "Accessing your own collections requires an API key. "
                "Please provide your API key when creating the AsyncXanax client."
            )

        if username:
            url = self._build_url(f"collections/{username}")
        else:
            url = self._build_url("collections")

        response = await self._request("GET", url)

        data = response.json()
        return [Collection(**item) for item in data["data"]]

    async def collection(self, username: str, collection_id: int) -> CollectionListing:
        """
        Get wallpapers in a specific collection.

        Args:
            username: Username who owns the collection.
            collection_id: Collection ID.

        Returns:
            CollectionListing with wallpapers and pagination metadata.

        Raises:
            AuthenticationError: If accessing a private collection without an API key.
            NotFoundError: If the collection does not exist.
        """
        url = self._build_url(f"collections/{username}/{collection_id}")
        response = await self._request("GET", url)

        data = response.json()
        return CollectionListing(**data)

    async def download(self, wallpaper: Wallpaper, path: Path | str | None = None) -> bytes:
        """
        Download the raw image bytes of a wallpaper.

        Args:
            wallpaper: The Wallpaper object to download.
            path: Optional file path to save the image. If provided, the bytes
                  are written to this path in addition to being returned.

        Returns:
            Raw image bytes.
        """
        response = await self._client.get(wallpaper.path, follow_redirects=True)
        response.raise_for_status()
        content = response.content
        if path is not None:
            Path(path).write_bytes(content)
        return content

    async def aiter_pages(self, params: SearchParams) -> AsyncIterator[SearchResult]:
        """
        Async-iterate over all pages of search results automatically.

        Each iteration yields a full :class:`~xanax.models.SearchResult` page.
        Pagination is handled transparently, including carrying forward any seed
        returned by the API for random-sorted results.

        Args:
            params: Starting SearchParams. The ``page`` field is managed automatically.

        Yields:
            SearchResult for each page, starting from the page in ``params``.

        Example:
            async for page in client.aiter_pages(SearchParams(query="anime")):
                for wallpaper in page.data:
                    print(wallpaper.id)
        """
        current_params = params
        while True:
            result = await self.search(current_params)
            yield result
            helper = PaginationHelper(result.meta)
            if not helper.has_next:
                break
            next_page = helper.next_page_number()
            if next_page is None:
                break
            update: dict[str, Any] = {"page": next_page}
            # Carry forward seed returned by the API (required for RANDOM sort pagination)
            if helper.seed is not None:
                update["seed"] = helper.seed
            current_params = SearchParams(**{**current_params.model_dump(mode="python"), **update})

    async def aiter_wallpapers(self, params: SearchParams) -> AsyncIterator[Wallpaper]:
        """
        Async-iterate over every wallpaper across all pages of search results.

        A convenience wrapper around :meth:`aiter_pages` that flattens pages into
        individual :class:`~xanax.models.Wallpaper` objects.

        Args:
            params: Starting SearchParams.

        Yields:
            Wallpaper objects across all pages.

        Example:
            async for wp in client.aiter_wallpapers(SearchParams(query="anime")):
                print(wp.path)
        """
        async for page in self.aiter_pages(params):
            for wallpaper in page.data:
                yield wallpaper

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncXanax":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        auth_status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"AsyncXanax({auth_status})"
