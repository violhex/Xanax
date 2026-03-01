# xanax

**xanax** is a Python client for wallpaper APIs. It gives you typed access to photos, search, and downloads across multiple sources — with both sync and async interfaces.

=== "Wallhaven"

    ```python
    from xanax import Xanax, SearchParams, Sort

    client = Xanax(api_key="your-api-key")

    for wallpaper in client.iter_wallpapers(SearchParams(query="nature", sorting=Sort.TOPLIST)):
        print(wallpaper.resolution, wallpaper.path)
    ```

=== "Unsplash"

    ```python
    from xanax.sources import Unsplash
    from xanax.sources.unsplash import UnsplashSearchParams

    unsplash = Unsplash(access_key="your-access-key")

    for photo in unsplash.iter_wallpapers(UnsplashSearchParams(query="mountains")):
        data = unsplash.download(photo)
    ```

## Why xanax?

The existing wallpaper libraries are either abandoned, untyped, or locked to a single source. xanax was built to fix that:

- **Typed all the way down** — every API response is a Pydantic model. No more `response["data"]["tags"][0]["name"]`.
- **Validated before sending** — invalid search parameters are caught before any network request goes out.
- **Both sync and async** — `Xanax`/`Unsplash` for scripts and CLI tools; `AsyncXanax`/`AsyncUnsplash` for web apps and async pipelines.
- **Multi-source** — Wallhaven and Unsplash share the same `download()` contract and iterator protocol, so source-agnostic code is easy to write.
- **Auto-pagination** — `iter_wallpapers()` and `aiter_wallpapers()` walk through all pages so you don't have to.
- **Secure by default** — API keys go in headers, never in query strings. They won't appear in logs.
- **Rate limit aware** — configurable retry with exponential backoff on 429 responses.

## Supported sources

| Source | Sync | Async | Auth |
| ------ | ---- | ----- | ---- |
| [Wallhaven](https://wallhaven.cc) | `Xanax` | `AsyncXanax` | `WALLHAVEN_API_KEY` (optional for SFW) |
| [Unsplash](https://unsplash.com) | `Unsplash` | `AsyncUnsplash` | `UNSPLASH_ACCESS_KEY` (required) |

## Features

| Feature | Details |
| ------- | ------- |
| Type safety | Pydantic v2 models for all responses |
| Parameter validation | Pre-flight checks before making requests |
| Multi-source | Wallhaven and Unsplash with a shared download/iterate contract |
| Sync clients | `Xanax`, `Unsplash` — built on `httpx.Client` |
| Async clients | `AsyncXanax`, `AsyncUnsplash` — built on `httpx.AsyncClient` |
| Auto-pagination | `iter_pages()`, `iter_wallpapers()`, async equivalents |
| Download helper | `client.download(photo)` fetches bytes, optionally saves to disk |
| Env var auth | `WALLHAVEN_API_KEY` / `UNSPLASH_ACCESS_KEY` picked up automatically |
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
- **[Unsplash →](sources/unsplash.md)** — royalty-free photography with `Unsplash` / `AsyncUnsplash`
- **[Async Client →](guide/async.md)** — `AsyncXanax`, async context managers, async iteration
- **[Error Handling →](guide/error-handling.md)** — the full exception hierarchy

## License

BSD-3-Clause. See [GitHub](https://github.com/violhex/xanax) for the source.
