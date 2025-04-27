"""
Description: Implement a bubble sort algorithm that sorts an array of integers
in ascending order. Your function should return the sorted array.

Requirements:
    - Your solution must correctly sort the input array using the bubble sort
    algorithm.
    - Handle edge cases appropriately (empty array, already sorted array).
    - Optimize your implementation to stop early if the array becomes sorted
    before all passes are complete.
    - Provide a brief explanation of your approach.

Input:
    array = [64, 34, 25, 12, 22, 11, 90]
Output:
    [11, 12, 22, 25, 34, 64, 90]
"""


def bubble_sort(array):
    """
    Classic bubble sort implementation where it 'bubbles' the highest values
    to the end of the array by swaps. It tracks the number of swaps during the
    process and stop early in case of no swaps (the array is already sorted).
    """
    is_sorted = False
    limit = len(array)
    while not is_sorted:
        swaps = 0
        for i in range(1, limit):
            if array[i] < array[i - 1]:
                array[i - 1], array[i] = array[i], array[i - 1]
                swaps += 1
        limit -= 1
        if swaps == 0:
            is_sorted = True
    return array
