"""
Enumerations and helpers for Wallhaven API parameters.

Provides type-safe options for search parameters and ensures only valid
values reach the API.
"""

from enum import StrEnum


class Category(StrEnum):
    """
    Wallpaper categories.

    - GENERAL: General wallpapers
    - ANIME: Anime and manga style
    - PEOPLE: People photography
    """

    GENERAL = "general"
    ANIME = "anime"
    PEOPLE = "people"


class Purity(StrEnum):
    """
    Content purity levels.

    - SFW: Safe for work
    - SKETCHY: May be questionable
    - NSFW: Not safe for work (requires API key)
    """

    SFW = "sfw"
    SKETCHY = "sketchy"
    NSFW = "nsfw"


class Sort(StrEnum):
    """
    Search result sorting options.

    - DATE_ADDED: Sort by upload date (default)
    - RELEVANCE: Sort by search relevance
    - RANDOM: Random ordering
    - VIEWS: Sort by view count
    - FAVORITES: Sort by favorites count
    - TOPLIST: Sort by toplist (requires ``top_range``)
    """

    DATE_ADDED = "date_added"
    RELEVANCE = "relevance"
    RANDOM = "random"
    VIEWS = "views"
    FAVORITES = "favorites"
    TOPLIST = "toplist"


class Order(StrEnum):
    """
    Sorting direction.

    - DESC: Descending (newest/highest first)
    - ASC: Ascending (oldest/lowest first)
    """

    DESC = "desc"
    ASC = "asc"


class TopRange(StrEnum):
    """
    Time range for toplist sorting.

    - ONE_DAY: Past 24 hours
    - THREE_DAYS: Past 3 days
    - ONE_WEEK: Past week
    - ONE_MONTH: Past month (default)
    - THREE_MONTHS: Past 3 months
    - SIX_MONTHS: Past 6 months
    - ONE_YEAR: Past year
    """

    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"
    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1y"


class Color(StrEnum):
    """Valid colors for color-based searching on Wallhaven."""

    MAROON = "660000"
    DARK_RED = "990000"
    RED = "cc0000"
    CRIMSON = "cc3333"
    PINK = "ea4c88"
    PURPLE = "993399"
    PLUM = "663399"
    INDIGO = "333399"
    BLUE = "0066cc"
    AZURE = "0099cc"
    CYAN = "66cccc"
    TEAL = "77cc33"
    GREEN = "669900"
    DARK_GREEN = "336600"
    OLIVE = "666600"
    YELLOW_GREEN = "999900"
    YELLOW = "cccc33"
    YELLOW_BRIGHT = "ffff00"
    ORANGE = "ffcc33"
    ORANGE_BRIGHT = "ff9900"
    VERMILLION = "ff6600"
    RED_ORANGE = "cc6633"
    BROWN = "996633"
    DARK_BROWN = "663300"
    BLACK = "000000"
    GREY = "999999"
    SILVER = "cccccc"
    WHITE = "ffffff"
    CHARCOAL = "424153"


class FileType(StrEnum):
    """File types for searching wallpapers."""

    PNG = "png"
    JPG = "jpg"


class Resolution:
    """Helper for validating and parsing wallpaper resolutions (``WIDTHxHEIGHT``)."""

    @staticmethod
    def validate(resolution: str) -> bool:
        parts = resolution.lower().split("x")
        if len(parts) != 2:
            return False
        try:
            width = int(parts[0])
            height = int(parts[1])
            return width >= 1 and height >= 1
        except ValueError:
            return False

    @staticmethod
    def parse(resolution: str) -> tuple[int, int]:
        parts = resolution.lower().split("x")
        if len(parts) != 2:
            raise ValueError(f"Invalid resolution format: {resolution}. Expected WIDTHxHEIGHT")
        width = int(parts[0])
        height = int(parts[1])
        if width < 1 or height < 1:
            raise ValueError(
                f"Invalid resolution values: {resolution}. "
                "Width and height must be positive integers."
            )
        return width, height


class Ratio:
    """Helper for validating and parsing aspect ratios (``WIDTH:HEIGHT`` or ``WIDTHxHEIGHT``)."""

    @staticmethod
    def validate(ratio: str) -> bool:
        parts = ratio.lower().split("x")
        if len(parts) != 2:
            parts = ratio.lower().split(":")
        if len(parts) != 2:
            return False
        try:
            width = float(parts[0])
            height = float(parts[1])
            return width > 0 and height > 0
        except ValueError:
            return False

    @staticmethod
    def parse(ratio: str) -> tuple[float, float]:
        parts = ratio.lower().split("x")
        if len(parts) != 2:
            parts = ratio.lower().split(":")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid ratio format: {ratio}. Expected WIDTH:HEIGHT or WIDTHxHEIGHT"
            )
        width = float(parts[0])
        height = float(parts[1])
        if width <= 0 or height <= 0:
            raise ValueError(
                f"Invalid ratio values: {ratio}. Width and height must be positive numbers."
            )
        return width, height


class Seed:
    """Helper for generating and validating random seeds (6 alphanumeric characters)."""

    LENGTH = 6

    @staticmethod
    def validate(seed: str) -> bool:
        return len(seed) == Seed.LENGTH and seed.isalnum()

    @staticmethod
    def generate() -> str:
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(Seed.LENGTH))
