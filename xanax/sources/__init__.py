"""
Multi-source media support for xanax.

Each source satisfies the :class:`~xanax.sources._base.MediaSource` protocol —
``download`` and ``iter_media`` work the same way regardless of source.

Available sources:
    - :class:`~xanax.sources.wallhaven.Wallhaven` — tagged wallpaper community
    - :class:`~xanax.sources.wallhaven.AsyncWallhaven` — async variant
    - :class:`~xanax.sources.unsplash.Unsplash` — royalty-free photography
    - :class:`~xanax.sources.unsplash.AsyncUnsplash` — async variant
    - :class:`~xanax.sources.reddit.Reddit` — subreddit media feeds
    - :class:`~xanax.sources.reddit.AsyncReddit` — async variant
"""

from xanax.sources.reddit import AsyncReddit, Reddit
from xanax.sources.unsplash import AsyncUnsplash, Unsplash
from xanax.sources.wallhaven import AsyncWallhaven, Wallhaven

__all__ = [
    "Wallhaven",
    "AsyncWallhaven",
    "Unsplash",
    "AsyncUnsplash",
    "Reddit",
    "AsyncReddit",
]
