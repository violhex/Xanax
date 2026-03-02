# Changelog

## v0.3.0

*Released 2026-03-01*

### New features

- **Reddit source** — `Reddit` and `AsyncReddit` clients for subreddit media feeds via the Reddit OAuth2 API.
  - `iter_media(RedditParams)` — iterate images, videos, and GIFs from any subreddit with automatic pagination.
  - `aiter_media(RedditParams)` — async equivalent.
  - `download(post, path=None)` — fetch image or video bytes; video posts download the MP4 fallback stream.
  - Gallery post expansion — gallery posts are automatically expanded into individual `RedditPost` objects.
  - `RedditParams` — filter by `subreddit`, `sort`, `time_filter`, `limit`, `media_type`, and `include_nsfw`.
  - OAuth2 client_credentials flow — tokens cached and auto-refreshed transparently.
  - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` environment variable support.
- **`MediaType` enum** — shared `IMAGE`, `VIDEO`, `GIF`, `ANY` filter across all sources. Importable from `xanax.enums`.
- **`xanax._internal` package** — internal shared infrastructure (`RateLimitHandler`, `MediaType`) decoupled from source packages.

### Breaking changes

- **Renamed clients** — `Xanax` → `Wallhaven`, `AsyncXanax` → `AsyncWallhaven`. Backwards-compatible aliases `Xanax` and `AsyncXanax` are retained for one major version.
- **Restructured source packages** — Wallhaven code moved from root (`xanax.client`, `xanax.models`, etc.) into `xanax.sources.wallhaven.*`. All public symbols remain importable from `xanax` directly.
- **Renamed iterator methods** — `iter_wallpapers` → `iter_media`, `aiter_wallpapers` → `aiter_media` on all clients. Old names removed.
- **Renamed protocols** — `WallpaperSource` → `MediaSource`, `AsyncWallpaperSource` → `AsyncMediaSource` in `xanax.sources._base`.
- **Docs migrated to Sphinx + Furo** — `mkdocs.yml` removed; `docs/conf.py` and `docs/index.rst` added.

### Migration guide

Rename client classes and iterator methods as described in the breaking changes above.

---

## v0.2.1

*Released 2026-03-01*

### New features

- **Multi-source architecture** — `xanax.sources` package introduces the `MediaSource` and `AsyncMediaSource` protocols. Any source client satisfying `download()` and `iter_media()` fits the protocol, enabling interchangeable source-agnostic code.
- **Unsplash source** — `Unsplash` and `AsyncUnsplash` clients for royalty-free photography via the Unsplash API v1.
  - `search(UnsplashSearchParams)` — search by query with orientation, color, order, per-page, and content-filter options.
  - `photo(id)` — fetch a full photo object (includes EXIF, location, tags).
  - `random(params=None)` — retrieve a single random photo, optionally filtered by collection, topic, username, query, or orientation.
  - `download(photo, path=None)` — two-step download: triggers attribution tracking at `download_location` (required by Unsplash ToS), then fetches image bytes from the CDN.
  - `iter_pages(params)` / `iter_media(params)` — auto-paginating generators.
  - `aiter_pages(params)` / `aiter_media(params)` — async equivalents.
- **Access key resolution** — `UNSPLASH_ACCESS_KEY` environment variable, mirroring the existing `WALLHAVEN_API_KEY` pattern.
- **`UnsplashPhoto.resolution`** and **`UnsplashPhoto.aspect_ratio`** — convenience properties matching the Wallhaven `Wallpaper` model's interface.
- **Retry on 429** — `Unsplash`/`AsyncUnsplash` reuse `RateLimitHandler` for configurable exponential backoff.

---

## v0.2.0

*Released 2026-02-28*

### New features

- **`AsyncWallhaven`** — a complete async client mirroring `Wallhaven`, built on `httpx.AsyncClient`. Supports `async with`, `await`, and async generators.
- **`iter_pages(params)`** / **`aiter_pages(params)`** — generators that auto-paginate, yielding each `SearchResult` page.
- **`iter_media(params)`** / **`aiter_media(params)`** — convenience generators that flatten pages into individual `Wallpaper` objects.
- **`client.download(wallpaper, path=None)`** — fetch raw image bytes and optionally save to disk. Available on both sync and async clients.
- **`WALLHAVEN_API_KEY` environment variable** — both clients now pick up the API key from the environment automatically.
- **`AsyncWallhaven`** exported from the top-level `xanax` package.
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

- Initial release: synchronous `Wallhaven` client with search, wallpaper, tag, settings, and collection endpoints.
- Pydantic v2 models for all responses.
- Type-safe `SearchParams` with pre-flight validation.
- `PaginationHelper` for manual pagination.
- Structured exception hierarchy.
