"""
Unsplash wallpaper source for xanax.

Provides type-safe sync and async clients for the Unsplash API v1.
Both clients satisfy the :class:`~xanax.sources._base.WallpaperSource`
protocol, so they can be used interchangeably with other xanax sources.

Example (sync):
    from xanax.sources.unsplash import Unsplash, UnsplashSearchParams

    unsplash = Unsplash(access_key="your-access-key")
    result = unsplash.search(UnsplashSearchParams(query="mountains"))
    data = unsplash.download(result.results[0])

Example (async):
    from xanax.sources.unsplash import AsyncUnsplash, UnsplashSearchParams

    async with AsyncUnsplash(access_key="your-access-key") as unsplash:
        result = await unsplash.search(UnsplashSearchParams(query="mountains"))
        async for photo in unsplash.aiter_wallpapers(UnsplashSearchParams(query="forest")):
            data = await unsplash.download(photo)
"""

from xanax.sources.unsplash.async_client import AsyncUnsplash
from xanax.sources.unsplash.client import Unsplash
from xanax.sources.unsplash.enums import (
    UnsplashColor,
    UnsplashContentFilter,
    UnsplashOrderBy,
    UnsplashOrientation,
)
from xanax.sources.unsplash.models import (
    UnsplashExif,
    UnsplashLocation,
    UnsplashPhoto,
    UnsplashPhotoLinks,
    UnsplashPhotoUrls,
    UnsplashPosition,
    UnsplashSearchResult,
    UnsplashTag,
    UnsplashUser,
    UnsplashUserLinks,
    UnsplashUserProfileImage,
)
from xanax.sources.unsplash.params import UnsplashRandomParams, UnsplashSearchParams

__all__ = [
    # Clients
    "Unsplash",
    "AsyncUnsplash",
    # Enums
    "UnsplashOrientation",
    "UnsplashColor",
    "UnsplashOrderBy",
    "UnsplashContentFilter",
    # Models
    "UnsplashPhoto",
    "UnsplashPhotoUrls",
    "UnsplashPhotoLinks",
    "UnsplashUser",
    "UnsplashUserProfileImage",
    "UnsplashUserLinks",
    "UnsplashExif",
    "UnsplashLocation",
    "UnsplashPosition",
    "UnsplashTag",
    "UnsplashSearchResult",
    # Params
    "UnsplashSearchParams",
    "UnsplashRandomParams",
]
