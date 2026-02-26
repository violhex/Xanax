"""
Tests for xanax pagination helpers.
"""

import pytest

from xanax.models import PaginationMeta
from xanax.pagination import (
    PaginationHelper,
    get_next_page,
    get_total_pages,
    has_next_page,
)


class TestPaginationHelper:
    def test_current_page(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.current_page == 1

    def test_last_page(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.last_page == 10

    def test_per_page(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.per_page == 24

    def test_total(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.total == 240

    def test_has_next_when_not_last(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_next is True

    def test_has_next_when_last(self):
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_next is False

    def test_has_previous_when_not_first(self):
        meta = PaginationMeta(current_page=5, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_previous is True

    def test_has_previous_when_first(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.has_previous is False

    def test_seed(self):
        meta = PaginationMeta(
            current_page=1,
            last_page=10,
            per_page=24,
            total=240,
            seed="abc123",
        )
        helper = PaginationHelper(meta)
        assert helper.seed == "abc123"

    def test_seed_none(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.seed is None

    def test_next_page_number(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.next_page_number() == 2

    def test_next_page_number_none_at_last(self):
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.next_page_number() is None

    def test_previous_page_number(self):
        meta = PaginationMeta(current_page=5, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.previous_page_number() == 4

    def test_previous_page_number_none_at_first(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        helper = PaginationHelper(meta)
        assert helper.previous_page_number() is None


class TestHelperFunctions:
    def test_has_next_page_true(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        result = has_next_page(type("SearchResult", (), {"meta": meta})())
        assert result is True

    def test_has_next_page_false(self):
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        result = has_next_page(type("SearchResult", (), {"meta": meta})())
        assert result is False

    def test_get_next_page(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        result = get_next_page(type("SearchResult", (), {"meta": meta})())
        assert result == 2

    def test_get_next_page_none(self):
        meta = PaginationMeta(current_page=10, last_page=10, per_page=24, total=240)
        result = get_next_page(type("SearchResult", (), {"meta": meta})())
        assert result is None

    def test_get_total_pages(self):
        meta = PaginationMeta(current_page=1, last_page=10, per_page=24, total=240)
        result = get_total_pages(type("SearchResult", (), {"meta": meta})())
        assert result == 10
