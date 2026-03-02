# Unsplash

[Unsplash](https://unsplash.com) provides royalty-free, high-resolution photography through a clean REST API. The xanax `Unsplash` and `AsyncUnsplash` clients wrap that API with typed, validated access.

:::{note}
Unlike Wallhaven's SFW tier, the Unsplash API requires an access key for all requests — including read-only search. Register at [unsplash.com/developers](https://unsplash.com/developers) to obtain one.
:::

## Authentication

Pass your access key directly, or set the `UNSPLASH_ACCESS_KEY` environment variable:

```python
from xanax.sources import Unsplash

# Explicit key
unsplash = Unsplash(access_key="your-access-key")

# From environment (UNSPLASH_ACCESS_KEY=...)
unsplash = Unsplash()
```

## Searching for photos

```python
from xanax.sources import Unsplash
from xanax.sources.unsplash import UnsplashSearchParams

unsplash = Unsplash(access_key="your-access-key")
result = unsplash.search(UnsplashSearchParams(query="mountains"))

print(result.total)
for photo in result.results:
    print(photo.id, photo.resolution, photo.urls.regular)
```

### Filter by orientation or color

```python
from xanax.sources.unsplash.enums import UnsplashOrientation, UnsplashColor

result = unsplash.search(UnsplashSearchParams(
    query="ocean",
    orientation=UnsplashOrientation.LANDSCAPE,
    color=UnsplashColor.BLUE,
))
```

## Iterating all pages

`iter_media()` flattens all pages into individual photo objects automatically:

```python
for photo in unsplash.iter_media(UnsplashSearchParams(query="landscape")):
    print(photo.id, photo.resolution)
```

## Getting a random photo

```python
photo = unsplash.random()
print(photo.id, photo.urls.full)
```

## Downloading

`download()` handles the Unsplash attribution tracking step automatically:

```python
from pathlib import Path

photo = unsplash.random()
data: bytes = unsplash.download(photo)
unsplash.download(photo, path=Path("wallpaper.jpg"))
```

:::{note}
Unsplash requires a GET to `photo.links.download_location` before downloading the actual image. `download()` does both steps automatically to satisfy the Unsplash Terms of Service.
:::

## Async client

```python
import asyncio
from xanax.sources import AsyncUnsplash
from xanax.sources.unsplash import UnsplashSearchParams

async def main():
    async with AsyncUnsplash(access_key="your-access-key") as unsplash:
        async for photo in unsplash.aiter_media(UnsplashSearchParams(query="forest")):
            data = await unsplash.download(photo)

asyncio.run(main())
```

## Rate limiting

Unsplash allows 50 demo requests per hour (1000 for production apps). Enable automatic retry:

```python
unsplash = Unsplash(access_key="your-key", max_retries=3)
```

## See also

- {doc}`../api/clients` — complete method signatures
- {doc}`../api/search` — search parameter reference
- {doc}`../guide/error-handling` — exception hierarchy
