"""
Tests for Reddit Pydantic models.
"""

from datetime import datetime

from xanax.enums import MediaType
from xanax.sources.reddit.models import RedditGalleryItem, RedditListing, RedditPost

# ---------------------------------------------------------------------------
# Shared raw API data fixtures
# ---------------------------------------------------------------------------

IMAGE_POST_DATA = {
    "id": "img001",
    "name": "t3_img001",
    "title": "Beautiful mountain",
    "subreddit": "EarthPorn",
    "author": "photographer",
    "score": 9500,
    "url": "https://i.redd.it/mountain.jpg",
    "url_overridden_by_dest": "https://i.redd.it/mountain.jpg",
    "domain": "i.redd.it",
    "post_hint": "image",
    "is_video": False,
    "is_gallery": False,
    "is_self": False,
    "over_18": False,
    "permalink": "/r/EarthPorn/comments/img001/beautiful_mountain/",
    "created_utc": 1700000000.0,
    "thumbnail": "https://b.thumbs.redditmedia.com/thumb.jpg",
    "preview": {
        "images": [
            {
                "source": {
                    "url": "https://preview.redd.it/mountain.jpg",
                    "width": 3840,
                    "height": 2160,
                },
            }
        ]
    },
}

VIDEO_POST_DATA = {
    "id": "vid001",
    "name": "t3_vid001",
    "title": "Timelapse sunset",
    "subreddit": "videos",
    "author": "filmmaker",
    "score": 4200,
    "url": "https://v.redd.it/vid001",
    "domain": "v.redd.it",
    "post_hint": "hosted:video",
    "is_video": True,
    "is_gallery": False,
    "is_self": False,
    "over_18": False,
    "permalink": "/r/videos/comments/vid001/timelapse_sunset/",
    "created_utc": 1700001000.0,
    "thumbnail": "https://b.thumbs.redditmedia.com/thumb.jpg",
    "secure_media": {
        "reddit_video": {
            "fallback_url": "https://v.redd.it/vid001/DASH_480.mp4?source=fallback",
            "width": 1920,
            "height": 1080,
            "duration": 60,
            "is_gif": False,
        }
    },
    "media": None,
}

GIF_POST_DATA = {
    "id": "gif001",
    "name": "t3_gif001",
    "title": "Cute cat loop",
    "subreddit": "gifs",
    "author": "catperson",
    "score": 11000,
    "url": "https://v.redd.it/gif001",
    "domain": "v.redd.it",
    "post_hint": "hosted:video",
    "is_video": True,
    "is_gallery": False,
    "is_self": False,
    "over_18": False,
    "permalink": "/r/gifs/comments/gif001/cute_cat_loop/",
    "created_utc": 1700002000.0,
    "thumbnail": "https://b.thumbs.redditmedia.com/thumb.jpg",
    "secure_media": {
        "reddit_video": {
            "fallback_url": "https://v.redd.it/gif001/DASH_480.mp4?source=fallback",
            "width": 640,
            "height": 480,
            "duration": 5,
            "is_gif": True,
        }
    },
    "media": None,
}

GALLERY_POST_DATA = {
    "id": "gal001",
    "name": "t3_gal001",
    "title": "Gallery of landscapes",
    "subreddit": "earthporn",
    "author": "traveler",
    "score": 7800,
    "url": "https://www.reddit.com/gallery/gal001",
    "domain": "reddit.com",
    "post_hint": "",
    "is_video": False,
    "is_gallery": True,
    "is_self": False,
    "over_18": False,
    "permalink": "/r/earthporn/comments/gal001/gallery_of_landscapes/",
    "created_utc": 1700003000.0,
    "thumbnail": "https://b.thumbs.redditmedia.com/thumb.jpg",
}

SELF_POST_DATA = {
    "id": "txt001",
    "name": "t3_txt001",
    "title": "Discussion thread",
    "subreddit": "wallpapers",
    "author": "user1",
    "score": 100,
    "url": "https://www.reddit.com/r/wallpapers/comments/txt001/discussion/",
    "domain": "self.wallpapers",
    "post_hint": "self",
    "is_video": False,
    "is_gallery": False,
    "is_self": True,
    "over_18": False,
    "permalink": "/r/wallpapers/comments/txt001/discussion/",
    "created_utc": 1700004000.0,
    "thumbnail": "self",
}

EXTERNAL_LINK_POST_DATA = {
    "id": "ext001",
    "name": "t3_ext001",
    "title": "Some website",
    "subreddit": "interesting",
    "author": "user2",
    "score": 50,
    "url": "https://www.example.com/article",
    "domain": "example.com",
    "post_hint": "link",
    "is_video": False,
    "is_gallery": False,
    "is_self": False,
    "over_18": False,
    "permalink": "/r/interesting/comments/ext001/",
    "created_utc": 1700005000.0,
    "thumbnail": "default",
}


# ---------------------------------------------------------------------------
# RedditPost.from_reddit_data
# ---------------------------------------------------------------------------


