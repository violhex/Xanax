# Collections

Wallhaven lets users organize wallpapers into named collections. xanax exposes two collection endpoints.

## List a user's collections

```python
from xanax import Wallhaven

client = Wallhaven()

# Public collections for any user (no API key needed)
collections = client.collections(username="someuser")
for col in collections:
    print(col.id, col.label, col.count, "wallpapers")
```

## Your own collections

Without a username, the API returns the authenticated user's own collections:

```python
client = Wallhaven(api_key="your-api-key")
collections = client.collections()
```

This requires an API key. Without one, `AuthenticationError` is raised.

## Get wallpapers in a collection

```python
listing = client.collection(username="someuser", collection_id=15)

print(f"Page {listing.meta.current_page} of {listing.meta.last_page}")

for wallpaper in listing.data:
    print(wallpaper.id, wallpaper.resolution)
```

`listing` is a `CollectionListing`, which has the same `data` and `meta` fields as a `SearchResult`.

## Collection metadata

Each `Collection` object has:

```python
collection.id       # int — collection ID
collection.label    # str — collection name
collection.views    # int — view count
collection.public   # bool — whether the collection is public
collection.count    # int — number of wallpapers
```

## Async

```python
import asyncio
from xanax import AsyncWallhaven

async def main():
    async with AsyncWallhaven(api_key="your-api-key") as client:
        collections = await client.collections(username="someuser")
        listing = await client.collection("someuser", collections[0].id)

        for wallpaper in listing.data:
            print(wallpaper.id)

asyncio.run(main())
```

## Paginating a collection

Collection listings use the same pagination metadata as search results. Use `PaginationHelper` or request pages manually:

```python
from xanax import PaginationHelper

listing = client.collection("someuser", 15)
helper = PaginationHelper(listing.meta)

while helper.has_next:
    listing = client.collection("someuser", 15)
    # ... process listing.data
```

Or use manual page control:

```python
page = 1
while True:
    listing = client.collection("someuser", 15)
    # process page...
    if listing.meta.current_page >= listing.meta.last_page:
        break
    page += 1
```
