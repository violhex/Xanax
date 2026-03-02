"""
Search and filter parameter models for the Unsplash API.

These models validate all parameters before any request is made, so
invalid combinations raise :class:`~xanax.errors.ValidationError`
immediately rather than producing a confusing API error.
"""

from typing import Any

from pydantic import BaseModel, Field

from xanax.sources.unsplash.enums import (
    UnsplashColor,
    UnsplashContentFilter,
    UnsplashOrderBy,
    UnsplashOrientation,
)


class UnsplashSearchParams(BaseModel):
    """
    Parameters for ``GET /search/photos``.

    The ``query`` field is required. All other fields have sensible defaults
    matching the Unsplash API's own defaults.

    Example:
        .. code-block:: python

            params = UnsplashSearchParams(
                query="mountains",
                orientation=UnsplashOrientation.LANDSCAPE,
                color=UnsplashColor.BLUE,
                order_by=UnsplashOrderBy.LATEST,
                per_page=30,
            )
            result = unsplash.search(params)

    Args:
        query: Search terms. Required.
        page: Page number (1-indexed). Default is 1.
        per_page: Results per page. Min 1, max 30. Default is 10.
        order_by: How to sort results. Default is ``RELEVANT``.
        collections: Collection IDs to narrow the search (comma-joined internally).
        content_filter: Content safety level. Default is ``LOW``.
        color: Filter by dominant color.
        orientation: Filter by photo orientation.
    """

    query: str = Field(description="Search terms")
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=10, ge=1, le=30, description="Results per page (max 30)")
    order_by: UnsplashOrderBy = Field(
        default=UnsplashOrderBy.RELEVANT,
        description="Sort order for results",
    )
    collections: list[str] = Field(
        default_factory=list,
        description="Collection IDs to restrict search to",
    )
    content_filter: UnsplashContentFilter = Field(
        default=UnsplashContentFilter.LOW,
        description="Content safety filter level",
    )
    color: UnsplashColor | None = Field(
        default=None,
        description="Filter by dominant color",
    )
    orientation: UnsplashOrientation | None = Field(
        default=None,
        description="Filter by photo orientation",
    )

    def to_query_params(self) -> dict[str, Any]:
        """
        Serialize parameters to a dict suitable for use as HTTP query params.

        Returns:
            Dictionary of query parameters for the API request.
        """
        params: dict[str, Any] = {"q": self.query}

        if self.page > 1:
            params["page"] = self.page

        params["per_page"] = self.per_page
        params["order_by"] = self.order_by.value

        if self.collections:
            params["collections"] = ",".join(self.collections)

        if self.content_filter != UnsplashContentFilter.LOW:
            params["content_filter"] = self.content_filter.value

        if self.color is not None:
            params["color"] = self.color.value

        if self.orientation is not None:
            params["orientation"] = self.orientation.value

        return params

    def with_page(self, page: int) -> "UnsplashSearchParams":
        """
        Return a new :class:`UnsplashSearchParams` with the page number updated.

        Args:
            page: New page number.

        Returns:
            New instance with ``page`` updated and all other fields preserved.
        """
        return UnsplashSearchParams(**{**self.model_dump(mode="python"), "page": page})


class UnsplashRandomParams(BaseModel):
    """
    Parameters for ``GET /photos/random``.

    All fields are optional. With no parameters, a completely random photo
    is returned. Parameters narrow the pool of eligible photos.

    Note:
        ``collections`` and ``topics`` cannot be combined with ``query``
        in the same request. The API will return an error if both are provided.

    Example:
        .. code-block:: python

            params = UnsplashRandomParams(
                query="forest",
                orientation=UnsplashOrientation.LANDSCAPE,
            )
            photo = unsplash.random(params)

    Args:
        collections: Collection IDs to restrict the random pool to.
        topics: Topic IDs to restrict the random pool to.
        username: Restrict to photos from a specific user.
        query: Restrict to photos matching a search term.
        orientation: Filter by photo orientation.
        content_filter: Content safety level. Default is ``LOW``.
    """

    collections: list[str] = Field(
        default_factory=list,
        description="Collection IDs to restrict the random pool to",
    )
    topics: list[str] = Field(
        default_factory=list,
        description="Topic IDs to restrict the random pool to",
    )
    username: str | None = Field(
        default=None,
        description="Restrict to photos from this user",
    )
    query: str | None = Field(
        default=None,
        description="Restrict to photos matching this search term",
    )
    orientation: UnsplashOrientation | None = Field(
        default=None,
        description="Filter by photo orientation",
    )
    content_filter: UnsplashContentFilter = Field(
        default=UnsplashContentFilter.LOW,
        description="Content safety filter level",
    )

    def to_query_params(self) -> dict[str, Any]:
        """
        Serialize parameters to a dict suitable for use as HTTP query params.

        Returns:
            Dictionary of query parameters for the API request.
        """
        params: dict[str, Any] = {}

        if self.collections:
            params["collections"] = ",".join(self.collections)

        if self.topics:
            params["topics"] = ",".join(self.topics)

        if self.username is not None:
            params["username"] = self.username

        if self.query is not None:
            params["query"] = self.query

        if self.orientation is not None:
            params["orientation"] = self.orientation.value

        if self.content_filter != UnsplashContentFilter.LOW:
            params["content_filter"] = self.content_filter.value

        return params
