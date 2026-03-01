"""
Pydantic models for Unsplash API responses.

Unsplash distinguishes between abbreviated photo objects (returned by search
and list endpoints) and full photo objects (returned by detail and random
endpoints). All optional fields correspond to data only present in full responses.

All models are immutable by default and fully typed.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UnsplashPhotoUrls(BaseModel):
    """Photo URLs at various resolutions provided by the Unsplash CDN."""

    raw: str = Field(description="Original, unprocessed image URL")
    full: str = Field(description="Full quality JPEG")
    regular: str = Field(description="1080px wide JPEG")
    small: str = Field(description="400px wide JPEG")
    thumb: str = Field(description="200px wide JPEG")


class UnsplashPhotoLinks(BaseModel):
    """Hypermedia links associated with a photo."""

    self: str = Field(description="API URL for this photo")
    html: str = Field(description="Unsplash web page for this photo")
    download: str = Field(description="Unsplash download page")
    download_location: str = Field(
        description="API endpoint to call when triggering a download (required for attribution)"
    )


class UnsplashUserProfileImage(BaseModel):
    """Photographer's profile image at different sizes."""

    small: str
    medium: str
    large: str


class UnsplashUserLinks(BaseModel):
    """Hypermedia links for a user."""

    self: str
    html: str
    photos: str
    portfolio: str | None = None


class UnsplashUser(BaseModel):
    """Photographer who uploaded the photo."""

    id: str
    username: str
    name: str
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    location: str | None = None
    portfolio_url: str | None = None
    instagram_username: str | None = None
    twitter_username: str | None = None
    total_collections: int = 0
    profile_image: UnsplashUserProfileImage | None = None
    links: UnsplashUserLinks | None = None


class UnsplashExif(BaseModel):
    """Camera EXIF metadata. Only present on full photo responses."""

    make: str | None = None
    model: str | None = None
    name: str | None = None
    exposure_time: str | None = None
    aperture: str | None = None
    focal_length: str | None = None
    iso: int | None = None


class UnsplashPosition(BaseModel):
    """Geographic coordinates."""

    latitude: float | None = None
    longitude: float | None = None


class UnsplashLocation(BaseModel):
    """Location metadata for a photo. Only present on full photo responses."""

    city: str | None = None
    country: str | None = None
    position: UnsplashPosition | None = None


class UnsplashTag(BaseModel):
    """A descriptive tag on a photo."""

    title: str


class UnsplashPhoto(BaseModel):
    """
    A photo from Unsplash.

    Fields with ``| None`` defaults correspond to data only present in full
    photo responses (from ``GET /photos/:id`` or ``GET /photos/random``).
    Search results return abbreviated objects with these fields absent.

    Example:
        photo = unsplash.photo("abc123")
        data = unsplash.download(photo)
    """

    id: str
    created_at: datetime
    updated_at: datetime | None = None
    width: int
    height: int
    color: str | None = None
    blur_hash: str | None = None
    description: str | None = None
    alt_description: str | None = None
    urls: UnsplashPhotoUrls
    links: UnsplashPhotoLinks
    user: UnsplashUser
    # Fields only present in full photo responses
    downloads: int | None = None
    public_domain: bool | None = None
    exif: UnsplashExif | None = None
    location: UnsplashLocation | None = None
    tags: list[UnsplashTag] = Field(default_factory=list)

    @property
    def resolution(self) -> str:
        """Formatted resolution string, e.g. ``'3840x2160'``."""
        return f"{self.width}x{self.height}"

    @property
    def aspect_ratio(self) -> float:
        """Width-to-height ratio, rounded to two decimal places."""
        return round(self.width / self.height, 2)


class UnsplashSearchResult(BaseModel):
    """
    Paginated search results from ``GET /search/photos``.

    Example:
        result = unsplash.search(UnsplashSearchParams(query="mountains"))
        print(result.total)         # total matching photos
        print(result.total_pages)   # number of pages available
        for photo in result.results:
            print(photo.id)
    """

    total: int = Field(description="Total number of photos matching the query")
    total_pages: int = Field(description="Total number of pages available")
    results: list[UnsplashPhoto] = Field(description="Photos on this page")
