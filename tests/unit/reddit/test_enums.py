"""
Tests for Reddit enumerations.
"""

from xanax.sources.reddit.enums import RedditSort, RedditTimeFilter

# ---------------------------------------------------------------------------
# RedditSort
# ---------------------------------------------------------------------------


class TestRedditSort:
    def test_hot_value(self) -> None:
        assert RedditSort.HOT == "hot"

    def test_new_value(self) -> None:
        assert RedditSort.NEW == "new"

    def test_top_value(self) -> None:
        assert RedditSort.TOP == "top"

    def test_rising_value(self) -> None:
        assert RedditSort.RISING == "rising"

    def test_controversial_value(self) -> None:
        assert RedditSort.CONTROVERSIAL == "controversial"

    def test_all_members(self) -> None:
        members = {e.value for e in RedditSort}
        assert members == {"hot", "new", "top", "rising", "controversial"}

    def test_str_comparison(self) -> None:
        assert RedditSort.HOT == "hot"
        assert RedditSort.TOP != "hot"

    def test_is_str(self) -> None:
        assert isinstance(RedditSort.NEW, str)


# ---------------------------------------------------------------------------
# RedditTimeFilter
# ---------------------------------------------------------------------------


class TestRedditTimeFilter:
    def test_hour_value(self) -> None:
        assert RedditTimeFilter.HOUR == "hour"

    def test_day_value(self) -> None:
        assert RedditTimeFilter.DAY == "day"

    def test_week_value(self) -> None:
        assert RedditTimeFilter.WEEK == "week"

    def test_month_value(self) -> None:
        assert RedditTimeFilter.MONTH == "month"

    def test_year_value(self) -> None:
        assert RedditTimeFilter.YEAR == "year"

    def test_all_value(self) -> None:
        assert RedditTimeFilter.ALL == "all"

    def test_all_members(self) -> None:
        members = {e.value for e in RedditTimeFilter}
        assert members == {"hour", "day", "week", "month", "year", "all"}

    def test_is_str(self) -> None:
        assert isinstance(RedditTimeFilter.WEEK, str)
