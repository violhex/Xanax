"""
Tests for the MediaSource protocol and sources package.
"""

from xanax.sources import AsyncUnsplash, Unsplash
from xanax.sources._base import AsyncMediaSource, MediaSource


class TestMediaSourceProtocol:
    def test_unsplash_satisfies_media_source(self) -> None:
        """Unsplash must satisfy the MediaSource protocol."""
        client = Unsplash(access_key="test-key")
        assert isinstance(client, MediaSource)

    def test_async_unsplash_satisfies_async_media_source(self) -> None:
        """AsyncUnsplash must satisfy the AsyncMediaSource protocol."""
        client = AsyncUnsplash(access_key="test-key")
        assert isinstance(client, AsyncMediaSource)

    def test_arbitrary_object_does_not_satisfy_protocol(self) -> None:
        class NotASource:
            pass

        assert not isinstance(NotASource(), MediaSource)

    def test_partial_implementation_does_not_satisfy_protocol(self) -> None:
        class PartialSource:
            def download(self, media, path=None):  # type: ignore[no-untyped-def]
                return b""

            # missing iter_media

        assert not isinstance(PartialSource(), MediaSource)


class TestSourcesPackageExports:
    def test_unsplash_importable_from_sources(self) -> None:
        assert Unsplash is not None

    def test_async_unsplash_importable_from_sources(self) -> None:
        assert AsyncUnsplash is not None
