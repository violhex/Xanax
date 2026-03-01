"""
Multi-source wallpaper support for xanax.

This package provides clients for additional wallpaper sources beyond Wallhaven.
Each source satisfies the :class:`~xanax.sources._base.WallpaperSource` protocol,
meaning download and iteration work the same way regardless of source.

Available sources:
    - :class:`~xanax.sources.unsplash.Unsplash` — royalty-free photography
    - :class:`~xanax.sources.unsplash.AsyncUnsplash` — async variant

Example:
    from xanax.sources import Unsplash, AsyncUnsplash
    from xanax.sources.unsplash import UnsplashSearchParams
"""

from xanax.sources.unsplash import AsyncUnsplash, Unsplash

__all__ = [
    "Unsplash",
    "AsyncUnsplash",
]
