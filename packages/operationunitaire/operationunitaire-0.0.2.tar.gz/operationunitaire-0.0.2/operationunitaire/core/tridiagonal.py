import numpy as np

def construct_tridiagonal_matrices(num_stages, coefficients, component):
    A = [coefficients[stage][component]["A"] for stage in range(1, num_stages + 1)]
    B = [coefficients[stage][component]["B"] for stage in range(1, num_stages + 1)]
    C = [coefficients[stage][component]["C"] for stage in range(1, num_stages + 1)]
    D = [coefficients[stage][component]["D"] for stage in range(1, num_stages + 1)]
    return A, B, C, D

def thomas_algorithm(A, B, C, D):
    n = len(B)
    C_prime = np.zeros(n - 1)
    D_prime = np.zeros(n)

    C_prime[0] = C[0] / B[0]
    D_prime[0] = D[0] / B[0]

    for i in range(1, n):
        divisor = B[i] - A[i - 1] * C_prime[i - 1]
        if i < n - 1:
            C_prime[i] = C[i] / divisor
        D_prime[i] = (D[i] - A[i - 1] * D_prime[i - 1]) / divisor

    F = np.zeros(n)
    F[-1] = D_prime[-1]
    for i in range(n - 2, -1, -1):
        F[i] = D_prime[i] - C_prime[i] * F[i + 1]

    return F
