import pytest
from challenge import bubble_sort


@pytest.mark.parametrize(
    "array, expected",
    [
        ([64, 34, 25, 12, 22, 11, 90], [11, 12, 22, 25, 34, 64, 90]),
        ([], []),
        ([5], [5]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([4, 2, 4, 1, 3, 2], [1, 2, 2, 3, 4, 4]),
        ([-5, -10, 0, -3, 8], [-10, -5, -3, 0, 8]),
        ([1000, 10, 100000, 1, 10000], [1, 10, 1000, 10000, 100000]),
        ([7, -3, 0, 12, -5, 8], [-5, -3, 0, 7, 8, 12])
    ]
)
def test_bubble_sort(array, expected):
    assert bubble_sort(array) == expected
