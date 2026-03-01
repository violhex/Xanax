# Pagination

The Wallhaven API paginates search results — by default you get 24 wallpapers per page. xanax gives you a few different ways to handle this.

## Auto-pagination with iter_wallpapers

The simplest option. This walks every page and yields wallpapers one at a time:

```python
from xanax import Xanax, SearchParams

client = Xanax(api_key="your-api-key")

for wallpaper in client.iter_wallpapers(SearchParams(query="space")):
    print(wallpaper.id, wallpaper.path)
```

Use this when you want to process individual wallpapers across all pages without thinking about pages at all.

## Auto-pagination with iter_pages

If you need page-level control — for example, to log progress or stop early — use `iter_pages()`:

```python
for page in client.iter_pages(SearchParams(query="anime")):
    print(f"Page {page.meta.current_page} of {page.meta.last_page}")
    for wallpaper in page.data:
        print(f"  {wallpaper.id}")
```

Each iteration yields a full `SearchResult`. The loop stops when the last page is reached.

## Manual pagination

For full control, call `search()` directly and manage pages yourself:

```python
params = SearchParams(query="nature")

# First page
result = client.search(params)

# Next page
if result.meta.current_page < result.meta.last_page:
    result = client.search(params.with_page(result.meta.current_page + 1))
```

## PaginationHelper

`PaginationHelper` provides a structured way to inspect and navigate pagination metadata:

```python
from xanax import Xanax, PaginationHelper, SearchParams

client = Xanax()
result = client.search(SearchParams(query="anime"))

helper = PaginationHelper(result.meta)

print(helper.current_page)   # 1
print(helper.last_page)      # e.g. 10
print(helper.total)          # e.g. 240
print(helper.has_next)       # True
print(helper.has_prev)       # False
print(helper.next_page_number())   # 2
print(helper.prev_page_number())   # None (on first page)

if helper.has_next:
    next_result = client.search(params.with_page(helper.next_page_number()))
```

## Random sort and seeds

When `sorting=Sort.RANDOM`, Wallhaven assigns a server-side seed that keeps the shuffle consistent across pages. The API returns this seed in `meta.seed`.

If you're paginating manually, carry the seed forward:

```python
from xanax.enums import Sort

params = SearchParams(sorting=Sort.RANDOM)
result = client.search(params)

if result.meta.seed:
    params = params.with_seed(result.meta.seed)
    page2 = client.search(params.with_page(2))
```

`iter_pages()` and `iter_wallpapers()` handle seed propagation automatically. You don't need to do anything.

## Async auto-pagination

`AsyncXanax` has async equivalents:

```python
import asyncio
from xanax import AsyncXanax, SearchParams

async def main():
    async with AsyncXanax(api_key="your-api-key") as client:
        # Flat wallpaper iteration
        async for wallpaper in client.aiter_wallpapers(SearchParams(query="space")):
            print(wallpaper.path)

        # Page-by-page
        async for page in client.aiter_pages(SearchParams(query="nature")):
            print(f"Page {page.meta.current_page}: {len(page.data)} wallpapers")

asyncio.run(main())
```

## Stopping early

Both sync and async generators support early exit cleanly:

```python
count = 0
for wallpaper in client.iter_wallpapers(SearchParams(query="anime")):
    print(wallpaper.id)
    count += 1
    if count >= 100:
        break
```
