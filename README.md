# xanax

A clean, type-safe Python client for multi-source media APIs — Wallhaven, Unsplash, and Reddit.

## Features

- **Typed all the way down** — every API response is a Pydantic model with full type hints
- **Validated before sending** — invalid parameters raise errors before any network request
- **Both sync and async** — sync clients for scripts; async clients for web apps and pipelines
- **Multi-source** — Wallhaven, Unsplash, and Reddit share the same `download()` and `iter_media()` contract
- **Auto-pagination** — `iter_media()` and `aiter_media()` walk through all pages automatically
- **Secure by default** — API keys go in headers, never in query strings
- **Rate limit aware** — configurable retry with exponential backoff on 429 responses

## Supported sources

| Source | Sync | Async | Auth |
| ------ | ---- | ----- | ---- |
| [Wallhaven](https://wallhaven.cc) | `Wallhaven` | `AsyncWallhaven` | `WALLHAVEN_API_KEY` (optional for SFW) |
| [Unsplash](https://unsplash.com) | `Unsplash` | `AsyncUnsplash` | `UNSPLASH_ACCESS_KEY` (required) |
| [Reddit](https://reddit.com) | `Reddit` | `AsyncReddit` | `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` |

## Installation

```bash
pip install xanax
```

```bash
uv add xanax
```

## Quick start

```python
from xanax import Wallhaven
from xanax.sources.wallhaven.params import SearchParams

client = Wallhaven(api_key="your-api-key")

for wallpaper in client.iter_media(SearchParams(query="nature")):
    client.download(wallpaper, path=f"{wallpaper.id}.jpg")
```

```python
from xanax import Unsplash
from xanax.sources.unsplash.params import UnsplashSearchParams

client = Unsplash(access_key="your-access-key")

for photo in client.iter_media(UnsplashSearchParams(query="mountains")):
    client.download(photo, path=f"{photo.id}.jpg")
```

```python
from xanax import Reddit
from xanax.sources.reddit.params import RedditParams
from xanax.sources.reddit.enums import RedditSort

client = Reddit(
    client_id="your-client-id",
    client_secret="your-client-secret",
    user_agent="python:myapp/1.0 (by u/yourname)",
)

for post in client.iter_media(RedditParams(subreddit="EarthPorn", sort=RedditSort.TOP)):
    client.download(post, path=f"{post.id}.jpg")
```

## Authentication

Credentials can be passed directly or read from environment variables:

```python
import os

# Wallhaven — optional for SFW content
os.environ["WALLHAVEN_API_KEY"] = "..."
client = Wallhaven()

# Unsplash — required
os.environ["UNSPLASH_ACCESS_KEY"] = "..."
client = Unsplash()

# Reddit — client_id, client_secret, and user_agent all required
os.environ["REDDIT_CLIENT_ID"] = "..."
os.environ["REDDIT_CLIENT_SECRET"] = "..."
os.environ["REDDIT_USER_AGENT"] = "python:myapp/1.0 (by u/yourname)"
client = Reddit()
```

## Async support

Every sync client has an async counterpart with identical methods:

```python
import asyncio
from xanax import AsyncWallhaven, AsyncUnsplash, AsyncReddit
from xanax.sources.wallhaven.params import SearchParams

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        async for wallpaper in client.aiter_media(SearchParams(query="space")):
            await client.download(wallpaper, path=f"{wallpaper.id}.jpg")

asyncio.run(main())
```

## Source-agnostic code

All clients satisfy `MediaSource` / `AsyncMediaSource`, so you can write code that works
with any source:

```python
from xanax.sources._base import MediaSource

def download_all(source: MediaSource, params) -> None:
    for media in source.iter_media(params):
        source.download(media, path=f"{media.id}.jpg")

download_all(Wallhaven(), SearchParams(query="anime"))
download_all(Unsplash(), UnsplashSearchParams(query="nature"))
```

## Downloading

`download()` returns raw bytes and optionally saves to disk:

```python
# Return bytes
data: bytes = client.download(media)

# Save to disk
client.download(media, path="output.jpg")
```

## Error handling

```python
from xanax.errors import (
    XanaxError,          # Base exception
    AuthenticationError, # 401 or missing credentials
    RateLimitError,      # 429 — has .retry_after attribute
    NotFoundError,       # 404
    ValidationError,     # Invalid parameters (before any request)
    APIError,            # Other HTTP errors — has .status_code
)

try:
    results = client.search(params)
except AuthenticationError:
    print("Invalid or missing credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Bad parameters: {e}")
```

Enable automatic retry on rate limits:

```python
client = Wallhaven(max_retries=3)  # exponential backoff on 429
```

## Development

```bash
uv sync --extra dev

uv run pytest                    # run tests
uv run pytest --cov=xanax        # with coverage
uv run mypy xanax/               # type check
uv run ruff check xanax/ tests/  # lint
```

## Documentation

Full API reference and guides: [xanax.readthedocs.io](https://xanax.readthedocs.io)

## License

BSD 3-Clause
