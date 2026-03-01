"""
Tests for the WallpaperSource protocol and sources package.
"""

from xanax.sources import AsyncUnsplash, Unsplash
from xanax.sources._base import AsyncWallpaperSource, WallpaperSource


class TestWallpaperSourceProtocol:
    def test_unsplash_satisfies_wallpaper_source(self) -> None:
        """Unsplash must satisfy the WallpaperSource protocol."""
        client = Unsplash(access_key="test-key")
        assert isinstance(client, WallpaperSource)

    def test_async_unsplash_satisfies_async_wallpaper_source(self) -> None:
        """AsyncUnsplash must satisfy the AsyncWallpaperSource protocol."""
        client = AsyncUnsplash(access_key="test-key")
        assert isinstance(client, AsyncWallpaperSource)

    def test_arbitrary_object_does_not_satisfy_protocol(self) -> None:
        class NotASource:
            pass

        assert not isinstance(NotASource(), WallpaperSource)

    def test_partial_implementation_does_not_satisfy_protocol(self) -> None:
        class PartialSource:
            def download(self, wallpaper, path=None):  # type: ignore[no-untyped-def]
                return b""

            # missing iter_wallpapers

        assert not isinstance(PartialSource(), WallpaperSource)


class TestSourcesPackageExports:
    def test_unsplash_importable_from_sources(self) -> None:
        assert Unsplash is not None

    def test_async_unsplash_importable_from_sources(self) -> None:
        assert AsyncUnsplash is not None
