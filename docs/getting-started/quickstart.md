# Quick Start

## Wallhaven — basic search

```python
from xanax import Wallhaven
from xanax.sources.wallhaven.params import SearchParams

client = Wallhaven(api_key="your-api-key")

results = client.search(SearchParams(query="anime"))
for wallpaper in results.data:
    print(wallpaper.id, wallpaper.resolution, wallpaper.path)
```

## Wallhaven — iterate through all pages

```python
from xanax import Wallhaven
from xanax.sources.wallhaven.params import SearchParams
from xanax.sources.wallhaven.enums import Sort

client = Wallhaven(api_key="your-api-key")

for wallpaper in client.iter_media(SearchParams(query="space", sorting=Sort.TOPLIST)):
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
from xanax import AsyncWallhaven
from xanax.sources.wallhaven.params import SearchParams

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        results = await client.search(SearchParams(query="nature"))

        async for wallpaper in client.aiter_media(SearchParams(query="space")):
            print(wallpaper.path)

asyncio.run(main())
```

---

## Unsplash — basic search

```python
from xanax.sources import Unsplash
from xanax.sources.unsplash.params import UnsplashSearchParams

unsplash = Unsplash(access_key="your-access-key")

result = unsplash.search(UnsplashSearchParams(query="mountains"))
for photo in result.results:
    print(photo.id, photo.resolution, photo.urls.regular)
```

## Unsplash — iterate through all pages

```python
for photo in unsplash.iter_media(UnsplashSearchParams(query="landscape")):
    print(photo.id, photo.resolution)
```

---

## Reddit — basic media fetch

```python
from xanax.sources.reddit import Reddit
from xanax.sources.reddit.params import RedditParams
from xanax.enums import MediaType

client = Reddit(
    client_id="your-client-id",
    client_secret="your-client-secret",
    user_agent="python:myapp/1.0 (by u/yourusername)",
)

for post in client.iter_media(RedditParams(
    subreddit="EarthPorn",
    media_type=MediaType.IMAGE,
)):
    client.download(post, path=f"{post.id}.jpg")
```

---

## Next steps

- {doc}`../guide/authentication` — full details on API keys
- {doc}`../guide/searching` — all `SearchParams` fields
- {doc}`../sources/unsplash` — Unsplash search, random, download
- {doc}`../sources/reddit` — Reddit subreddit media feeds
- {doc}`../guide/async` — async clients and async iteration
