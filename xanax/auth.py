"""
Authentication handling for Wallhaven API.

Handles API key storage and header management.
The API key is never logged or exposed in any output.
"""

from typing import Any


class AuthHandler:
    """
    Manages authentication for Wallhaven API requests.

    Supports two authentication methods:
    1. Header-based (preferred) - uses X-API-Key header
    2. Query parameter (fallback) - uses apikey query parameter

    The API key is stored securely and never exposed in __repr__
    or any string representations.
    """

    API_HEADER = "X-API-Key"
    API_QUERY_PARAM = "apikey"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key

    @property
    def has_api_key(self) -> bool:
        """Check if an API key is configured."""
        return self._api_key is not None and self._api_key != ""

    @property
    def api_key(self) -> str | None:
        """Get the API key (for internal use only)."""
        return self._api_key

    def get_headers(self) -> dict[str, str]:
        """
        Get headers for authenticated request.

        Returns:
            Dictionary containing the X-API-Key header if key is set.
        """
        if self.has_api_key and self._api_key:
            return {self.API_HEADER: self._api_key}
        return {}

    def get_query_params(self) -> dict[str, Any]:
        """
        Get query parameters for authenticated request.

        This is the fallback method if header-based auth is not used.

        Returns:
            Dictionary containing the apikey parameter if key is set.
        """
        if self.has_api_key:
            return {self.API_QUERY_PARAM: self._api_key}
        return {}

    def check_nsfw_access(self, purity_includes_nsfw: bool) -> bool:
        """
        Check if NSFW content can be accessed.

        Args:
            purity_includes_nsfw: Whether the request includes NSFW purity.

        Returns:
            True if NSFW can be accessed, False otherwise.
        """
        if purity_includes_nsfw:
            return self.has_api_key
        return True

    def __repr__(self) -> str:
        """Secure repr that never exposes the API key."""
        has_key = "yes" if self.has_api_key else "no"
        return f"AuthHandler(api_key_present={has_key})"

    def __str__(self) -> str:
        """Secure string representation."""
        return self.__repr__()
