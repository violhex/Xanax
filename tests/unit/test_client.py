"""
Tests for xanax client.
"""

import pytest
from unittest.mock import Mock, patch

from xanax import Xanax
from xanax.enums import Purity
from xanax.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestXanaxInit:
    def test_default_init(self):
        client = Xanax()
        assert client.is_authenticated is False

    def test_with_api_key(self):
        client = Xanax(api_key="test-key-123")
        assert client.is_authenticated is True

    def test_repr(self):
        client = Xanax()
        assert "unauthenticated" in repr(client)

        client_with_key = Xanax(api_key="test")
        assert "authenticated" in repr(client_with_key)


class TestXanaxWallpaper:
    @patch("xanax.client.httpx.Client")
    def test_get_wallpaper_success(self, mock_client_cls):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
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
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()
        wallpaper = client.wallpaper("94x38z")

        assert wallpaper.id == "94x38z"
        assert wallpaper.resolution == "6742x3534"

    @patch("xanax.client.httpx.Client")
    def test_get_wallpaper_not_found(self, mock_client_cls):
        mock_response = Mock()
        mock_response.status_code = 404

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()

        with pytest.raises(NotFoundError):
            client.wallpaper("nonexistent")

    @patch("xanax.client.httpx.Client")
    def test_get_wallpaper_rate_limited(self, mock_client_cls):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()

        with pytest.raises(RateLimitError):
            client.wallpaper("94x38z")


class TestXanaxSearch:
    @patch("xanax.client.httpx.Client")
    def test_search_success(self, mock_client_cls):
        from xanax.search import SearchParams

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
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
                }
            ],
            "meta": {
                "current_page": 1,
                "last_page": 10,
                "per_page": 24,
                "total": 240,
            },
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()
        params = SearchParams(query="anime")
        result = client.search(params)

        assert len(result.data) == 1
        assert result.data[0].id == "94x38z"
        assert result.meta.total == 240

    def test_search_nsfw_without_key_raises(self):
        from xanax.search import SearchParams

        client = Xanax()

        with pytest.raises(AuthenticationError) as exc_info:
            client.search(SearchParams(purity=[Purity.NSFW]))

        assert "API key" in str(exc_info.value)

    def test_search_with_toplist_without_toplist_sorting_raises(self):
        from xanax.enums import Sort, TopRange
        from xanax.search import SearchParams

        client = Xanax()

        with pytest.raises(ValidationError):
            client.search(SearchParams(sorting=Sort.DATE_ADDED, top_range=TopRange.ONE_MONTH))


class TestXanaxTag:
    @patch("xanax.client.httpx.Client")
    def test_get_tag_success(self, mock_client_cls):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": 1,
                "name": "anime",
                "alias": "Chinese cartoons",
                "category_id": 1,
                "category": "Anime & Manga",
                "purity": "sfw",
                "created_at": "2015-01-16 02:06:45",
            }
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()
        tag = client.tag(1)

        assert tag.id == 1
        assert tag.name == "anime"


class TestXanaxCollections:
    @patch("xanax.client.httpx.Client")
    def test_get_collections_with_username(self, mock_client_cls):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": 15,
                    "label": "Default",
                    "views": 38,
                    "public": 1,
                    "count": 10,
                }
            ]
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client = Xanax()
        collections = client.collections(username="testuser")

        assert len(collections) == 1
        assert collections[0].label == "Default"

    def test_get_collections_no_username_no_key_raises(self):
        client = Xanax()

        with pytest.raises(AuthenticationError) as exc_info:
            client.collections()

        assert "API key" in str(exc_info.value)


class TestXanaxContextManager:
    @patch("xanax.client.httpx.Client")
    def test_context_manager(self, mock_client_cls):
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        with Xanax() as client:
            pass

        mock_client.close.assert_called_once()
