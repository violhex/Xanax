# Downloading Wallpapers

`download()` fetches the full-resolution image of a wallpaper and returns it as bytes. Optionally, it also writes the file to disk.

## Download to memory

```python
from xanax import Wallhaven

client = Wallhaven(api_key="your-api-key")
wallpaper = client.wallpaper("94x38z")

image_bytes: bytes = client.download(wallpaper)
```

## Download to disk

Pass a file path as the second argument:

```python
from pathlib import Path

client.download(wallpaper, path="wallpaper.jpg")

# Or use a Path object
client.download(wallpaper, path=Path("~/wallpapers/94x38z.jpg").expanduser())
```

The bytes are also returned, so you can write to disk and process in memory at the same time:

```python
data = client.download(wallpaper, path="wallpaper.jpg")
# data is the image bytes; file is also saved
```

## Async download

`AsyncWallhaven.download()` works the same way:

```python
import asyncio
from xanax import AsyncWallhaven

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        wallpaper = await client.wallpaper("94x38z")
        data = await client.download(wallpaper, path="wallpaper.jpg")

asyncio.run(main())
```

## Batch download

Combine with `iter_media()` or `aiter_media()` to download multiple wallpapers:

```python
from pathlib import Path
from xanax import Wallhaven, SearchParams, Sort

client = Wallhaven(api_key="your-api-key")
output_dir = Path("wallpapers")
output_dir.mkdir(exist_ok=True)

params = SearchParams(query="space", sorting=Sort.TOPLIST)

for wallpaper in client.iter_media(params):
    # Derive a filename from the wallpaper ID and file type
    ext = wallpaper.file_type.split("/")[-1]  # "image/jpeg" -> "jpeg"
    filename = output_dir / f"{wallpaper.id}.{ext}"
    client.download(wallpaper, path=filename)
    print(f"Saved {filename}")
```

## Async batch download

```python
import asyncio
from pathlib import Path
from xanax import AsyncWallhaven, SearchParams, Sort

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        output_dir = Path("wallpapers")
        output_dir.mkdir(exist_ok=True)

        params = SearchParams(query="nature", sorting=Sort.TOPLIST)

        async for wallpaper in client.aiter_media(params):
            ext = wallpaper.file_type.split("/")[-1]
            filename = output_dir / f"{wallpaper.id}.{ext}"
            await client.download(wallpaper, path=filename)
            print(f"Saved {filename}")

asyncio.run(main())
```

## Notes

- The download URL comes from `wallpaper.path` — the full CDN URL to the image file.
- Redirects are followed automatically.
- If the CDN returns an error, `httpx.HTTPStatusError` is raised via `raise_for_status()`.
- Large images (some are 50+ MB) are loaded fully into memory before being written to disk.
