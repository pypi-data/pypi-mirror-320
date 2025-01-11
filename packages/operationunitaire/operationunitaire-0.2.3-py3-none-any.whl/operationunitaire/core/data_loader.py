import os
import pandas as pd


class DataLoader:
    def __init__(self, data_folder=None):
        """
        Initialize the DataLoader.
        
        :param data_folder: Optional path to the folder containing the CSV files.
                            If None, it defaults to the package's internal `data` folder.
        """
        if data_folder is None:
            # Use the `data` folder inside the package
            data_folder = os.path.join(os.path.dirname(__file__), "data")
        
        if not os.path.exists(data_folder):
            raise FileNotFoundError(f"The data folder '{data_folder}' does not exist.")
        
        self.data_folder = data_folder
        self.data = {}

    def load_csv_files(self):
        """
        Load all CSV files in the data folder into a dictionary.
        The keys are component names derived from the filenames.
        """
        for file in os.listdir(self.data_folder):
            if file.endswith(".csv"):
                component_name = file.split(".")[0]
                file_path = os.path.join(self.data_folder, file)
                self.data[component_name] = pd.read_csv(file_path)
        if not self.data:
            raise ValueError("No CSV files found in the data folder.")

    def get_component_data(self, component_name):
        """
        Retrieve the DataFrame for a specific component.
        
        :param component_name: Name of the component (e.g., 'C3').
        :return: Pandas DataFrame with temperature and K values for the component.
        """
        if component_name not in self.data:
            raise KeyError(f"Component '{component_name}' not found in the data.")
        return self.data[component_name]
