"""
Pydantic models for Wallhaven API responses.

All API responses are parsed into typed models for type safety
and easier data access.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Avatar(BaseModel):
    """User avatar at different sizes."""

    large: str | None = Field(default=None, description="200px avatar URL")
    medium: str | None = Field(default=None, description="128px avatar URL")
    small: str | None = Field(default=None, description="32px avatar URL")
    tiny: str | None = Field(default=None, description="20px avatar URL")

    @classmethod
    def from_dict(cls, data: dict[str, str] | None) -> "Avatar | None":
        if data is None:
            return None
        return cls(
            large=data.get("200px"),
            medium=data.get("128px"),
            small=data.get("32px"),
            tiny=data.get("20px"),
        )


class Uploader(BaseModel):
    """Information about the wallpaper uploader."""

    username: str
    group: str
    avatar: Avatar | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Uploader":
        return cls(
            username=data["username"],
            group=data["group"],
            avatar=Avatar.from_dict(data.get("avatar")),
        )


class Thumbnails(BaseModel):
    """Thumbnail URLs at different sizes."""

    large: str
    original: str
    small: str


class Tag(BaseModel):
    """Information about a tag."""

    id: int
    name: str
    alias: str | None = None
    category_id: int | None = None
    category: str | None = None
    purity: str | None = None
    created_at: datetime | None = None


class Wallpaper(BaseModel):
    """Single wallpaper information."""

    id: str
    url: str
    short_url: str
    views: int
    favorites: int
    source: str
    purity: str
    category: str
    dimension_x: int
    dimension_y: int
    resolution: str
    ratio: str
    file_size: int
    file_type: str
    created_at: datetime
    colors: list[str]
    path: str
    thumbs: Thumbnails
    tags: list[Tag] = Field(default_factory=list)
    uploader: Uploader | None = None


class QueryInfo(BaseModel):
    """Information about a resolved search query."""

    id: int
    tag: str


class PaginationMeta(BaseModel):
    """Pagination metadata for search results."""

    current_page: int
    last_page: int
    per_page: int
    total: int
    query: str | QueryInfo | None = None
    seed: str | None = None


class SearchResult(BaseModel):
    """Search results with pagination metadata."""

    data: list[Wallpaper]
    meta: PaginationMeta


class UserSettings(BaseModel):
    """User account settings."""

    thumb_size: str
    per_page: str
    purity: list[str]
    categories: list[str]
    resolutions: list[str]
    aspect_ratios: list[str]
    toplist_range: str
    tag_blacklist: list[str]
    user_blacklist: list[str]


class Collection(BaseModel):
    """User collection information."""

    id: int
    label: str
    views: int
    public: int
    count: int


class CollectionListing(BaseModel):
    """Collection listing response (similar to search results)."""

    data: list[Wallpaper]
    meta: PaginationMeta
