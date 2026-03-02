"""
xanax — a clean, type-safe Python client for multi-source media APIs.

Supports Wallhaven, Unsplash, and Reddit out of the box. Every source
shares the same ``download()`` contract and ``iter_media()`` iterator,
so you can swap or combine sources with minimal ceremony.

Supported sources:
    - Wallhaven (``Wallhaven`` / ``AsyncWallhaven``) — tagged wallpaper community
    - Unsplash (``Unsplash`` / ``AsyncUnsplash``) — royalty-free photography
    - Reddit (``Reddit`` / ``AsyncReddit``) — subreddit media feeds

Example usage — Wallhaven:
    from xanax import Wallhaven, SearchParams

    client = Wallhaven(api_key="your-api-key")
    for wallpaper in client.iter_media(SearchParams(query="nature")):
        client.download(wallpaper, path=f"{wallpaper.id}.jpg")

Example usage — Unsplash:
    from xanax import Unsplash
    from xanax.sources.unsplash import UnsplashSearchParams

    client = Unsplash(access_key="your-access-key")
    for photo in client.iter_media(UnsplashSearchParams(query="mountains")):
        client.download(photo, path=f"{photo.id}.jpg")

Example usage — Reddit:
    from xanax import Reddit
    from xanax.sources.reddit import RedditParams
    from xanax.sources.reddit.enums import RedditSort
    from xanax.enums import MediaType

    client = Reddit(
        client_id="...",
        client_secret="...",
        user_agent="python:xanax/0.3.0 (by u/yourname)",
    )
    params = RedditParams(subreddit="EarthPorn", sort=RedditSort.TOP, media_type=MediaType.IMAGE)
    for post in client.iter_media(params):
        client.download(post, path=f"{post.id}.jpg")
"""

from xanax.enums import (
    Category,
    Color,
    FileType,
    MediaType,
    Order,
    Purity,
    Ratio,
    Resolution,
    Seed,
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
from xanax.pagination import PaginationHelper
from xanax.sources import AsyncReddit, AsyncUnsplash, AsyncWallhaven, Reddit, Unsplash, Wallhaven
from xanax.sources.wallhaven.models import (
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
from xanax.sources.wallhaven.params import SearchParams

__version__ = "0.3.1"

# Backwards-compatible aliases — Xanax/AsyncXanax renamed to Wallhaven/AsyncWallhaven in v0.3.0.
Xanax = Wallhaven
AsyncXanax = AsyncWallhaven

__all__ = [
    # Wallhaven clients (primary)
    "Wallhaven",
    "AsyncWallhaven",
    # Unsplash clients
    "Unsplash",
    "AsyncUnsplash",
    # Reddit clients
    "Reddit",
    "AsyncReddit",
    # Errors
    "XanaxError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "APIError",
    # Shared enums
    "MediaType",
    # Wallhaven enums
    "Category",
    "Purity",
    "Sort",
    "Order",
    "TopRange",
    "Color",
    "Ratio",
    "Resolution",
    "FileType",
    "Seed",
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
    # Wallhaven search params
    "SearchParams",
    # Pagination
    "PaginationHelper",
    # Backwards-compat aliases
    "Xanax",
    "AsyncXanax",
]
