# Searching

All searches go through `SearchParams`. It's a Pydantic model, so invalid combinations are caught and raise `ValidationError` before any HTTP request is made.

## Basic search

```python
from xanax import Wallhaven, SearchParams

client = Wallhaven()
results = client.search(SearchParams(query="anime"))
```

## Search query syntax

The `query` field supports Wallhaven's tag-based search syntax:

```python
# Require a tag
SearchParams(query="+nature")

# Exclude a tag
SearchParams(query="-water")

# Combine
SearchParams(query="+nature -water +forest")

# Search by tag ID
SearchParams(query="id:1")

# Search by uploader
SearchParams(query="@username")

# Free-text (untagged search)
SearchParams(query="mountain lake")
```

## Categories

Control which content categories to include. By default all three are included.

```python
from xanax import SearchParams
from xanax.enums import Category

# Only anime
params = SearchParams(categories=[Category.ANIME])

# General and people, no anime
params = SearchParams(categories=[Category.GENERAL, Category.PEOPLE])

# All categories (default)
params = SearchParams()  # categories defaults to all three
```

## Purity

```python
from xanax.enums import Purity

# SFW only (default)
SearchParams(purity=[Purity.SFW])

# SFW and sketchy
SearchParams(purity=[Purity.SFW, Purity.SKETCHY])

# NSFW (requires API key)
SearchParams(purity=[Purity.NSFW])
```

:::{note}
Requesting NSFW without an API key raises `AuthenticationError` immediately, before the request is sent.
:::
## Sorting

```python
from xanax.enums import Sort, Order

SearchParams(sorting=Sort.DATE_ADDED)   # newest first (default)
SearchParams(sorting=Sort.RELEVANCE)    # best match
SearchParams(sorting=Sort.RANDOM)       # random
SearchParams(sorting=Sort.VIEWS)        # most viewed
SearchParams(sorting=Sort.FAVORITES)    # most favorited
SearchParams(sorting=Sort.TOPLIST)      # toplist (requires top_range)

# Direction
SearchParams(sorting=Sort.DATE_ADDED, order=Order.ASC)  # oldest first
```

## Toplist

When sorting by toplist, you must also provide a time range:

```python
from xanax.enums import Sort, TopRange

SearchParams(sorting=Sort.TOPLIST, top_range=TopRange.ONE_MONTH)
```

Available ranges:

| Value | Period |
| ----- | ------ |
| `TopRange.ONE_DAY` | Past 24 hours |
| `TopRange.THREE_DAYS` | Past 3 days |
| `TopRange.ONE_WEEK` | Past week |
| `TopRange.ONE_MONTH` | Past month |
| `TopRange.THREE_MONTHS` | Past 3 months |
| `TopRange.SIX_MONTHS` | Past 6 months |
| `TopRange.ONE_YEAR` | Past year |

Setting `top_range` without `sorting=Sort.TOPLIST` raises `ValidationError`.

## Resolutions

Filter to exact resolutions. Format: `WIDTHxHEIGHT`.

```python
SearchParams(resolutions=["1920x1080", "2560x1440"])
```

Invalid formats raise `ValidationError`.

## Aspect ratios

Filter by aspect ratio. Format: `WIDTHxHEIGHT` or `WIDTH:HEIGHT`.

```python
SearchParams(ratios=["16x9", "4x3"])
SearchParams(ratios=["16:9"])
```

## Colors

Filter wallpapers by dominant color. Use the `Color` enum:

```python
from xanax.enums import Color

SearchParams(colors=[Color.BLUE, Color.TEAL])
```

All 29 color options are available as `Color.*` enum members.

## File type

```python
from xanax.enums import FileType

SearchParams(file_type=FileType.PNG)
SearchParams(file_type=FileType.JPG)
```

## Similar wallpapers

Find wallpapers similar to a given ID:

```python
SearchParams(like="94x38z")
```

## Pagination

```python
SearchParams(page=2)
```

Pages start at 1. Setting `page=0` raises a `pydantic.ValidationError`.

## Random seed

For random-sorted results, a seed locks the shuffle so you get consistent pages:

```python
from xanax.enums import Sort

params = SearchParams(sorting=Sort.RANDOM, seed="abc123")
```

Seeds are 6 alphanumeric characters. An invalid seed raises `ValidationError`.

When using auto-pagination with `iter_pages()`, seeds returned by the API are carried forward automatically — you don't need to manage them yourself.

## Copying params with changes

`SearchParams` is immutable (Pydantic frozen model). Use `with_page()` and `with_seed()` to get new instances:

```python
params = SearchParams(query="anime", sorting=Sort.TOPLIST, top_range=TopRange.ONE_MONTH)

page2 = params.with_page(2)
seeded = params.with_seed("xyz789")
```

Both return a new `SearchParams` with the single field updated and everything else preserved.

## Full example

```python
from xanax import Wallhaven, SearchParams
from xanax.enums import Category, Color, FileType, Order, Purity, Sort, TopRange

client = Wallhaven(api_key="your-api-key")

params = SearchParams(
    query="+nature -water",
    categories=[Category.GENERAL, Category.ANIME],
    purity=[Purity.SFW, Purity.SKETCHY],
    sorting=Sort.TOPLIST,
    order=Order.DESC,
    top_range=TopRange.ONE_MONTH,
    resolutions=["1920x1080", "2560x1440"],
    ratios=["16x9"],
    colors=[Color.GREEN],
    file_type=FileType.PNG,
    page=1,
)

result = client.search(params)
print(f"Found {result.meta.total} wallpapers across {result.meta.last_page} pages")
```
