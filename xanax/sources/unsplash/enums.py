"""
Enumerations for Unsplash API parameters.

These enums provide type-safe options for search and random photo
parameters, ensuring only valid values reach the API.
"""

from enum import StrEnum


class UnsplashOrientation(StrEnum):
    """
    Photo orientation filter.

    - LANDSCAPE: Wider than tall
    - PORTRAIT: Taller than wide
    - SQUARISH: Approximately square
    """

    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARISH = "squarish"


class UnsplashColor(StrEnum):
    """
    Dominant color filter for photo search.

    Only applicable to :class:`~xanax.sources.unsplash.params.UnsplashSearchParams`.
    """

    BLACK_AND_WHITE = "black_and_white"
    BLACK = "black"
    WHITE = "white"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    PURPLE = "purple"
    MAGENTA = "magenta"
    GREEN = "green"
    TEAL = "teal"
    BLUE = "blue"


class UnsplashOrderBy(StrEnum):
    """
    Sort order for search results.

    - RELEVANT: Sort by relevance to the query (default)
    - LATEST: Sort by upload date, newest first
    """

    RELEVANT = "relevant"
    LATEST = "latest"


class UnsplashContentFilter(StrEnum):
    """
    Content safety filter level.

    - LOW: Default filtering (some mature content may appear)
    - HIGH: Strict filtering, suitable for all audiences
    """

    LOW = "low"
    HIGH = "high"
