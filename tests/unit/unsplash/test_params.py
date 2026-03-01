"""
Tests for Unsplash parameter models.
"""

import pydantic
import pytest

from xanax.sources.unsplash.enums import (
    UnsplashColor,
    UnsplashContentFilter,
    UnsplashOrderBy,
    UnsplashOrientation,
)
from xanax.sources.unsplash.params import UnsplashRandomParams, UnsplashSearchParams

# ---------------------------------------------------------------------------
# UnsplashSearchParams
# ---------------------------------------------------------------------------


class TestUnsplashSearchParams:
    def test_minimal(self) -> None:
        params = UnsplashSearchParams(query="mountains")
        assert params.query == "mountains"
        assert params.page == 1
        assert params.per_page == 10
        assert params.order_by == UnsplashOrderBy.RELEVANT
        assert params.collections == []
        assert params.content_filter == UnsplashContentFilter.LOW
        assert params.color is None
        assert params.orientation is None

    def test_page_minimum_is_one(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            UnsplashSearchParams(query="x", page=0)

    def test_per_page_minimum_is_one(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            UnsplashSearchParams(query="x", per_page=0)

    def test_per_page_maximum_is_thirty(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            UnsplashSearchParams(query="x", per_page=31)

    def test_per_page_thirty_is_valid(self) -> None:
        params = UnsplashSearchParams(query="x", per_page=30)
        assert params.per_page == 30

    def test_to_query_params_minimal(self) -> None:
        params = UnsplashSearchParams(query="mountains")
        result = params.to_query_params()
        assert result["q"] == "mountains"
        assert result["per_page"] == 10
        assert result["order_by"] == "relevant"
        assert "page" not in result  # page=1 is default, omitted
        assert "collections" not in result
        assert "content_filter" not in result  # LOW is default, omitted
        assert "color" not in result
        assert "orientation" not in result

    def test_to_query_params_with_page(self) -> None:
        params = UnsplashSearchParams(query="x", page=3)
        result = params.to_query_params()
        assert result["page"] == 3

    def test_to_query_params_with_collections(self) -> None:
        params = UnsplashSearchParams(query="x", collections=["col1", "col2"])
        result = params.to_query_params()
        assert result["collections"] == "col1,col2"

    def test_to_query_params_with_high_content_filter(self) -> None:
        params = UnsplashSearchParams(query="x", content_filter=UnsplashContentFilter.HIGH)
        result = params.to_query_params()
        assert result["content_filter"] == "high"

    def test_to_query_params_with_color(self) -> None:
        params = UnsplashSearchParams(query="x", color=UnsplashColor.BLUE)
        result = params.to_query_params()
        assert result["color"] == "blue"

    def test_to_query_params_with_orientation(self) -> None:
        params = UnsplashSearchParams(query="x", orientation=UnsplashOrientation.LANDSCAPE)
        result = params.to_query_params()
        assert result["orientation"] == "landscape"

    def test_to_query_params_with_order_by_latest(self) -> None:
        params = UnsplashSearchParams(query="x", order_by=UnsplashOrderBy.LATEST)
        result = params.to_query_params()
        assert result["order_by"] == "latest"

    def test_with_page(self) -> None:
        params = UnsplashSearchParams(query="mountains", page=1, color=UnsplashColor.GREEN)
        new_params = params.with_page(5)
        assert new_params.page == 5
        assert new_params.query == "mountains"
        assert new_params.color == UnsplashColor.GREEN

    def test_with_page_does_not_mutate_original(self) -> None:
        params = UnsplashSearchParams(query="x", page=1)
        _ = params.with_page(2)
        assert params.page == 1


# ---------------------------------------------------------------------------
# UnsplashRandomParams
# ---------------------------------------------------------------------------


class TestUnsplashRandomParams:
    def test_all_defaults(self) -> None:
        params = UnsplashRandomParams()
        assert params.collections == []
        assert params.topics == []
        assert params.username is None
        assert params.query is None
        assert params.orientation is None
        assert params.content_filter == UnsplashContentFilter.LOW

    def test_to_query_params_empty(self) -> None:
        params = UnsplashRandomParams()
        result = params.to_query_params()
        assert result == {}

    def test_to_query_params_with_query(self) -> None:
        params = UnsplashRandomParams(query="forest")
        result = params.to_query_params()
        assert result["query"] == "forest"

    def test_to_query_params_with_username(self) -> None:
        params = UnsplashRandomParams(username="natgeo")
        result = params.to_query_params()
        assert result["username"] == "natgeo"

    def test_to_query_params_with_collections(self) -> None:
        params = UnsplashRandomParams(collections=["abc", "def"])
        result = params.to_query_params()
        assert result["collections"] == "abc,def"

    def test_to_query_params_with_topics(self) -> None:
        params = UnsplashRandomParams(topics=["nature", "animals"])
        result = params.to_query_params()
        assert result["topics"] == "nature,animals"

    def test_to_query_params_with_orientation(self) -> None:
        params = UnsplashRandomParams(orientation=UnsplashOrientation.PORTRAIT)
        result = params.to_query_params()
        assert result["orientation"] == "portrait"

    def test_to_query_params_with_high_filter(self) -> None:
        params = UnsplashRandomParams(content_filter=UnsplashContentFilter.HIGH)
        result = params.to_query_params()
        assert result["content_filter"] == "high"

    def test_to_query_params_low_filter_omitted(self) -> None:
        params = UnsplashRandomParams(content_filter=UnsplashContentFilter.LOW)
        result = params.to_query_params()
        assert "content_filter" not in result
