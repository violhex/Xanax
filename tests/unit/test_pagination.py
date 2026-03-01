"""
Tests for xanax pagination helpers.
"""


from xanax.models import PaginationMeta
from xanax.pagination import PaginationHelper


class TestPaginationHelper:
    def test_current_page(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.current_page == 1

    def test_last_page(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.last_page == 10

    def test_per_page(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.per_page == 24

    def test_total(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.total == 240

    def test_has_next_when_not_last(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_next is True

    def test_has_next_when_last(self) -> None:
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_next is False

    def test_has_previous_when_not_first(self) -> None:
        meta = PaginationMeta(current_page=5, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_previous is True

    def test_has_previous_when_first(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_previous is False

    def test_seed(self) -> None:
        meta = PaginationMeta(
            current_page=1,
            last_page=10,
            per_page=24,
            total=240,
            seed="abc123",
        )
        helper = PaginationHelper(meta)
        assert helper.seed == "abc123"

    def test_seed_none(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.seed is None

    def test_next_page_number(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.next_page_number() == 2

    def test_next_page_number_none_at_last(self) -> None:
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.next_page_number() is None

    def test_previous_page_number(self) -> None:
        meta = PaginationMeta(current_page=5, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.previous_page_number() == 4

    def test_previous_page_number_none_at_first(self) -> None:
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.previous_page_number() is None
