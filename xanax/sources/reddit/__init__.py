"""
Reddit media source for xanax.

Provides type-safe sync and async clients for fetching media posts from
public Reddit subreddits. Both clients satisfy the
:class:`~xanax.sources._base.MediaSource` protocol and can be used
interchangeably with other xanax sources.

Authentication uses OAuth2 app-only credentials — no user login required
for public subreddits. Credentials can be passed as arguments or read from
environment variables ``REDDIT_CLIENT_ID``, ``REDDIT_CLIENT_SECRET``, and
``REDDIT_USER_AGENT``.

Example (sync):
    from xanax.sources.reddit import Reddit, RedditParams, RedditSort

    with Reddit(
        client_id="...",
        client_secret="...",
        user_agent="python:myapp/0.1 (by u/myname)",
    ) as reddit:
        for post in reddit.iter_media(RedditParams(subreddit="EarthPorn", sort=RedditSort.TOP)):
            reddit.download(post, path=f"{post.id}.jpg")

Example (async):
    from xanax.sources.reddit import AsyncReddit, RedditParams, RedditSort

    async with AsyncReddit(
        client_id="...",
        client_secret="...",
        user_agent="python:myapp/0.1 (by u/myname)",
    ) as reddit:
        async for post in reddit.aiter_media(RedditParams(subreddit="wallpapers")):
            await reddit.download(post, path=f"{post.id}.jpg")
"""

from xanax.sources.reddit.async_client import AsyncReddit
from xanax.sources.reddit.client import Reddit
from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter
from xanax.sources.reddit.models import RedditGalleryItem, RedditListing, RedditPost
from xanax.sources.reddit.params import RedditParams

__all__ = [
    # Clients
    "Reddit",
    "AsyncReddit",
    # Enums
    "RedditSort",
    "RedditTimeFilter",
    # Models
    "RedditPost",
    "RedditGalleryItem",
    "RedditListing",
    # Params
    "RedditParams",
]
