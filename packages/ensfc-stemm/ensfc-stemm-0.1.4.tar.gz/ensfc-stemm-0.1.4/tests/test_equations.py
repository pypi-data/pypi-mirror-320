from ensfc_stemm.equations import solve_quadratic, nth_term

def test_solve_quadratic():
    coeffs = [1, 10, 25]
    roots = solve_quadratic(coeffs[0], coeffs[1], coeffs[2])
    assert roots == -5.0

def test_nth_term():
    terms = [1, 4, 9, 16, 25]
    nth = nth_term(*terms)
    assert nth == "n^2"

    terms = [2, 4, 8, 16]
    nth = nth_term(*terms)
    assert nth == "n(n^2 - 3n + 8)/3"