"""
Tests for the synchronous Reddit client.
"""

from unittest.mock import Mock, patch

import pytest

from xanax.enums import MediaType
from xanax.errors import APIError, AuthenticationError, NotFoundError, RateLimitError
from xanax.sources.reddit.client import Reddit
from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter
from xanax.sources.reddit.models import RedditPost
from xanax.sources.reddit.params import RedditParams

# ---------------------------------------------------------------------------
# Shared test data
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
}

VIDEO_POST_DATA = {
    "id": "vid001",
    "name": "t3_vid001",
    "title": "Timelapse",
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
    "permalink": "/r/videos/comments/vid001/",
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

NSFW_POST_DATA = {
    **IMAGE_POST_DATA,
    "id": "nsfw001",
    "name": "t3_nsfw001",
    "over_18": True,
}

GALLERY_POST_DATA = {
    "id": "gal001",
    "name": "t3_gal001",
    "title": "Gallery",
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
    "permalink": "/r/earthporn/comments/gal001/gallery/",
    "created_utc": 1700003000.0,
    "thumbnail": "https://b.thumbs.redditmedia.com/thumb.jpg",
    "gallery_data": {
        "items": [
            {"media_id": "m1", "id": 1},
            {"media_id": "m2", "id": 2},
        ]
    },
    "media_metadata": {
        "m1": {"s": {"u": "https://i.redd.it/m1.jpg", "x": 1920, "y": 1080}, "m": "image/jpg"},
        "m2": {"s": {"u": "https://i.redd.it/m2.jpg", "x": 800, "y": 600}, "m": "image/jpg"},
    },
}


def _make_listing_response(posts: list[dict], after: str | None = None) -> dict:
    children = [{"kind": "t3", "data": p} for p in posts]
    return {
        "kind": "Listing",
        "data": {
            "children": children,
            "after": after,
            "before": None,
            "dist": len(children),
        },
    }


def _make_response(status_code: int, json_data: object = None) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.headers = {}
    if json_data is not None:
        response.json.return_value = json_data
    return response


def _make_reddit(
    mock_client_cls: Mock,
    mock_auth_cls: Mock | None = None,
    max_retries: int = 0,
) -> Reddit:
    """Create a Reddit client with mocked httpx.Client and RedditAuth."""
    mock_client = Mock()
    mock_client_cls.return_value = mock_client
    return Reddit(
        client_id="test-id",
        client_secret="test-secret",
        user_agent="python:test/1.0 (by u/user)",
        max_retries=max_retries,
    ), mock_client


# ---------------------------------------------------------------------------
# Init / Auth
# ---------------------------------------------------------------------------


class TestRedditInit:
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_with_explicit_credentials(self, mock_client_cls: Mock) -> None:
        mock_client_cls.return_value = Mock()
        client = Reddit(
            client_id="cid",
            client_secret="csecret",
            user_agent="python:test/1.0 (by u/user)",
        )
        assert repr(client) == "Reddit(authenticated)"

    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_env_var_credentials(
        self, mock_client_cls: Mock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("REDDIT_CLIENT_ID", "env-id")
        monkeypatch.setenv("REDDIT_CLIENT_SECRET", "env-secret")
        monkeypatch.setenv("REDDIT_USER_AGENT", "python:test/1.0 (by u/user)")
        mock_client_cls.return_value = Mock()
        client = Reddit()
        assert "authenticated" in repr(client)

    def test_no_client_id_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            Reddit(client_secret="s", user_agent="ua")
        assert "client_id" in str(exc_info.value).lower()

    def test_no_client_secret_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            Reddit(client_id="id", user_agent="ua")
        assert "client_secret" in str(exc_info.value).lower()

    def test_no_user_agent_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("REDDIT_USER_AGENT", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            Reddit(client_id="id", client_secret="s")
        assert "user_agent" in str(exc_info.value).lower()

    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_secret_not_in_repr(self, mock_client_cls: Mock) -> None:
        mock_client_cls.return_value = Mock()
        client = Reddit(client_id="cid", client_secret="super-secret", user_agent="ua")
        assert "super-secret" not in repr(client)


# ---------------------------------------------------------------------------
# HTTP error handling
# ---------------------------------------------------------------------------


class TestRedditErrorHandling:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_401_raises_authentication_error(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(401)
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(AuthenticationError):
            client.listing(RedditParams(subreddit="x"))

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_404_raises_not_found(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(404)
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(NotFoundError):
            client.listing(RedditParams(subreddit="nonexistent"))

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_429_raises_rate_limit_error(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(429)
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(RateLimitError):
            client.listing(RedditParams(subreddit="x"))

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_5xx_raises_api_error(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(500)
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(APIError) as exc_info:
            client.listing(RedditParams(subreddit="x"))
        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# listing()
# ---------------------------------------------------------------------------


class TestRedditListing:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_success(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA])
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        listing = client.listing(RedditParams(subreddit="EarthPorn"))

        assert len(listing.posts) == 1
        assert listing.posts[0].id == "img001"
        assert listing.dist == 1

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_calls_correct_url(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(RedditParams(subreddit="wallpapers", sort=RedditSort.TOP))

        call_args = mock_client.request.call_args
        url = call_args[0][1]
        assert "wallpapers/top" in url

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_passes_t_param_for_top(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(
            RedditParams(subreddit="x", sort=RedditSort.TOP, time_filter=RedditTimeFilter.WEEK)
        )

        call_kwargs = mock_client.request.call_args[1]
        params = call_kwargs.get("params", {})
        assert params.get("t") == "week"

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_passes_t_param_for_controversial(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(
            RedditParams(
                subreddit="x",
                sort=RedditSort.CONTROVERSIAL,
                time_filter=RedditTimeFilter.MONTH,
            )
        )

        call_kwargs = mock_client.request.call_args[1]
        params = call_kwargs.get("params", {})
        assert params.get("t") == "month"

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_no_t_param_for_hot(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(RedditParams(subreddit="x", sort=RedditSort.HOT))

        call_kwargs = mock_client.request.call_args[1]
        params = call_kwargs.get("params", {})
        assert "t" not in params

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_passes_after_cursor(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(RedditParams(subreddit="x", after="t3_abc"))

        call_kwargs = mock_client.request.call_args[1]
        params = call_kwargs.get("params", {})
        assert params.get("after") == "t3_abc"

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_listing_always_passes_raw_json(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, _make_listing_response([]))
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        client.listing(RedditParams(subreddit="x"))

        call_kwargs = mock_client.request.call_args[1]
        params = call_kwargs.get("params", {})
        assert params.get("raw_json") == 1


# ---------------------------------------------------------------------------
# download()
# ---------------------------------------------------------------------------


class TestRedditDownload:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_download_image_uses_url(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        image_response = Mock()
        image_response.content = b"image-bytes"
        image_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.get.return_value = image_response
        mock_client_cls.return_value = mock_client

        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        result = client.download(post)

        assert result == b"image-bytes"
        mock_client.get.assert_called_once_with("https://i.redd.it/mountain.jpg")

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_download_video_uses_video_url(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        image_response = Mock()
        image_response.content = b"video-bytes"
        image_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.get.return_value = image_response
        mock_client_cls.return_value = mock_client

        post = RedditPost.from_reddit_data(VIDEO_POST_DATA)
        assert post is not None

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        result = client.download(post)

        assert result == b"video-bytes"
        call_url = mock_client.get.call_args[0][0]
        assert "DASH_480" in call_url

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_download_raises_for_empty_url(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client_cls.return_value = Mock()

        # Gallery post with no URL
        gallery_post = RedditPost.from_reddit_data(GALLERY_POST_DATA)
        assert gallery_post is not None
        assert gallery_post.url == ""

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(ValueError, match="no downloadable URL"):
            client.download(gallery_post)

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_download_saves_to_path(
        self, mock_client_cls: Mock, mock_get_headers: Mock, tmp_path: pytest.TempPathFactory
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        image_response = Mock()
        image_response.content = b"saved-bytes"
        image_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.get.return_value = image_response
        mock_client_cls.return_value = mock_client

        post = RedditPost.from_reddit_data(IMAGE_POST_DATA)
        assert post is not None
        dest = tmp_path / "photo.jpg"  # type: ignore[operator]

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        result = client.download(post, path=dest)

        assert result == b"saved-bytes"
        assert dest.read_bytes() == b"saved-bytes"


# ---------------------------------------------------------------------------
# iter_pages()
# ---------------------------------------------------------------------------


class TestRedditIterPages:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_pages_single_page_no_after(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA], after=None)
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        pages = list(client.iter_pages(RedditParams(subreddit="x")))

        assert len(pages) == 1
        assert mock_client.request.call_count == 1

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_pages_follows_cursor(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.side_effect = [
            _make_response(200, _make_listing_response([IMAGE_POST_DATA], after="t3_p2")),
            _make_response(200, _make_listing_response([IMAGE_POST_DATA], after=None)),
        ]
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        pages = list(client.iter_pages(RedditParams(subreddit="x")))

        assert len(pages) == 2
        assert mock_client.request.call_count == 2

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_pages_stops_on_empty_posts(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        # Returns after cursor but empty posts — should stop
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([], after="t3_next")
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        pages = list(client.iter_pages(RedditParams(subreddit="x")))

        assert len(pages) == 1
        assert mock_client.request.call_count == 1


# ---------------------------------------------------------------------------
# iter_media()
# ---------------------------------------------------------------------------


class TestRedditIterMedia:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_media_yields_posts(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA])
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        posts = list(client.iter_media(RedditParams(subreddit="EarthPorn")))

        assert len(posts) == 1
        assert posts[0].id == "img001"

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_media_filters_by_media_type(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA, VIDEO_POST_DATA])
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        posts = list(client.iter_media(RedditParams(subreddit="x", media_type=MediaType.VIDEO)))

        assert len(posts) == 1
        assert posts[0].media_type == MediaType.VIDEO

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_media_filters_nsfw_by_default(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA, NSFW_POST_DATA])
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        posts = list(client.iter_media(RedditParams(subreddit="x", include_nsfw=False)))

        assert len(posts) == 1
        assert not posts[0].is_nsfw

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_media_includes_nsfw_when_enabled(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200, _make_listing_response([IMAGE_POST_DATA, NSFW_POST_DATA])
        )
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        posts = list(client.iter_media(RedditParams(subreddit="x", include_nsfw=True)))

        assert len(posts) == 2

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_iter_media_expands_gallery(
        self, mock_client_cls: Mock, mock_get_headers: Mock
    ) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()

        # First call: listing with gallery post
        # Second call: fetch gallery post details for expansion
        comments_response = [
            {"data": {"children": [{"data": GALLERY_POST_DATA}]}},
            {"data": {"children": []}},
        ]
        mock_client.request.side_effect = [
            _make_response(200, _make_listing_response([GALLERY_POST_DATA])),
            _make_response(200, comments_response),
        ]
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        posts = list(client.iter_media(RedditParams(subreddit="earthporn")))

        # Gallery has 2 items — should yield 2 posts
        assert len(posts) == 2
        assert posts[0].gallery_index == 0
        assert posts[0].gallery_id == "gal001"
        assert posts[1].gallery_index == 1


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


class TestRedditRetry:
    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_retry_on_429(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.side_effect = [
            _make_response(429),
            _make_response(200, _make_listing_response([IMAGE_POST_DATA])),
        ]
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua", max_retries=1)
        with patch("time.sleep"):
            listing = client.listing(RedditParams(subreddit="x"))

        assert len(listing.posts) == 1
        assert mock_client.request.call_count == 2

    @patch("xanax.sources.reddit.client.RedditAuth.get_headers")
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_no_retry_by_default(self, mock_client_cls: Mock, mock_get_headers: Mock) -> None:
        mock_get_headers.return_value = {"Authorization": "Bearer tok", "User-Agent": "ua"}
        mock_client = Mock()
        mock_client.request.return_value = _make_response(429)
        mock_client_cls.return_value = mock_client

        client = Reddit(client_id="id", client_secret="s", user_agent="ua")
        with pytest.raises(RateLimitError):
            client.listing(RedditParams(subreddit="x"))

        assert mock_client.request.call_count == 1


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestRedditContextManager:
    @patch("xanax.sources.reddit.client.httpx.Client")
    def test_context_manager_closes_client(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        with Reddit(client_id="id", client_secret="s", user_agent="ua"):
            pass

        mock_client.close.assert_called_once()
