# Error Handling

All xanax exceptions inherit from `XanaxError`. This means you can catch everything with a single `except XanaxError` or be specific about what you handle.

## Exception hierarchy

```
XanaxError
├── AuthenticationError    — 401 responses, or missing API key for protected content
├── RateLimitError         — 429 responses; has .retry_after
├── NotFoundError          — 404 responses
├── ValidationError        — invalid parameters (raised before any request)
└── APIError               — other 4xx/5xx responses; has .status_code
```

## Full example

```python
from xanax import Xanax, SearchParams
from xanax.errors import (
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    APIError,
    XanaxError,
)

client = Xanax(api_key="your-api-key")

try:
    results = client.search(SearchParams(query="anime"))
except AuthenticationError:
    print("Invalid or missing API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except XanaxError as e:
    print(f"Unexpected xanax error: {e}")
```

## AuthenticationError

Raised in two situations:

1. The server returns HTTP 401
2. You call a protected endpoint without an API key (raised locally, no request made)

```python
client = Xanax()

try:
    client.settings()  # requires API key
except AuthenticationError as e:
    print(e)  # "User settings require an API key..."
```

## RateLimitError

Raised when the API returns HTTP 429. The Wallhaven API allows 45 requests per minute.

```python
from xanax.errors import RateLimitError

try:
    result = client.search(params)
except RateLimitError as e:
    print(e.retry_after)  # seconds to wait (float or None if not provided by API)
```

To avoid handling this yourself, configure automatic retry:

```python
client = Xanax(max_retries=3)  # retry up to 3 times with exponential backoff
```

With `max_retries=3`, the client waits `2^attempt` seconds between retries (1s, 2s, 4s). If all retries are exhausted, `RateLimitError` is raised.

## NotFoundError

Raised on HTTP 404. Typically means the wallpaper or tag ID doesn't exist:

```python
try:
    wallpaper = client.wallpaper("doesnotexist")
except NotFoundError:
    print("Wallpaper not found")
```

## ValidationError

Raised locally before any network request when search parameters are invalid.

Common causes:

- `top_range` set without `sorting=Sort.TOPLIST`
- Invalid resolution format (e.g., `"1920-1080"` instead of `"1920x1080"`)
- Invalid ratio format
- Invalid seed length or characters

```python
from xanax.errors import ValidationError

try:
    SearchParams(sorting=Sort.DATE_ADDED, top_range=TopRange.ONE_MONTH)
except ValidationError as e:
    print(e)  # "top_range requires sorting=toplist"
```

## APIError

Catch-all for other HTTP errors (500, 503, etc.):

```python
from xanax.errors import APIError

try:
    result = client.search(params)
except APIError as e:
    print(e.status_code)  # e.g. 503
    print(e.message)
```

## Async error handling

The async client raises the same exceptions:

```python
import asyncio
from xanax import AsyncXanax, SearchParams
from xanax.errors import RateLimitError

async def main():
    async with AsyncXanax(api_key="your-api-key", max_retries=3) as client:
        try:
            result = await client.search(SearchParams(query="anime"))
        except RateLimitError as e:
            print(f"Still rate limited after retries: {e.retry_after}s")

asyncio.run(main())
```
