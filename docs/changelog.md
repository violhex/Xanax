# Changelog

## v0.2.1

*Released 2026-03-01*

### New features

- **Multi-source architecture** — `xanax.sources` package introduces the `WallpaperSource` and `AsyncWallpaperSource` protocols. Any source client satisfying `download()` and `iter_wallpapers()` fits the protocol, enabling interchangeable source-agnostic code.
- **Unsplash source** — `Unsplash` and `AsyncUnsplash` clients for royalty-free photography via the Unsplash API v1.
  - `search(UnsplashSearchParams)` — search by query with orientation, color, order, per-page, and content-filter options.
  - `photo(id)` — fetch a full photo object (includes EXIF, location, tags).
  - `random(params=None)` — retrieve a single random photo, optionally filtered by collection, topic, username, query, or orientation.
  - `download(photo, path=None)` — two-step download: triggers attribution tracking at `download_location` (required by Unsplash ToS), then fetches image bytes from the CDN.
  - `iter_pages(params)` / `iter_wallpapers(params)` — auto-paginating generators.
  - `aiter_pages(params)` / `aiter_wallpapers(params)` — async equivalents.
- **Access key resolution** — `UNSPLASH_ACCESS_KEY` environment variable, mirroring the existing `WALLHAVEN_API_KEY` pattern.
- **`UnsplashPhoto.resolution`** and **`UnsplashPhoto.aspect_ratio`** — convenience properties matching the Wallhaven `Wallpaper` model's interface.
- **Retry on 429** — `Unsplash`/`AsyncUnsplash` reuse `RateLimitHandler` for configurable exponential backoff.

---

## v0.2.0

*Released 2026-02-28*

### New features

- **`AsyncXanax`** — a complete async client mirroring `Xanax`, built on `httpx.AsyncClient`. Supports `async with`, `await`, and async generators.
- **`iter_pages(params)`** / **`aiter_pages(params)`** — generators that auto-paginate, yielding each `SearchResult` page.
- **`iter_wallpapers(params)`** / **`aiter_wallpapers(params)`** — convenience generators that flatten pages into individual `Wallpaper` objects.
- **`client.download(wallpaper, path=None)`** — fetch raw image bytes and optionally save to disk. Available on both sync and async clients.
- **`WALLHAVEN_API_KEY` environment variable** — both clients now pick up the API key from the environment automatically.
- **`AsyncXanax`** exported from the top-level `xanax` package.
- **`Avatar`** and **`QueryInfo`** added to the public API exports (they existed as models but weren't importable from `xanax` directly).

### Bug fixes

- **Double auth header** — the API key was previously sent in both the `X-API-Key` header and as an `apikey` query parameter on every request. It is now sent in the header only.
- **Default categories** — `SearchParams` previously defaulted to `[Category.GENERAL]` only, silently excluding anime and people wallpapers. The default is now all three categories, matching Wallhaven's actual default.
- **`with_page()` / `with_seed()`** — these methods previously manually enumerated all fields, meaning any newly added field would silently be dropped in the copy. Both now use `model_dump()` internally and are future-proof.
- **`Collection.public`** — changed from `int` to `bool`. The API returns 0/1; Pydantic coerces this cleanly.

### Removed

- `get_query_params()` from `AuthHandler` — it was a redundant method that caused the API key double-send.
- Module-level `has_next_page()`, `get_next_page()`, `get_total_pages()` from `pagination.py` — they duplicated `PaginationHelper` and weren't part of the public API.

---

## v0.1.1

*Released 2025*

- Version metadata fix.

## v0.1.0

*Released 2025*

- Initial release: synchronous `Xanax` client with search, wallpaper, tag, settings, and collection endpoints.
- Pydantic v2 models for all responses.
- Type-safe `SearchParams` with pre-flight validation.
- `PaginationHelper` for manual pagination.
- Structured exception hierarchy.
