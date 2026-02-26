"""
Pagination utilities for search results.

Provides helpers for navigating through paginated results
and working with pagination metadata.
"""

from xanax.models import PaginationMeta, SearchResult


class PaginationHelper:
    """
    Helper class for navigating paginated search results.

    This class provides utility methods for working with pagination
    data from search results.
    """

    def __init__(self, meta: PaginationMeta) -> None:
        self._meta = meta

    @property
    def current_page(self) -> int:
        """Current page number (1-indexed)."""
        return self._meta.current_page

    @property
    def last_page(self) -> int:
        """Last available page number."""
        return self._meta.last_page

    @property
    def per_page(self) -> int:
        """Number of results per page."""
        return self._meta.per_page

    @property
    def total(self) -> int:
        """Total number of results across all pages."""
        return self._meta.total

    @property
    def has_next(self) -> bool:
        """Check if there is a next page available."""
        return self._meta.current_page < self._meta.last_page

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self._meta.current_page > 1

    @property
    def seed(self) -> str | None:
        """Seed value for random sorting (used for consistent pagination)."""
        return self._meta.seed

    def next_page_number(self) -> int | None:
        """Get the next page number, or None if at last page."""
        if self.has_next:
            return self._meta.current_page + 1
        return None

    def previous_page_number(self) -> int | None:
        """Get the previous page number, or None if at first page."""
        if self.has_previous:
            return self._meta.current_page - 1
        return None


def has_next_page(result: SearchResult) -> bool:
    """Check if there are more pages available."""
    return result.meta.current_page < result.meta.last_page


def get_next_page(result: SearchResult) -> int | None:
    """Get the next page number, or None if at the last page."""
    if has_next_page(result):
        return result.meta.current_page + 1
    return None


def get_total_pages(result: SearchResult) -> int:
    """Get the total number of pages."""
    return result.meta.last_page
