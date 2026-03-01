"""
Base protocols for xanax wallpaper sources.

Every source client — Wallhaven, Unsplash, Reddit, etc. — satisfies
these protocols. This allows duck-typed multi-source code without
requiring inheritance.

Example:
    from xanax.sources._base import WallpaperSource

    def download_all(source: WallpaperSource, params: Any) -> list[bytes]:
        return [source.download(wp) for wp in source.iter_wallpapers(params)]
"""

from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class WallpaperSource(Protocol):
    """
    Protocol satisfied by all synchronous wallpaper source clients.

    Any object implementing ``download`` and ``iter_wallpapers`` satisfies
    this protocol, enabling interchangeable multi-source code without
    coupling to a specific client class.
    """

    def download(self, wallpaper: Any, path: str | Path | None = None) -> bytes:
        """
        Download raw image bytes for the given wallpaper.

        Args:
            wallpaper: Source-specific wallpaper object.
            path: Optional path to write the image to disk.

        Returns:
            Raw image bytes.
        """
        ...

    def iter_wallpapers(self, params: Any) -> Iterator[Any]:
        """
        Iterate over wallpapers matching the given parameters.

        Args:
            params: Source-specific search/filter parameters.

        Yields:
            Source-specific wallpaper objects.
        """
        ...


@runtime_checkable
class AsyncWallpaperSource(Protocol):
    """
    Protocol satisfied by all asynchronous wallpaper source clients.

    The async counterpart to :class:`WallpaperSource`. Implement
    ``download`` and ``aiter_wallpapers`` to satisfy this protocol.
    """

    async def download(self, wallpaper: Any, path: str | Path | None = None) -> bytes:
        """
        Download raw image bytes for the given wallpaper.

        Args:
            wallpaper: Source-specific wallpaper object.
            path: Optional path to write the image to disk.

        Returns:
            Raw image bytes.
        """
        ...

    async def aiter_wallpapers(self, params: Any) -> AsyncIterator[Any]:
        """
        Async-iterate over wallpapers matching the given parameters.

        Args:
            params: Source-specific search/filter parameters.

        Yields:
            Source-specific wallpaper objects.
        """
        ...
