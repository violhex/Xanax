"""
Search parameter handling for Wallhaven API.

Provides a structured SearchParams model with validation
to ensure only valid queries reach the API.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from xanax.enums import Category, Color, FileType, Order, Purity, Ratio, Sort, TopRange
from xanax.errors import ValidationError


class SearchParams(BaseModel):
    """
    Parameters for wallpaper search.

    This model validates all search parameters and ensures
    only valid combinations are used.

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
        default_factory=lambda: [Category.GENERAL],
        description="Categories to search",
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
        description="Exact resolutions to search for",
    )
    ratios: list[str] = Field(
        default_factory=list,
        description="Aspect ratios to search for",
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

        if self.seed is not None and self.sorting != Sort.RANDOM:
            pass

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
        Create a new SearchParams with updated page number.

        Args:
            page: New page number.

        Returns:
            New SearchParams instance with updated page.
        """
        return SearchParams(
            query=self.query,
            categories=self.categories,
            purity=self.purity,
            sorting=self.sorting,
            order=self.order,
            top_range=self.top_range,
            resolutions=self.resolutions,
            ratios=self.ratios,
            colors=self.colors,
            page=page,
            seed=self.seed,
            file_type=self.file_type,
            like=self.like,
        )

    def with_seed(self, seed: str) -> "SearchParams":
        """
        Create a new SearchParams with updated seed.

        Args:
            seed: New seed value (6 alphanumeric characters).

        Returns:
            New SearchParams instance with updated seed.
        """
        return SearchParams(
            query=self.query,
            categories=self.categories,
            purity=self.purity,
            sorting=self.sorting,
            order=self.order,
            top_range=self.top_range,
            resolutions=self.resolutions,
            ratios=self.ratios,
            colors=self.colors,
            page=self.page,
            seed=seed,
            file_type=self.file_type,
            like=self.like,
        )


class Resolution:
    """Helper class for validating wallpaper resolutions."""

    @staticmethod
    def validate(resolution: str) -> bool:
        parts = resolution.lower().split("x")
        if len(parts) != 2:
            return False

        try:
            width = int(parts[0])
            height = int(parts[1])
            return width >= 1 and height >= 1
        except ValueError:
            return False
