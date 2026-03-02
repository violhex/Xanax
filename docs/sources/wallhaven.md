# Wallhaven

[Wallhaven](https://wallhaven.cc) is a community-driven wallpaper site with millions of high-resolution images. xanax provides `Wallhaven` and `AsyncWallhaven` clients that give you typed, validated access to its search, download, and collection endpoints.

:::{note}
Public (SFW) content works without any authentication. An API key is only required for NSFW wallpapers, account settings, and private collections. Get one from [wallhaven.cc/settings/account](https://wallhaven.cc/settings/account).
:::

## Authentication

Pass your API key directly, or set the `WALLHAVEN_API_KEY` environment variable:

```python
from xanax import Wallhaven

# Explicit key
client = Wallhaven(api_key="your-api-key")

# From environment (WALLHAVEN_API_KEY=...)
client = Wallhaven()
```

## Searching

```python
from xanax.sources.wallhaven.params import SearchParams

result = client.search(SearchParams(query="space"))

print(result.meta.total)
for wallpaper in result.data:
    print(wallpaper.id, wallpaper.resolution)
```

### Filter by category and purity

```python
from xanax.sources.wallhaven.enums import Category, Purity

result = client.search(SearchParams(
    categories=[Category.ANIME],
    purity=[Purity.SFW, Purity.SKETCHY],
))
```

### Sort by toplist

```python
from xanax.sources.wallhaven.enums import Sort, TopRange

result = client.search(SearchParams(
    query="nature",
    sorting=Sort.TOPLIST,
    top_range=TopRange.ONE_MONTH,
))
```

## Iterating all pages

`iter_media()` flattens all pages into individual wallpaper objects automatically:

```python
for wallpaper in client.iter_media(SearchParams(query="landscape")):
    print(wallpaper.id, wallpaper.resolution)
```

## Downloading

```python
from pathlib import Path

wallpaper = client.wallpaper("94x38z")

# Memory only
data: bytes = client.download(wallpaper)

# Save to disk (bytes also returned)
client.download(wallpaper, path=Path("wallpaper.jpg"))
```

## Async client

```python
import asyncio
from xanax import AsyncWallhaven
from xanax.sources.wallhaven.params import SearchParams

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        async for wallpaper in client.aiter_media(SearchParams(query="forest")):
            data = await client.download(wallpaper)

asyncio.run(main())
```

## Collections

```python
# Public collections for any user
collections = client.collections(username="someuser")
listing = client.collection(username="someuser", collection_id=15)
for wallpaper in listing.data:
    print(wallpaper.id)
```

## Rate limiting

Enable automatic retry with exponential backoff:

```python
client = Wallhaven(api_key="your-key", max_retries=3)
```
