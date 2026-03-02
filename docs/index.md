# xanax

**xanax** is a multi-source media API client for Python. It gives you typed access
to images, photos, and video across multiple platforms — with both sync and async interfaces.

```python
from xanax import Wallhaven
from xanax.sources.wallhaven.params import SearchParams

client = Wallhaven(api_key="your-api-key")
for wallpaper in client.iter_media(SearchParams(query="nature")):
    client.download(wallpaper, path=f"{wallpaper.id}.jpg")
```

## Why xanax?

- **Typed all the way down** — every API response is a Pydantic model.
- **Validated before sending** — invalid parameters are caught before any network request.
- **Both sync and async** — sync clients for scripts; async clients for web apps and pipelines.
- **Multi-source** — Wallhaven, Unsplash, and Reddit share the same `download()` and `iter_media()` contract.
- **Auto-pagination** — `iter_media()` and `aiter_media()` walk through all pages automatically.
- **Secure by default** — API keys go in headers, never in query strings.
- **Rate limit aware** — configurable retry with exponential backoff on 429 responses.

## Supported sources

| Source | Sync | Async | Auth |
| ------ | ---- | ----- | ---- |
| [Wallhaven](https://wallhaven.cc) | `Wallhaven` | `AsyncWallhaven` | `WALLHAVEN_API_KEY` (optional for SFW) |
| [Unsplash](https://unsplash.com) | `Unsplash` | `AsyncUnsplash` | `UNSPLASH_ACCESS_KEY` (required) |
| [Reddit](https://reddit.com) | `Reddit` | `AsyncReddit` | `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` |

## Installation

```bash
pip install xanax
```

```bash
uv add xanax
```
