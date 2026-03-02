"""
Parameter model for Reddit listing requests.

:class:`RedditParams` validates all fields before any HTTP request is made,
so invalid combinations fail immediately with a clear Pydantic error rather
than producing a confusing API response.
"""

from pydantic import BaseModel, Field

from xanax._internal.media_type import MediaType
from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter


class RedditParams(BaseModel, frozen=True):
    """
    Parameters for a subreddit media listing request.

    The ``subreddit`` field is required. All other fields have sensible
    defaults. Use the ``+`` separator to fetch from multiple subreddits at
    once (e.g. ``"EarthPorn+spaceporn"``).

    Cursor-based pagination is handled via the ``after`` field. Use
    :meth:`with_after` to build the next-page params from a listing's
    ``after`` cursor rather than mutating the instance.

    Note:
        :attr:`time_filter` only affects results when ``sort`` is
        :attr:`~xanax.sources.reddit.enums.RedditSort.TOP` or
        :attr:`~xanax.sources.reddit.enums.RedditSort.CONTROVERSIAL`.
        It is silently ignored for all other sort orders.

    Example:
        .. code-block:: python

            params = RedditParams(
                subreddit="EarthPorn",
                sort=RedditSort.TOP,
                time_filter=RedditTimeFilter.WEEK,
                limit=50,
            )
            for post in reddit.iter_media(params):
                reddit.download(post, path=f"{post.id}.jpg")

    Args:
        subreddit: Target subreddit(s). Use ``+`` to combine multiple, e.g.
                   ``"wallpapers+EarthPorn"``. Required.
        sort: Listing sort order. Default is :attr:`~RedditSort.HOT`.
        time_filter: Time window for TOP/CONTROVERSIAL listings.
                     Default is :attr:`~RedditTimeFilter.ALL`.
        limit: Posts per page (1–100). Default is 25.
        after: Cursor for the next page (fullname like ``'t3_abc123'``).
               ``None`` fetches the first page.
        media_type: Media type filter applied client-side. Default is
                    :attr:`~xanax.enums.MediaType.ANY` (no filtering).
        include_nsfw: Whether to include NSFW posts. Default is ``False``.
    """

    subreddit: str = Field(description="Target subreddit(s), e.g. 'EarthPorn' or 'a+b'")
    sort: RedditSort = Field(
        default=RedditSort.HOT,
        description="Listing sort order",
    )
    time_filter: RedditTimeFilter = Field(
        default=RedditTimeFilter.ALL,
        description="Time window (applies only to TOP and CONTROVERSIAL sorts)",
    )
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Number of posts per page (1–100)",
    )
    after: str | None = Field(
        default=None,
        description="Cursor for the next page (fullname like 't3_abc123')",
    )
    media_type: MediaType = Field(
        default=MediaType.ANY,
        description="Client-side media type filter",
    )
    include_nsfw: bool = Field(
        default=False,
        description="Whether to yield NSFW-flagged posts",
    )

    def with_after(self, after: str) -> "RedditParams":
        """
        Return a new :class:`RedditParams` with the pagination cursor updated.

        All other fields are preserved unchanged.

        Args:
            after: New cursor value (fullname from :attr:`RedditListing.after`).

        Returns:
            New :class:`RedditParams` instance with ``after`` set.
        """
        return RedditParams(**{**self.model_dump(), "after": after})
