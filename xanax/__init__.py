"""
xanax - A clean, type-safe Python client for Wallhaven.cc API v1.

This library provides a simple and safe interface to interact with
the Wallhaven wallpaper API. All responses are parsed into typed
models, and invalid parameters are validated before making requests.

Example usage:
    from xanax import Xanax, SearchParams, Purity

    client = Xanax(api_key="your-api-key")

    params = SearchParams(
        query="+anime -sketch",
        purity=[Purity.SFW],
    )

    results = client.search(params)

    for wallpaper in results.data:
        print(wallpaper.resolution, wallpaper.path)
"""

from xanax.client import Xanax
from xanax.enums import (
    Category,
    Color,
    FileType,
    Order,
    Purity,
    Ratio,
    Sort,
    TopRange,
)
from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    XanaxError,
)
from xanax.models import (
    Collection,
    CollectionListing,
    PaginationMeta,
    SearchResult,
    Tag,
    Thumbnails,
    Uploader,
    UserSettings,
    Wallpaper,
)
from xanax.pagination import PaginationHelper
from xanax.search import SearchParams

__version__ = "0.1.0"

__all__ = [
    # Client
    "Xanax",
    # Errors
    "XanaxError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "APIError",
    # Enums
    "Category",
    "Purity",
    "Sort",
    "Order",
    "TopRange",
    "Color",
    "Ratio",
    "FileType",
    # Models
    "Wallpaper",
    "Tag",
    "Uploader",
    "Avatar",
    "Thumbnails",
    "SearchResult",
    "PaginationMeta",
    "UserSettings",
    "Collection",
    "CollectionListing",
    # Search
    "SearchParams",
    # Pagination
    "PaginationHelper",
]
