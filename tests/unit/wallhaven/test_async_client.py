"""
Tests for AsyncWallhaven client.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from xanax.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from xanax.sources.wallhaven import AsyncWallhaven
from xanax.sources.wallhaven.enums import Purity
from xanax.sources.wallhaven.models import Wallpaper
from xanax.sources.wallhaven.params import SearchParams

# ---------------------------------------------------------------------------
# Shared test data
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
# Init & repr
# ---------------------------------------------------------------------------


class TestAsyncWallhavenInit:
    def test_default_init(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = AsyncWallhaven()
        assert client.is_authenticated is False

    def test_with_api_key(self) -> None:
        client = AsyncWallhaven(api_key="test-key-123")
        assert client.is_authenticated is True

    def test_env_var_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WALLHAVEN_API_KEY", "env-key")
        client = AsyncWallhaven()
        assert client.is_authenticated is True

    def test_repr_unauthenticated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = AsyncWallhaven()
        assert "unauthenticated" in repr(client)

    def test_repr_authenticated(self) -> None:
        client = AsyncWallhaven(api_key="key")
        assert "authenticated" in repr(client)


# ---------------------------------------------------------------------------
# Wallpaper
# ---------------------------------------------------------------------------


class TestAsyncWallhavenWallpaper:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_get_wallpaper_success(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(200, {"data": WALLPAPER_DATA}))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        wallpaper = await client.wallpaper("94x38z")

        assert wallpaper.id == "94x38z"
        assert wallpaper.resolution == "6742x3534"

    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_get_wallpaper_not_found(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(404))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()

        with pytest.raises(NotFoundError):
            await client.wallpaper("nonexistent")

    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_get_wallpaper_rate_limited(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(429))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()

        with pytest.raises(RateLimitError):
            await client.wallpaper("94x38z")

    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_auth_header_sent_not_query_param(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(200, {"data": WALLPAPER_DATA}))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven(api_key="my-secret-key")
        await client.wallpaper("94x38z")

        call_kwargs = mock_client.request.call_args
        headers = call_kwargs[1].get("headers") or {}
        params = call_kwargs[1].get("params") or {}

        assert "X-API-Key" in headers
        assert "apikey" not in params


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestAsyncWallhavenSearch:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_search_success(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(200, SEARCH_RESPONSE))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        result = await client.search(SearchParams(query="anime"))

        assert len(result.data) == 1
        assert result.meta.total == 48

    async def test_search_nsfw_without_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = AsyncWallhaven()

        with pytest.raises(AuthenticationError):
            await client.search(SearchParams(purity=[Purity.NSFW]))

    async def test_search_toplist_validates(self) -> None:
        from xanax.sources.wallhaven.enums import Sort, TopRange

        client = AsyncWallhaven()

        with pytest.raises(ValidationError):
            await client.search(SearchParams(sorting=Sort.DATE_ADDED, top_range=TopRange.ONE_MONTH))


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TestAsyncWallhavenTag:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_get_tag_success(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(
            return_value=_make_response(
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
        )
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        tag = await client.tag(1)

        assert tag.id == 1
        assert tag.name == "anime"


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class TestAsyncWallhavenSettings:
    async def test_settings_without_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = AsyncWallhaven()

        with pytest.raises(AuthenticationError):
            await client.settings()


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------


class TestAsyncWallhavenCollections:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_get_collections_with_username(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(
            return_value=_make_response(
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
        )
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        collections = await client.collections(username="testuser")

        assert len(collections) == 1
        assert collections[0].label == "Default"
        assert collections[0].public is True

    async def test_get_own_collections_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WALLHAVEN_API_KEY", raising=False)
        client = AsyncWallhaven()

        with pytest.raises(AuthenticationError):
            await client.collections()


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


class TestAsyncWallhavenDownload:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_download_returns_bytes(self, mock_client_cls: Mock) -> None:
        mock_dl_response = Mock()
        mock_dl_response.content = b"fake-image-bytes"
        mock_dl_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_dl_response)
        mock_client_cls.return_value = mock_client

        wallpaper = Wallpaper(**WALLPAPER_DATA)
        client = AsyncWallhaven()
        result = await client.download(wallpaper)

        assert result == b"fake-image-bytes"
        mock_client.get.assert_called_once_with(wallpaper.path, follow_redirects=True)

    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_download_saves_to_path(
        self, mock_client_cls: Mock, tmp_path: pytest.TempPathFactory
    ) -> None:
        mock_dl_response = Mock()
        mock_dl_response.content = b"fake-image-bytes"
        mock_dl_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_dl_response)
        mock_client_cls.return_value = mock_client

        wallpaper = Wallpaper(**WALLPAPER_DATA)
        dest = tmp_path / "wallpaper.jpg"  # type: ignore[operator]
        client = AsyncWallhaven()
        result = await client.download(wallpaper, path=dest)

        assert result == b"fake-image-bytes"
        assert dest.read_bytes() == b"fake-image-bytes"


# ---------------------------------------------------------------------------
# aiter_pages / aiter_media
# ---------------------------------------------------------------------------


class TestAsyncWallhavenIterPages:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_aiter_pages_single_page(self, mock_client_cls: Mock) -> None:
        single_page = {
            "data": [WALLPAPER_DATA],
            "meta": {"current_page": 1, "last_page": 1, "per_page": 24, "total": 1},
        }

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=_make_response(200, single_page))
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        pages = [page async for page in client.aiter_pages(SearchParams(query="anime"))]

        assert len(pages) == 1

    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_aiter_pages_multiple_pages(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(
            side_effect=[
                _make_response(200, SEARCH_RESPONSE),
                _make_response(200, SEARCH_RESPONSE_PAGE2),
            ]
        )
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        pages = [page async for page in client.aiter_pages(SearchParams(query="anime"))]

        assert len(pages) == 2
        assert pages[0].meta.current_page == 1
        assert pages[1].meta.current_page == 2


class TestAsyncWallhavenIterMedia:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_aiter_media_flattens_pages(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(
            side_effect=[
                _make_response(200, SEARCH_RESPONSE),
                _make_response(200, SEARCH_RESPONSE_PAGE2),
            ]
        )
        mock_client_cls.return_value = mock_client

        client = AsyncWallhaven()
        wallpapers = [wp async for wp in client.aiter_media(SearchParams(query="anime"))]

        assert len(wallpapers) == 2
        assert all(wp.id == "94x38z" for wp in wallpapers)


# ---------------------------------------------------------------------------
# Async context manager
# ---------------------------------------------------------------------------


class TestAsyncWallhavenContextManager:
    @patch("xanax.sources.wallhaven.async_client.httpx.AsyncClient")
    async def test_async_context_manager(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        async with AsyncWallhaven() as client:
            assert client is not None

        mock_client.aclose.assert_called_once()
