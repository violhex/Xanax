# xanax

A clean, type-safe Python client for the Wallhaven.cc API v1.

## Features

- **Type-safe**: All responses are parsed into Pydantic models with full type hints
- **Validated parameters**: Search parameters are validated before making API requests
- **Clean error handling**: Structured error hierarchy for easy error handling
- **Rate limit aware**: Handles rate limiting with optional retry support
- **Secure**: API key is never logged or exposed in any output
- **Async support**: Full async client (`AsyncXanax`) built on `httpx.AsyncClient`
- **Auto-pagination**: `iter_pages()` / `aiter_pages()` handle all pages automatically
- **Download helper**: `client.download(wallpaper)` fetches raw bytes and optionally saves to disk
- **Env var auth**: API key can be set via `WALLHAVEN_API_KEY` environment variable

## Installation

```bash
pip install xanax
```

Or with uv:

```bash
uv add xanax
```

## Quick Start

```python
from xanax import Xanax, SearchParams, Purity, Sort

# API key can also be set via WALLHAVEN_API_KEY env var
client = Xanax(api_key="your-api-key")

# Search for wallpapers (all categories included by default)
params = SearchParams(
    query="+anime -sketch",
    purity=[Purity.SFW],
    sorting=Sort.TOPLIST,
)

results = client.search(params)

# Iterate through results
for wallpaper in results.data:
    print(f"{wallpaper.resolution} - {wallpaper.path}")

# Check pagination
print(f"Page {results.meta.current_page} of {results.meta.last_page}")
```

## Authentication

