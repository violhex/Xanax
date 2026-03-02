# Reddit

[Reddit](https://reddit.com) hosts millions of media posts across thousands of subreddits. The xanax `Reddit` and `AsyncReddit` clients provide typed, paginated access to subreddit media feeds.

:::{note}
Reddit requires OAuth2 client credentials (script app) for all API access. Register an application at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and select the "script" type to obtain a client ID and secret.
:::

## Authentication

Pass your credentials directly or use environment variables:

```python
from xanax.sources.reddit import Reddit

# Explicit credentials
client = Reddit(
    client_id="your-client-id",
    client_secret="your-client-secret",
    user_agent="python:myapp/1.0 (by u/yourusername)",
)

# From environment variables:
# REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
client = Reddit()
```

Tokens are fetched automatically using the OAuth2 client_credentials flow and cached for up to 3600 seconds. Refresh is transparent — no action required.

## Fetching media

`iter_media()` iterates over media posts (images, GIFs, videos) from a subreddit:

```python
from xanax.sources.reddit.params import RedditParams
from xanax.sources.reddit.enums import RedditSort

for post in client.iter_media(RedditParams(subreddit="EarthPorn")):
    print(post.id, post.media_type, post.url)
```

### Filter by media type

```python
from xanax.enums import MediaType

# Images only
for post in client.iter_media(RedditParams(
    subreddit="EarthPorn",
    media_type=MediaType.IMAGE,
)):
    client.download(post, path=f"{post.id}.jpg")
```

### Sort and time filter

```python
from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter

for post in client.iter_media(RedditParams(
    subreddit="pics",
    sort=RedditSort.TOP,
    time_filter=RedditTimeFilter.WEEK,
    limit=25,
)):
    print(post.title, post.score)
```

## Downloading

`download()` returns raw bytes and optionally saves to disk:

```python
post = next(client.iter_media(RedditParams(subreddit="EarthPorn")))

# Memory only
data: bytes = client.download(post)

# Save to disk
from pathlib import Path
client.download(post, path=Path(f"{post.id}.jpg"))
```

:::{note}
Video posts (`media_type=MediaType.VIDEO`) download the video-only MP4 stream via `fallback_url`. Audio is a separate DASH stream — merging audio and video requires `ffmpeg` and is not handled by xanax.
:::

## Gallery posts

Reddit gallery posts contain multiple images. `iter_media()` expands gallery posts into individual `RedditPost` objects automatically, one per image:

```python
for post in client.iter_media(RedditParams(subreddit="WidescreenWallpaper")):
    # Each gallery image appears as a separate post
    print(post.id, post.url, post.gallery_index)
```

## Getting a single post

```python
post = client.post("abc123")
if post:
    print(post.title, post.media_type, post.url)
```

## Async client

```python
import asyncio
from xanax.sources.reddit import AsyncReddit
from xanax.sources.reddit.params import RedditParams

async def main():
    async with AsyncReddit(
        client_id="your-client-id",
        client_secret="your-client-secret",
        user_agent="python:myapp/1.0 (by u/yourusername)",
    ) as client:
        async for post in client.aiter_media(RedditParams(subreddit="EarthPorn")):
            data = await client.download(post)

asyncio.run(main())
```

## NSFW content

NSFW posts are excluded by default. To include them:

```python
params = RedditParams(subreddit="pics", include_nsfw=True)
```

## Rate limiting

Reddit enforces rate limits via `X-Ratelimit-*` response headers. Enable automatic retry:

```python
client = Reddit(client_id="...", client_secret="...", user_agent="...", max_retries=3)
```

## Post model reference

`RedditPost` contains:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | `str` | Unique post ID |
| `title` | `str` | Post title |
| `subreddit` | `str` | Subreddit name |
| `url` | `str` | Direct media URL |
| `media_type` | `MediaType` | `IMAGE`, `VIDEO`, `GIF`, or `ANY` |
| `permalink` | `str` | Reddit page URL |
| `score` | `int` | Upvotes minus downvotes |
| `upvote_ratio` | `float` | Ratio of upvotes to total votes |
| `author` | `str` | Post author username |
| `created_utc` | `datetime` | Post creation time |
| `is_nsfw` | `bool` | NSFW flag |
| `video_url` | `str \| None` | Fallback MP4 URL for video posts |
| `gallery_index` | `int \| None` | Position within gallery (0-based) |

## See also

- {doc}`../api/clients` — complete method signatures
- {doc}`../api/search` — `RedditParams` reference
- {doc}`../guide/error-handling` — exception hierarchy
