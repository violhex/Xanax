"""
Asynchronous Reddit client.

Drop-in async counterpart to :class:`~xanax.sources.reddit.client.Reddit`.
All public methods are coroutines. Use as an async context manager for
automatic resource cleanup.

Reddit requires a meaningful ``User-Agent`` header on all requests.
See :class:`~xanax.sources.reddit.client.Reddit` for the recommended format.
"""

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import UTC
from pathlib import Path
from typing import Any

import httpx

from xanax._internal.media_type import MediaType
from xanax._internal.rate_limit import RateLimitHandler
from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from xanax.sources.reddit.auth import AsyncRedditAuth
from xanax.sources.reddit.enums import RedditSort
from xanax.sources.reddit.models import RedditGalleryItem, RedditListing, RedditPost
from xanax.sources.reddit.params import RedditParams


class AsyncReddit:
    """
    Asynchronous Reddit client.

    Drop-in async counterpart to :class:`~xanax.sources.reddit.client.Reddit`.
    All public methods are coroutines. Use as an async context manager for
    automatic resource cleanup.

    Authentication uses OAuth2 app-only credentials (``client_id`` +
    ``client_secret``). No user login is required for public subreddits.
    Credentials can be passed explicitly or read from environment variables
    ``REDDIT_CLIENT_ID``, ``REDDIT_CLIENT_SECRET``, and
    ``REDDIT_USER_AGENT``.

    Example:
        async with AsyncReddit(
            client_id="...",
            client_secret="...",
            user_agent="python:xanax/0.3.0 (by u/yourname)",
        ) as reddit:
            async for post in reddit.aiter_media(
                RedditParams(subreddit="EarthPorn", sort=RedditSort.TOP)
            ):
                await reddit.download(post, path=f"{post.id}.jpg")

    Args:
        client_id: Reddit app client ID. Falls back to ``REDDIT_CLIENT_ID``.
        client_secret: Reddit app client secret. Falls back to
                       ``REDDIT_CLIENT_SECRET``.
        user_agent: Required User-Agent string. Falls back to
                    ``REDDIT_USER_AGENT``.
        timeout: Request timeout in seconds. Default is 30.
        max_retries: Maximum retries on 429 rate-limit responses. Default is 0
                     (fail-fast).

    Raises:
        AuthenticationError: If any credential cannot be resolved.
    """

    BASE_URL = "https://oauth.reddit.com"

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> None:
        resolved_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
        resolved_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
        resolved_ua = user_agent or os.environ.get("REDDIT_USER_AGENT")

        if not resolved_id:
            raise AuthenticationError(
                "Reddit client_id is required. "
                "Pass client_id= or set the REDDIT_CLIENT_ID environment variable."
            )
        if not resolved_secret:
            raise AuthenticationError(
                "Reddit client_secret is required. "
                "Pass client_secret= or set the REDDIT_CLIENT_SECRET environment variable."
            )
        if not resolved_ua:
            raise AuthenticationError(
                "Reddit user_agent is required. "
                "Pass user_agent= or set the REDDIT_USER_AGENT environment variable."
            )

        self._auth = AsyncRedditAuth(resolved_id, resolved_secret, resolved_ua)
        self._rate_limit = RateLimitHandler(max_retries=max_retries)
        self._client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        attempt: int = 0,
    ) -> httpx.Response:
        response = await self._client.request(
            method,
            url,
            params=params,
            headers=await self._auth.get_headers(),
        )

        if response.status_code == 401:
            raise AuthenticationError(
                "Reddit API authentication failed. Check your client credentials."
            )

        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {url}")

        if response.status_code == 429:
            if self._rate_limit.should_retry(response, attempt):
                delay = self._rate_limit.calculate_delay(attempt)
                await asyncio.sleep(delay)
                return await self._request(method, url, params, attempt + 1)
            self._rate_limit.handle_rate_limit(response)

        if response.status_code >= 400:
            raise APIError(
                message=f"Reddit API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        return response

    async def listing(self, params: RedditParams) -> RedditListing:
        """
        Fetch one page of posts from a subreddit listing.

        Args:
            params: :class:`~xanax.sources.reddit.params.RedditParams` with
                    subreddit, sort, limit, and optional cursor.

        Returns:
            :class:`~xanax.sources.reddit.models.RedditListing` with parsed
            posts, pagination cursors, and the raw ``dist`` count.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If the subreddit does not exist.
            RateLimitError: If the rate limit is exceeded.
            APIError: For any other non-success HTTP status.
        """
        url = self._build_url(f"r/{params.subreddit}/{params.sort.value}")
        query: dict[str, Any] = {
            "limit": params.limit,
            "raw_json": 1,
        }
        if params.after is not None:
            query["after"] = params.after

        if params.sort in (RedditSort.TOP, RedditSort.CONTROVERSIAL):
            query["t"] = params.time_filter.value

        response = await self._request("GET", url, params=query)
        body = response.json()
        data = body.get("data", {})
        children = data.get("children", [])
        dist: int = data.get("dist", len(children))

        posts: list[RedditPost] = []
        for child in children:
            child_data = child.get("data", {})
            post = RedditPost.from_reddit_data(child_data)
            if post is not None:
                posts.append(post)

        return RedditListing(
            posts=posts,
            after=data.get("after"),
            before=data.get("before"),
            dist=dist,
        )

    async def post(self, post_id: str) -> RedditPost | None:
        """
        Fetch a single post by its base-36 ID.

        Returns ``None`` if the post exists but has no supported media.

        Args:
            post_id: Base-36 Reddit post ID (e.g. ``"abc123"``).

        Returns:
            Parsed :class:`~xanax.sources.reddit.models.RedditPost`, or
            ``None`` if no media is present.

        Raises:
            NotFoundError: If the post does not exist.
            AuthenticationError: If credentials are invalid.
            APIError: For unexpected HTTP errors.
        """
        url = self._build_url(f"comments/{post_id}")
        response = await self._request("GET", url, params={"raw_json": 1})
        listings = response.json()
        post_listing = listings[0] if listings else {}
        children = post_listing.get("data", {}).get("children", [])
        if not children:
            return None
        return RedditPost.from_reddit_data(children[0].get("data", {}))

    async def download(self, post: RedditPost, path: Path | str | None = None) -> bytes:
        """
        Download the raw media bytes for a post.

        For VIDEO and GIF posts the :attr:`~RedditPost.video_url` is used
        (video-only stream, no audio). For IMAGE posts the direct
        :attr:`~RedditPost.url` is fetched.

        Note:
            Reddit video does not include audio in the ``fallback_url``
            stream. Only video bytes are returned.

        Args:
            post: The :class:`~xanax.sources.reddit.models.RedditPost` to
                  download.
            path: Optional file path to save the bytes.

        Returns:
            Raw media bytes.

        Raises:
            ValueError: If the post has no downloadable URL.
            httpx.HTTPStatusError: If the download request fails.
        """
        if post.media_type in (MediaType.VIDEO, MediaType.GIF):
            download_url = post.video_url or post.url
        else:
            download_url = post.url

        if not download_url:
            raise ValueError(
                f"Post '{post.id}' has no downloadable URL. "
                "Gallery posts must be expanded before downloading."
            )

        response = await self._client.get(download_url)
        response.raise_for_status()
        content = response.content

        if path is not None:
            Path(path).write_bytes(content)

        return content

    async def aiter_pages(self, params: RedditParams) -> AsyncIterator[RedditListing]:
        """
        Async-iterate through all pages of a subreddit listing.

        Args:
            params: Starting :class:`~xanax.sources.reddit.params.RedditParams`.
                    The ``after`` cursor is managed automatically.

        Yields:
            :class:`~xanax.sources.reddit.models.RedditListing` for each page.

        Example:
            async for page in reddit.aiter_pages(RedditParams(subreddit="wallpapers")):
                for post in page.posts:
                    print(post.id)
        """
        current_params = params
        while True:
            listing = await self.listing(current_params)
            yield listing
            if not listing.after or not listing.posts:
                break
            current_params = current_params.with_after(listing.after)

    async def aiter_media(self, params: RedditParams) -> AsyncIterator[RedditPost]:
        """
        Async-iterate over all media posts, flattening pages and expanding galleries.

        Applies the same filtering as the sync
        :meth:`~xanax.sources.reddit.client.Reddit.iter_media`:

        - Skips posts whose :attr:`~RedditPost.media_type` does not match
          ``params.media_type`` (unless ``media_type=ANY``).
        - Skips NSFW posts unless ``params.include_nsfw=True``.
        - Expands gallery posts into individual
          :class:`~xanax.sources.reddit.models.RedditPost` objects.

        Args:
            params: :class:`~xanax.sources.reddit.params.RedditParams` with
                    filter and pagination settings.

        Yields:
            :class:`~xanax.sources.reddit.models.RedditPost` objects.

        Example:
            async for post in reddit.aiter_media(
                RedditParams(subreddit="EarthPorn", sort=RedditSort.TOP)
            ):
                await reddit.download(post, path=f"{post.id}.jpg")
        """
        async for page in self.aiter_pages(params):
            for post in page.posts:
                if post.is_nsfw and not params.include_nsfw:
                    continue

                if post.is_gallery:
                    url = self._build_url(f"comments/{post.id}")
                    try:
                        response = await self._request("GET", url, params={"raw_json": 1})
                        listings = response.json()
                        children = listings[0].get("data", {}).get("children", [])
                        raw_post_data = children[0].get("data", {}) if children else {}
                    except (APIError, NotFoundError, RateLimitError):
                        continue

                    for expanded in self._expand_gallery(raw_post_data):
                        if expanded.is_nsfw and not params.include_nsfw:
                            continue
                        type_mismatch = (
                            params.media_type != MediaType.ANY
                            and expanded.media_type != params.media_type
                        )
                        if type_mismatch:
                            continue
                        yield expanded
                    continue

                if params.media_type != MediaType.ANY and post.media_type != params.media_type:
                    continue

                yield post

    def _expand_gallery(self, post_data: dict) -> list[RedditPost]:
        """
        Expand a gallery post into individual :class:`RedditPost` objects.

        See :meth:`~xanax.sources.reddit.client.Reddit._expand_gallery` for
        full documentation. This sync helper is safe to call from async
        contexts since it performs no I/O.

        Args:
            post_data: Raw post data dict (``data.children[0].data``).

        Returns:
            List of expanded :class:`~xanax.sources.reddit.models.RedditPost`
            objects.
        """
        from datetime import datetime

        gallery_items = (post_data.get("gallery_data") or {}).get("items", [])
        media_metadata = post_data.get("media_metadata") or {}
        post_id = post_data.get("id", "")

        results: list[RedditPost] = []
        for index, item in enumerate(gallery_items):
            media_id = item.get("media_id", "")
            if not media_id:
                continue

            meta = media_metadata.get(media_id, {})
            source = meta.get("s", {})
            url = source.get("u", "") or source.get("gif", "")
            url = url.replace("&amp;", "&")
            width: int | None = source.get("x")
            height: int | None = source.get("y")
            mime_type: str | None = meta.get("m")
            caption: str | None = item.get("caption")

            gallery_item = RedditGalleryItem(
                media_id=media_id,
                url=url,
                width=width,
                height=height,
                mime_type=mime_type,
                caption=caption,
            )

            created_utc = datetime.fromtimestamp(post_data.get("created_utc", 0), tz=UTC)
            thumbnail = post_data.get("thumbnail")
            thumbnail_url = thumbnail if thumbnail and thumbnail.startswith("http") else None

            post = RedditPost(
                id=f"{post_id}_{media_id}",
                fullname=f"t3_{post_id}",
                title=post_data.get("title", ""),
                subreddit=post_data.get("subreddit", ""),
                author=post_data.get("author", "[deleted]"),
                score=post_data.get("score", 0),
                url=gallery_item.url,
                media_type=MediaType.IMAGE,
                width=gallery_item.width,
                height=gallery_item.height,
                duration=None,
                video_url=None,
                is_nsfw=post_data.get("over_18", False),
                permalink=post_data.get("permalink", ""),
                created_utc=created_utc,
                is_gallery=True,
                gallery_index=index,
                gallery_id=post_id,
                thumbnail_url=thumbnail_url,
            )
            results.append(post)

        return results

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncReddit":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return "AsyncReddit(authenticated)"
