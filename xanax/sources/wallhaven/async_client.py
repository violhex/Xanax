"""
Asynchronous Wallhaven client.

Drop-in async counterpart to :class:`~xanax.sources.wallhaven.client.Wallhaven`.
All public methods are coroutines. Use as an async context manager for
automatic resource cleanup.
"""

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx

from xanax._internal.rate_limit import RateLimitHandler
from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
)
from xanax.pagination import PaginationHelper
from xanax.sources.wallhaven.auth import AuthHandler
from xanax.sources.wallhaven.enums import Purity
from xanax.sources.wallhaven.models import (
    Collection,
    CollectionListing,
    SearchResult,
    Tag,
    UserSettings,
    Wallpaper,
)
from xanax.sources.wallhaven.params import SearchParams


class AsyncWallhaven:
    """
    Asynchronous client for the Wallhaven API v1.

    Satisfies :class:`~xanax.sources._base.AsyncMediaSource`: ``download``
    and ``aiter_media`` work identically across all xanax async sources.

    Example:
        async with AsyncWallhaven(api_key="your-api-key") as client:
            results = await client.search(SearchParams(query="anime"))

            async for wallpaper in client.aiter_media(SearchParams(query="nature")):
                print(wallpaper.path)

    Args:
        api_key: Wallhaven API key. Falls back to ``WALLHAVEN_API_KEY`` env var.
        timeout: Request timeout in seconds. Default is 30.
        max_retries: Maximum retries on rate limiting (429). Default is 0
                     (fail-fast). Set to 3 for exponential backoff.
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
        self._client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    @property
    def is_authenticated(self) -> bool:
        """Return True if the client has an API key configured."""
        return self._auth.has_api_key

    def _check_nsfw_access(self, purity: list[Purity]) -> None:
        if Purity.NSFW in purity and not self._auth.has_api_key:
            raise AuthenticationError(
                "NSFW content requires an API key. "
                "Please provide your API key when creating the AsyncWallhaven client."
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
        Get full metadata for a specific wallpaper.

        Args:
            wallpaper_id: The wallpaper ID (e.g., ``"94x38z"``).

        Returns:
            :class:`~xanax.sources.wallhaven.models.Wallpaper` with full details.

        Raises:
            NotFoundError: If the wallpaper does not exist.
        """
        url = self._build_url(f"w/{wallpaper_id}")
        response = await self._request("GET", url)
        return Wallpaper(**response.json()["data"])

    async def search(self, params: SearchParams) -> SearchResult:
        """
        Search for wallpapers.

        Args:
            params: :class:`~xanax.sources.wallhaven.params.SearchParams` with search criteria.

        Returns:
            :class:`~xanax.sources.wallhaven.models.SearchResult`.

        Raises:
            AuthenticationError: If NSFW is requested without an API key.
        """
        self._check_nsfw_access(params.purity)
        url = self._build_url("search")
        response = await self._request("GET", url, params=params.to_query_params())
        return SearchResult(**response.json())

    async def tag(self, tag_id: int) -> Tag:
        """
        Get information about a specific tag.

        Args:
            tag_id: The tag ID.

        Returns:
            :class:`~xanax.sources.wallhaven.models.Tag`.

        Raises:
            NotFoundError: If the tag does not exist.
        """
        url = self._build_url(f"tag/{tag_id}")
        response = await self._request("GET", url)
        return Tag(**response.json()["data"])

    async def settings(self) -> UserSettings:
        """
        Get the authenticated user's settings. Requires an API key.

        Returns:
            :class:`~xanax.sources.wallhaven.models.UserSettings`.

        Raises:
            AuthenticationError: If no API key is configured.
        """
        if not self._auth.has_api_key:
            raise AuthenticationError(
                "User settings require an API key. "
                "Please provide your API key when creating the AsyncWallhaven client."
            )
        url = self._build_url("settings")
        response = await self._request("GET", url)
        return UserSettings(**response.json()["data"])

    async def collections(self, username: str | None = None) -> list[Collection]:
        """
        Get collections for the authenticated user or a given username.

        Args:
            username: Optional username. If omitted, returns the authenticated
                      user's own collections (requires an API key).

        Returns:
            List of :class:`~xanax.sources.wallhaven.models.Collection`.

        Raises:
            AuthenticationError: If accessing own collections without an API key.
        """
        if username is None and not self._auth.has_api_key:
            raise AuthenticationError(
                "Accessing your own collections requires an API key. "
                "Please provide your API key when creating the AsyncWallhaven client."
            )
        url = (
            self._build_url(f"collections/{username}")
            if username
            else self._build_url("collections")
        )
        response = await self._request("GET", url)
        return [Collection(**item) for item in response.json()["data"]]

    async def collection(self, username: str, collection_id: int) -> CollectionListing:
        """
        Get wallpapers in a specific collection.

        Args:
            username: Username who owns the collection.
            collection_id: Collection ID.

        Returns:
            :class:`~xanax.sources.wallhaven.models.CollectionListing`.

        Raises:
            NotFoundError: If the collection does not exist.
        """
        url = self._build_url(f"collections/{username}/{collection_id}")
        response = await self._request("GET", url)
        return CollectionListing(**response.json())

    async def download(self, wallpaper: Wallpaper, path: Path | str | None = None) -> bytes:
        """
        Download the full-resolution image bytes for a wallpaper.

        Args:
            wallpaper: The :class:`~xanax.sources.wallhaven.models.Wallpaper` to download.
            path: Optional path to write the image to disk. Bytes are also returned.

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
        Async-iterate over all pages of search results.

        Args:
            params: Starting :class:`~xanax.sources.wallhaven.params.SearchParams`.

        Yields:
            :class:`~xanax.sources.wallhaven.models.SearchResult` per page.
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
            if helper.seed is not None:
                update["seed"] = helper.seed
            current_params = SearchParams(**{**current_params.model_dump(mode="python"), **update})

    async def aiter_media(self, params: SearchParams) -> AsyncIterator[Wallpaper]:
        """
        Async-iterate over every wallpaper across all pages.

        A convenience wrapper around :meth:`aiter_pages` that flattens pages
        into individual :class:`~xanax.sources.wallhaven.models.Wallpaper` objects.

        Args:
            params: Starting :class:`~xanax.sources.wallhaven.params.SearchParams`.

        Yields:
            :class:`~xanax.sources.wallhaven.models.Wallpaper` objects.
        """
        async for page in self.aiter_pages(params):
            for wallpaper in page.data:
                yield wallpaper

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncWallhaven":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        auth_status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"AsyncWallhaven({auth_status})"
