# Unsplash

[Unsplash](https://unsplash.com) provides royalty-free, high-resolution photography through a clean REST API. The xanax `Unsplash` and `AsyncUnsplash` clients wrap that API with the same typed interface you already know from `Xanax`.

!!! note "Access key required"
    Unlike Wallhaven's SFW tier, the Unsplash API requires an access key for all requests — including read-only search. Register at [unsplash.com/developers](https://unsplash.com/developers) to obtain one.

## Authentication

Pass your access key directly, or set the `UNSPLASH_ACCESS_KEY` environment variable:

```python
from xanax.sources import Unsplash

# Explicit key
unsplash = Unsplash(access_key="your-access-key")

# From environment (UNSPLASH_ACCESS_KEY=...)
unsplash = Unsplash()
```

The key is sent in the `Authorization: Client-ID <key>` header on every request. It is never logged or exposed in `repr()`.

## Searching for photos

Use `UnsplashSearchParams` to define your search. The only required field is `query`:

```python
from xanax.sources import Unsplash
from xanax.sources.unsplash import UnsplashSearchParams

unsplash = Unsplash(access_key="your-access-key")
result = unsplash.search(UnsplashSearchParams(query="mountains"))

print(result.total)       # total matching photos across all pages
print(result.total_pages) # number of pages available
for photo in result.results:
    print(photo.id, photo.resolution, photo.urls.regular)
```

### Filter by orientation

```python
from xanax.sources.unsplash import UnsplashOrientation

result = unsplash.search(
    UnsplashSearchParams(
        query="forest",
        orientation=UnsplashOrientation.LANDSCAPE,
    )
)
```

### Filter by dominant color

```python
from xanax.sources.unsplash import UnsplashColor

result = unsplash.search(
    UnsplashSearchParams(
        query="ocean",
        color=UnsplashColor.BLUE,
    )
)
```

### Sort by latest

```python
from xanax.sources.unsplash import UnsplashOrderBy

result = unsplash.search(
    UnsplashSearchParams(
        query="city",
        order_by=UnsplashOrderBy.LATEST,
        per_page=30,
    )
)
```

### Content filtering

```python
from xanax.sources.unsplash import UnsplashContentFilter

result = unsplash.search(
    UnsplashSearchParams(
        query="nature",
        content_filter=UnsplashContentFilter.HIGH,
    )
)
```

## Iterating through all pages

`iter_wallpapers()` flattens all pages into individual photo objects automatically:

```python
for photo in unsplash.iter_wallpapers(UnsplashSearchParams(query="landscape")):
    print(photo.id, photo.resolution)
```

To iterate page by page:

```python
for page in unsplash.iter_pages(UnsplashSearchParams(query="landscape")):
    print(f"Page has {len(page.results)} photos")
    for photo in page.results:
        print(photo.id)
```

## Getting a random photo

```python
photo = unsplash.random()
print(photo.id, photo.urls.full)
```

Narrow the random pool with `UnsplashRandomParams`:

```python
from xanax.sources.unsplash import UnsplashRandomParams

# Random landscape photo
photo = unsplash.random(
    UnsplashRandomParams(
        query="mountains",
        orientation=UnsplashOrientation.LANDSCAPE,
    )
)
```

## Getting a photo by ID

```python
photo = unsplash.photo("Dwu85P9SOIk")

# Full photo includes EXIF, location, tags
if photo.exif:
    print(photo.exif.make, photo.exif.model)
if photo.location:
    print(photo.location.city, photo.location.country)
```

## Downloading

`download()` handles everything — including the attribution tracking step that Unsplash's API Terms of Service require. You don't need to call anything separately.

```python
photo = unsplash.random()
data: bytes = unsplash.download(photo)
```

Save to disk at the same time:

```python
from pathlib import Path

unsplash.download(photo, path=Path("wallpaper.jpg"))
```

!!! info "Two-step download"
    Unsplash requires a GET to `photo.links.download_location` (an API endpoint) before downloading the actual image. This increments the download counter on Unsplash's backend and satisfies their attribution requirements. `download()` does both steps automatically.

## Batch download

```python
from pathlib import Path

output = Path("wallpapers")
output.mkdir(exist_ok=True)

for photo in unsplash.iter_wallpapers(UnsplashSearchParams(query="space", per_page=30)):
    unsplash.download(photo, path=output / f"{photo.id}.jpg")
    print(f"Saved {photo.id} ({photo.resolution})")
```

## Async client

`AsyncUnsplash` is the async counterpart. All methods are coroutines:

```python
import asyncio
from xanax.sources import AsyncUnsplash
from xanax.sources.unsplash import UnsplashSearchParams

async def main():
    async with AsyncUnsplash(access_key="your-access-key") as unsplash:
        result = await unsplash.search(UnsplashSearchParams(query="mountains"))
        print(result.total)

        # Iterate photos across all pages
        async for photo in unsplash.aiter_wallpapers(UnsplashSearchParams(query="forest")):
            data = await unsplash.download(photo)

asyncio.run(main())
```

## Using as a context manager

Both clients implement the context manager protocol for automatic cleanup:

=== "Sync"

    ```python
    with Unsplash(access_key="your-key") as unsplash:
        photo = unsplash.random()
        data = unsplash.download(photo)
    ```

=== "Async"

    ```python
    async with AsyncUnsplash(access_key="your-key") as unsplash:
        photo = await unsplash.random()
        data = await unsplash.download(photo)
    ```

## The WallpaperSource protocol

Both `Unsplash` and `AsyncUnsplash` satisfy the `WallpaperSource` / `AsyncWallpaperSource` protocols defined in `xanax.sources._base`. This means you can write source-agnostic code using duck typing:

```python
from xanax.sources._base import WallpaperSource

def save_random_wallpaper(source: WallpaperSource, params, output_dir):
    for photo in source.iter_wallpapers(params):
        source.download(photo, path=output_dir / f"{photo.id}.jpg")
        break  # just the first one

# Works with any source that implements the protocol
save_random_wallpaper(unsplash, UnsplashSearchParams(query="nature"), Path("output"))
```

## Rate limiting

Unsplash allows 50 demo requests per hour (1000 for production apps). The client raises `RateLimitError` on 429 responses by default.

Enable automatic retry with exponential backoff:

```python
unsplash = Unsplash(access_key="your-key", max_retries=3)
```

## Photo model reference

`UnsplashPhoto` contains:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | `str` | Unique photo ID |
| `created_at` | `datetime` | Upload timestamp |
| `width` / `height` | `int` | Pixel dimensions |
| `resolution` | `str` (property) | `"3840x2160"` |
| `aspect_ratio` | `float` (property) | `1.78` |
| `color` | `str \| None` | Dominant hex color |
| `blur_hash` | `str \| None` | BlurHash placeholder |
| `description` | `str \| None` | Photo description |
| `urls` | `UnsplashPhotoUrls` | `raw`, `full`, `regular`, `small`, `thumb` |
| `links` | `UnsplashPhotoLinks` | `download_location` and web links |
| `user` | `UnsplashUser` | Photographer info |
| `exif` | `UnsplashExif \| None` | Camera metadata (full photos only) |
| `location` | `UnsplashLocation \| None` | City/country/coords (full photos only) |
| `tags` | `list[UnsplashTag]` | Descriptive tags (full photos only) |
| `downloads` | `int \| None` | Download count (full photos only) |

!!! tip "Abbreviated vs full photos"
    Search results return abbreviated photo objects — `exif`, `location`, `tags`, and `downloads` will be `None`. Use `unsplash.photo(id)` or `unsplash.random()` to get the full model.

## See also

- [Sources API Reference](../api/sources.md) — complete method signatures and parameters
- [Error Handling](../guide/error-handling.md) — the full exception hierarchy
