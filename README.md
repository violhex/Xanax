# xanax

A clean, type-safe Python client for the Wallhaven.cc API v1.

## Features

- **Type-safe**: All responses are parsed into Pydantic models with full type hints
- **Validated parameters**: Search parameters are validated before making API requests
- **Clean error handling**: Structured error hierarchy for easy error handling
- **Rate limit aware**: Handles rate limiting with optional retry support
- **Secure**: API key is never logged or exposed in any output
- **No magic**: Explicit method calls, no hidden defaults

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

# Create a client (optional API key for NSFW content)
client = Xanax(api_key="your-api-key")

# Search for wallpapers
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

The Wallhaven API requires an API key for NSFW content. You can get your API key from your [Wallhaven account settings](https://wallhaven.cc/settings/account).

```python
client = Xanax(api_key="your-api-key")
```

The API key is stored securely and never exposed in any string representations.

## Search Parameters

`SearchParams` provides type-safe search parameters:

```python
from xanax import SearchParams
from xanax.enums import Category, Purity, Sort, Order, TopRange, Color, FileType

params = SearchParams(
    query="+nature -water",      # Include/exclude tags
    categories=[Category.GENERAL, Category.ANIME],
    purity=[Purity.SFW],         # SFW, SKETCHY, NSFW (requires API key)
    sorting=Sort.TOPLIST,        # date_added, relevance, random, views, favorites, toplist
    order=Order.DESC,            # desc or asc
    top_range=TopRange.ONE_MONTH, # 1d, 3d, 1w, 1M, 3M, 6M, 1y (only with toplist sorting)
    resolutions=["1920x1080", "2560x1440"],
    ratios=["16x9", "4x3"],
    colors=[Color.BLUE, Color.GREEN],
    file_type=FileType.PNG,     # Filter by file type (png or jpg)
    like="94x38z",              # Find wallpapers similar to this ID
    page=1,
    seed="abc123",              # For random sorting consistency
)
```

## API Reference

### Xanax Client

```python
client = Xanax(api_key=None, timeout=30.0, max_retries=0)
```

**Methods:**

- `client.wallpaper(id: str) -> Wallpaper` - Get a specific wallpaper
- `client.search(params: SearchParams) -> SearchResult` - Search for wallpapers
- `client.tag(id: int) -> Tag` - Get tag information
- `client.settings() -> UserSettings` - Get authenticated user's settings
- `client.collections(username: str | None = None) -> list[Collection]` - Get collections
- `client.collection(username: str, id: int) -> CollectionListing` - Get wallpapers in a collection

### Error Handling

```python
from xanax import Xanax
from xanax.errors import (
    XanaxError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    APIError,
)

try:
    client = Xanax(api_key="your-key")
    results = client.search(SearchParams(query="anime"))
except AuthenticationError:
    print("Invalid API key")
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

```python
from xanax.pagination import PaginationHelper

results = client.search(params)

# Use the helper for easier pagination
helper = PaginationHelper(results.meta)

if helper.has_next:
    next_page = helper.next_page_number()
    next_params = params.with_page(next_page)
    next_results = client.search(next_params)
```

## Models

All API responses are parsed into typed Pydantic models:

- `Wallpaper` - Single wallpaper details
- `Tag` - Tag information
- `Uploader` - User uploader info with avatar
- `Avatar` - User avatar at different sizes
- `Thumbnails` - Thumbnail URLs
- `SearchResult` - Search results with wallpapers and meta
- `PaginationMeta` - Pagination information
- `QueryInfo` - Resolved search query info
- `UserSettings` - User preferences
- `Collection` - Collection info
- `CollectionListing` - Collection wallpapers

## Enumerations

All search parameters have type-safe enums:

- `Category` - general, anime, people
- `Purity` - sfw, sketchy, nsfw
- `Sort` - date_added, relevance, random, views, favorites, toplist
- `Order` - desc, asc
- `TopRange` - 1d, 3d, 1w, 1M, 3M, 6M, 1y
- `Color` - All valid wallhaven colors
- `FileType` - png, jpg

## Rate Limiting

The Wallhaven API allows 45 requests per minute. By default, the client fails fast when rate limited. You can enable automatic retries:

```python
client = Xanax(max_retries=3)  # Retry up to 3 times with exponential backoff
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=xanax
```

## License

MIT
