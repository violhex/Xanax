"""
Tests for xanax enums.
"""

import pytest

from xanax.enums import Category, Color, Order, Purity, Ratio, Sort, TopRange, Resolution, Seed


class TestCategory:
    def test_all_values(self):
        assert Category.GENERAL.value == "general"
        assert Category.ANIME.value == "anime"
        assert Category.PEOPLE.value == "people"


class TestPurity:
    def test_all_values(self):
        assert Purity.SFW.value == "sfw"
        assert Purity.SKETCHY.value == "sketchy"
        assert Purity.NSFW.value == "nsfw"


class TestSort:
    def test_all_values(self):
        assert Sort.DATE_ADDED.value == "date_added"
        assert Sort.RELEVANCE.value == "relevance"
        assert Sort.RANDOM.value == "random"
        assert Sort.VIEWS.value == "views"
        assert Sort.FAVORITES.value == "favorites"
        assert Sort.TOPLIST.value == "toplist"


class TestOrder:
    def test_all_values(self):
        assert Order.DESC.value == "desc"
        assert Order.ASC.value == "asc"


class TestTopRange:
    def test_all_values(self):
        assert TopRange.ONE_DAY.value == "1d"
        assert TopRange.THREE_DAYS.value == "3d"
        assert TopRange.ONE_WEEK.value == "1w"
        assert TopRange.ONE_MONTH.value == "1M"
        assert TopRange.THREE_MONTHS.value == "3M"
        assert TopRange.SIX_MONTHS.value == "6M"
        assert TopRange.ONE_YEAR.value == "1y"


class TestColor:
    def test_all_values(self):
        assert Color.MAROON.value == "660000"
        assert Color.BLACK.value == "000000"
        assert Color.WHITE.value == "ffffff"
        assert Color.CHARCOAL.value == "424153"


class TestResolution:
    def test_valid_resolutions(self):
        assert Resolution.validate("1920x1080") is True
        assert Resolution.validate("2560x1440") is True
        assert Resolution.validate("800x600") is True
        assert Resolution.validate("3840x2160") is True

    def test_invalid_resolutions(self):
        assert Resolution.validate("1920") is False
        assert Resolution.validate("invalid") is False
        assert Resolution.validate("1920x") is False
        assert Resolution.validate("x1080") is False

    def test_parse_valid(self):
        width, height = Resolution.parse("1920x1080")
        assert width == 1920
        assert height == 1080

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            Resolution.parse("invalid")


class TestRatio:
    def test_valid_ratios(self):
        assert Ratio.validate("16x9") is True
        assert Ratio.validate("16:9") is True
        assert Ratio.validate("4x3") is True
        assert Ratio.validate("21x9") is True

    def test_invalid_ratios(self):
        assert Ratio.validate("16") is False
        assert Ratio.validate("invalid") is False


class TestSeed:
    def test_generate_length(self):
        seed = Seed.generate()
        assert len(seed) == 6

    def test_generate_alphanumeric(self):
        seed = Seed.generate()
        assert seed.isalnum()

    def test_validate_valid_seeds(self):
        assert Seed.validate("abc123") is True
        assert Seed.validate("ABCDEF") is True
        assert Seed.validate("a1b2c3") is True

    def test_validate_invalid_seeds(self):
        assert Seed.validate("abc") is False
        assert Seed.validate("abc1234") is False
        assert Seed.validate("abc-12") is False
        assert Seed.validate("") is False
