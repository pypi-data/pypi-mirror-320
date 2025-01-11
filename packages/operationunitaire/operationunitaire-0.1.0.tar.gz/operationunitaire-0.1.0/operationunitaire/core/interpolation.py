import numpy as np
from scipy.interpolate import interp1d
from operationunitaire.core.data_loader import DataLoader

class Interpolator:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def interpolate_volatility(self, temperature, component_name):
        """
        Interpolates or extrapolates the K-value for a given temperature and component.
        
        :param temperature: Temperature (float) for which to interpolate the K-value.
        :param component_name: Name of the component (e.g., 'C3').
        :return: Interpolated or extrapolated K-value (float).
        """
        component_data = self.data_loader.get_component_data(component_name)
        T = component_data.iloc[:, 0].values  # Temperature column
        K = component_data.iloc[:, 1].values  # Volatility column

        # Create interpolation function with extrapolation
        interp_function = interp1d(T, K, fill_value="extrapolate", bounds_error=False)

        # Debugging: Print details about the interpolation
        print(f"Interpolating for {component_name}: T={T}, K={K}, input_temperature={temperature}")

        return interp_function(temperature)

    def calculate_volatilities(self, stage_temperatures, feed_composition):
        """
        Calculates K-values for all components and stages, allowing for extrapolation.
        
        :param stage_temperatures: Dictionary of stage temperatures (e.g., {1: 65, 2: 100, ...}).
        :param feed_composition: Dictionary of feed composition (e.g., {'C3': 0.3, 'NC4': 0.3, 'NC5': 0.4}).
        :return: Dictionary of volatilities for each stage and component.
                 Format: {1: {'C3': K1_C3, 'NC4': K1_NC4, ...}, 2: {...}, ...}.
        """
        volatilities = {}
        for stage, temperature in stage_temperatures.items():
            volatilities[stage] = {}
            for component_name in feed_composition.keys():
                if component_name not in self.data_loader.data:
                    raise KeyError(f"Component '{component_name}' not in the loaded data.")
                volatilities[stage][component_name] = self.interpolate_volatility(temperature, component_name)
        return volatilities