The Wallhaven API requires an API key for NSFW content. You can get your API key from your
[Wallhaven account settings](https://wallhaven.cc/settings/account).

```python
# Explicit key
client = Xanax(api_key="your-api-key")

# Or set WALLHAVEN_API_KEY in your environment
import os
os.environ["WALLHAVEN_API_KEY"] = "your-api-key"
client = Xanax()  # picks it up automatically
```

The API key is stored securely and never exposed in any string representations.

## Async Client

`AsyncXanax` mirrors the sync client exactly, using `httpx.AsyncClient` internally:

```python
import asyncio
from xanax import AsyncXanax, SearchParams

async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="anime"))

        # Auto-paginate asynchronously
        async for wallpaper in client.aiter_wallpapers(SearchParams(query="nature")):
            print(wallpaper.path)

asyncio.run(main())
```

## Auto-Pagination

Both clients expose generators that handle pagination automatically, including seed
propagation for random-sorted results:

```python
# Sync: iterate over every wallpaper across all pages
for wallpaper in client.iter_wallpapers(SearchParams(query="space")):
    print(wallpaper.id)

# Sync: iterate page by page
for page in client.iter_pages(SearchParams(query="space")):
    print(f"Page {page.meta.current_page}: {len(page.data)} results")

# Async equivalents
async for wallpaper in client.aiter_wallpapers(SearchParams(query="space")):
    print(wallpaper.id)
```

## Downloading Wallpapers

```python
wallpaper = client.wallpaper("94x38z")

# Download to memory
data: bytes = client.download(wallpaper)

# Download and save to disk
client.download(wallpaper, path="wallpaper.jpg")

# Async
data = await async_client.download(wallpaper, path="wallpaper.jpg")
```

## Search Parameters

`SearchParams` provides type-safe search parameters with pre-flight validation:

```python
from xanax import SearchParams
from xanax.enums import Category, Purity, Sort, Order, TopRange, Color, FileType

params = SearchParams(
    query="+nature -water",       # Include/exclude tags
    categories=[Category.GENERAL, Category.ANIME],
    purity=[Purity.SFW],          # SFW, SKETCHY, NSFW (requires API key)
    sorting=Sort.TOPLIST,         # date_added, relevance, random, views, favorites, toplist
    order=Order.DESC,             # desc or asc
    top_range=TopRange.ONE_MONTH, # 1d, 3d, 1w, 1M, 3M, 6M, 1y (toplist only)
    resolutions=["1920x1080", "2560x1440"],
    ratios=["16x9", "4x3"],
    colors=[Color.BLUE, Color.GREEN],
    file_type=FileType.PNG,       # Filter by file type
    like="94x38z",                # Find wallpapers similar to this ID
    page=1,
    seed="abc123",                # For random sorting consistency
)
```

`with_page()` and `with_seed()` return new instances with the field updated:

```python
page2_params = params.with_page(2)
seeded_params = params.with_seed("xyz789")
```

## API Reference

### Xanax / AsyncXanax

```python
client = Xanax(api_key=None, timeout=30.0, max_retries=0)
client = AsyncXanax(api_key=None, timeout=30.0, max_retries=0)
```

**Methods (async variants are identical with `await` / `async for`):**

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `wallpaper(id)` | `Wallpaper` | Fetch a specific wallpaper |
| `search(params)` | `SearchResult` | Search wallpapers |
| `tag(id)` | `Tag` | Fetch tag info |
| `settings()` | `UserSettings` | Authenticated user settings |
| `collections(username?)` | `list[Collection]` | User collections |
| `collection(username, id)` | `CollectionListing` | Wallpapers in a collection |
| `download(wallpaper, path?)` | `bytes` | Download wallpaper image |
| `iter_pages(params)` | `Iterator[SearchResult]` | Auto-paginate (sync) |
| `iter_wallpapers(params)` | `Iterator[Wallpaper]` | Flat wallpaper iterator (sync) |
| `aiter_pages(params)` | `AsyncIterator[SearchResult]` | Auto-paginate (async) |
| `aiter_wallpapers(params)` | `AsyncIterator[Wallpaper]` | Flat wallpaper iterator (async) |

### Error Handling

```python
from xanax.errors import (
    XanaxError,          # Base exception
    AuthenticationError, # 401 or missing API key
    RateLimitError,      # 429, has .retry_after attribute
    NotFoundError,       # 404
    ValidationError,     # Invalid parameters (raised before any request)
    APIError,            # Other HTTP errors, has .status_code attribute
)

try:
    results = client.search(SearchParams(query="anime"))
except AuthenticationError:
    print("Invalid or missing API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
except APIError as e:
    print(f"API error: {e.status_code}")
```

### Pagination Helper

For manual pagination control:

```python
from xanax import PaginationHelper

results = client.search(params)
helper = PaginationHelper(results.meta)

print(helper.current_page, helper.last_page, helper.total)

if helper.has_next:
    next_results = client.search(params.with_page(helper.next_page_number()))
```

## Models

All API responses are parsed into typed Pydantic models:

- `Wallpaper` - Single wallpaper with all metadata
- `Tag` - Tag information
- `Uploader` - User uploader info
- `Avatar` - User avatar at different sizes
- `Thumbnails` - Thumbnail URLs
- `SearchResult` - Search results with wallpapers and pagination
- `PaginationMeta` - Pagination information (current page, last page, total, seed)
- `QueryInfo` - Resolved search query info
- `UserSettings` - User account preferences
- `Collection` - Collection metadata
- `CollectionListing` - Collection wallpapers with pagination

## Enumerations

All search parameters have type-safe `StrEnum` members:

- `Category` - `GENERAL`, `ANIME`, `PEOPLE`
- `Purity` - `SFW`, `SKETCHY`, `NSFW`
- `Sort` - `DATE_ADDED`, `RELEVANCE`, `RANDOM`, `VIEWS`, `FAVORITES`, `TOPLIST`
- `Order` - `DESC`, `ASC`
- `TopRange` - `ONE_DAY`, `THREE_DAYS`, `ONE_WEEK`, `ONE_MONTH`, `THREE_MONTHS`, `SIX_MONTHS`, `ONE_YEAR`
- `Color` - 29 named color options (e.g., `Color.BLUE`, `Color.CRIMSON`)
- `FileType` - `PNG`, `JPG`

## Rate Limiting

The Wallhaven API allows 45 requests per minute. By default, the client raises `RateLimitError`
immediately on a 429 response. Enable automatic retry with exponential backoff:

```python
client = Xanax(max_retries=3)  # Retry up to 3 times with exponential backoff
```

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=xanax

# Type check
uv run mypy xanax/

# Lint
uv run ruff check xanax/
```

## License

MIT
