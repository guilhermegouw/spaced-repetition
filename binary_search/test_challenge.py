import pytest
from challenge import binary_search


@pytest.mark.parametrize(
    "array, value, expected",
    [
        ([1, 3, 5, 7, 9, 11], 9, 4),
        ([1, 3, 5, 7, 9, 11], 1, 0),
        ([1, 3, 5, 7, 9, 11], 11, 5),
        ([], 5, -1),
        ([42], 42, 0),
        ([42], 99, -1),
        ([1, 3, 5, 7, 9], 0, -1),
        ([1, 3, 5, 7, 9], 10, -1),
        ([1, 3, 5, 7, 9], 4, -1),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 7, 6),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11, -1),
        ([-5, -3, 0, 2, 4], 0, 2),
        ([-5, -3, 0, 2, 4], -4, -1),
    ]
)
def test_binary_search(array, value, expected):
    assert binary_search(array, value) == expected
