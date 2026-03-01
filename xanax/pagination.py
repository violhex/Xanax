"""
Pagination utilities for search results.

Provides helpers for navigating through paginated results
and working with pagination metadata.
"""

from xanax.models import PaginationMeta


class PaginationHelper:
    """
    Helper class for navigating paginated search results.

    Wraps :class:`~xanax.models.PaginationMeta` and exposes clean properties
    and methods for driving pagination loops.

    Example:
        results = client.search(params)
        helper = PaginationHelper(results.meta)

        if helper.has_next:
            next_params = params.with_page(helper.next_page_number())
            next_results = client.search(next_params)
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
        """Return the next page number, or None if already on the last page."""
        if self.has_next:
            return self._meta.current_page + 1
        return None

    def previous_page_number(self) -> int | None:
        """Return the previous page number, or None if already on the first page."""
        if self.has_previous:
            return self._meta.current_page - 1
        return None
