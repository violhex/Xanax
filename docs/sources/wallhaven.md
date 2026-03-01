# Wallhaven

[Wallhaven](https://wallhaven.cc) is a community-driven wallpaper site with millions of high-resolution images. xanax provides `Xanax` and `AsyncXanax` clients that give you typed, validated access to its search, download, and collection endpoints.

!!! note "API key optional for SFW"
    Public (SFW) content works without any authentication. An API key is only required for NSFW wallpapers, your own account settings, and your own private collections. Get one from [wallhaven.cc/settings/account](https://wallhaven.cc/settings/account).

## Authentication

Pass your API key directly, or set the `WALLHAVEN_API_KEY` environment variable:

```python
from xanax import Xanax

# Explicit key
client = Xanax(api_key="your-api-key")

# From environment (WALLHAVEN_API_KEY=...)
client = Xanax()
```

The key is sent in the `X-API-Key` header on every request. It is never sent in query parameters, never logged, and never exposed in `repr()`.

```python
print(client)  # Xanax(authenticated)  — key not visible
```

## Searching for wallpapers

Use `SearchParams` to define your search. All fields are optional:

```python
from xanax import Xanax, SearchParams

client = Xanax(api_key="your-api-key")
result = client.search(SearchParams(query="space"))

print(result.meta.total)       # total matching wallpapers
print(result.meta.last_page)   # number of pages available
for wallpaper in result.data:
    print(wallpaper.id, wallpaper.resolution, wallpaper.path)
```

### Filter by category

```python
from xanax.enums import Category

result = client.search(SearchParams(categories=[Category.ANIME]))
```

### Filter by purity

```python
from xanax.enums import Purity

# SFW and sketchy (no key needed)
result = client.search(SearchParams(purity=[Purity.SFW, Purity.SKETCHY]))

# NSFW (API key required)
result = client.search(SearchParams(purity=[Purity.NSFW]))
```

### Sort by toplist

```python
from xanax.enums import Sort, TopRange

result = client.search(
    SearchParams(
        query="nature",
        sorting=Sort.TOPLIST,
        top_range=TopRange.ONE_MONTH,
    )
)
```

### Filter by resolution or ratio

```python
result = client.search(
    SearchParams(
        query="cityscape",
        resolutions=["1920x1080", "2560x1440"],
        ratios=["16x9"],
    )
)
```

## Iterating through all pages

`iter_wallpapers()` flattens all pages into individual wallpaper objects automatically:

```python
for wallpaper in client.iter_wallpapers(SearchParams(query="landscape")):
    print(wallpaper.id, wallpaper.resolution)
```

To iterate page by page:

```python
for page in client.iter_pages(SearchParams(query="anime")):
    print(f"Page {page.meta.current_page} of {page.meta.last_page}")
    for wallpaper in page.data:
        print(wallpaper.id)
```

## Getting a single wallpaper

Fetch the full metadata for a known wallpaper ID:

```python
wallpaper = client.wallpaper("94x38z")
print(wallpaper.resolution, wallpaper.tags)
```

## Downloading

`download()` fetches the full-resolution image and returns bytes. Optionally saves to disk at the same time:

```python
from pathlib import Path

wallpaper = client.wallpaper("94x38z")

# Memory only
data: bytes = client.download(wallpaper)

# Save to disk (bytes also returned)
client.download(wallpaper, path=Path("wallpaper.jpg"))
```

### Batch download

```python
from pathlib import Path
from xanax.enums import Sort

output = Path("wallpapers")
output.mkdir(exist_ok=True)

for wallpaper in client.iter_wallpapers(SearchParams(query="space", sorting=Sort.TOPLIST)):
    ext = wallpaper.file_type.split("/")[-1]  # "image/jpeg" -> "jpeg"
    client.download(wallpaper, path=output / f"{wallpaper.id}.{ext}")
    print(f"Saved {wallpaper.id} ({wallpaper.resolution})")
```

## Collections

```python
# Public collections for any user (no key needed)
collections = client.collections(username="someuser")
for col in collections:
    print(col.id, col.label, col.count)

# Browse wallpapers in a collection
listing = client.collection(username="someuser", collection_id=15)
for wallpaper in listing.data:
    print(wallpaper.id)
```

## Async client

`AsyncXanax` is the async counterpart. All methods are coroutines:

```python
import asyncio
from xanax import AsyncXanax, SearchParams

async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        result = await client.search(SearchParams(query="mountains"))
        print(result.meta.total)

        # Iterate wallpapers across all pages
        async for wallpaper in client.aiter_wallpapers(SearchParams(query="forest")):
            data = await client.download(wallpaper)

asyncio.run(main())
```

## Using as a context manager

Both clients implement the context manager protocol for automatic session cleanup:

=== "Sync"

    ```python
    with Xanax(api_key="your-key") as client:
        wallpaper = client.wallpaper("94x38z")
        data = client.download(wallpaper)
    ```

=== "Async"

    ```python
    async with AsyncXanax(api_key="your-key") as client:
        wallpaper = await client.wallpaper("94x38z")
        data = await client.download(wallpaper)
    ```

## The WallpaperSource protocol

`Xanax` and `AsyncXanax` satisfy the `WallpaperSource` / `AsyncWallpaperSource` protocols defined in `xanax.sources._base`. This means you can write source-agnostic code that works with any supported source:

```python
from xanax.sources._base import WallpaperSource

def save_wallpapers(source: WallpaperSource, params, output_dir):
    for wallpaper in source.iter_wallpapers(params):
        source.download(wallpaper, path=output_dir / f"{wallpaper.id}.jpg")

# Works with Xanax, Unsplash, or any other compliant source
save_wallpapers(client, SearchParams(query="nature"), Path("output"))
```

## Rate limiting

Wallhaven enforces rate limits on its API. The client raises `RateLimitError` on 429 responses by default.

Enable automatic retry with exponential backoff:

```python
client = Xanax(api_key="your-key", max_retries=3)
```

## Wallpaper model reference

`Wallpaper` contains:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | `str` | Unique wallpaper ID |
| `url` | `str` | Wallhaven page URL |
| `short_url` | `str` | Short link |
| `views` | `int` | View count |
| `favorites` | `int` | Favourite count |
| `source` | `str` | Original source URL |
| `purity` | `Purity` | `SFW`, `SKETCHY`, or `NSFW` |
| `category` | `Category` | `GENERAL`, `ANIME`, or `PEOPLE` |
| `dimension_x` / `dimension_y` | `int` | Pixel dimensions |
| `resolution` | `str` | `"1920x1080"` |
| `ratio` | `str` | `"16x9"` |
| `file_size` | `int` | Bytes |
| `file_type` | `str` | MIME type (`"image/jpeg"`) |
| `created_at` | `datetime` | Upload timestamp |
| `colors` | `list[str]` | Dominant hex colors |
| `path` | `str` | Direct CDN URL to the image |
| `thumbs` | `dict[str, str]` | Thumbnail URLs (`large`, `original`, `small`) |
| `tags` | `list[Tag]` | Associated tags |

## See also

- [Authentication →](../guide/authentication.md) — NSFW access, key security, `is_authenticated`
- [Searching →](../guide/searching.md) — all `SearchParams` fields, query syntax, color/resolution filters
- [Pagination →](../guide/pagination.md) — `PaginationHelper`, random seeds, stopping early
- [Downloading →](../guide/downloading.md) — batch download, async download
- [Collections →](../guide/collections.md) — listing and browsing user collections
- [Async Client →](../guide/async.md) — `AsyncXanax`, async context managers, async iteration
- [API Reference →](../api/clients.md) — complete method signatures
