import pytest
from ensfc_stemm.calculations import calculate_mean

def test_calculate_mean():
    data = [1, 2, 3, 4, 5]
    result = calculate_mean(data)
    assert result == 3.0