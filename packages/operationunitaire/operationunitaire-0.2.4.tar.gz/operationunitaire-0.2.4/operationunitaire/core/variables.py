class StageVariables:
    def __init__(self, num_stages, V, F, K, z):
        """
        Initialize stage variables.

        :param num_stages: Total number of stages (int).
        :param V: List of vapor flow rates per stage [V1, V2, ..., Vn].
        :param F: List of feed flow rates per stage [F1, F2, ..., Fn].
        :param K: List of equilibrium constants per stage [K1, K2, ..., Kn].
        :param z: Feed composition per stage [z1, z2, ..., zn].
        """
        if len(V) != num_stages or len(F) != num_stages or len(K) != num_stages or len(z) != num_stages:
            raise ValueError("V, F, K, and z must have the same length as num_stages.")
        
        self.num_stages = num_stages
        self.V = V
        self.F = F
        self.K = K
        self.z = z

    def compute_A(self, j):
        """
        Compute A_j for stage j (0-indexed).
        :param j: Stage index (0-indexed).
        :return: Value of A_j.
        """
        return self.V[j] + sum(self.F[:j]) - self.V[0]

    def compute_B(self, j):
        """
        Compute B_j for stage j (0-indexed).
        :param j: Stage index (0-indexed).
        :return: Value of B_j.
        """
        return -(self.V[j + 1] + sum(self.F[:j + 1]) - self.V[0] + self.V[j] * self.K[j])

    def compute_C(self, j):
        """
        Compute C_j for stage j (0-indexed).
        :param j: Stage index (0-indexed).
        :return: Value of C_j.
        """
        if j == self.num_stages - 1:
            return 0  # No stage above the last one
        return self.V[j + 1] + self.K[j + 1]

    def compute_D(self, j):
        """
        Compute D_j for stage j (0-indexed).
        :param j: Stage index (0-indexed).
        :return: Value of D_j.
        """
        return -self.F[j] * self.z[j]

    def get_variables(self, j):
        """
        Get A_j, B_j, C_j, D_j for stage j.
        :param j: Stage index (1-indexed for external calls).
        :return: Tuple (A_j, B_j, C_j, D_j)
        """
        if j < 1 or j > self.num_stages:
            raise ValueError(f"Stage index {j} out of bounds (1 to {self.num_stages}).")
        j_index = j - 1  # Convert to 0-indexed
        return self.compute_A(j_index), self.compute_B(j_index), self.compute_C(j_index), self.compute_D(j_index)
