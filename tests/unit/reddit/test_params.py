"""
Tests for Reddit parameter models.
"""

import pytest
from pydantic import ValidationError

from xanax.enums import MediaType
from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter
from xanax.sources.reddit.params import RedditParams

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


class TestRedditParamsDefaults:
    def test_required_subreddit(self) -> None:
        params = RedditParams(subreddit="EarthPorn")
        assert params.subreddit == "EarthPorn"

    def test_default_sort(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.sort == RedditSort.HOT

    def test_default_time_filter(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.time_filter == RedditTimeFilter.ALL

    def test_default_limit(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.limit == 25

    def test_default_after(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.after is None

    def test_default_media_type(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.media_type == MediaType.ANY

    def test_default_include_nsfw(self) -> None:
        params = RedditParams(subreddit="x")
        assert params.include_nsfw is False


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestRedditParamsValidation:
    def test_limit_min(self) -> None:
        params = RedditParams(subreddit="x", limit=1)
        assert params.limit == 1

    def test_limit_max(self) -> None:
        params = RedditParams(subreddit="x", limit=100)
        assert params.limit == 100

    def test_limit_below_min_raises(self) -> None:
        with pytest.raises(ValidationError):
            RedditParams(subreddit="x", limit=0)

    def test_limit_above_max_raises(self) -> None:
        with pytest.raises(ValidationError):
            RedditParams(subreddit="x", limit=101)

    def test_subreddit_required(self) -> None:
        with pytest.raises(ValidationError):
            RedditParams()  # type: ignore[call-arg]

    def test_frozen(self) -> None:
        params = RedditParams(subreddit="EarthPorn")
        with pytest.raises((TypeError, ValidationError)):
            params.subreddit = "wallpapers"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Custom values
# ---------------------------------------------------------------------------


class TestRedditParamsCustomValues:
    def test_sort_top(self) -> None:
        params = RedditParams(subreddit="x", sort=RedditSort.TOP)
        assert params.sort == RedditSort.TOP

    def test_time_filter_week(self) -> None:
        params = RedditParams(subreddit="x", time_filter=RedditTimeFilter.WEEK)
        assert params.time_filter == RedditTimeFilter.WEEK

    def test_media_type_image(self) -> None:
        params = RedditParams(subreddit="x", media_type=MediaType.IMAGE)
        assert params.media_type == MediaType.IMAGE

    def test_include_nsfw_true(self) -> None:
        params = RedditParams(subreddit="x", include_nsfw=True)
        assert params.include_nsfw is True

    def test_after_cursor(self) -> None:
        params = RedditParams(subreddit="x", after="t3_abc123")
        assert params.after == "t3_abc123"

    def test_multi_subreddit(self) -> None:
        params = RedditParams(subreddit="EarthPorn+wallpapers")
        assert params.subreddit == "EarthPorn+wallpapers"


# ---------------------------------------------------------------------------
# with_after()
# ---------------------------------------------------------------------------


class TestRedditParamsWithAfter:
    def test_with_after_sets_cursor(self) -> None:
        params = RedditParams(subreddit="EarthPorn")
        next_params = params.with_after("t3_xyz789")
        assert next_params.after == "t3_xyz789"

    def test_with_after_preserves_other_fields(self) -> None:
        params = RedditParams(
            subreddit="EarthPorn",
            sort=RedditSort.TOP,
            time_filter=RedditTimeFilter.WEEK,
            limit=50,
            media_type=MediaType.IMAGE,
            include_nsfw=True,
        )
        next_params = params.with_after("t3_abc")
        assert next_params.subreddit == "EarthPorn"
        assert next_params.sort == RedditSort.TOP
        assert next_params.time_filter == RedditTimeFilter.WEEK
        assert next_params.limit == 50
        assert next_params.media_type == MediaType.IMAGE
        assert next_params.include_nsfw is True

    def test_with_after_returns_new_instance(self) -> None:
        params = RedditParams(subreddit="x")
        next_params = params.with_after("t3_abc")
        assert params is not next_params

    def test_with_after_original_unchanged(self) -> None:
        params = RedditParams(subreddit="x")
        params.with_after("t3_abc")
        assert params.after is None
