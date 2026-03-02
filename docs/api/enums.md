# Enumerations

All search parameter options are expressed as `StrEnum` members, providing both type safety and string compatibility.

```python
from xanax.enums import Sort

Sort.TOPLIST == "toplist"  # True
```

## Shared enumerations

```{eval-rst}
.. autoclass:: xanax._internal.media_type.MediaType
   :members:
```

---

## Wallhaven enumerations

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.Category
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.Purity
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.Sort
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.Order
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.TopRange
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.wallhaven.enums.Color
   :members:
```

---

## Unsplash enumerations

```{eval-rst}
.. autoclass:: xanax.sources.unsplash.enums.UnsplashOrientation
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.unsplash.enums.UnsplashColor
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.unsplash.enums.UnsplashOrderBy
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.unsplash.enums.UnsplashContentFilter
   :members:
```

---

## Reddit enumerations

```{eval-rst}
.. autoclass:: xanax.sources.reddit.enums.RedditSort
   :members:
```

```{eval-rst}
.. autoclass:: xanax.sources.reddit.enums.RedditTimeFilter
   :members:
```
