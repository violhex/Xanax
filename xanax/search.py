"""
Search parameter handling for Wallhaven API.

Provides a structured SearchParams model with validation
to ensure only valid queries reach the API.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from xanax.enums import Category, Color, FileType, Order, Purity, Ratio, Resolution, Sort, TopRange
from xanax.errors import ValidationError


class SearchParams(BaseModel):
    """
    Parameters for wallpaper search.

    This model validates all search parameters and ensures
    only valid combinations are used. Invalid combinations
    raise :class:`~xanax.errors.ValidationError` immediately, before
    any network request is made.

    The default ``categories`` includes all three (general, anime, people),
    matching Wallhaven's own default search behaviour.

    Example:
        params = SearchParams(
            query="+anime -sketch",
            categories=[Category.ANIME],
            purity=[Purity.SFW],
            sorting=Sort.TOPLIST,
            top_range=TopRange.ONE_MONTH,
        )
    """

    query: str | None = Field(default=None, description="Search query string")
    categories: list[Category] = Field(
        default_factory=lambda: list(Category),
        description="Categories to search (default: all three)",
    )
    purity: list[Purity] = Field(
        default_factory=lambda: [Purity.SFW],
        description="Purity levels to include",
    )
    sorting: Sort = Field(
        default=Sort.DATE_ADDED,
        description="How to sort results",
    )
    order: Order = Field(
        default=Order.DESC,
        description="Sort order direction",
    )
    top_range: TopRange | None = Field(
        default=None,
        description="Time range for toplist sorting",
    )
    resolutions: list[str] = Field(
        default_factory=list,
        description="Exact resolutions to filter by (e.g., '1920x1080')",
    )
    ratios: list[str] = Field(
        default_factory=list,
        description="Aspect ratios to filter by (e.g., '16x9' or '16:9')",
    )
    colors: list[Color] = Field(
        default_factory=list,
        description="Colors to search for",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
    )
    seed: str | None = Field(
        default=None,
        description="Seed for random sorting (6 alphanumeric characters)",
    )
    file_type: FileType | None = Field(
        default=None,
        description="Filter by file type (png or jpg)",
    )
    like: str | None = Field(
        default=None,
        description="Find wallpapers with similar tags to this wallpaper ID",
    )

    @field_validator("resolutions", mode="before")
    @classmethod
    def validate_resolutions(cls, v: list[str] | str | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]

        for res in v:
            if not Resolution.validate(res):
                raise ValidationError(
                    f"Invalid resolution format: {res}. "
                    "Expected format: WIDTHxHEIGHT (e.g., 1920x1080)"
                )

        return v

    @field_validator("ratios", mode="before")
    @classmethod
    def validate_ratios(cls, v: list[str] | str | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]

        for ratio in v:
            if not Ratio.validate(ratio):
                raise ValidationError(
                    f"Invalid ratio format: {ratio}. "
                    "Expected format: WIDTH:HEIGHT or WIDTHxHEIGHT (e.g., 16:9 or 16x9)"
                )

        return v

    @field_validator("seed")
    @classmethod
    def validate_seed(cls, v: str | None) -> str | None:
        if v is not None and not (len(v) == 6 and v.isalnum()):
            raise ValidationError(
                f"Invalid seed: {v}. Seed must be exactly 6 alphanumeric characters."
            )
        return v

    def model_post_init(self, __context: Any) -> None:
        if self.top_range is not None and self.sorting != Sort.TOPLIST:
            raise ValidationError(
                "top_range can only be used when sorting is set to 'toplist'. "
                f"Current sorting: {self.sorting.value}"
            )

    def to_query_params(self) -> dict[str, Any]:
        """
        Convert parameters to API query parameters.

        Returns:
            Dictionary of query parameters for the API request.
        """
        params: dict[str, Any] = {}

        if self.query:
            params["q"] = self.query

        if self.categories:
            cats = "".join("1" if c in self.categories else "0" for c in Category)
            params["categories"] = cats

        if self.purity:
            purity_str = "".join("1" if p in self.purity else "0" for p in Purity)
            params["purity"] = purity_str

        params["sorting"] = self.sorting.value
        params["order"] = self.order.value

        if self.top_range:
            params["topRange"] = self.top_range.value

        if self.resolutions:
            params["resolutions"] = ",".join(self.resolutions)

        if self.ratios:
            params["ratios"] = ",".join(self.ratios)

        if self.colors:
            params["colors"] = ",".join(c.value for c in self.colors)

        if self.page > 1:
            params["page"] = self.page

        if self.seed:
            params["seed"] = self.seed

        if self.file_type:
            params["type"] = self.file_type.value

        if self.like:
            params["like"] = self.like

        return params

    def with_page(self, page: int) -> "SearchParams":
        """
        Return a new SearchParams with the page number updated.

        Args:
            page: New page number.

        Returns:
            New SearchParams instance with the page updated and all other fields preserved.
        """
        return SearchParams(**{**self.model_dump(mode="python"), "page": page})

    def with_seed(self, seed: str) -> "SearchParams":
        """
        Return a new SearchParams with the seed updated.

        Args:
            seed: New seed value (6 alphanumeric characters).

        Returns:
            New SearchParams instance with the seed updated and all other fields preserved.
        """
        return SearchParams(**{**self.model_dump(mode="python"), "seed": seed})