class TestRedditPostFromRedditData:
    def test_image_post_hint(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert post.id == "img001"
        assert post.media_type == MediaType.IMAGE
        assert post.url == "https://i.redd.it/mountain.jpg"
        assert post.title == "Beautiful mountain"
        assert post.subreddit == "EarthPorn"
        assert post.author == "photographer"
        assert post.score == 9500
        assert post.is_nsfw is False
        assert post.is_gallery is False
        assert post.gallery_index is None
        assert post.gallery_id is None

    def test_image_post_dimensions_from_preview(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert post.width == 3840
        assert post.height == 2160

    def test_image_post_thumbnail(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert post.thumbnail_url == "https://b.thumbs.redditmedia.com/thumb.jpg"

    def test_image_post_created_utc_is_datetime(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert isinstance(post.created_utc, datetime)
        assert post.created_utc.tzinfo is not None

    def test_image_post_permalink(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert post.permalink == "/r/EarthPorn/comments/img001/beautiful_mountain/"

    def test_video_post(self) -> None:
        post = RedditPost.from_reddit_data(VIDEO_POST_DATA)
        assert post is not None
        assert post.id == "vid001"
        assert post.media_type == MediaType.VIDEO
        assert "DASH_480" in post.url
        assert post.video_url is not None
        assert "DASH_480" in post.video_url
        assert post.width == 1920
        assert post.height == 1080
        assert post.duration == 60

    def test_video_post_url_equals_video_url(self) -> None:
        post = RedditPost.from_reddit_data(VIDEO_POST_DATA)
        assert post is not None
        assert post.url == post.video_url

    def test_gif_video_post(self) -> None:
        post = RedditPost.from_reddit_data(GIF_POST_DATA)
        assert post is not None
        assert post.id == "gif001"
        assert post.media_type == MediaType.GIF
        assert post.duration == 5

    def test_gallery_post(self) -> None:
        post = RedditPost.from_reddit_data(GALLERY_POST_DATA)
        assert post is not None
        assert post.id == "gal001"
        assert post.media_type == MediaType.IMAGE
        assert post.is_gallery is True
        assert post.url == ""
        assert post.gallery_index is None
        assert post.gallery_id is None

    def test_self_post_returns_none(self) -> None:
        result = RedditPost.from_reddit_data(SELF_POST_DATA)
        assert result is None

    def test_external_link_returns_none(self) -> None:
        result = RedditPost.from_reddit_data(EXTERNAL_LINK_POST_DATA)
        assert result is None

    def test_nsfw_flag(self) -> None:
        data = {**IMAGE_POST_DATA, "over_18": True}
        post = RedditPost.from_reddit_data(data)
        assert post is not None
        assert post.is_nsfw is True

    def test_imgur_domain_treated_as_image(self) -> None:
        data = {
            **IMAGE_POST_DATA,
            "domain": "i.imgur.com",
            "post_hint": "",
            "url": "https://i.imgur.com/abc.jpg",
            "url_overridden_by_dest": "https://i.imgur.com/abc.jpg",
        }
        post = RedditPost.from_reddit_data(data)
        assert post is not None
        assert post.media_type == MediaType.IMAGE
        assert post.url == "https://i.imgur.com/abc.jpg"

    def test_non_http_thumbnail_is_none(self) -> None:
        data = {**IMAGE_POST_DATA, "thumbnail": "self"}
        post = RedditPost.from_reddit_data(data)
        assert post is not None
        assert post.thumbnail_url is None

    def test_missing_preview_gives_none_dimensions(self) -> None:
        data = {k: v for k, v in IMAGE_POST_DATA.items() if k != "preview"}
        post = RedditPost.from_reddit_data(data)
        assert post is not None
        assert post.width is None
        assert post.height is None

    def test_fullname_from_name_field(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        assert post.fullname == "t3_img001"

    def test_video_fallback_uses_media_when_secure_media_missing(self) -> None:
        data = {
            **VIDEO_POST_DATA,
            "secure_media": None,
            "media": {
                "reddit_video": {
                    "fallback_url": "https://v.redd.it/vid001/DASH_360.mp4",
                    "width": 1280,
                    "height": 720,
                    "duration": 30,
                    "is_gif": False,
                }
            },
        }
        post = RedditPost.from_reddit_data(data)
        assert post is not None
        assert post.media_type == MediaType.VIDEO
        assert "DASH_360" in post.url


# ---------------------------------------------------------------------------
# RedditGalleryItem
# ---------------------------------------------------------------------------


class TestRedditGalleryItem:
    def test_all_fields(self) -> None:
        item = RedditGalleryItem(
            media_id="abc123",
            url="https://i.redd.it/abc123.jpg",
            width=2560,
            height=1440,
            mime_type="image/jpg",
            caption="A sunset",
        )
        assert item.media_id == "abc123"
        assert item.url == "https://i.redd.it/abc123.jpg"
        assert item.width == 2560
        assert item.height == 1440
        assert item.mime_type == "image/jpg"
        assert item.caption == "A sunset"

    def test_optional_fields_default_none(self) -> None:
        item = RedditGalleryItem(media_id="xyz", url="https://example.com/img.jpg")
        assert item.width is None
        assert item.height is None
        assert item.mime_type is None
        assert item.caption is None


# ---------------------------------------------------------------------------
# RedditListing
# ---------------------------------------------------------------------------


class TestRedditListing:
    def test_with_posts(self) -> None:
        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        listing = RedditListing(
            posts=[post],
            after="t3_nextpost",
            before=None,
            dist=25,
        )
        assert len(listing.posts) == 1
        assert listing.after == "t3_nextpost"
        assert listing.before is None
        assert listing.dist == 25

    def test_empty_listing(self) -> None:
        listing = RedditListing(posts=[], after=None, before=None, dist=0)
        assert listing.posts == []
        assert listing.after is None
        assert listing.dist == 0

    def test_after_and_before_cursors(self) -> None:
        listing = RedditListing(
            posts=[],
            after="t3_abc",
            before="t3_xyz",
            dist=10,
        )
        assert listing.after == "t3_abc"
        assert listing.before == "t3_xyz"
