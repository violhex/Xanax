"""
Tests verifying Reddit clients satisfy the MediaSource and AsyncMediaSource protocols.
"""

from xanax.sources._base import AsyncMediaSource, MediaSource
from xanax.sources.reddit import AsyncReddit, Reddit


class TestRedditProtocolConformance:
    def test_reddit_satisfies_media_source(self) -> None:
        """Reddit must satisfy the synchronous MediaSource protocol."""
        client = Reddit(
            client_id="test-id",
            client_secret="test-secret",
            user_agent="python:test/1.0 (by u/user)",
        )
        assert isinstance(client, MediaSource)

    def test_async_reddit_satisfies_async_media_source(self) -> None:
        """AsyncReddit must satisfy the AsyncMediaSource protocol."""
        client = AsyncReddit(
            client_id="test-id",
            client_secret="test-secret",
            user_agent="python:test/1.0 (by u/user)",
        )
        assert isinstance(client, AsyncMediaSource)

    def test_arbitrary_object_does_not_satisfy_media_source(self) -> None:
        class NotASource:
            pass

        assert not isinstance(NotASource(), MediaSource)

    def test_arbitrary_object_does_not_satisfy_async_media_source(self) -> None:
        class NotASource:
            pass

        assert not isinstance(NotASource(), AsyncMediaSource)

    def test_partial_implementation_does_not_satisfy_media_source(self) -> None:
        """An object with only download() but not iter_media() does not satisfy."""

        class PartialSource:
            def download(self, media, path=None):  # type: ignore[no-untyped-def]
                return b""

            # missing iter_media

        assert not isinstance(PartialSource(), MediaSource)

    def test_partial_async_implementation_does_not_satisfy_async_media_source(self) -> None:
        """An object with only download() but not aiter_media() does not satisfy."""

        class PartialAsync:
            async def download(self, media, path=None):  # type: ignore[no-untyped-def]
                return b""

            # missing aiter_media

        assert not isinstance(PartialAsync(), AsyncMediaSource)


class TestRedditPackageExports:
    def test_reddit_importable_from_sources_reddit(self) -> None:
        assert Reddit is not None

    def test_async_reddit_importable_from_sources_reddit(self) -> None:
        assert AsyncReddit is not None

    def test_reddit_importable_from_sources(self) -> None:
        from xanax.sources import Reddit as RedditCls

        assert RedditCls is Reddit

    def test_async_reddit_importable_from_sources(self) -> None:
        from xanax.sources import AsyncReddit as AsyncRedditCls

        assert AsyncRedditCls is AsyncReddit
