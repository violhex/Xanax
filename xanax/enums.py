"""
Shared enumerations for xanax.

:class:`MediaType` is defined here and applies across all sources.
Wallhaven-specific enums are re-exported from this module for
backwards compatibility — ``from xanax.enums import Category`` continues
to work unchanged.

Note: MediaType is imported from xanax._internal.media_type (not defined here
directly) to avoid a circular import: xanax.enums → xanax.sources.wallhaven.enums
→ xanax.sources.__init__ → xanax.sources.reddit → xanax.enums.
"""

# ruff: noqa: E402
from xanax._internal.media_type import MediaType  # noqa: E402
from xanax.sources.wallhaven.enums import (  # Re-export for backwards compatibility.
    Category,
    Color,
    FileType,
    Order,
    Purity,
    Ratio,
    Resolution,
    Seed,
    Sort,
    TopRange,
)

__all__ = [
    "MediaType",
    "Category",
    "Color",
    "FileType",
    "Order",
    "Purity",
    "Ratio",
    "Resolution",
    "Seed",
    "Sort",
    "TopRange",
]
