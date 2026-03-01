# Quick Start

## Wallhaven — basic search

```python
from xanax import Xanax, SearchParams

client = Xanax(api_key="your-api-key")

results = client.search(SearchParams(query="anime"))

for wallpaper in results.data:
    print(wallpaper.id, wallpaper.resolution, wallpaper.path)
```

That's it. `results` is a `SearchResult` with a `data` list of typed `Wallpaper` objects and a `meta` field with pagination info.

## Wallhaven — iterate through all pages

Instead of manually requesting page 2, 3, ... use `iter_wallpapers()`:

```python
from xanax import Xanax, SearchParams, Sort

client = Xanax(api_key="your-api-key")

params = SearchParams(query="space", sorting=Sort.TOPLIST)

for wallpaper in client.iter_wallpapers(params):
    print(wallpaper.resolution, wallpaper.path)
```

## Wallhaven — download a wallpaper

```python
wallpaper = client.wallpaper("94x38z")
client.download(wallpaper, path="wallpaper.jpg")
```

## Wallhaven — async version

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

## Wallhaven — without an API key

Public (SFW) content works without authentication:

```python
from xanax import Xanax, SearchParams, Purity

client = Xanax()  # no key needed for SFW

results = client.search(SearchParams(query="landscape", purity=[Purity.SFW]))
```

NSFW content requires an API key. Attempting it without one raises `AuthenticationError` immediately — before any network request.

## Wallhaven — using an environment variable

Set `WALLHAVEN_API_KEY` in your environment and omit the `api_key` argument:

```bash
export WALLHAVEN_API_KEY=your-api-key
```

```python
client = Xanax()  # picks up the key automatically
```

---

## Unsplash — basic search

```python
from xanax.sources import Unsplash
from xanax.sources.unsplash import UnsplashSearchParams

unsplash = Unsplash(access_key="your-access-key")

result = unsplash.search(UnsplashSearchParams(query="mountains"))
print(result.total, result.total_pages)

for photo in result.results:
    print(photo.id, photo.resolution, photo.urls.regular)
```

## Unsplash — download a photo

```python
photo = unsplash.random()
data = unsplash.download(photo, path="wallpaper.jpg")
```

`download()` automatically triggers Unsplash's required attribution tracking step before fetching the image.

## Unsplash — iterate through all pages

```python
for photo in unsplash.iter_wallpapers(UnsplashSearchParams(query="landscape")):
    print(photo.id, photo.resolution)
```

## Unsplash — async version

```python
import asyncio
from xanax.sources import AsyncUnsplash
from xanax.sources.unsplash import UnsplashSearchParams

async def main():
    async with AsyncUnsplash(access_key="your-access-key") as unsplash:
        result = await unsplash.search(UnsplashSearchParams(query="nature"))

        async for photo in unsplash.aiter_wallpapers(UnsplashSearchParams(query="space")):
            data = await unsplash.download(photo)

asyncio.run(main())
```

## Unsplash — using an environment variable

```bash
export UNSPLASH_ACCESS_KEY=your-access-key
```

```python
unsplash = Unsplash()  # picks up the key automatically
```

---

## Next steps

- [Authentication](../guide/authentication.md) — full details on API keys and purity access
- [Searching](../guide/searching.md) — all `SearchParams` fields and examples
- [Unsplash](../sources/unsplash.md) — Unsplash search, random, download, and async usage
- [Async Client](../guide/async.md) — working with `AsyncXanax`
