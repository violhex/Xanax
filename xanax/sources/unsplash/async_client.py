"""
Asynchronous Unsplash client.

Drop-in async counterpart to :class:`~xanax.sources.unsplash.client.Unsplash`.
All public methods are coroutines. Use as an async context manager for
automatic resource cleanup.

Unsplash requires attribution. The :meth:`~AsyncUnsplash.download` method
automatically triggers the required tracking endpoint before fetching
image bytes, satisfying the Unsplash API Terms of Service.
"""

import asyncio
import os
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
from xanax.sources.unsplash.models import UnsplashPhoto, UnsplashSearchResult
from xanax.sources.unsplash.params import UnsplashRandomParams, UnsplashSearchParams


class AsyncUnsplash:
    """
    Asynchronous client for the Unsplash API.

    Drop-in async counterpart to :class:`~xanax.sources.unsplash.client.Unsplash`.
    All public methods are coroutines. Use as an async context manager for
    automatic resource cleanup.

    The access key can be passed directly or read from the ``UNSPLASH_ACCESS_KEY``
    environment variable.

    Example:
        async with AsyncUnsplash(access_key="your-access-key") as unsplash:
            result = await unsplash.search(UnsplashSearchParams(query="mountains"))

            async for photo in unsplash.aiter_media(UnsplashSearchParams(query="forest")):
                data = await unsplash.download(photo)

    Args:
        access_key: Unsplash API access key. Falls back to the
                    ``UNSPLASH_ACCESS_KEY`` environment variable.
        timeout: Request timeout in seconds. Default is 30.
        max_retries: Maximum retries on rate limiting (429).
                     Default is 0 (fail-fast). Set to 3 for exponential backoff.

    Raises:
        AuthenticationError: If no access key is provided or discoverable.
    """

    BASE_URL = "https://api.unsplash.com"

    def __init__(
        self,
        access_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> None:
        resolved_key = access_key or os.environ.get("UNSPLASH_ACCESS_KEY")
        if not resolved_key:
            raise AuthenticationError(
                "Unsplash access key is required. "
                "Pass access_key= or set the UNSPLASH_ACCESS_KEY environment variable."
            )
        self._access_key = resolved_key
        self._rate_limit = RateLimitHandler(max_retries=max_retries)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        )

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Client-ID {self._access_key}"}

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        attempt: int = 0,
    ) -> httpx.Response:
        response = await self._client.request(
            method, url, params=params, headers=self._auth_headers()
        )

        if response.status_code == 401:
            raise AuthenticationError("Unsplash authentication failed. Check your access key.")

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
                message=f"Unsplash API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        return response

    async def search(self, params: UnsplashSearchParams) -> UnsplashSearchResult:
        """
        Search for photos matching the given parameters.

        Args:
            params: :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`
                    with query and optional filters.

        Returns:
            :class:`~xanax.sources.unsplash.models.UnsplashSearchResult` with
            ``total``, ``total_pages``, and ``results``.

        Raises:
            AuthenticationError: If the access key is invalid.
        """
        url = self._build_url("search/photos")
        response = await self._request("GET", url, params=params.to_query_params())
        return UnsplashSearchResult(**response.json())

    async def photo(self, photo_id: str) -> UnsplashPhoto:
        """
        Retrieve a full photo object by ID.

        Unlike search results, the returned photo includes ``exif``,
        ``location``, ``tags``, ``downloads``, and ``public_domain``.

        Args:
            photo_id: Unsplash photo ID (e.g. ``"Dwu85P9SOIk"``).

        Returns:
            Full :class:`~xanax.sources.unsplash.models.UnsplashPhoto`.

        Raises:
            NotFoundError: If the photo does not exist.
        """
        url = self._build_url(f"photos/{photo_id}")
        response = await self._request("GET", url)
        return UnsplashPhoto(**response.json())

    async def random(self, params: UnsplashRandomParams | None = None) -> UnsplashPhoto:
        """
        Retrieve a single random photo.

        Without parameters, a completely random photo is returned. Parameters
        narrow the eligible pool (by collection, topic, user, query, or orientation).

        Args:
            params: Optional :class:`~xanax.sources.unsplash.params.UnsplashRandomParams`
                    to constrain the random selection.

        Returns:
            A :class:`~xanax.sources.unsplash.models.UnsplashPhoto`.

        Raises:
            AuthenticationError: If the access key is invalid.
        """
        url = self._build_url("photos/random")
        query_params = params.to_query_params() if params is not None else {}
        response = await self._request("GET", url, params=query_params)
        return UnsplashPhoto(**response.json())

    async def download(self, photo: UnsplashPhoto, path: Path | str | None = None) -> bytes:
        """
        Download the raw image bytes for a photo.

        Unsplash's API Terms of Service require triggering a tracking request
        before downloading. This method performs both steps automatically:

        1. GET ``photo.links.download_location`` (triggers attribution tracking).
        2. GET the CDN URL returned from step 1 (fetches actual image bytes).

        Args:
            photo: The :class:`~xanax.sources.unsplash.models.UnsplashPhoto`
                   to download.
            path: Optional file path to save the image. If provided, the bytes
                  are written to this path in addition to being returned.

        Returns:
            Raw image bytes.

        Raises:
            httpx.HTTPStatusError: If either request fails.
        """
        # Step 1: trigger download tracking (required by Unsplash ToS)
        tracking_response = await self._client.get(
            photo.links.download_location,
            headers=self._auth_headers(),
            follow_redirects=True,
        )
        tracking_response.raise_for_status()
        cdn_url: str = tracking_response.json()["url"]

        # Step 2: fetch image bytes from CDN
        image_response = await self._client.get(cdn_url, follow_redirects=True)
        image_response.raise_for_status()
        content = image_response.content

        if path is not None:
            Path(path).write_bytes(content)

        return content

    async def aiter_pages(
        self, params: UnsplashSearchParams
    ) -> AsyncIterator[UnsplashSearchResult]:
        """
        Async-iterate over all pages of search results automatically.

        Each iteration yields a full :class:`~xanax.sources.unsplash.models.UnsplashSearchResult`
        page. Pagination is handled transparently.

        Args:
            params: Starting :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`.
                    The ``page`` field is managed automatically.

        Yields:
            :class:`~xanax.sources.unsplash.models.UnsplashSearchResult` for each page.

        Example:
            async for page in unsplash.aiter_pages(UnsplashSearchParams(query="nature")):
                for photo in page.results:
                    print(photo.id)
        """
        current_params = params
        while True:
            result = await self.search(current_params)
            yield result
            if current_params.page >= result.total_pages:
                break
            current_params = current_params.with_page(current_params.page + 1)

    async def aiter_media(self, params: UnsplashSearchParams) -> AsyncIterator[UnsplashPhoto]:
        """
        Async-iterate over every photo across all pages of search results.

        A convenience wrapper around :meth:`aiter_pages` that flattens pages
        into individual :class:`~xanax.sources.unsplash.models.UnsplashPhoto` objects.

        Args:
            params: Starting :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`.

        Yields:
            :class:`~xanax.sources.unsplash.models.UnsplashPhoto` objects across all pages.

        Example:
            async for photo in unsplash.aiter_media(UnsplashSearchParams(query="forest")):
                data = await unsplash.download(photo)
        """
        async for page in self.aiter_pages(params):
            for photo in page.results:
                yield photo

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncUnsplash":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return "AsyncUnsplash(authenticated)"
