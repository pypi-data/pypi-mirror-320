from .coefficients import calculate_coefficients
from .tridiagonal import construct_tridiagonal_matrices, thomas_algorithm

def solve_liquid_fractions(num_stages, vapor_flow_rates, feed_flow_rates, formatted_volatilities, feed_composition):
    coefficients = calculate_coefficients(num_stages, vapor_flow_rates, feed_flow_rates, formatted_volatilities, feed_composition)
    results = {}

    for component in feed_composition.keys():
        A, B, C, D = construct_tridiagonal_matrices(num_stages, coefficients, component)
        liquid_fractions = thomas_algorithm(A[1:], B, C[:-1], D)
        results[component] = liquid_fractions

    return results
