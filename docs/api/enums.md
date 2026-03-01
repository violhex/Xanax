# Enumerations

All search parameter options are expressed as `StrEnum` members, so they have both type safety and string compatibility. Every enum member can be compared to its string value directly.

```python
from xanax.enums import Sort

Sort.TOPLIST == "toplist"  # True
```

## Wallhaven enumerations

::: xanax.enums.Category

::: xanax.enums.Purity

::: xanax.enums.Sort

::: xanax.enums.Order

::: xanax.enums.TopRange

::: xanax.enums.Color

::: xanax.enums.FileType

---

## Unsplash enumerations

::: xanax.sources.unsplash.enums.UnsplashOrientation

::: xanax.sources.unsplash.enums.UnsplashColor

::: xanax.sources.unsplash.enums.UnsplashOrderBy

::: xanax.sources.unsplash.enums.UnsplashContentFilter
