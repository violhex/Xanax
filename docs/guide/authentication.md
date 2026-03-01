# Authentication

Wallhaven has a public API that anyone can use for SFW content. An API key is required for:

- NSFW wallpapers
- Your own account settings
- Your own private collections

You can get your API key from [Wallhaven account settings](https://wallhaven.cc/settings/account).

## Passing a key directly

```python
from xanax import Xanax

client = Xanax(api_key="your-api-key")
print(client.is_authenticated)  # True
```

## Using an environment variable

Set `WALLHAVEN_API_KEY` in your environment before running your script:

```bash
export WALLHAVEN_API_KEY=your-api-key
```

```python
client = Xanax()  # automatically picks up WALLHAVEN_API_KEY
print(client.is_authenticated)  # True
```

This works for both `Xanax` and `AsyncXanax`. The explicit `api_key` argument always takes precedence over the environment variable.

## Key security

The API key is transmitted via the `X-API-Key` HTTP header on every authenticated request. It is never included in query parameters, never logged, and never exposed in `repr()` or `str()` output.

```python
client = Xanax(api_key="my-secret-key")
print(client)  # Xanax(authenticated)  — key not visible
```

## Checking authentication status

```python
if client.is_authenticated:
    settings = client.settings()
```

## What happens without a key

Calling NSFW-protected endpoints without a key raises `AuthenticationError` before any network request is made:

```python
from xanax import Xanax, SearchParams, Purity
from xanax.errors import AuthenticationError

client = Xanax()  # no key

try:
    client.search(SearchParams(purity=[Purity.NSFW]))
except AuthenticationError as e:
    print(e)  # "NSFW content requires an API key..."
```

The same applies to:

- `client.settings()` — always requires a key
- `client.collections()` without a username — requires a key (your own collections)
- `client.collections(username="someone")` — public collections, no key needed
