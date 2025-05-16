import pytest

from src.bot.routers.printing.printing_tools import (
    count_of_pages_to_print,
    count_of_papers_to_print,
    recalculate_page_ranges,
    sub,
)


@pytest.mark.parametrize(
    "pages,page_ranges,number_up,sides,copies,expected",
    [
        (10, None, "1", "one-sided", "1", 10),  # print all pages
        (10, "1-4", "1", "one-sided", "1", 4),  # basic range
        (10, "1-4", "1", "two-sided", "1", 2),  # double-sided
        (10, "1-4", "4", "one-sided", "1", 1),  # 2x2 layout (4 pages on 1 sheet)
        (10, "1-8", "4", "one-sided", "1", 2),  # 2x2 layout (8 pages on 2 sheets)
        (10, "1-4", "1", "one-sided", "2", 8),  # multiple copies
        (10, "1-8", "4", "two-sided", "2", 2),  # complex case (8 pages, 2x2, double-sided, 2 copies)
    ],
)
def test_count_of_papers_to_print(pages, page_ranges, number_up, sides, copies, expected):
    assert count_of_papers_to_print(pages, page_ranges, number_up, sides, copies) == expected


@pytest.mark.parametrize(
    "input_iter,expected",
    [
        (iter([1, 5]), 5),  # basic range
        (iter([1]), 1),  # single page
        (iter([1, 2]), 2),  # consecutive pages
    ],
)
def test_sub(input_iter, expected):
    assert sub(input_iter) == expected


@pytest.mark.parametrize(
    "pages,page_ranges,expected",
    [
        (10, None, 10),  # print all pages
        (10, "1", 1),  # single page
        (10, "1-5", 5),  # page range
        (20, "1-5,7,9-12", 10),  # multiple ranges
        (20, "1-3,5-7,9,11-13", 10),  # complex ranges
        (10, "", 0),  # empty string
        (10, "1-15", 10),  # range exceeding total pages
        (10, "15", 0),  # single page exceeding total pages
        (10, "1-5,15", 5),  # mixed valid and invalid pages
    ],
)
def test_count_of_pages_to_print(pages, page_ranges, expected):
    assert count_of_pages_to_print(pages, page_ranges) == expected


@pytest.mark.parametrize(
    "page_range,number_up,expected",
    [
        ("1-5", "1", "1-5"),  # 1-up (no change)
        ("1-4", "4", "1-1"),  # 2x2 layout
        ("1-8", "4", "1-2"),  # 2x2 layout
        ("1-9", "9", "1-1"),  # 3x3 layout
        ("1-18", "9", "1-2"),  # 3x3 layout
        ("1-4,7,9-12", "4", "1-1,2,3-3"),  # mixed ranges
    ],
)
def test_recalculate_page_ranges(page_range, number_up, expected):
    assert recalculate_page_ranges(page_range, number_up) == expected


def test_edge_cases():
    # Test empty page range
    assert count_of_papers_to_print(10, "", "1", "one-sided", "1") == 0

    # Test single page
    assert count_of_papers_to_print(10, "1", "1", "one-sided", "1") == 1

    # Test zero copies
    assert count_of_papers_to_print(10, "1-4", "1", "one-sided", "0") == 0

    # Test zero total pages
    assert count_of_papers_to_print(0, None, "1", "one-sided", "1") == 0


def test_invalid_inputs():
    # Test invalid number_up
    with pytest.raises(ValueError, match="number_up must be positive"):
        count_of_papers_to_print(10, "1-4", "0", "one-sided", "1")

    # Test invalid page range format
    with pytest.raises(ValueError):
        count_of_pages_to_print(10, "1-2-3")

    # Test negative total pages
    with pytest.raises(ValueError, match="pages must be non-negative"):
        count_of_papers_to_print(-1, None, "1", "one-sided", "1")

    # Test negative pages in count_of_pages_to_print
    with pytest.raises(ValueError, match="pages must be non-negative"):
        count_of_pages_to_print(-1, "1-5")
