"""
xanax - A clean, type-safe Python client for wallpaper APIs.

This library provides a simple and safe interface to interact with
wallpaper APIs. All responses are parsed into typed models, and invalid
parameters are validated before making requests.

Both synchronous and asynchronous clients are available for all sources.

Supported sources:
    - Wallhaven (``Xanax`` / ``AsyncXanax``) — tagged wallpaper community
    - Unsplash (``Unsplash`` / ``AsyncUnsplash``) — royalty-free photography

Example usage — Wallhaven (sync):
    from xanax import Xanax, SearchParams, Purity

    client = Xanax(api_key="your-api-key")

    params = SearchParams(
        query="+anime -sketch",
        purity=[Purity.SFW],
    )

    results = client.search(params)

    for wallpaper in results.data:
        print(wallpaper.resolution, wallpaper.path)

Example usage — Wallhaven (async):
    from xanax import AsyncXanax, SearchParams, Purity

    async with AsyncXanax(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="anime"))
        async for wp in client.aiter_wallpapers(SearchParams(query="nature")):
            print(wp.path)

Example usage — Unsplash (sync):
    from xanax.sources import Unsplash
    from xanax.sources.unsplash import UnsplashSearchParams

    unsplash = Unsplash(access_key="your-access-key")
    result = unsplash.search(UnsplashSearchParams(query="mountains"))
    data = unsplash.download(result.results[0])

Example usage — Unsplash (async):
    from xanax.sources import AsyncUnsplash
    from xanax.sources.unsplash import UnsplashSearchParams

    async with AsyncUnsplash(access_key="your-access-key") as unsplash:
        result = await unsplash.search(UnsplashSearchParams(query="mountains"))
        async for photo in unsplash.aiter_wallpapers(UnsplashSearchParams(query="forest")):
            data = await unsplash.download(photo)
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
from xanax.sources import AsyncUnsplash, Unsplash

__version__ = "0.2.1"

__all__ = [
    # Wallhaven clients
    "Xanax",
    "AsyncXanax",
    # Unsplash clients
    "Unsplash",
    "AsyncUnsplash",
    # Errors
    "XanaxError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "APIError",
    # Wallhaven enums
    "Category",
    "Purity",
    "Sort",
    "Order",
    "TopRange",
    "Color",
    "Ratio",
    "FileType",
    # Wallhaven models
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
    # Wallhaven search
    "SearchParams",
    # Pagination
    "PaginationHelper",
]
