"""
Tests for Wallhaven search parameters.
"""

import pytest

from xanax.errors import ValidationError
from xanax.sources.wallhaven.enums import Category, Color, Order, Purity, Sort, TopRange
from xanax.sources.wallhaven.params import SearchParams


class TestSearchParams:
    def test_defaults(self) -> None:
        params = SearchParams()
        assert params.query is None
        assert params.categories == list(Category)
        assert params.purity == [Purity.SFW]
        assert params.sorting == Sort.DATE_ADDED
        assert params.order == Order.DESC
        assert params.top_range is None
        assert params.resolutions == []
        assert params.ratios == []
        assert params.colors == []
        assert params.page == 1
        assert params.seed is None

    def test_basic_search(self) -> None:
        params = SearchParams(query="anime")
        assert params.query == "anime"

    def test_with_purity(self) -> None:
        params = SearchParams(purity=[Purity.SFW, Purity.SKETCHY])
        assert params.purity == [Purity.SFW, Purity.SKETCHY]

    def test_with_sorting(self) -> None:
        params = SearchParams(sorting=Sort.RANDOM)
        assert params.sorting == Sort.RANDOM

    def test_with_toplist(self) -> None:
        params = SearchParams(
            sorting=Sort.TOPLIST,
            top_range=TopRange.ONE_MONTH,
        )
        assert params.sorting == Sort.TOPLIST
        assert params.top_range == TopRange.ONE_MONTH

    def test_top_range_without_toplist_fails(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SearchParams(
                sorting=Sort.DATE_ADDED,
                top_range=TopRange.ONE_MONTH,
            )

        assert "toplist" in str(exc_info.value).lower()

    def test_invalid_resolution_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SearchParams(resolutions=["invalid"])

        assert "resolution" in str(exc_info.value).lower()

    def test_invalid_ratio_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SearchParams(ratios=["invalid"])

        assert "ratio" in str(exc_info.value).lower()

    def test_invalid_seed_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SearchParams(seed="abc")

        assert "seed" in str(exc_info.value).lower()


class TestSearchParamsToQueryParams:
    def test_empty_params(self) -> None:
        params = SearchParams()
        query = params.to_query_params()
        assert query["sorting"] == "date_added"
        assert query["order"] == "desc"
        # Default categories is all three → "111"
        assert query["categories"] == "111"
        assert query["purity"] == "100"

    def test_with_query(self) -> None:
        params = SearchParams(query="anime")
        query = params.to_query_params()
        assert query["q"] == "anime"

    def test_with_multiple_purity(self) -> None:
        params = SearchParams(purity=[Purity.SFW, Purity.NSFW])
        query = params.to_query_params()
        assert query["purity"] == "101"

    def test_with_multiple_categories(self) -> None:
        params = SearchParams(categories=[Category.GENERAL, Category.ANIME])
        query = params.to_query_params()
        assert query["categories"] == "110"

    def test_single_category(self) -> None:
        params = SearchParams(categories=[Category.GENERAL])
        query = params.to_query_params()
        assert query["categories"] == "100"

    def test_toplist_includes_toprange(self) -> None:
        params = SearchParams(
            sorting=Sort.TOPLIST,
            top_range=TopRange.ONE_MONTH,
        )
        query = params.to_query_params()
        assert query["topRange"] == "1M"

    def test_page_not_included_when_1(self) -> None:
        params = SearchParams(page=1)
        query = params.to_query_params()
        assert "page" not in query

    def test_page_included_when_greater_than_1(self) -> None:
        params = SearchParams(page=5)
        query = params.to_query_params()
        assert query["page"] == 5

    def test_seed_included_when_provided(self) -> None:
        params = SearchParams(seed="abc123")
        query = params.to_query_params()
        assert query["seed"] == "abc123"

    def test_resolutions_joined(self) -> None:
        params = SearchParams(resolutions=["1920x1080", "2560x1440"])
        query = params.to_query_params()
        assert query["resolutions"] == "1920x1080,2560x1440"

    def test_ratios_joined(self) -> None:
        params = SearchParams(ratios=["16x9", "4x3"])
        query = params.to_query_params()
        assert query["ratios"] == "16x9,4x3"

    def test_colors_joined(self) -> None:
        params = SearchParams(colors=[Color.BLUE, Color.RED])
        query = params.to_query_params()
        assert query["colors"] == "0066cc,cc0000"


class TestSearchParamsWithPage:
    def test_with_page(self) -> None:
        params = SearchParams(query="anime")
        new_params = params.with_page(5)
        assert new_params.page == 5
        assert new_params.query == "anime"

    def test_preserves_other_params(self) -> None:
        params = SearchParams(
            query="test",
            categories=[Category.ANIME],
            sorting=Sort.RANDOM,
        )
        new_params = params.with_page(3)
        assert new_params.query == "test"
        assert new_params.categories == [Category.ANIME]
        assert new_params.sorting == Sort.RANDOM
        assert new_params.page == 3

    def test_with_page_validates(self) -> None:
        import pydantic

        params = SearchParams(query="anime")
        with pytest.raises(pydantic.ValidationError):
            params.with_page(0)


class TestSearchParamsWithSeed:
    def test_with_seed(self) -> None:
        params = SearchParams(sorting=Sort.RANDOM)
        new_params = params.with_seed("xyz123")
        assert new_params.seed == "xyz123"
        assert new_params.sorting == Sort.RANDOM

    def test_with_seed_validates(self) -> None:
        params = SearchParams(sorting=Sort.RANDOM)
        with pytest.raises(ValidationError):
            params.with_seed("bad")
