"""
Tests for Wallhaven models.
"""

from xanax.sources.wallhaven.enums import Category, Purity
from xanax.sources.wallhaven.models import (
    Avatar,
    Collection,
    PaginationMeta,
    QueryInfo,
    Tag,
    Thumbnails,
    Uploader,
    UserSettings,
    Wallpaper,
)


class TestAvatar:
    def test_from_dict_with_data(self):
        data = {
            "200px": "https://example.com/avatar/200.png",
            "128px": "https://example.com/avatar/128.png",
            "32px": "https://example.com/avatar/32.png",
            "20px": "https://example.com/avatar/20.png",
        }
        avatar = Avatar.from_dict(data)
        assert avatar.large == "https://example.com/avatar/200.png"
        assert avatar.medium == "https://example.com/avatar/128.png"
        assert avatar.small == "https://example.com/avatar/32.png"
        assert avatar.tiny == "https://example.com/avatar/20.png"

    def test_from_dict_none(self):
        avatar = Avatar.from_dict(None)
        assert avatar is None


class TestThumbnails:
    def test_from_dict(self):
        data = {
            "large": "https://th.wallhaven.cc/lg/94/94x38z.jpg",
            "original": "https://th.wallhaven.cc/orig/94/94x38z.jpg",
            "small": "https://th.wallhaven.cc/small/94/94x38z.jpg",
        }
        thumbs = Thumbnails(**data)
        assert thumbs.large == "https://th.wallhaven.cc/lg/94/94x38z.jpg"
        assert thumbs.original == "https://th.wallhaven.cc/orig/94/94x38z.jpg"
        assert thumbs.small == "https://th.wallhaven.cc/small/94/94x38z.jpg"


class TestTag:
    def test_full_tag(self):
        data = {
            "id": 1,
            "name": "anime",
            "alias": "Chinese cartoons",
            "category_id": 1,
            "category": "Anime & Manga",
            "purity": "sfw",
            "created_at": "2015-01-16 02:06:45",
        }
        tag = Tag(**data)
        assert tag.id == 1
        assert tag.name == "anime"
        assert tag.alias == "Chinese cartoons"
        assert tag.purity == "sfw"


class TestUploader:
    def test_full_uploader(self):
        data = {
            "username": "test-user",
            "group": "User",
            "avatar": {
                "200px": "https://wallhaven.cc/images/user/avatar/200/11.png",
                "128px": "https://wallhaven.cc/images/user/avatar/128/11.png",
            },
        }
        uploader = Uploader.from_dict(data)
        assert uploader.username == "test-user"
        assert uploader.group == "User"
        assert uploader.avatar is not None
        assert uploader.avatar.large == "https://wallhaven.cc/images/user/avatar/200/11.png"


class TestWallpaper:
    def test_full_wallpaper(self):
        data = {
            "id": "94x38z",
            "url": "https://wallhaven.cc/w/94x38z",
            "short_url": "http://whvn.cc/94x38z",
            "views": 12,
            "favorites": 0,
            "source": "",
            "purity": "sfw",
            "category": "anime",
            "dimension_x": 6742,
            "dimension_y": 3534,
            "resolution": "6742x3534",
            "ratio": "1.91",
            "file_size": 5070446,
            "file_type": "image/jpeg",
            "created_at": "2018-10-31 01:23:10",
            "colors": ["#000000", "#abbcda"],
            "path": "https://w.wallhaven.cc/full/94/wallhaven-94x38z.jpg",
            "thumbs": {
                "large": "https://th.wallhaven.cc/lg/94/94x38z.jpg",
                "original": "https://th.wallhaven.cc/orig/94/94x38z.jpg",
                "small": "https://th.wallhaven.cc/small/94/94x38z.jpg",
            },
            "tags": [
                {
                    "id": 1,
                    "name": "anime",
                    "alias": "Chinese cartoons",
                    "category_id": 1,
                    "category": "Anime & Manga",
                    "purity": "sfw",
                    "created_at": "2015-01-16 02:06:45",
                }
            ],
            "uploader": {
                "username": "test-user",
                "group": "User",
                "avatar": {
                    "200px": "https://wallhaven.cc/images/user/avatar/200/11.png",
                },
            },
        }
        wallpaper = Wallpaper(**data)
        assert wallpaper.id == "94x38z"
        assert wallpaper.resolution == "6742x3534"
        assert wallpaper.purity == "sfw"
        assert len(wallpaper.tags) == 1
        assert wallpaper.tags[0].name == "anime"


class TestPaginationMeta:
    def test_basic_pagination(self):
        data = {
            "current_page": 1,
            "last_page": 10,
            "per_page": 24,
            "total": 240,
        }
        meta = PaginationMeta(**data)
        assert meta.current_page == 1
        assert meta.last_page == 10
        assert meta.per_page == 24
        assert meta.total == 240

    def test_pagination_with_query(self):
        data = {
            "current_page": 1,
            "last_page": 10,
            "per_page": 24,
            "total": 240,
            "query": "anime",
            "seed": "abc123",
        }
        meta = PaginationMeta(**data)
        assert meta.query == "anime"
        assert meta.seed == "abc123"

    def test_pagination_with_tag_query(self):
        data = {
            "current_page": 1,
            "last_page": 10,
            "per_page": 24,
            "total": 240,
            "query": {"id": 1, "tag": "anime"},
        }
        meta = PaginationMeta(**data)
        assert isinstance(meta.query, QueryInfo)
        assert meta.query.id == 1
        assert meta.query.tag == "anime"


class TestUserSettings:
    def test_full_settings(self):
        data = {
            "thumb_size": "orig",
            "per_page": "24",
            "purity": ["sfw", "sketchy", "nsfw"],
            "categories": ["general", "anime", "people"],
            "resolutions": ["1920x1080", "2560x1440"],
            "aspect_ratios": ["16x9"],
            "toplist_range": "6M",
            "tag_blacklist": ["blacklist tag"],
            "user_blacklist": [],
        }
        settings = UserSettings(**data)
        assert settings.thumb_size == "orig"
        assert Purity.SFW.value in settings.purity
        assert Category.GENERAL.value in settings.categories


class TestCollection:
    def test_basic_collection(self):
        data = {
            "id": 15,
            "label": "Default",
            "views": 38,
            "public": 1,
            "count": 10,
        }
        collection = Collection(**data)
        assert collection.id == 15
        assert collection.label == "Default"
        assert collection.public is True

    def test_collection_public_false(self):
        data = {
            "id": 16,
            "label": "Private",
            "views": 0,
            "public": 0,
            "count": 5,
        }
        collection = Collection(**data)
        assert collection.public is False
