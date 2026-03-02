"""
Authentication handler for the Wallhaven API.

Resolves the API key from the constructor argument or the
``WALLHAVEN_API_KEY`` environment variable. The key is never logged
or exposed in any string representation.
"""

import os


class AuthHandler:
    """
    Manages authentication for Wallhaven API requests.

    Uses header-based authentication via the ``X-API-Key`` header.

    Key resolution order:

    1. Explicit ``api_key`` argument
    2. ``WALLHAVEN_API_KEY`` environment variable

    Args:
        api_key: Wallhaven API key. Falls back to the ``WALLHAVEN_API_KEY``
                 environment variable if not provided.
    """

    API_HEADER = "X-API-Key"

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = os.environ.get("WALLHAVEN_API_KEY")
        self._api_key = api_key

    @property
    def has_api_key(self) -> bool:
        """Return True if an API key is configured."""
        return self._api_key is not None and self._api_key != ""

    @property
    def api_key(self) -> str | None:
        """Return the raw API key (internal use only)."""
        return self._api_key

    def get_headers(self) -> dict[str, str]:
        """
        Return headers for an authenticated request.

        Returns:
            Dict containing ``X-API-Key`` if a key is configured, otherwise empty.
        """
        if self.has_api_key and self._api_key:
            return {self.API_HEADER: self._api_key}
        return {}

    def check_nsfw_access(self, purity_includes_nsfw: bool) -> bool:
        """Return True if NSFW content can be accessed with current credentials."""
        if purity_includes_nsfw:
            return self.has_api_key
        return True

    def __repr__(self) -> str:
        has_key = "yes" if self.has_api_key else "no"
        return f"AuthHandler(api_key_present={has_key})"

    def __str__(self) -> str:
        return self.__repr__()
