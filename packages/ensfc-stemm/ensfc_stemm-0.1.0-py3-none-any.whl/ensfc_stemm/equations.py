import math
from typing import List

def solve_quadratic(a: float, b: float, c: float) -> float | tuple[float, float] | None:
    d = b**2 - 4*a*c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2*a)
    else:
        return (-b + math.sqrt(d)) / (2*a), (-b - math.sqrt(d)) / (2*a)
'''
def nth_term(*terms: float) -> List[float]:
    order = 1
    differences = [terms[i+1] - terms[i] for i in range(len(terms) - 1)]
    while len(set(differences)) > 1:
        differences = [differences[i+1] - differences[i] for i in range(len(differences) - 1)]
        order += 1
    
    return 0 if differences[0] == 0 else order
'''
