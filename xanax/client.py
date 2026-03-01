"""
Main Xanax client for interacting with Wallhaven API.

This is the primary interface for the library. All API interactions
go through this client class.
"""

from collections.abc import Iterator
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


class Xanax:
    """
    Main client for Wallhaven API v1.

    This client provides methods to interact with all Wallhaven API endpoints.
    The API key can be passed directly or read from the ``WALLHAVEN_API_KEY``
    environment variable.

    Example:
        client = Xanax(api_key="your-api-key")

        params = SearchParams(query="anime", purity=[Purity.SFW])
        results = client.search(params)

        for wallpaper in results.data:
            print(wallpaper.resolution, wallpaper.path)

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
        self._client = httpx.Client(
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
                "Please provide your API key when creating the Xanax client."
            )

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        attempt: int = 0,
    ) -> httpx.Response:
        headers = self._auth.get_headers()
        response = self._client.request(method, url, params=params, headers=headers)

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed. Please check your API key.")

        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {url}")

        if response.status_code == 429:
            if self._rate_limit.should_retry(response, attempt):
                self._rate_limit.wait_before_retry(attempt)
                return self._request(method, url, params, attempt + 1)
            self._rate_limit.handle_rate_limit(response)

        if response.status_code >= 400:
            raise APIError(
                message=f"API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        return response

    def wallpaper(self, wallpaper_id: str) -> Wallpaper:
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
        response = self._request("GET", url)

        data = response.json()
        return Wallpaper(**data["data"])

    def search(self, params: SearchParams) -> SearchResult:
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

        response = self._request("GET", url, params=query_params)
        data = response.json()

        return SearchResult(**data)

    def tag(self, tag_id: int) -> Tag:
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
        response = self._request("GET", url)

        data = response.json()
        return Tag(**data["data"])

    def settings(self) -> UserSettings:
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
                "Please provide your API key when creating the Xanax client."
            )

        url = self._build_url("settings")
        response = self._request("GET", url)

        data = response.json()
        return UserSettings(**data["data"])

    def collections(self, username: str | None = None) -> list[Collection]:
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
                "Please provide your API key when creating the Xanax client."
            )

        if username:
            url = self._build_url(f"collections/{username}")
        else:
            url = self._build_url("collections")

        response = self._request("GET", url)

        data = response.json()
        return [Collection(**item) for item in data["data"]]

    def collection(self, username: str, collection_id: int) -> CollectionListing:
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
        response = self._request("GET", url)

        data = response.json()
        return CollectionListing(**data)

    def download(self, wallpaper: Wallpaper, path: Path | str | None = None) -> bytes:
        """
        Download the raw image bytes of a wallpaper.

        Args:
            wallpaper: The Wallpaper object to download.
            path: Optional file path to save the image. If provided, the bytes
                  are written to this path in addition to being returned.

        Returns:
            Raw image bytes.
        """
        response = self._client.get(wallpaper.path, follow_redirects=True)
        response.raise_for_status()
        content = response.content
        if path is not None:
            Path(path).write_bytes(content)
        return content

    def iter_pages(self, params: SearchParams) -> Iterator[SearchResult]:
        """
        Iterate over all pages of search results automatically.

        Each iteration yields a full :class:`~xanax.models.SearchResult` page.
        Pagination is handled transparently, including carrying forward any seed
        returned by the API for random-sorted results.

        Args:
            params: Starting SearchParams. The ``page`` field is managed automatically.

        Yields:
            SearchResult for each page, starting from the page in ``params``.

        Example:
            for page in client.iter_pages(SearchParams(query="anime")):
                for wallpaper in page.data:
                    print(wallpaper.id)
        """
        current_params = params
        while True:
            result = self.search(current_params)
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

    def iter_wallpapers(self, params: SearchParams) -> Iterator[Wallpaper]:
        """
        Iterate over every wallpaper across all pages of search results.

        A convenience wrapper around :meth:`iter_pages` that flattens pages into
        individual :class:`~xanax.models.Wallpaper` objects.

        Args:
            params: Starting SearchParams.

        Yields:
            Wallpaper objects across all pages.

        Example:
            for wp in client.iter_wallpapers(SearchParams(query="anime")):
                print(wp.path)
        """
        for page in self.iter_pages(params):
            yield from page.data

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "Xanax":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        auth_status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"Xanax({auth_status})"
