"""
xanax - A clean, type-safe Python client for Wallhaven.cc API v1.

This library provides a simple and safe interface to interact with
the Wallhaven wallpaper API. All responses are parsed into typed
models, and invalid parameters are validated before making requests.

Both synchronous and asynchronous clients are available.

Example usage (sync):
    from xanax import Xanax, SearchParams, Purity

    client = Xanax(api_key="your-api-key")

    params = SearchParams(
        query="+anime -sketch",
        purity=[Purity.SFW],
    )

    results = client.search(params)

    for wallpaper in results.data:
        print(wallpaper.resolution, wallpaper.path)

Example usage (async):
    from xanax import AsyncXanax, SearchParams, Purity

    async with AsyncXanax(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="anime"))
        async for wp in client.aiter_wallpapers(SearchParams(query="nature")):
            print(wp.path)
"""

from xanax.async_client import AsyncXanax
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
    Avatar,
    Collection,
    CollectionListing,
    PaginationMeta,
    QueryInfo,
    SearchResult,
    Tag,
    Thumbnails,
    Uploader,
    UserSettings,
    Wallpaper,
)
from xanax.pagination import PaginationHelper
from xanax.search import SearchParams

__version__ = "0.2.0"

__all__ = [
    # Clients
    "Xanax",
    "AsyncXanax",
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
    "QueryInfo",
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
