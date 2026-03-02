"""
Pydantic models for Reddit API responses.

Reddit returns post data in a nested ``t3_`` listing wrapper. The models
here present a flat, typed interface over that structure.

:class:`RedditPost` is the primary media object. Factory method
:meth:`~RedditPost.from_reddit_data` parses raw post dicts from the API.
Gallery posts (multiple images in one submission) are first detected here
and then expanded by the client into individual :class:`RedditPost` objects
via :meth:`~xanax.sources.reddit.client.Reddit._expand_gallery`.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from xanax._internal.media_type import MediaType


class RedditPost(BaseModel):
    """
    A single media post from Reddit.

    Represents one image, video, or GIF found in a subreddit listing.
    Gallery posts are not returned directly — the client expands them into
    one :class:`RedditPost` per image, populating :attr:`gallery_index` and
    :attr:`gallery_id`.

    Example:
        .. code-block:: python

            post = reddit.post("abc123")
            if post:
                data = reddit.download(post)
    """

    id: str = Field(description="Base-36 post ID (or '<post_id>_<media_id>' for gallery items)")
    fullname: str = Field(description="Reddit fullname, e.g. 't3_abc123'")
    title: str = Field(description="Post title")
    subreddit: str = Field(description="Subreddit name (without r/)")
    author: str = Field(description="Username of the post author")
    score: int = Field(description="Net upvote count")
    url: str = Field(description="Direct URL to the media file")
    media_type: MediaType = Field(description="Type of media: IMAGE, VIDEO, or GIF")
    width: int | None = Field(default=None, description="Media width in pixels")
    height: int | None = Field(default=None, description="Media height in pixels")
    duration: int | None = Field(
        default=None, description="Duration in seconds (VIDEO and GIF only)"
    )
    video_url: str | None = Field(
        default=None,
        description="Video-only stream URL for v.redd.it posts (no audio track)",
    )
    is_nsfw: bool = Field(description="Whether the post is marked NSFW")
    permalink: str = Field(description="Relative permalink, e.g. '/r/EarthPorn/comments/...'")
    created_utc: datetime = Field(description="Post creation timestamp (UTC)")
    is_gallery: bool = Field(description="Whether this post is a Reddit gallery")
    gallery_index: int | None = Field(
        default=None,
        description="0-based index within the parent gallery (set when expanded from gallery)",
    )
    gallery_id: str | None = Field(
        default=None,
        description="Parent post ID when this item was expanded from a gallery",
    )
    thumbnail_url: str | None = Field(
        default=None,
        description="Thumbnail URL provided by Reddit (may be 'self', 'default', etc.)",
    )

    @classmethod
    def from_reddit_data(cls, data: dict[str, Any]) -> "RedditPost | None":
        """
        Build a :class:`RedditPost` from a raw Reddit API post dict.

        Detects the media type and extracts the appropriate URL and dimension
        fields. Returns ``None`` for post types that carry no downloadable
        media (text posts, external links without supported image domains,
        polls, etc.).

        Media type detection order:

        1. ``is_self=True`` — text post, skip (return ``None``).
        2. ``is_video=True`` and ``domain='v.redd.it'`` — VIDEO (or GIF when
           ``is_gif=True`` on the reddit_video object).
        3. ``is_gallery=True`` — IMAGE; ``url`` is left empty because the
           client calls :meth:`~xanax.sources.reddit.client.Reddit._expand_gallery`
           to produce per-image posts.
        4. ``post_hint='image'`` or ``domain`` in ``('i.redd.it', 'i.imgur.com')``
           — IMAGE.
        5. Anything else — skip (return ``None``).

        Args:
            data: Raw post data dict from ``data.children[n].data``.

        Returns:
            Parsed :class:`RedditPost`, or ``None`` if the post has no
            supported media.
        """
        # Text / self posts have no media
        if data.get("is_self", False):
            return None

        is_video = data.get("is_video", False)
        is_gallery = data.get("is_gallery", False)
        post_hint = data.get("post_hint", "")
        domain = data.get("domain", "")

        url = ""
        video_url: str | None = None
        width: int | None = None
        height: int | None = None
        duration: int | None = None
        media_type: MediaType

        if is_video and domain == "v.redd.it":
            # Reddit-hosted video — video-only stream lives in secure_media or media
            reddit_video = (
                (data.get("secure_media") or {}).get("reddit_video")
                or (data.get("media") or {}).get("reddit_video")
                or {}
            )
            is_gif = reddit_video.get("is_gif", False)
            media_type = MediaType.GIF if is_gif else MediaType.VIDEO
            fallback_url = reddit_video.get("fallback_url", "")
            url = fallback_url
            video_url = fallback_url or None
            width = reddit_video.get("width")
            height = reddit_video.get("height")
            duration = reddit_video.get("duration")

        elif is_gallery:
            # Gallery: no single direct URL at the post level; caller expands
            media_type = MediaType.IMAGE
            url = ""

        elif post_hint == "image" or domain in ("i.redd.it", "i.imgur.com"):
            media_type = MediaType.IMAGE
            url = data.get("url_overridden_by_dest") or data.get("url", "")
            # Attempt to extract dimensions from preview
            preview_images = (data.get("preview") or {}).get("images") or []
            if preview_images:
                source = preview_images[0].get("source", {})
                width = source.get("width")
                height = source.get("height")

        else:
            # Unsupported post type (external link, etc.)
            return None

        created_utc = datetime.fromtimestamp(data.get("created_utc", 0), tz=UTC)

        thumbnail = data.get("thumbnail")
        thumbnail_url = thumbnail if thumbnail and thumbnail.startswith("http") else None

        return cls(
            id=data["id"],
            fullname=data.get("name", f"t3_{data['id']}"),
            title=data.get("title", ""),
            subreddit=data.get("subreddit", ""),
            author=data.get("author", "[deleted]"),
            score=data.get("score", 0),
            url=url,
            media_type=media_type,
            width=width,
            height=height,
            duration=duration,
            video_url=video_url,
            is_nsfw=data.get("over_18", False),
            permalink=data.get("permalink", ""),
            created_utc=created_utc,
            is_gallery=is_gallery,
            gallery_index=None,
            gallery_id=None,
            thumbnail_url=thumbnail_url,
        )


class RedditGalleryItem(BaseModel):
    """
    A single image extracted from a Reddit gallery post.

    Reddit galleries store image metadata in ``media_metadata`` keyed by
    ``media_id``. :class:`RedditGalleryItem` holds the parsed fields for
    one such entry.
    """

    media_id: str = Field(description="Media ID as used in media_metadata")
    url: str = Field(description="Direct URL to the full-size image")
    width: int | None = Field(default=None, description="Image width in pixels")
    height: int | None = Field(default=None, description="Image height in pixels")
    mime_type: str | None = Field(default=None, description="MIME type, e.g. 'image/jpg'")
    caption: str | None = Field(default=None, description="Optional caption for this gallery item")


class RedditListing(BaseModel):
    """
    A paginated page of posts from a subreddit listing endpoint.

    Example:
        .. code-block:: python

            listing = reddit.listing(RedditParams(subreddit="EarthPorn"))
            for post in listing.posts:
                print(post.id, post.url)
            if listing.after:
                next_listing = reddit.listing(params.with_after(listing.after))
    """

    posts: list[RedditPost] = Field(description="Media posts on this page (non-media filtered out)")
    after: str | None = Field(
        default=None,
        description="Cursor for the next page (fullname like 't3_abc123')",
    )
    before: str | None = Field(
        default=None,
        description="Cursor for the previous page",
    )
    dist: int = Field(description="Number of items returned by the API before client filtering")
