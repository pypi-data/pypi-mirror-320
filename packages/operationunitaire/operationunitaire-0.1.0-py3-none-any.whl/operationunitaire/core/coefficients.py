def calculate_coefficients(num_stages, vapor_flow_rates, feed_flow_rates, formatted_volatilities, feed_composition):
    coefficients = {}
    for stage in range(1, num_stages + 1):
        coefficients[stage] = {}
        for component, fraction in feed_composition.items():
            V_j = vapor_flow_rates[stage]
            K_ij = formatted_volatilities[stage][component]
            F_j = feed_flow_rates[stage]  # Feed flow rate for the current stage
            z_ij = fraction  # Fraction of the feed composition

            # Calculate coefficients
            A_j = V_j + sum(feed_flow_rates.get(m, 0) for m in range(1, stage)) - vapor_flow_rates[1]
            B_j = -(vapor_flow_rates.get(stage + 1, 0) + sum(feed_flow_rates.get(m, 0) for m in range(1, stage + 1))
                    - vapor_flow_rates[1] + V_j * K_ij)
            C_j = vapor_flow_rates.get(stage + 1, 0) + K_ij
            D_j = -F_j * z_ij

            # Store coefficients
            coefficients[stage][component] = {
                "A": round(A_j, 4),
                "B": round(B_j, 4),
                "C": round(C_j, 4),
                "D": round(D_j, 4)
            }
    return coefficients
