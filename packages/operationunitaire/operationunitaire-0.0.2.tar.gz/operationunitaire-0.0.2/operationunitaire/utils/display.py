from tabulate import tabulate

def display_results(stage_temperatures, feed_composition, vapor_flow_rates, feed_flow_rates, volatilities, results):
    print("\nInputs:")
    print(tabulate(stage_temperatures.items(), headers=["Stage", "Temperature (°C)"], tablefmt="fancy_grid"))
    print(tabulate(feed_composition.items(), headers=["Component", "Fraction"], tablefmt="fancy_grid"))
    print(tabulate(vapor_flow_rates.items(), headers=["Stage", "Vapor Flow (mol/s)"], tablefmt="fancy_grid"))
    print(tabulate(feed_flow_rates.items(), headers=["Stage", "Feed Flow (mol/s)"], tablefmt="fancy_grid"))

    print("\nCalculated Volatilities (K-values):")
    for stage, comps in volatilities.items():
        table = [[comp, k_value] for comp, k_value in comps.items()]
        print(f"\nStage {stage}:")
        print(tabulate(table, headers=["Component", "K-value"], tablefmt="fancy_grid"))

    print("\nLiquid Fractions:")
    for component, fractions in results.items():
        print(f"\nComponent: {component}")
        print(tabulate(enumerate(fractions, start=1), headers=["Stage", "Liquid Fraction"], tablefmt="fancy_grid"))
