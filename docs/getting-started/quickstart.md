# Quick Start

## Basic search

```python
from xanax import Xanax, SearchParams

client = Xanax(api_key="your-api-key")

results = client.search(SearchParams(query="anime"))

for wallpaper in results.data:
    print(wallpaper.id, wallpaper.resolution, wallpaper.path)
```

That's it. `results` is a `SearchResult` with a `data` list of typed `Wallpaper` objects and a `meta` field with pagination info.

## Iterate through all pages

Instead of manually requesting page 2, 3, ... use `iter_wallpapers()`:

```python
from xanax import Xanax, SearchParams, Sort

client = Xanax(api_key="your-api-key")

params = SearchParams(query="space", sorting=Sort.TOPLIST)

for wallpaper in client.iter_wallpapers(params):
    print(wallpaper.resolution, wallpaper.path)
```

This automatically fetches every page and yields individual `Wallpaper` objects.

## Download a wallpaper

```python
wallpaper = client.wallpaper("94x38z")
client.download(wallpaper, path="wallpaper.jpg")
```

## Async version

```python
import asyncio
from xanax import AsyncXanax, SearchParams

async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="nature"))

        async for wallpaper in client.aiter_wallpapers(SearchParams(query="space")):
            print(wallpaper.path)

asyncio.run(main())
```

## Without an API key

Public (SFW) content works without authentication:

```python
from xanax import Xanax, SearchParams, Purity

client = Xanax()  # no key needed for SFW

results = client.search(SearchParams(query="landscape", purity=[Purity.SFW]))
```

NSFW content requires an API key. Attempting it without one raises `AuthenticationError` immediately — before any network request.

## Using an environment variable

Set `WALLHAVEN_API_KEY` in your environment and omit the `api_key` argument:

```bash
export WALLHAVEN_API_KEY=your-api-key
```

```python
client = Xanax()  # picks up the key automatically
```

## Next steps

- [Authentication](../guide/authentication.md) — full details on API keys and purity access
- [Searching](../guide/searching.md) — all `SearchParams` fields and examples
- [Async Client](../guide/async.md) — working with `AsyncXanax`
