from operationunitaire.core.data_loader import DataLoader
from operationunitaire.core.interpolation import Interpolator
from operationunitaire.core.solver import solve_liquid_fractions
from operationunitaire.utils.display import display_results


def run_simulation(stage_temperatures, feed_composition, vapor_flow_rates, feed_flow_rates):
    """
    Run the distillation simulation.

    :param stage_temperatures: Dictionary of temperatures for each stage.
    :param feed_composition: Dictionary of feed composition fractions.
    :param vapor_flow_rates: Dictionary of vapor flow rates for each stage.
    :param feed_flow_rates: Dictionary of feed flow rates for each stage.
    """
    # Default path to the data folder (can be made configurable)
    data_folder = "data"

    # Load component data
    data_loader = DataLoader(data_folder)
    data_loader.load_csv_files()

    # Calculate volatilities
    interpolator = Interpolator(data_loader)
    volatilities = interpolator.calculate_volatilities(stage_temperatures, feed_composition)

    # Solve for liquid fractions
    num_stages = len(stage_temperatures)
    results = solve_liquid_fractions(
        num_stages, vapor_flow_rates, feed_flow_rates, volatilities, feed_composition
    )

    # Display results
    display_results(stage_temperatures, feed_composition, vapor_flow_rates, feed_flow_rates, volatilities, results)
