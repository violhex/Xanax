"""
Tests for Unsplash enums.
"""

from xanax.sources.unsplash.enums import (
    UnsplashColor,
    UnsplashContentFilter,
    UnsplashOrderBy,
    UnsplashOrientation,
)


class TestUnsplashOrientation:
    def test_values(self) -> None:
        assert UnsplashOrientation.LANDSCAPE == "landscape"
        assert UnsplashOrientation.PORTRAIT == "portrait"
        assert UnsplashOrientation.SQUARISH == "squarish"

    def test_str_behaviour(self) -> None:
        assert str(UnsplashOrientation.LANDSCAPE) == "landscape"

    def test_is_str_enum(self) -> None:
        assert isinstance(UnsplashOrientation.LANDSCAPE, str)


class TestUnsplashColor:
    def test_values(self) -> None:
        assert UnsplashColor.BLACK_AND_WHITE == "black_and_white"
        assert UnsplashColor.BLACK == "black"
        assert UnsplashColor.WHITE == "white"
        assert UnsplashColor.BLUE == "blue"
        assert UnsplashColor.RED == "red"
        assert UnsplashColor.GREEN == "green"

    def test_all_members_are_str(self) -> None:
        for member in UnsplashColor:
            assert isinstance(member, str)


class TestUnsplashOrderBy:
    def test_values(self) -> None:
        assert UnsplashOrderBy.RELEVANT == "relevant"
        assert UnsplashOrderBy.LATEST == "latest"

    def test_is_str_enum(self) -> None:
        assert isinstance(UnsplashOrderBy.RELEVANT, str)


class TestUnsplashContentFilter:
    def test_values(self) -> None:
        assert UnsplashContentFilter.LOW == "low"
        assert UnsplashContentFilter.HIGH == "high"

    def test_is_str_enum(self) -> None:
        assert isinstance(UnsplashContentFilter.LOW, str)
