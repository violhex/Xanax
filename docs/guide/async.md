# Async Client

`AsyncXanax` is a complete async counterpart to `Xanax`. Every method is `async def`, it uses `httpx.AsyncClient` internally, and it supports async context managers and async generators.

## Basic usage

```python
import asyncio
from xanax import AsyncXanax, SearchParams

async def main():
    client = AsyncXanax(api_key="your-api-key")

    results = await client.search(SearchParams(query="anime"))
    for wallpaper in results.data:
        print(wallpaper.resolution, wallpaper.path)

    await client.aclose()

asyncio.run(main())
```

## Recommended: async context manager

The context manager handles cleanup automatically:

```python
async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="nature"))
        wallpaper = await client.wallpaper("94x38z")
```

## Auto-pagination

```python
async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        # Flat iteration over all wallpapers
        async for wallpaper in client.aiter_wallpapers(SearchParams(query="space")):
            print(wallpaper.id, wallpaper.path)

        # Page-by-page
        async for page in client.aiter_pages(SearchParams(query="forest")):
            print(f"Page {page.meta.current_page}: {len(page.data)} results")
```

## Available methods

All sync `Xanax` methods have async equivalents:

| Sync | Async |
| ---- | ----- |
| `wallpaper(id)` | `await client.wallpaper(id)` |
| `search(params)` | `await client.search(params)` |
| `tag(id)` | `await client.tag(id)` |
| `settings()` | `await client.settings()` |
| `collections(username?)` | `await client.collections(username?)` |
| `collection(username, id)` | `await client.collection(username, id)` |
| `download(wallpaper, path?)` | `await client.download(wallpaper, path?)` |
| `iter_pages(params)` | `client.aiter_pages(params)` (async generator) |
| `iter_wallpapers(params)` | `client.aiter_wallpapers(params)` (async generator) |

## Rate limit retry

Retry with exponential backoff uses `asyncio.sleep()`, so it never blocks the event loop:

```python
client = AsyncXanax(api_key="your-api-key", max_retries=3)
```

## Authentication and environment variables

`AsyncXanax` reads `WALLHAVEN_API_KEY` from the environment the same way `Xanax` does:

```python
import os
os.environ["WALLHAVEN_API_KEY"] = "your-api-key"

async with AsyncXanax() as client:  # key picked up automatically
    ...
```

## Concurrent requests

Because `AsyncXanax` is fully async, you can use `asyncio.gather()` or `asyncio.TaskGroup` to run requests concurrently:

```python
import asyncio
from xanax import AsyncXanax

async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        wp1, wp2, wp3 = await asyncio.gather(
            client.wallpaper("94x38z"),
            client.wallpaper("3l3mpl"),
            client.wallpaper("kw7k78"),
        )
        print(wp1.resolution, wp2.resolution, wp3.resolution)

asyncio.run(main())
```

## Integration with web frameworks

`AsyncXanax` works naturally with async web frameworks like FastAPI:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from xanax import AsyncXanax, SearchParams

client: AsyncXanax

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = AsyncXanax(api_key="your-api-key")
    yield
    await client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/search")
async def search(q: str):
    results = await client.search(SearchParams(query=q))
    return {"total": results.meta.total, "wallpapers": [w.id for w in results.data]}
```
