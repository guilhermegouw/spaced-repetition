"""
Description: Implement a binary search algorithm that searches for a target
value in a sorted array of integers. Your function should return the index of
the target if found, or -1 if the target is not present in the array.

Requirements:
    - Your solution must have O(log n) time complexity
    - The array is guaranteed to be sorted in ascending order
    - Handle edge cases appropriately (empty array, target not found)
    - Provide a brief explanation of your approach

Input:
    array = [1, 3, 5, 7, 9, 11]
    value = 9
Output:
    4
"""


def binary_search(array, value):
    """
    This is a classical binary seach implementation where each iteration
    reduces the possibilities in half by tracking a middle possition and
    updating the extremes based on that.
    """
    left = 0
    right = len(array) - 1
    while left <= right:
        middle = (left + right) // 2
        if array[middle] == value:
            return middle
        elif array[middle] < value:
            left = middle + 1
        else:
            right = middle - 1
    return -1


binary_search([1, 3, 5, 7, 9, 11], 11)
