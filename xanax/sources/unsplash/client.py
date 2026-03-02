"""
Synchronous Unsplash client.

Provides a clean, type-safe interface to the Unsplash API v1.
All responses are parsed into typed models and the download contract
matches the :class:`~xanax.sources._base.MediaSource` protocol.

Unsplash requires attribution. The :meth:`~Unsplash.download` method
automatically triggers the required tracking endpoint before fetching
image bytes, satisfying the Unsplash API Terms of Service.
"""

import os
from collections.abc import Iterator
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


class Unsplash:
    """
    Synchronous client for the Unsplash API.

    Authenticates via an access key (``Authorization: Client-ID <key>``).
    The key can be passed directly or read from the ``UNSPLASH_ACCESS_KEY``
    environment variable.

    Satisfies :class:`~xanax.sources._base.MediaSource`: ``download``
    and ``iter_media`` work identically to the Wallhaven client, making
    it straightforward to write source-agnostic code.

    Example:
        .. code-block:: python

            unsplash = Unsplash(access_key="your-access-key")

            result = unsplash.search(UnsplashSearchParams(query="mountains"))
            for photo in result.results:
                print(photo.id, photo.resolution)

            photo = unsplash.random()
            data = unsplash.download(photo)

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
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
        )

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Client-ID {self._access_key}"}

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        attempt: int = 0,
    ) -> httpx.Response:
        response = self._client.request(method, url, params=params, headers=self._auth_headers())

        if response.status_code == 401:
            raise AuthenticationError("Unsplash authentication failed. Check your access key.")

        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {url}")

        if response.status_code == 429:
            if self._rate_limit.should_retry(response, attempt):
                self._rate_limit.wait_before_retry(attempt)
                return self._request(method, url, params, attempt + 1)
            self._rate_limit.handle_rate_limit(response)

        if response.status_code >= 400:
            raise APIError(
                message=f"Unsplash API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        return response

    def search(self, params: UnsplashSearchParams) -> UnsplashSearchResult:
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
        response = self._request("GET", url, params=params.to_query_params())
        return UnsplashSearchResult(**response.json())

    def photo(self, photo_id: str) -> UnsplashPhoto:
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
        response = self._request("GET", url)
        return UnsplashPhoto(**response.json())

    def random(self, params: UnsplashRandomParams | None = None) -> UnsplashPhoto:
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
        response = self._request("GET", url, params=query_params)
        return UnsplashPhoto(**response.json())

    def download(self, photo: UnsplashPhoto, path: Path | str | None = None) -> bytes:
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
        tracking_response = self._client.get(
            photo.links.download_location,
            headers=self._auth_headers(),
            follow_redirects=True,
        )
        tracking_response.raise_for_status()
        cdn_url: str = tracking_response.json()["url"]

        # Step 2: fetch image bytes from CDN
        image_response = self._client.get(cdn_url, follow_redirects=True)
        image_response.raise_for_status()
        content = image_response.content

        if path is not None:
            Path(path).write_bytes(content)

        return content

    def iter_pages(self, params: UnsplashSearchParams) -> Iterator[UnsplashSearchResult]:
        """
        Iterate over all pages of search results automatically.

        Each iteration yields a full :class:`~xanax.sources.unsplash.models.UnsplashSearchResult`
        page. Pagination is handled transparently.

        Args:
            params: Starting :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`.
                    The ``page`` field is managed automatically.

        Yields:
            :class:`~xanax.sources.unsplash.models.UnsplashSearchResult` for each page.

        Example:
            for page in unsplash.iter_pages(UnsplashSearchParams(query="nature")):
                for photo in page.results:
                    print(photo.id)
        """
        current_params = params
        while True:
            result = self.search(current_params)
            yield result
            if current_params.page >= result.total_pages:
                break
            current_params = current_params.with_page(current_params.page + 1)

    def iter_media(self, params: UnsplashSearchParams) -> Iterator[UnsplashPhoto]:
        """
        Iterate over every photo across all pages of search results.

        A convenience wrapper around :meth:`iter_pages` that flattens pages
        into individual :class:`~xanax.sources.unsplash.models.UnsplashPhoto` objects.

        Args:
            params: Starting :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`.

        Yields:
            :class:`~xanax.sources.unsplash.models.UnsplashPhoto` objects across all pages.

        Example:
            for photo in unsplash.iter_media(UnsplashSearchParams(query="forest")):
                data = unsplash.download(photo)
        """
        for page in self.iter_pages(params):
            yield from page.results

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "Unsplash":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return "Unsplash(authenticated)"
