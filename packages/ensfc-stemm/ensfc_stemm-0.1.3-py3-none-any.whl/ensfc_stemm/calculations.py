import statistics
from typing import List

def calculate_mean(data: List) -> float:
    '''
    Calculate the mean of a list of numbers using `statistics.mean()`.
    '''
    return statistics.mean(data)