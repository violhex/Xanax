"""
Base protocols for all xanax media sources.

Every source client — Wallhaven, Unsplash, Reddit, etc. — satisfies
these protocols. This allows duck-typed multi-source code without
requiring inheritance.

Example:
    from xanax.sources._base import MediaSource

    def download_all(source: MediaSource, params: Any) -> list[bytes]:
        return [source.download(item) for item in source.iter_media(params)]
"""

from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MediaSource(Protocol):
    """
    Protocol satisfied by all synchronous media source clients.

    Any object implementing ``download`` and ``iter_media`` satisfies
    this protocol, enabling interchangeable multi-source code without
    coupling to a specific client class.
    """

    def download(self, media: Any, path: str | Path | None = None) -> bytes:
        """
        Download raw bytes for the given media item.

        Args:
            media: Source-specific media object.
            path: Optional path to write the file to disk.

        Returns:
            Raw bytes.
        """
        ...

    def iter_media(self, params: Any) -> Iterator[Any]:
        """
        Iterate over media items matching the given parameters.

        Args:
            params: Source-specific search/filter parameters.

        Yields:
            Source-specific media objects.
        """
        ...


@runtime_checkable
class AsyncMediaSource(Protocol):
    """
    Protocol satisfied by all asynchronous media source clients.

    The async counterpart to :class:`MediaSource`. Implement
    ``download`` and ``aiter_media`` to satisfy this protocol.
    """

    async def download(self, media: Any, path: str | Path | None = None) -> bytes:
        """
        Download raw bytes for the given media item.

        Args:
            media: Source-specific media object.
            path: Optional path to write the file to disk.

        Returns:
            Raw bytes.
        """
        ...

    async def aiter_media(self, params: Any) -> AsyncIterator[Any]:
        """
        Async-iterate over media items matching the given parameters.

        Args:
            params: Source-specific search/filter parameters.

        Yields:
            Source-specific media objects.
        """
        ...
