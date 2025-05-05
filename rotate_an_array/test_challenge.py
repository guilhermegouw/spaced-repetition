import pytest
from challenge import rotate_an_array


@pytest.mark.parametrize(
    "array, k, expected",
    [
        ([1, 2, 3, 4, 5, 6, 7], 3, [5, 6, 7, 1, 2, 3, 4]),
        ([-1, -100, 3, 99], 2, [3, 99, -1, -100]),
        ([], 5, []),
        ([1], 3, [1]),
        ([1, 2], 0, [1, 2]),
        ([1, 2], 5, [2, 1]),
        ([1, 2, 3, 4], 12, [1, 2, 3, 4]),
        ([1, 2, 3, 4], 6, [3, 4, 1, 2]),
        ([2, 2, 2, 2], 1, [2, 2, 2, 2]),
        ([1, 2, 2, 3, 3, 4], 3, [2, 3, 3, 4, 1, 2]),
        (list(range(10)), 4, [6, 7, 8, 9, 0, 1, 2, 3, 4, 5]),
        ([-3, -2, -1, 0, 1, 2], 2, [1, 2, -3, -2, -1, 0]),
        ([1, 2, 3, 4, 5], 10**5, [1, 2, 3, 4, 5]),
    ]
)
def test_rotate_array(array, k, expected):
    assert rotate_an_array(array, k) == expected


def test_large_array_performance():
    large_array = list(range(10**4))
    large_k = 10**3
    result = rotate_an_array(large_array, large_k)
    expected = list(range(
        10**4 - large_k, 10**4)
    ) + list(range(0, 10**4 - large_k))
    assert result == expected


def test_k_greater_than_array_length():
    array = [1, 2, 3, 4]
    assert rotate_an_array(array, 5) == rotate_an_array(array, 1)
    assert rotate_an_array(array, 9) == rotate_an_array(array, 1)
