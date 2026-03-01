"""
Tests for Unsplash Pydantic models.
"""

import pytest

from xanax.sources.unsplash.models import (
    UnsplashExif,
    UnsplashLocation,
    UnsplashPhoto,
    UnsplashPhotoLinks,
    UnsplashPhotoUrls,
    UnsplashPosition,
    UnsplashSearchResult,
    UnsplashTag,
    UnsplashUser,
    UnsplashUserProfileImage,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

PHOTO_URLS = {
    "raw": "https://images.unsplash.com/photo-1?ixid=raw",
    "full": "https://images.unsplash.com/photo-1?q=75&fm=jpg",
    "regular": "https://images.unsplash.com/photo-1?q=75&fm=jpg&w=1080",
    "small": "https://images.unsplash.com/photo-1?q=75&fm=jpg&w=400",
    "thumb": "https://images.unsplash.com/photo-1?q=75&fm=jpg&w=200",
}

PHOTO_LINKS = {
    "self": "https://api.unsplash.com/photos/abc123",
    "html": "https://unsplash.com/photos/abc123",
    "download": "https://unsplash.com/photos/abc123/download",
    "download_location": "https://api.unsplash.com/photos/abc123/download",
}

USER_DATA = {
    "id": "user1",
    "username": "photographer",
    "name": "Jane Doe",
    "total_collections": 0,
}

PHOTO_DATA = {
    "id": "abc123",
    "created_at": "2023-06-15T12:00:00Z",
    "width": 3840,
    "height": 2160,
    "urls": PHOTO_URLS,
    "links": PHOTO_LINKS,
    "user": USER_DATA,
}


# ---------------------------------------------------------------------------
# UnsplashPhotoUrls
# ---------------------------------------------------------------------------


class TestUnsplashPhotoUrls:
    def test_all_fields(self) -> None:
        urls = UnsplashPhotoUrls(**PHOTO_URLS)
        assert urls.raw == PHOTO_URLS["raw"]
        assert urls.full == PHOTO_URLS["full"]
        assert urls.regular == PHOTO_URLS["regular"]
        assert urls.small == PHOTO_URLS["small"]
        assert urls.thumb == PHOTO_URLS["thumb"]


# ---------------------------------------------------------------------------
# UnsplashPhotoLinks
# ---------------------------------------------------------------------------


class TestUnsplashPhotoLinks:
    def test_all_fields(self) -> None:
        links = UnsplashPhotoLinks(**PHOTO_LINKS)
        assert links.self == PHOTO_LINKS["self"]
        assert links.html == PHOTO_LINKS["html"]
        assert links.download == PHOTO_LINKS["download"]
        assert links.download_location == PHOTO_LINKS["download_location"]


# ---------------------------------------------------------------------------
# UnsplashUser
# ---------------------------------------------------------------------------


class TestUnsplashUser:
    def test_minimal(self) -> None:
        user = UnsplashUser(**USER_DATA)
        assert user.id == "user1"
        assert user.username == "photographer"
        assert user.name == "Jane Doe"

    def test_optional_fields_default_none(self) -> None:
        user = UnsplashUser(**USER_DATA)
        assert user.bio is None
        assert user.location is None
        assert user.portfolio_url is None
        assert user.instagram_username is None
        assert user.twitter_username is None
        assert user.profile_image is None
        assert user.links is None

    def test_total_collections_default(self) -> None:
        user = UnsplashUser(**USER_DATA)
        assert user.total_collections == 0

    def test_with_profile_image(self) -> None:
        user = UnsplashUser(
            **USER_DATA,
            profile_image={"small": "s.jpg", "medium": "m.jpg", "large": "l.jpg"},
        )
        assert isinstance(user.profile_image, UnsplashUserProfileImage)
        assert user.profile_image.small == "s.jpg"


# ---------------------------------------------------------------------------
# UnsplashExif
# ---------------------------------------------------------------------------


class TestUnsplashExif:
    def test_all_optional(self) -> None:
        exif = UnsplashExif()
        assert exif.make is None
        assert exif.model is None
        assert exif.iso is None

    def test_with_data(self) -> None:
        exif = UnsplashExif(make="Canon", model="EOS 5D", iso=100)
        assert exif.make == "Canon"
        assert exif.iso == 100


# ---------------------------------------------------------------------------
# UnsplashLocation
# ---------------------------------------------------------------------------


class TestUnsplashLocation:
    def test_all_optional(self) -> None:
        loc = UnsplashLocation()
        assert loc.city is None
        assert loc.country is None
        assert loc.position is None

    def test_with_position(self) -> None:
        loc = UnsplashLocation(
            city="Montreal",
            country="Canada",
            position={"latitude": 45.5, "longitude": -73.6},
        )
        assert loc.city == "Montreal"
        assert isinstance(loc.position, UnsplashPosition)
        assert loc.position.latitude == 45.5


# ---------------------------------------------------------------------------
# UnsplashTag
# ---------------------------------------------------------------------------


class TestUnsplashTag:
    def test_title(self) -> None:
        tag = UnsplashTag(title="mountain")
        assert tag.title == "mountain"


# ---------------------------------------------------------------------------
# UnsplashPhoto
# ---------------------------------------------------------------------------


class TestUnsplashPhoto:
    def test_minimal(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert photo.id == "abc123"
        assert photo.width == 3840
        assert photo.height == 2160

    def test_optional_fields_default(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert photo.color is None
        assert photo.blur_hash is None
        assert photo.description is None
        assert photo.alt_description is None
        assert photo.downloads is None
        assert photo.public_domain is None
        assert photo.exif is None
        assert photo.location is None
        assert photo.tags == []

    def test_resolution_property(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert photo.resolution == "3840x2160"

    def test_aspect_ratio_property(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert photo.aspect_ratio == round(3840 / 2160, 2)

    def test_with_optional_fields(self) -> None:
        data = {
            **PHOTO_DATA,
            "description": "A mountain landscape",
            "downloads": 1500,
            "public_domain": False,
            "tags": [{"title": "mountain"}, {"title": "landscape"}],
            "exif": {"make": "Sony", "iso": 200},
            "location": {"city": "Denver", "country": "USA"},
        }
        photo = UnsplashPhoto(**data)
        assert photo.description == "A mountain landscape"
        assert photo.downloads == 1500
        assert photo.public_domain is False
        assert len(photo.tags) == 2
        assert photo.tags[0].title == "mountain"
        assert isinstance(photo.exif, UnsplashExif)
        assert photo.exif.make == "Sony"
        assert isinstance(photo.location, UnsplashLocation)
        assert photo.location.city == "Denver"

    def test_nested_urls_and_links_parsed(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert isinstance(photo.urls, UnsplashPhotoUrls)
        assert isinstance(photo.links, UnsplashPhotoLinks)
        assert photo.links.download_location == PHOTO_LINKS["download_location"]

    def test_user_parsed(self) -> None:
        photo = UnsplashPhoto(**PHOTO_DATA)
        assert isinstance(photo.user, UnsplashUser)
        assert photo.user.username == "photographer"

    def test_datetime_parsing(self) -> None:
        from datetime import datetime

        photo = UnsplashPhoto(**PHOTO_DATA)
        assert isinstance(photo.created_at, datetime)
        assert photo.created_at.tzinfo is not None or photo.created_at.year == 2023

    def test_invalid_missing_required_field(self) -> None:
        import pydantic

        data = {k: v for k, v in PHOTO_DATA.items() if k != "urls"}
        with pytest.raises(pydantic.ValidationError):
            UnsplashPhoto(**data)


# ---------------------------------------------------------------------------
# UnsplashSearchResult
# ---------------------------------------------------------------------------


class TestUnsplashSearchResult:
    def test_fields(self) -> None:
        result = UnsplashSearchResult(
            total=100,
            total_pages=5,
            results=[UnsplashPhoto(**PHOTO_DATA)],
        )
        assert result.total == 100
        assert result.total_pages == 5
        assert len(result.results) == 1
        assert result.results[0].id == "abc123"

    def test_empty_results(self) -> None:
        result = UnsplashSearchResult(total=0, total_pages=0, results=[])
        assert result.results == []
