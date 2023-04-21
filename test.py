from typing import List
import math


def min_array(nums: List[int]) -> int:
    res = nums[0]
    max_int = max(nums)
    max_idx = len(nums) - list(reversed(nums)).index(max_int) - 1
    total = sum(nums[:max_idx])
    for i in range(max_idx, len(nums)):
        total += nums[i]
        res = max(res, math.ceil(total / (i + 1)))

    return res


print(min_array([4, 7, 2, 2, 9, 19, 16, 0, 3, 15]))
