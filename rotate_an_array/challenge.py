"""
Title: Array Right Rotation

Description:
Write a function that rotates an array of integers to the right by k steps,
where k is a non-negative integer.

For example, with the array [1, 2, 3, 4, 5, 6, 7] and k = 3, the result should
be [5, 6, 7, 1, 2, 3, 4].

Rotation involves moving each element to the right by k positions. Elements
that would fall off the end of the array wrap around to the beginning.

Requirements:
1. The function should accept an array of integers and an integer k
2. The array should be rotated in-place if possible (without creating a
                                                     completely new array)
3. The function should handle cases where k is larger than the array length
4. Handle edge cases such as empty arrays or when k = 0

Examples:

Example 1:

Input: array = [1, 2, 3, 4, 5, 6, 7], k = 3
Output: [5, 6, 7, 1, 2, 3, 4]

Explanation: The array is rotated 3 steps to the right:
  [1, 2, 3, 4, 5, 6, 7]
→ [7, 1, 2, 3, 4, 5, 6]
→ [6, 7, 1, 2, 3, 4, 5]
→ [5, 6, 7, 1, 2, 3, 4]

Example 2:
Input: array = [-1, -100, 3, 99], k = 2
Output: [3, 99, -1, -100]
Explanation: The array is rotated 2 steps to the right:
  [-1, -100, 3, 99]
→ [99, -1, -100, 3]
→ [3, 99, -1, -100]

Example 3:
Input: array = [1, 2], k = 5
Output: [2, 1]
Explanation: Since k = 5 and array length = 2, we calculate k % 2 = 1, so we rotate once.
"""


def rotate_an_array(array, k):
    pass
