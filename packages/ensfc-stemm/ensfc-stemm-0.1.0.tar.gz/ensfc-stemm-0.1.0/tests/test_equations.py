from ensfc_stemm.equations import solve_quadratic

def test_solve_quadratic():
    coeffs = [1, 10, 25]
    roots = solve_quadratic(coeffs[0], coeffs[1], coeffs[2])
    assert roots == -5.0