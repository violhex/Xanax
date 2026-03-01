# xanax

**xanax** is a Python client for the [Wallhaven.cc](https://wallhaven.cc) API v1. It gives you typed access to wallpapers, tags, collections, and search — with both sync and async interfaces.

```python
from xanax import Xanax, SearchParams, Sort

client = Xanax(api_key="your-api-key")

for wallpaper in client.iter_wallpapers(SearchParams(query="nature", sorting=Sort.TOPLIST)):
    print(wallpaper.resolution, wallpaper.path)
```

## Why xanax?

The existing Wallhaven libraries are either abandoned, untyped, or both. xanax was built to fix that:

- **Typed all the way down** — every API response is a Pydantic model. No more `response["data"]["tags"][0]["name"]`.
- **Validated before sending** — invalid search parameters are caught before any network request goes out.
- **Both sync and async** — `Xanax` for scripts and CLI tools, `AsyncXanax` for web apps and async pipelines.
- **Auto-pagination** — `iter_wallpapers()` and `aiter_wallpapers()` walk through all pages so you don't have to.
- **Secure by default** — the API key goes in a header, never in a query string. It won't appear in logs.
- **Rate limit aware** — configurable retry with exponential backoff on 429 responses.

## Features

| Feature | Details |
| ------- | ------- |
| Type safety | Pydantic v2 models for all responses |
| Parameter validation | Pre-flight checks before making requests |
| Sync client | `Xanax` — built on `httpx.Client` |
| Async client | `AsyncXanax` — built on `httpx.AsyncClient` |
| Auto-pagination | `iter_pages()`, `iter_wallpapers()`, async equivalents |
| Download helper | `client.download(wallpaper)` fetches bytes, optionally saves to disk |
| Env var auth | `WALLHAVEN_API_KEY` is picked up automatically |
| Rate limiting | Configurable retry with exponential backoff |
| Python 3.12+ | Uses modern type syntax throughout |

## Installation

```bash
pip install xanax
```

```bash
uv add xanax
```

## Quick navigation

- **[Installation →](getting-started/installation.md)** — pip, uv, Python requirements
- **[Quick Start →](getting-started/quickstart.md)** — first search in under a minute
- **[Authentication →](guide/authentication.md)** — API keys, env vars, NSFW access
- **[Searching →](guide/searching.md)** — all `SearchParams` options
- **[Async Client →](guide/async.md)** — `AsyncXanax`, async context managers, async iteration
- **[Error Handling →](guide/error-handling.md)** — the full exception hierarchy

## License

BSD-3-Clause. See [GitHub](https://github.com/violhex/xanax) for the source.
