"""
Tests for Wallhaven sync client.
"""

from unittest.mock import Mock, patch

import pytest

from xanax.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from xanax.sources.wallhaven import Wallhaven
from xanax.sources.wallhaven.enums import Purity
from xanax.sources.wallhaven.models import Wallpaper
from xanax.sources.wallhaven.params import SearchParams

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

WALLPAPER_DATA = {
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
    "colors": ["#000000"],
    "path": "https://w.wallhaven.cc/full/94/wallhaven-94x38z.jpg",
    "thumbs": {
        "large": "https://th.wallhaven.cc/lg/94/94x38z.jpg",
        "original": "https://th.wallhaven.cc/orig/94/94x38z.jpg",
        "small": "https://th.wallhaven.cc/small/94/94x38z.jpg",
    },
    "tags": [],
    "uploader": None,
}

SEARCH_RESPONSE = {
    "data": [WALLPAPER_DATA],
    "meta": {
        "current_page": 1,
        "last_page": 2,
        "per_page": 24,
        "total": 48,
    },
}

SEARCH_RESPONSE_PAGE2 = {
    "data": [WALLPAPER_DATA],
    "meta": {
        "current_page": 2,
        "last_page": 2,
        "per_page": 24,
        "total": 48,
    },
}


def _make_response(status_code: int, json_data: dict | None = None) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.headers = {}
    if json_data is not None:
        response.json.return_value = json_data
    return response


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------


