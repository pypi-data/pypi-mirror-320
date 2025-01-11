import math
from typing import List
import sympy as sp

def solve_quadratic(a: float, b: float, c: float) -> float | tuple[float, float] | None:
    d = b**2 - 4*a*c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2*a)
    else:
        return (-b + math.sqrt(d)) / (2*a), (-b - math.sqrt(d)) / (2*a)

def nth_term(*terms):
    """
    Determine the nth term formula for a given sequence.

    Args:
        terms: A sequence of integers representing the sequence.

    Returns:
        A string representing the nth term in simplified polynomial form.
    """
    if len(terms) < 2:
        raise ValueError("At least two terms are required to determine a pattern.")
    
    n = sp.symbols('n')
    indices = list(range(1, len(terms) + 1))
    polynomial = sp.interpolate(list(zip(indices, terms)), n)
    polynomial = sp.simplify(polynomial)
    formatted_polynomial = str(polynomial).replace("**", "^")
    formatted_polynomial = formatted_polynomial.replace("*", "")

    return formatted_polynomial