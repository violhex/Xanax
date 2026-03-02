"""
MediaType enumeration — internal module.

Defined here to avoid circular imports between xanax.enums (which re-exports
Wallhaven enums that trigger xanax.sources.__init__) and source packages
that need MediaType at import time.

External code should import MediaType from xanax.enums, not this module.
"""

from enum import StrEnum


class MediaType(StrEnum):
    """
    Type of media returned by a source.

    Used for filtering in :class:`~xanax.sources.reddit.params.RedditParams`
    and carried on media objects that can be images, videos, or GIFs.

    - IMAGE: Static image (jpg, png, webp, …)
    - VIDEO: Video file (mp4, …)
    - GIF:   Animated GIF or silent looping video
    - ANY:   No filter — include all media types
    """

    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    ANY = "any"
