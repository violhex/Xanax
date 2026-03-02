"""
Tests for the asynchronous AsyncUnsplash client.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from xanax.errors import APIError, AuthenticationError, NotFoundError, RateLimitError
from xanax.sources.unsplash.async_client import AsyncUnsplash
from xanax.sources.unsplash.models import UnsplashPhoto
from xanax.sources.unsplash.params import UnsplashRandomParams, UnsplashSearchParams

# ---------------------------------------------------------------------------
# Shared test data (mirrors test_client.py)
# ---------------------------------------------------------------------------

PHOTO_DATA = {
    "id": "abc123",
    "created_at": "2023-06-15T12:00:00Z",
    "width": 3840,
    "height": 2160,
    "urls": {
        "raw": "https://images.unsplash.com/photo-1?ixid=raw",
        "full": "https://images.unsplash.com/photo-1?q=75",
        "regular": "https://images.unsplash.com/photo-1?w=1080",
        "small": "https://images.unsplash.com/photo-1?w=400",
        "thumb": "https://images.unsplash.com/photo-1?w=200",
    },
    "links": {
        "self": "https://api.unsplash.com/photos/abc123",
        "html": "https://unsplash.com/photos/abc123",
        "download": "https://unsplash.com/photos/abc123/download",
        "download_location": "https://api.unsplash.com/photos/abc123/download",
    },
    "user": {
        "id": "user1",
        "username": "photographer",
        "name": "Jane Doe",
        "total_collections": 0,
    },
}

SEARCH_RESPONSE = {
    "total": 50,
    "total_pages": 5,
    "results": [PHOTO_DATA],
}


def _make_response(status_code: int, json_data: dict | None = None) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.headers = {}
    if json_data is not None:
        response.json.return_value = json_data
    return response


# ---------------------------------------------------------------------------
# Init / Auth
# ---------------------------------------------------------------------------


class TestAsyncUnsplashInit:
    def test_with_access_key(self) -> None:
        client = AsyncUnsplash(access_key="test-key")
        assert repr(client) == "AsyncUnsplash(authenticated)"

    def test_env_var_access_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "env-key")
        client = AsyncUnsplash()
        assert "authenticated" in repr(client)

    def test_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("UNSPLASH_ACCESS_KEY", raising=False)
        with pytest.raises(AuthenticationError):
            AsyncUnsplash()

    def test_auth_header_format(self) -> None:
        client = AsyncUnsplash(access_key="my-key")
        assert client._auth_headers() == {"Authorization": "Client-ID my-key"}


# ---------------------------------------------------------------------------
# HTTP error handling
# ---------------------------------------------------------------------------


class TestAsyncUnsplashErrorHandling:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_401_raises_authentication_error(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(401)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="bad-key")
        with pytest.raises(AuthenticationError):
            await client.search(UnsplashSearchParams(query="x"))

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_404_raises_not_found(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(404)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        with pytest.raises(NotFoundError):
            await client.photo("nonexistent")

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_429_raises_rate_limit_error(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(429)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        with pytest.raises(RateLimitError):
            await client.search(UnsplashSearchParams(query="x"))

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_5xx_raises_api_error(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(500)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        with pytest.raises(APIError) as exc_info:
            await client.search(UnsplashSearchParams(query="x"))
        assert exc_info.value.status_code == 500

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_auth_header_sent_not_query_param(self, mock_client_cls: Mock) -> None:
        """Access key must appear in Authorization header, never in query params."""
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, SEARCH_RESPONSE)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="my-secret")
        await client.search(UnsplashSearchParams(query="x"))

        call_kwargs = mock_client.request.call_args
        headers = call_kwargs[1].get("headers") or {}
        params = call_kwargs[1].get("params") or {}

        assert "Authorization" in headers
        assert headers["Authorization"] == "Client-ID my-secret"
        assert "client_id" not in params


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


class TestAsyncUnsplashSearch:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_search_success(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, SEARCH_RESPONSE)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        result = await client.search(UnsplashSearchParams(query="mountains"))

        assert result.total == 50
        assert result.total_pages == 5
        assert len(result.results) == 1
        assert result.results[0].id == "abc123"


# ---------------------------------------------------------------------------
# photo()
# ---------------------------------------------------------------------------


class TestAsyncUnsplashPhoto:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_photo_success(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, PHOTO_DATA)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        photo = await client.photo("abc123")

        assert photo.id == "abc123"
        assert photo.width == 3840

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_photo_not_found(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(404)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        with pytest.raises(NotFoundError):
            await client.photo("nonexistent")


# ---------------------------------------------------------------------------
# random()
# ---------------------------------------------------------------------------


class TestAsyncUnsplashRandom:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_random_no_params(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, PHOTO_DATA)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        photo = await client.random()

        assert isinstance(photo, UnsplashPhoto)
        assert photo.id == "abc123"

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_random_with_params(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, PHOTO_DATA)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        params = UnsplashRandomParams(query="ocean")
        photo = await client.random(params)

        assert isinstance(photo, UnsplashPhoto)
        call_kwargs = mock_client.request.call_args
        sent_params = call_kwargs[1].get("params") or {}
        assert sent_params.get("query") == "ocean"


# ---------------------------------------------------------------------------
# download()
# ---------------------------------------------------------------------------


class TestAsyncUnsplashDownload:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_download_triggers_tracking_then_fetches_cdn(self, mock_client_cls: Mock) -> None:
        """download() must call download_location first, then fetch the CDN URL."""
        # Use plain Mock for responses: httpx Response.json() is synchronous, not a coroutine
        tracking_response = Mock()
        tracking_response.json.return_value = {"url": "https://cdn.example.com/photo.jpg"}
        tracking_response.raise_for_status = Mock()

        image_response = Mock()
        image_response.content = b"fake-image-bytes"
        image_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get.side_effect = [tracking_response, image_response]
        mock_client_cls.return_value = mock_client

        photo = UnsplashPhoto(**PHOTO_DATA)
        client = AsyncUnsplash(access_key="key")
        result = await client.download(photo)

        assert result == b"fake-image-bytes"

        first_call = mock_client.get.call_args_list[0]
        assert first_call[0][0] == "https://api.unsplash.com/photos/abc123/download"

        second_call = mock_client.get.call_args_list[1]
        assert second_call[0][0] == "https://cdn.example.com/photo.jpg"

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_download_saves_to_path(
        self, mock_client_cls: Mock, tmp_path: pytest.TempPathFactory
    ) -> None:
        tracking_response = Mock()
        tracking_response.json.return_value = {"url": "https://cdn.example.com/photo.jpg"}
        tracking_response.raise_for_status = Mock()

        image_response = Mock()
        image_response.content = b"image-data"
        image_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get.side_effect = [tracking_response, image_response]
        mock_client_cls.return_value = mock_client

        photo = UnsplashPhoto(**PHOTO_DATA)
        dest = tmp_path / "photo.jpg"  # type: ignore[operator]
        client = AsyncUnsplash(access_key="key")
        result = await client.download(photo, path=dest)

        assert result == b"image-data"
        assert dest.read_bytes() == b"image-data"

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_download_tracking_uses_auth_header(self, mock_client_cls: Mock) -> None:
        tracking_response = Mock()
        tracking_response.json.return_value = {"url": "https://cdn.example.com/photo.jpg"}
        tracking_response.raise_for_status = Mock()

        image_response = Mock()
        image_response.content = b"img"
        image_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get.side_effect = [tracking_response, image_response]
        mock_client_cls.return_value = mock_client

        photo = UnsplashPhoto(**PHOTO_DATA)
        client = AsyncUnsplash(access_key="my-key")
        await client.download(photo)

        first_call_kwargs = mock_client.get.call_args_list[0][1]
        assert first_call_kwargs.get("headers", {}).get("Authorization") == "Client-ID my-key"


# ---------------------------------------------------------------------------
# aiter_pages() / aiter_media()
# ---------------------------------------------------------------------------


class TestAsyncUnsplashIterPages:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_aiter_pages_single_page(self, mock_client_cls: Mock) -> None:
        single_page = {"total": 5, "total_pages": 1, "results": [PHOTO_DATA]}
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, single_page)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        pages = []
        async for page in client.aiter_pages(UnsplashSearchParams(query="x")):
            pages.append(page)

        assert len(pages) == 1
        assert len(pages[0].results) == 1

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_aiter_pages_multiple_pages(self, mock_client_cls: Mock) -> None:
        page1 = {"total": 20, "total_pages": 2, "results": [PHOTO_DATA]}
        page2 = {"total": 20, "total_pages": 2, "results": [PHOTO_DATA]}

        mock_client = AsyncMock()
        mock_client.request.side_effect = [
            _make_response(200, page1),
            _make_response(200, page2),
        ]
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        pages = []
        async for page in client.aiter_pages(UnsplashSearchParams(query="x")):
            pages.append(page)

        assert len(pages) == 2

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_aiter_pages_stops_at_last_page(self, mock_client_cls: Mock) -> None:
        page1 = {"total": 10, "total_pages": 1, "results": [PHOTO_DATA]}
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(200, page1)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        async for _ in client.aiter_pages(UnsplashSearchParams(query="x")):
            pass

        assert mock_client.request.call_count == 1


class TestAsyncUnsplashIterMedia:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_aiter_media_flattens_pages(self, mock_client_cls: Mock) -> None:
        page1 = {"total": 20, "total_pages": 2, "results": [PHOTO_DATA]}
        page2 = {"total": 20, "total_pages": 2, "results": [PHOTO_DATA]}

        mock_client = AsyncMock()
        mock_client.request.side_effect = [
            _make_response(200, page1),
            _make_response(200, page2),
        ]
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        photos = []
        async for photo in client.aiter_media(UnsplashSearchParams(query="x")):
            photos.append(photo)

        assert len(photos) == 2
        assert all(p.id == "abc123" for p in photos)


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


class TestAsyncUnsplashRetry:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_retry_on_429(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.side_effect = [
            _make_response(429),
            _make_response(200, SEARCH_RESPONSE),
        ]
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key", max_retries=1)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await client.search(UnsplashSearchParams(query="x"))

        assert result.total == 50
        assert mock_client.request.call_count == 2

    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_no_retry_by_default(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client.request.return_value = _make_response(429)
        mock_client_cls.return_value = mock_client

        client = AsyncUnsplash(access_key="key")
        with pytest.raises(RateLimitError):
            await client.search(UnsplashSearchParams(query="x"))

        assert mock_client.request.call_count == 1


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestAsyncUnsplashContextManager:
    @patch("xanax.sources.unsplash.async_client.httpx.AsyncClient")
    async def test_async_context_manager_closes_client(self, mock_client_cls: Mock) -> None:
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        async with AsyncUnsplash(access_key="key"):
            pass

        mock_client.aclose.assert_called_once()