class TestWallhavenInit:
    def test_default_init(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = Wallhaven()
        assert client.is_authenticated is False

    def test_with_api_key(self) -> None:
        client = Wallhaven(api_key="test-key-123")
        assert client.is_authenticated is True

    def test_env_var_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WALLHAVEN_API_KEY", "env-key")
        client = Wallhaven()
        assert client.is_authenticated is True

    def test_repr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = Wallhaven()
        assert "unauthenticated" in repr(client)

        client_with_key = Wallhaven(api_key="test")
        assert "authenticated" in repr(client_with_key)


# ---------------------------------------------------------------------------
# Wallpaper
# ---------------------------------------------------------------------------


class TestWallhavenWallpaper:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_get_wallpaper_success(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, {"data": WALLPAPER_DATA})
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        wallpaper = client.wallpaper("94x38z")

        assert wallpaper.id == "94x38z"
        assert wallpaper.resolution == "6742x3534"

    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_get_wallpaper_not_found(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(404)
        mock_client_cls.return_value = mock_client

        client = Wallhaven()

        with pytest.raises(NotFoundError):
            client.wallpaper("nonexistent")

    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_get_wallpaper_rate_limited(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(429)
        mock_client_cls.return_value = mock_client

        client = Wallhaven()

        with pytest.raises(RateLimitError):
            client.wallpaper("94x38z")

    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_auth_header_sent_not_query_param(self, mock_client_cls: Mock) -> None:
        """API key must go in headers only, never as a query parameter."""
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, {"data": WALLPAPER_DATA})
        mock_client_cls.return_value = mock_client

        client = Wallhaven(api_key="my-secret-key")
        client.wallpaper("94x38z")

        call_kwargs = mock_client.request.call_args
        headers = call_kwargs[1]["headers"] if "headers" in call_kwargs[1] else call_kwargs[0][3]
        params = call_kwargs[1].get("params") or {}

        assert "X-API-Key" in headers
        assert "apikey" not in (params or {})


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestWallhavenSearch:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_search_success(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, SEARCH_RESPONSE)
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        params = SearchParams(query="anime")
        result = client.search(params)

        assert len(result.data) == 1
        assert result.data[0].id == "94x38z"
        assert result.meta.total == 48

    def test_search_nsfw_without_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = Wallhaven()

        with pytest.raises(AuthenticationError) as exc_info:
            client.search(SearchParams(purity=[Purity.NSFW]))

        assert "API key" in str(exc_info.value)

    def test_search_with_toplist_without_toplist_sorting_raises(self) -> None:
        from xanax.sources.wallhaven.enums import Sort, TopRange

        client = Wallhaven()

        with pytest.raises(ValidationError):
            client.search(SearchParams(sorting=Sort.DATE_ADDED, top_range=TopRange.ONE_MONTH))


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TestWallhavenTag:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_get_tag_success(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200,
            {
                "data": {
                    "id": 1,
                    "name": "anime",
                    "alias": "Chinese cartoons",
                    "category_id": 1,
                    "category": "Anime & Manga",
                    "purity": "sfw",
                    "created_at": "2015-01-16 02:06:45",
                }
            },
        )
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        tag = client.tag(1)

        assert tag.id == 1
        assert tag.name == "anime"


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------


class TestWallhavenCollections:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_get_collections_with_username(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.return_value = _make_response(
            200,
            {
                "data": [
                    {
                        "id": 15,
                        "label": "Default",
                        "views": 38,
                        "public": 1,
                        "count": 10,
                    }
                ]
            },
        )
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        collections = client.collections(username="testuser")

        assert len(collections) == 1
        assert collections[0].label == "Default"
        assert collections[0].public is True

    def test_get_collections_no_username_no_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = Wallhaven()

        with pytest.raises(AuthenticationError) as exc_info:
            client.collections()

        assert "API key" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


class TestWallhavenDownload:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_download_returns_bytes(self, mock_client_cls: Mock) -> None:
        mock_response = Mock()
        mock_response.content = b"fake-image-bytes"
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        wallpaper = Wallpaper(**WALLPAPER_DATA)
        client = Wallhaven()
        result = client.download(wallpaper)

        assert result == b"fake-image-bytes"
        mock_client.get.assert_called_once_with(wallpaper.path, follow_redirects=True)

    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_download_saves_to_path(
        self, mock_client_cls: Mock, tmp_path: pytest.TempPathFactory
    ) -> None:
        mock_response = Mock()
        mock_response.content = b"fake-image-bytes"
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        wallpaper = Wallpaper(**WALLPAPER_DATA)
        dest = tmp_path / "wallpaper.jpg"  # type: ignore[operator]
        client = Wallhaven()
        result = client.download(wallpaper, path=dest)

        assert result == b"fake-image-bytes"
        assert dest.read_bytes() == b"fake-image-bytes"


# ---------------------------------------------------------------------------
# iter_pages / iter_media
# ---------------------------------------------------------------------------


class TestWallhavenIterPages:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_iter_pages_single_page(self, mock_client_cls: Mock) -> None:
        single_page_response = {
            "data": [WALLPAPER_DATA],
            "meta": {
                "current_page": 1,
                "last_page": 1,
                "per_page": 24,
                "total": 1,
            },
        }

        mock_client = Mock()
        mock_client.request.return_value = _make_response(200, single_page_response)
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        pages = list(client.iter_pages(SearchParams(query="anime")))

        assert len(pages) == 1
        assert len(pages[0].data) == 1

    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_iter_pages_multiple_pages(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.side_effect = [
            _make_response(200, SEARCH_RESPONSE),
            _make_response(200, SEARCH_RESPONSE_PAGE2),
        ]
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        pages = list(client.iter_pages(SearchParams(query="anime")))

        assert len(pages) == 2
        assert pages[0].meta.current_page == 1
        assert pages[1].meta.current_page == 2


class TestWallhavenIterMedia:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_iter_media_flattens_pages(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client.request.side_effect = [
            _make_response(200, SEARCH_RESPONSE),
            _make_response(200, SEARCH_RESPONSE_PAGE2),
        ]
        mock_client_cls.return_value = mock_client

        client = Wallhaven()
        wallpapers = list(client.iter_media(SearchParams(query="anime")))

        assert len(wallpapers) == 2
        assert all(wp.id == "94x38z" for wp in wallpapers)


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestWallhavenContextManager:
    @patch("xanax.sources.wallhaven.client.httpx.Client")
    def test_context_manager(self, mock_client_cls: Mock) -> None:
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        with Wallhaven():
            pass

        mock_client.close.assert_called_once()
