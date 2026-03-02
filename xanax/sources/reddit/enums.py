"""
Enumerations for Reddit API parameters.

These enums provide type-safe options for listing sort order and time
filtering, ensuring only valid values are sent to the Reddit API.
"""

from enum import StrEnum


class RedditSort(StrEnum):
    """
    Sort order for a subreddit listing.

    - HOT: Posts currently trending based on score and recency
    - NEW: Most recently submitted posts
    - TOP: Highest-scored posts (filtered by :class:`RedditTimeFilter`)
    - RISING: Posts gaining momentum rapidly
    - CONTROVERSIAL: Posts with high engagement on both sides (filtered by
      :class:`RedditTimeFilter`)
    """

    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"
    CONTROVERSIAL = "controversial"


class RedditTimeFilter(StrEnum):
    """
    Time window for filtering ``TOP`` and ``CONTROVERSIAL`` listings.

    Only applies when ``sort`` is :attr:`RedditSort.TOP` or
    :attr:`RedditSort.CONTROVERSIAL`. Ignored for all other sort orders.

    - HOUR: Past hour
    - DAY: Past 24 hours
    - WEEK: Past 7 days
    - MONTH: Past 30 days
    - YEAR: Past 365 days
    - ALL: All time
    """

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"
